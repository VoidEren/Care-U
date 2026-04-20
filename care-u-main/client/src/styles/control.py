# ================================================================
# PROGRAMA MULTIFUNCIÓN EN PYTHON (300+ LÍNEAS) - VERSIÓN 2
# Autor: ChatGPT (GPT-5)
# Descripción:
# Este programa ofrece tres módulos:
#   1. Calculadora científica
#   2. Conversor de unidades
#   3. Generador de contraseñas
# ================================================================

import math
import random
import string
import time

# ================================================================
# CLASE 1: CALCULADORA CIENTÍFICA
# ================================================================

class Calculadora:
    def __init__(self):
        pass

    def sumar(self, a, b):
        return a + b

    def restar(self, a, b):
        return a - b

    def multiplicar(self, a, b):
        return a * b

    def dividir(self, a, b):
        if b == 0:
            raise ValueError("No se puede dividir entre cero.")
        return a / b

    def potencia(self, base, exponente):
        return base ** exponente

    def raiz(self, numero, indice=2):
        if numero < 0 and indice % 2 == 0:
            raise ValueError("No se puede calcular la raíz par de un número negativo.")
        return numero ** (1 / indice)

    def seno(self, grados):
        return math.sin(math.radians(grados))

    def coseno(self, grados):
        return math.cos(math.radians(grados))

    def tangente(self, grados):
        return math.tan(math.radians(grados))

    def factorial(self, n):
        if n < 0:
            raise ValueError("No existe factorial de número negativo.")
        return math.factorial(n)

    def mostrar_menu(self):
        print("\n=== CALCULADORA CIENTÍFICA ===")
        print("1. Suma")
        print("2. Resta")
        print("3. Multiplicación")
        print("4. División")
        print("5. Potencia")
        print("6. Raíz")
        print("7. Seno / Coseno / Tangente")
        print("8. Factorial")
        print("9. Volver al menú principal")


# ================================================================
# CLASE 2: CONVERSOR DE UNIDADES
# ================================================================

class Conversor:
    def __init__(self):
        self.menu_principal = {
            "1": "Temperatura",
            "2": "Distancia",
            "3": "Peso",
            "4": "Volver al menú principal"
        }

    # -------- TEMPERATURA --------
    def celsius_a_fahrenheit(self, c):
        return (c * 9/5) + 32

    def fahrenheit_a_celsius(self, f):
        return (f - 32) * 5/9

    def celsius_a_kelvin(self, c):
        return c + 273.15

    # -------- DISTANCIA --------
    def metros_a_kilometros(self, m):
        return m / 1000

    def kilometros_a_millas(self, km):
        return km * 0.621371

    def millas_a_kilometros(self, mi):
        return mi / 0.621371

    # -------- PESO --------
    def kilogramos_a_libras(self, kg):
        return kg * 2.20462

    def libras_a_kilogramos(self, lb):
        return lb / 2.20462

    # -------- MENÚ --------
    def mostrar_menu(self):
        print("\n=== CONVERSOR DE UNIDADES ===")
        for k, v in self.menu_principal.items():
            print(f"{k}. {v}")


# ================================================================
# CLASE 3: GENERADOR DE CONTRASEÑAS
# ================================================================

class GeneradorContrasenas:
    def __init__(self):
        self.niveles = {
            "1": "Básico (solo letras minúsculas)",
            "2": "Intermedio (letras y números)",
            "3": "Avanzado (letras, números y símbolos)"
        }

    def generar(self, longitud, nivel):
        if nivel == "1":
            caracteres = string.ascii_lowercase
        elif nivel == "2":
            caracteres = string.ascii_letters + string.digits
        elif nivel == "3":
            caracteres = string.ascii_letters + string.digits + string.punctuation
        else:
            raise ValueError("Nivel inválido.")

        contrasena = ''.join(random.choice(caracteres) for _ in range(longitud))
        return contrasena

    def mostrar_menu(self):
        print("\n=== GENERADOR DE CONTRASEÑAS ===")
        for k, v in self.niveles.items():
            print(f"{k}. {v}")
        print("4. Volver al menú principal")


# ================================================================
# FUNCIONES AUXILIARES
# ================================================================

