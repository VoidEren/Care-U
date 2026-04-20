#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import textwrap
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional

STORE_FILE = "flashlearn.json"
DATE_FMT = "%Y-%m-%d"

# --------------------------------------------------------------------------------------
# Modelo de datos
# --------------------------------------------------------------------------------------

@dataclass
class Card:
    id: int
    front: str
    back: str
    deck: str
    # Parámetros SM-2 simplificados
    ease: float = 2.5           # Factor de facilidad
    interval: int = 0           # Intervalo (días)
    repetition: int = 0         # Repeticiones seguidas exitosas
    due: str = field(default_factory=lambda: datetime.now().strftime(DATE_FMT))  # fecha de próxima revisión

    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    lapses: int = 0             # Veces que se ha fallado

    def is_due(self, day: datetime) -> bool:
        try:
            return day.date() >= datetime.strptime(self.due, DATE_FMT).date()
        except Exception:
            return True

@dataclass
class Deck:
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

@dataclass
class Store:
    meta: Dict = field(default_factory=dict)
    decks: Dict[str, Deck] = field(default_factory=dict)
    cards: Dict[int, Card] = field(default_factory=dict)
    next_id: int = 1

    def add_deck(self, name: str, description: str = ""):
        name = name.strip()
        if not name:
            raise ValueError("El nombre del mazo no puede estar vacío.")
        if name in self.decks:
            raise ValueError("Ese mazo ya existe.")
        self.decks[name] = Deck(name=name, description=description)
        self._touch_deck(name)

    def _touch_deck(self, name: str):
        d = self.decks[name]
        d.updated_at = datetime.now().isoformat(timespec="seconds")

    def add_card(self, deck: str, front: str, back: str) -> int:
        if deck not in self.decks:
            raise ValueError("El mazo no existe.")
        cid = self.next_id
        self.next_id += 1
        c = Card(id=cid, front=front.strip(), back=back.strip(), deck=deck)
        self.cards[cid] = c
        self._touch_deck(deck)
        return cid

    def find_cards_by_deck(self, deck: str) -> List[Card]:
        return [c for c in self.cards.values() if c.deck == deck]

    def stats(self) -> Dict[str, Dict[str, int]]:
        today = datetime.now()
        res = {}
        for d in self.decks:
            cards = self.find_cards_by_deck(d)
            total = len(cards)
            due = sum(1 for c in cards if c.is_due(today))
            new = sum(1 for c in cards if c.repetition == 0)
            res[d] = {"total": total, "vencidas": due, "nuevas": new}
        return res

# --------------------------------------------------------------------------------------
# Persistencia
# --------------------------------------------------------------------------------------

def load_store() -> Store:
    if not os.path.exists(STORE_FILE):
        s = Store(meta={"created": datetime.now().isoformat(timespec="seconds")})
        save_store(s)
        return s
    with open(STORE_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Reconstrucción manual de dataclasses
    s = Store(meta=raw.get("meta", {}),
              decks={k: Deck(**v) for k, v in raw.get("decks", {}).items()},
              cards={}, next_id=raw.get("next_id", 1))
    for cid, cdict in raw.get("cards", {}).items():
        cdict["id"] = int(cdict["id"]) if "id" in cdict else int(cid)
        s.cards[int(cid)] = Card(**cdict)
    return s

def save_store(s: Store):
    data = {
        "meta": s.meta,
        "decks": {k: asdict(v) for k, v in s.decks.items()},
        "cards": {str(k): asdict(v) for k, v in s.cards.items()},
        "next_id": s.next_id
    }
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --------------------------------------------------------------------------------------
# Utilidades de impresión
# --------------------------------------------------------------------------------------

def hr(char="─", width=70):
    print(char * width)

def wrap(s: str, width: int = 72) -> str:
    return "\n".join(textwrap.wrap(s, width=width)) if s else ""

def print_title(title: str):
    hr("=")
    print(title)
    hr("=")

def print_table(rows: List[List[str]], headers: Optional[List[str]] = None, width: int = 20):
    if headers:
        print(" | ".join(h.ljust(width) for h in headers))
        print("-+-".join("-" * width for _ in headers))
    for r in rows:
        print(" | ".join((r[i] if i < len(r) else "").ljust(width) for i in range(len(headers or r))))
    print()

# --------------------------------------------------------------------------------------
# SM-2 Simplificado
# --------------------------------------------------------------------------------------

def sm2_update(card: Card, quality: int):
    """
    quality: 0..5
    - 0-2 = fallo (reset repetición, intervalo = 1, ease -= 0.2)
    - 3-5 = éxito (repetición +=1, actualiza intervalo según SM-2)
    """
    now = datetime.now()
    card.updated_at = now.isoformat(timespec="seconds")

    quality = max(0, min(5, int(quality)))

    if quality < 3:
        card.repetition = 0
        card.interval = 1
        card.ease = max(1.3, card.ease - 0.2)
        card.lapses += 1
    else:
        if card.repetition == 0:
            card.interval = 1
        elif card.repetition == 1:
            card.interval = 6
        else:
            # int(round(interval * ease))
            card.interval = int(round(card.interval * card.ease))
        card.repetition += 1
        # Actualizar ease (E-Factor)
        card.ease = max(1.3, card.ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    # Programar siguiente fecha
    card.due = (now + timedelta(days=card.interval)).strftime(DATE_FMT)

# --------------------------------------------------------------------------------------
# Búsqueda y filtrado
# --------------------------------------------------------------------------------------

def search_cards(s: Store, text: str, deck: Optional[str] = None) -> List[Card]:
    text = text.lower().strip()
    cards = list(s.cards.values())
    if deck:
        cards = [c for c in cards if c.deck == deck]
    if not text:
        return cards
    res = []
    for c in cards:
        if text in c.front.lower() or text in c.back.lower():
            res.append(c)
    return res

def due_cards(s: Store, deck: Optional[str], limit: int = 50) -> List[Card]:
    today = datetime.now()
    cards = list(s.cards.values())
    if deck:
        cards = [c for c in cards if c.deck == deck]
    cards = [c for c in cards if c.is_due(today)]
    random.shuffle(cards)
    return cards[:limit]

# --------------------------------------------------------------------------------------
# Interfaz de línea de comandos (CLI)
# --------------------------------------------------------------------------------------

def menu() -> str:
    print_title("FlashLearn – Repaso espaciado (SM-2)")
    print("1) Crear mazo")
    print("2) Listar mazos")
    print("3) Añadir tarjeta")
    print("4) Buscar tarjetas")
    print("5) Estudiar (sesión)")
    print("6) Estadísticas")
    print("7) Editar/Eliminar tarjeta")
    print("0) Salir")
    return input("> Elige una opción: ").strip()

def cli_create_deck(s: Store):
    print_title("Crear mazo")
    name = input("Nombre del mazo: ").strip()
    desc = input("Descripción (opcional): ").strip()
    try:
        s.add_deck(name, desc)
        save_store(s)
        print("✅ Mazo creado.")
    except Exception as e:
        print(f"❌ {e}")

def cli_list_decks(s: Store):
    print_title("Mazos")
    if not s.decks:
        print("No hay mazos aún. Crea uno con la opción 1.")
        return
    rows = []
    st = s.stats()
    for name, d in s.decks.items():
        rows.append([
            name,
            st.get(name, {}).get("total", 0),
            st.get(name, {}).get("vencidas", 0),
            st.get(name, {}).get("nuevas", 0),
            d.updated_at
        ])
    print_table(rows, headers=["Mazo", "Total", "Vencidas", "Nuevas", "Actualizado"], width=16)

def cli_add_card(s: Store):
    print_title("Añadir tarjeta")
    if not s.decks:
        print("Primero crea un mazo (opción 1).")
        return
    deck = choose_deck(s, allow_all=False)
    if not deck:
        print("Operación cancelada.")
        return
    print("\nEscribe el anverso (pregunta / concepto). Finaliza con una línea vacía:")
    front = read_multiline()
    print("\nEscribe el reverso (respuesta / definición). Finaliza con una línea vacía:")
    back = read_multiline()
    if not front or not back:
        print("❌ La tarjeta necesita anverso y reverso.")
        return
    cid = s.add_card(deck, front, back)
    save_store(s)
    print(f"✅ Tarjeta #{cid} añadida al mazo '{deck}'.")

def read_multiline() -> str:
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()

def choose_deck(s: Store, allow_all: bool = True) -> Optional[str]:
    names = sorted(s.decks.keys())
    if not names:
        return None
    print("\nMazos disponibles:")
    for i, n in enumerate(names, 1):
        print(f"  {i}) {n}")
    if allow_all:
        print(f"  0) (Todos los mazos)")
    idx = input("> Selecciona: ").strip()
    if allow_all and idx == "0":
        return None
    try:
        i = int(idx) - 1
        if 0 <= i < len(names):
            return names[i]
    except ValueError:
        pass
    print("Selección inválida.")
    return None

def cli_search(s: Store):
    print_title("Buscar tarjetas")
    if not s.cards:
        print("No hay tarjetas aún.")
        return
    deck = choose_deck(s, allow_all=True)
    text = input("Texto a buscar (vacío = todas): ").strip()
    results = search_cards(s, text, deck)
    if not results:
        print("No se encontraron tarjetas.")
        return
    print_cards_list(results)

def print_cards_list(cards: List[Card]):
    rows = []
    for c in sorted(cards, key=lambda x: (x.deck, x.id)):
        rows.append([
            str(c.id),
            c.deck,
            preview(c.front),
            preview(c.back),
            f"{c.repetition}",
            f"{c.interval}d",
            f"{c.ease:.2f}",
            c.due
        ])
    print_table(rows, headers=["ID", "Mazo", "Front", "Back", "Rep", "Int", "Ease", "Due"], width=14)

def preview(s: str, n: int = 22) -> str:
    flat = " ".join(s.split())
    return flat if len(flat) <= n else flat[: n - 1] + "…"

# --------------------------------------------------------------------------------------
# Estudio
# --------------------------------------------------------------------------------------

def cli_study(s: Store):
    print_title("Estudiar")
    if not s.decks:
        print("Crea un mazo primero.")
        return
    deck = choose_deck(s, allow_all=True)
    limit = ask_int("¿Cuántas tarjetas (máx 50)? ", 1, 50, default=20)
    cards = due_cards(s, deck, limit=limit)
    if not cards:
        print("🎉 ¡No tienes tarjetas vencidas por hoy!")
        return
    print(f"Revisaremos {len(cards)} tarjeta(s). Califica 0..5 (0=olvido total, 5=perfecto).")
    hr()
    studied = 0
    again: List[Card] = []
    for c in cards:
        studied += 1
        print(f"[{studied}/{len(cards)}] #{c.id} | Mazo: {c.deck} | Rep: {c.repetition} | Int: {c.interval}d | Ease: {c.ease:.2f}")
        hr("-")
        print(wrap(c.front))
        input("\nPulsa ENTER para ver la respuesta…")
        print("\n" + wrap(c.back))
        q = ask_int("Califica (0..5): ", 0, 5, default=3)
        before_due = c.due
        sm2_update(c, q)
        save_store(s)
        print(f"→ Intervalo: {before_due} → próximo en {c.interval} día(s), due={c.due}, ease={c.ease:.2f}\n")
        # Si la calificación es muy baja, la reponemos una vez en la misma sesión
        if q <= 2:
            again.append(c)

    # Repetición rápida de fallos (sólo una ronda)
    if again:
        print_title("Repetición rápida de fallos")
        for c in again:
            print(f"#{c.id} ({c.deck})")
            print(wrap(c.front))
            input("\nENTER → respuesta…")
            print("\n" + wrap(c.back))
            q = ask_int("Califica (0..5): ", 0, 5, default=3)
            before_due = c.due
            sm2_update(c, q)
            save_store(s)
            print(f"→ Intervalo: {before_due} → próximo en {c.interval} día(s), due={c.due}, ease={c.ease:.2f}\n")

    print("✅ Sesión finalizada.")

def ask_int(prompt: str, lo: int, hi: int, default: Optional[int] = None) -> int:
    while True:
        s = input(prompt).strip()
        if s == "" and default is not None:
            return default
        try:
            v = int(s)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print(f"Ingresa un número entre {lo} y {hi}.")

# --------------------------------------------------------------------------------------
# Edición y eliminación
# --------------------------------------------------------------------------------------

def cli_edit_or_delete(s: Store):
    print_title("Editar / Eliminar tarjeta")
    if not s.cards:
        print("No hay tarjetas aún.")
        return
    try:
        cid = int(input("ID de tarjeta: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    c = s.cards.get(cid)
    if not c:
        print("No existe esa tarjeta.")
        return
    print("\nTarjeta actual:")
    print(f"Deck : {c.deck}")
    print(f"Front: {c.front}")
    print(f"Back : {c.back}")
    print(f"Rep  : {c.repetition}  Int: {c.interval}d  Ease: {c.ease:.2f}  Due: {c.due}")
    print("\n1) Editar texto")
    print("2) Mover a otro mazo")
    print("3) Resetear aprendizaje (repetition/interval)")
    print("4) Eliminar")
    print("0) Cancelar")
    opt = input("> Opción: ").strip()
    if opt == "1":
        new_front = input("Nuevo front (vacío = mantener): ")
        new_back = input("Nuevo back  (vacío = mantener): ")
        if new_front.strip():
            c.front = new_front.strip()
        if new_back.strip():
            c.back = new_back.strip()
        c.updated_at = datetime.now().isoformat(timespec="seconds")
        save_store(s)
        print("✅ Actualizado.")
    elif opt == "2":
        deck = choose_deck(s, allow_all=False)
        if not deck:
            print("Cancelado.")
            return
        c.deck = deck
        c.updated_at = datetime.now().isoformat(timespec="seconds")
        save_store(s)
        print("✅ Movido.")
    elif opt == "3":
        c.repetition = 0
        c.interval = 0
        c.ease = 2.5
        c.due = datetime.now().strftime(DATE_FMT)
        c.lapses = 0
        c.updated_at = datetime.now().isoformat(timespec="seconds")
        save_store(s)
        print("✅ Reseteado.")
    elif opt == "4":
        confirm = input("¿Seguro? Escribe 'ELIMINAR' para confirmar: ").strip()
        if confirm == "ELIMINAR":
            del s.cards[cid]
            save_store(s)
            print("🗑️  Eliminada.")
        else:
            print("Cancelado.")
    else:
        print("Cancelado.")

# --------------------------------------------------------------------------------------
# Estadísticas
# --------------------------------------------------------------------------------------

def cli_stats(s: Store):
    print_title("Estadísticas")
    st = s.stats()
    if not st:
        print("No hay mazos.")
        return
    rows = []
    for deck, d in st.items():
        rows.append([deck, str(d["total"]), str(d["vencidas"]), str(d["nuevas"])])
    print_table(rows, headers=["Mazo", "Total", "Vencidas hoy", "Nuevas"], width=16)

    # Top tarjetas más difíciles (por lapses)
    difficult = sorted(s.cards.values(), key=lambda c: (-c.lapses, c.ease))[:10]
    if difficult:
        print("Top 10 tarjetas con más fallos (lapses):")
        rows = []
        for c in difficult:
            rows.append([str(c.id), c.deck, str(c.lapses), f"{c.ease:.2f}", preview(c.front, 30)])
        print_table(rows, headers=["ID", "Mazo", "Lapses", "Ease", "Front"], width=14)

# --------------------------------------------------------------------------------------
# Main loop
# --------------------------------------------------------------------------------------

def main():
    s = load_store()
    while True:
        try:
            opt = menu()
            if opt == "1":
                cli_create_deck(s)
            elif opt == "2":
                cli_list_decks(s)
            elif opt == "3":
                cli_add_card(s)
            elif opt == "4":
                cli_search(s)
            elif opt == "5":
                cli_study(s)
            elif opt == "6":
                cli_stats(s)
            elif opt == "7":
                cli_edit_or_delete(s)
            elif opt == "0":
                print("¡Nos vemos! 📚")
                break
            else:
                print("Opción inválida.")
            input("\n(ENTER para continuar) ")
        except KeyboardInterrupt:
            print("\nInterrumpido. Guardando…")
            save_store(s)
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            input("(ENTER para continuar) ")

if __name__ == "__main__":
    main()