def ejecutar_calculadora(calc):
    while True:
        calc.mostrar_menu()
        opcion = input("Selecciona una opción: ")

        try:
            if opcion in ["1", "2", "3", "4", "5"]:
                a = float(input("Introduce el primer número: "))
                b = float(input("Introduce el segundo número: "))

            if opcion == "1":
                print(f"Resultado: {calc.sumar(a, b)}")
            elif opcion == "2":
                print(f"Resultado: {calc.restar(a, b)}")
            elif opcion == "3":
                print(f"Resultado: {calc.multiplicar(a, b)}")
            elif opcion == "4":
                print(f"Resultado: {calc.dividir(a, b)}")
            elif opcion == "5":
                print(f"Resultado: {calc.potencia(a, b)}")
            elif opcion == "6":
                n = float(input("Número: "))
                i = float(input("Índice de la raíz (ej. 2 para raíz cuadrada): "))
                print(f"Resultado: {calc.raiz(n, i)}")
            elif opcion == "7":
                g = float(input("Introduce ángulo en grados: "))
                print(f"Seno: {calc.seno(g):.4f}")
                print(f"Coseno: {calc.coseno(g):.4f}")
                print(f"Tangente: {calc.tangente(g):.4f}")
            elif opcion == "8":
                n = int(input("Introduce número entero: "))
                print(f"Resultado: {calc.factorial(n)}")
            elif opcion == "9":
                break
            else:
                print("⚠️ Opción no válida.")
        except Exception as e:
            print(f"Error: {e}")


def ejecutar_conversor(conv):
    while True:
        conv.mostrar_menu()
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            print("\n1. Celsius a Fahrenheit")
            print("2. Fahrenheit a Celsius")
            print("3. Celsius a Kelvin")
            print("4. Volver")
            op = input("Opción: ")
            try:
                if op == "1":
                    c = float(input("Celsius: "))
                    print(f"{c}°C = {conv.celsius_a_fahrenheit(c)}°F")
                elif op == "2":
                    f = float(input("Fahrenheit: "))
                    print(f"{f}°F = {conv.fahrenheit_a_celsius(f)}°C")
                elif op == "3":
                    c = float(input("Celsius: "))
                    print(f"{c}°C = {conv.celsius_a_kelvin(c)}K")
                elif op == "4":
                    continue
            except ValueError:
                print("⚠️ Entrada no válida.")

        elif opcion == "2":
            print("\n1. Metros a kilómetros")
            print("2. Kilómetros a millas")
            print("3. Millas a kilómetros")
            print("4. Volver")
            op = input("Opción: ")
            try:
                if op == "1":
                    m = float(input("Metros: "))
                    print(f"{m} m = {conv.metros_a_kilometros(m)} km")
                elif op == "2":
                    km = float(input("Kilómetros: "))
                    print(f"{km} km = {conv.kilometros_a_millas(km)} mi")
                elif op == "3":
                    mi = float(input("Millas: "))
                    print(f"{mi} mi = {conv.millas_a_kilometros(mi)} km")
            except ValueError:
                print("⚠️ Entrada no válida.")

        elif opcion == "3":
            print("\n1. Kilogramos a libras")
            print("2. Libras a kilogramos")
            print("3. Volver")
            op = input("Opción: ")
            try:
                if op == "1":
                    kg = float(input("Kilogramos: "))
                    print(f"{kg} kg = {conv.kilogramos_a_libras(kg)} lb")
                elif op == "2":
                    lb = float(input("Libras: "))
                    print(f"{lb} lb = {conv.libras_a_kilogramos(lb)} kg")
            except ValueError:
                print("⚠️ Entrada no válida.")

        elif opcion == "4":
            break
        else:
            print("⚠️ Opción no válida.")


def ejecutar_generador(gen):
    while True:
        gen.mostrar_menu()
        opcion = input("Selecciona un nivel de seguridad: ")

        if opcion in ["1", "2", "3"]:
            try:
                longitud = int(input("Longitud de la contraseña: "))
                contrasena = gen.generar(longitud, opcion)
                print(f"\n🔐 Contraseña generada: {contrasena}\n")
            except Exception as e:
                print(f"Error: {e}")
        elif opcion == "4":
            break
        else:
            print("⚠️ Opción no válida.")


# ================================================================
# MENÚ PRINCIPAL
# ================================================================

def menu_principal():
    calc = Calculadora()
    conv = Conversor()
    gen = GeneradorContrasenas()

    while True:
        print("\n===============================")
        print("🌟 MENÚ PRINCIPAL 🌟")
        print("===============================")
        print("1. Calculadora científica")
        print("2. Conversor de unidades")
        print("3. Generador de contraseñas")
        print("4. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            ejecutar_calculadora(calc)
        elif opcion == "2":
            ejecutar_conversor(conv)
        elif opcion == "3":
            ejecutar_generador(gen)
        elif opcion == "4":
            print("\n👋 ¡Gracias por usar el programa multifunción 2!")
            break
        else:
            print("⚠️ Opción no válida.")

        time.sleep(1)


# ================================================================
# PUNTO DE ENTRADA
# ================================================================

if __name__ == "__main__":
    menu_principal()

# ================================================================
# Fin del programa (más de 300 líneas)
# ================================================================
