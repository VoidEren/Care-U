from __future__ import annotations
import math
import random
import sys
import time
import heapq
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Set, Deque
from collections import deque, defaultdict, Counter
def timing(fn: Callable) -> Callable:
    """Decorador simple para medir el tiempo de ejecución."""
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"[timing] {fn.__name__} tardó {t1 - t0:.6f}s")
        return result
    return wrapper
def clamp(x: float, low: float, high: float) -> float:
    """Restringe x al intervalo [low, high]."""
    return max(low, min(high, x))
def chunks(seq: Iterable[Any], size: int) -> Iterable[List[Any]]:
    """Genera bloques de longitud `size` de un iterable."""
    buf = []
    for item in seq:
        buf.append(item)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf
def is_prime(n: int) -> bool:
    """Test de primalidad simple (para n >= 2)."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True
def primes_up_to(n: int) -> List[int]:
    """Criba de Eratóstenes simple."""
    if n < 2:
        return []
    sieve = [True]*(n+1)
    sieve[0]=sieve[1]=False
    for p in range(2, int(n**0.5)+1):
        if sieve[p]:
            step = p
            start = p*p
            sieve[start:n+1:step] = [False]*(((n - start)//step)+1)
    return [i for i,ok in enumerate(sieve) if ok]
@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)
class MinPriorityQueue:
    """Cola de prioridad mínima (envoltura de heapq)."""
    def __init__(self):
        self._heap: List[PrioritizedItem] = []
    def push(self, priority: int, item: Any) -> None:
        heapq.heappush(self._heap, PrioritizedItem(priority, item))
    def pop(self) -> Any:
        return heapq.heappop(self._heap).item
    def __len__(self) -> int:
        return len(self._heap)
class DisjointSet:
    """Unión-Búsqueda (Union-Find) con compresión de caminos y unión por rango."""
    def __init__(self):
        self.parent: Dict[Any, Any] = {}
        self.rank: Dict[Any, int] = {}
    def find(self, x: Any) -> Any:
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)
    def union(self, a: Any, b: Any) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank.get(ra, 0) < self.rank.get(rb, 0):
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank.get(ra, 0) == self.rank.get(rb, 0):
            self.rank[ra] = self.rank.get(ra, 0) + 1
    def add(self, x: Any) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
class Graph:
    def __init__(self):
        self.adj: Dict[Any, List[Tuple[Any, float]]] = defaultdict(list)
    def add_edge(self, u: Any, v: Any, w: float=1.0, bidir: bool=True):
        self.adj[u].append((v, w))
        if bidir:
            self.adj[v].append((u, w))
    def neighbors(self, u: Any) -> List[Tuple[Any, float]]:
        return self.adj.get(u, [])
def bfs(graph: Graph, start: Any) -> Dict[Any, int]:
    """Retorna distancias no ponderadas desde start."""
    dist = {start: 0}
    q: Deque[Any] = deque([start])
    while q:
        u = q.popleft()
        for v, _ in graph.neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
def dfs(graph: Graph, start: Any) -> List[Any]:
    """Recorrido en profundidad."""
    visited: Set[Any] = set()
    order: List[Any] = []
    def _dfs(u: Any):
        visited.add(u)
        order.append(u)
        for v, _ in graph.neighbors(u):
            if v not in visited:
                _dfs(v)
    _dfs(start)
    return order
def dijkstra(graph: Graph, start: Any) -> Dict[Any, float]:
    dist: Dict[Any, float] = defaultdict(lambda: math.inf)
    dist[start] = 0.0
    pq: List[Tuple[float, Any]] = [(0.0, start)]
    while pq:
        d,u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, w in graph.neighbors(u):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq,(nd,v))
    return dict(dist)
def a_star(graph: Graph, start: Any, goal: Any, h: Callable[[Any,Any],float]) -> Tuple[float, List[Any]]:
    """A* retorna costo y camino aproximado."""
    open_set: List[Tuple[float, Any]] = []
    heapq.heappush(open_set, (0.0, start))
    came: Dict[Any, Any] = {start: None}
    g: Dict[Any, float] = defaultdict(lambda: math.inf)
    g[start] = 0.0
    f: Dict[Any, float] = defaultdict(lambda: math.inf)
    f[start] = h(start, goal)
    while open_set:
        _, u = heapq.heappop(open_set)
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = came[u]
            path.reverse()
            return g[goal], path
        for v, w in graph.neighbors(u):
            tentative = g[u] + w
            if tentative < g[v]:
                came[v] = u
                g[v] = tentative
                f[v] = tentative + h(v, goal)
                heapq.heappush(open_set, (f[v], v))
    return math.inf, []
def knapsack_01(weights: List[int], values: List[int], W: int) -> Tuple[int, List[int]]:
    """Mochila 0/1: retorna (valor_max, indices_seleccionados)."""
    n = len(weights)
    dp = [[0]*(W+1) for _ in range(n+1)]
    for i in range(1, n+1):
        wi, vi = weights[i-1], values[i-1]
        for w in range(W+1):
            dp[i][w] = dp[i-1][w]
            if wi <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w-wi] + vi)
    res = dp[n][W]
    w = W
    chosen = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            chosen.append(i-1)
            w -= weights[i-1]
    chosen.reverse()
    return res, chosen
def lis(seq: List[int]) -> List[int]:
    """Longest Increasing Subsequence (retorna una subsecuencia)."""
    if not seq:
        return []
    tails = []
    prev = [-1]*len(seq)
    idx = []
    for i,x in enumerate(seq):
        j = lower_bound(tails, x)
        if j == len(tails):
            tails.append(x)
            idx.append(i)
        else:
            tails[j] = x
            idx[j] = i
        if j > 0:
            prev[i] = idx[j-1]
    k = idx[len(tails)-1]
    ans = []
    while k != -1:
        ans.append(seq[k])
        k = prev[k]
    ans.reverse()
    return ans
def lower_bound(arr: List[int], x: int) -> int:
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi)//2
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    if not xs:
        return float('nan')
    return sum(xs)/len(xs)
def variance(xs: Iterable[float], sample: bool=True) -> float:
    xs = list(xs)
    n = len(xs)
    if n < 2:
        return float('nan')
    mu = mean(xs)
    ss = sum((x-mu)**2 for x in xs)
    return ss/(n-1 if sample else n)
def linear_regression(xs: List[float], ys: List[float]) -> Tuple[float, float, float]:
    """Retorna (pendiente m, intercepto b, R^2)."""
    if len(xs) != len(ys) or len(xs) == 0:
        return float('nan'), float('nan'), float('nan')
    n = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs)
    syy = sum(y*y for y in ys)
    sxy = sum(x*y for x,y in zip(xs,ys))
    denom = n*sxx - sx*sx
    if denom == 0:
        return float('nan'), float('nan'), float('nan')
    m = (n*sxy - sx*sy)/denom
    b = (sy - m*sx)/n
    yhat = [m*x + b for x in xs]
    ss_res = sum((y - yh)**2 for y,yh in zip(ys,yhat))
    ss_tot = sum((y - mean(ys))**2 for y in ys)
    r2 = 1 - ss_res/ss_tot if ss_tot != 0 else float('nan')
    return m, b, r2
def tokenize(text: str) -> List[str]:
    """Divide por caracteres no alfanuméricos y minúsculas."""
    token = []
    out = []
    for ch in text.lower():
        if ch.isalnum():
            token.append(ch)
        else:
            if token:
                out.append(''.join(token))
                token = []
    if token:
        out.append(''.join(token))
    return out
def word_count(text: str) -> Counter:
    return Counter(tokenize(text))
def kmp_build(pattern: str) -> List[int]:
    """Construye la tabla de fallos para KMP."""
    m = len(pattern)
    lps = [0]*m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length-1]
        else:
            lps[i] = 0
            i += 1
    return lps
def kmp_search(text: str, pattern: str) -> List[int]:
    if pattern == "":
        return list(range(len(text)+1))
    lps = kmp_build(pattern)
    i = j = 0
    res = []
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1; j += 1
            if j == len(pattern):
                res.append(i-j)
                j = lps[j-1]
        else:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return res
def random_walk(steps: int, seed: Optional[int]=None) -> Tuple[int,int]:
    if seed is not None:
        random.seed(seed)
    x = y = 0
    for _ in range(steps):
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        x += dx; y += dy
    return x,y
def monte_carlo_pi(samples: int, seed: Optional[int]=None) -> float:
    if seed is not None:
        random.seed(seed)
    inside = 0
    for _ in range(samples):
        x = random.random(); y = random.random()
        if x*x + y*y <= 1.0:
            inside += 1
    return 4.0*inside/samples if samples>0 else float('nan')
class Task:
    def __init__(self, name: str, action: Callable[[], None], interval: float):
        self.name = name
        self.action = action
        self.interval = interval
        self.next_time = time.perf_counter() + interval
    def tick(self, now: float) -> None:
        if now >= self.next_time:
            print(f"[task] Ejecutando {self.name}")
            self.action()
            self.next_time = now + self.interval
class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []
    def every(self, seconds: float, name: str, action: Callable[[], None]) -> None:
        self.tasks.append(Task(name, action, seconds))
    def run_for(self, seconds: float) -> None:
        end = time.perf_counter() + seconds
        while time.perf_counter() < end:
            now = time.perf_counter()
            for t in self.tasks:
                t.tick(now)
            time.sleep(0.01)
def demo_primes():
    print("== Primos hasta 100 ==")
    print(primes_up_to(100))
def demo_graph():
    print("== Grafo y Dijkstra ==")
    g = Graph()
    g.add_edge('A','B', 4)
    g.add_edge('A','C', 2)
    g.add_edge('B','C', 5)
    g.add_edge('B','D', 10)
    g.add_edge('C','E', 3)
    g.add_edge('E','D', 4)
    g.add_edge('D','F', 11)
    dist = dijkstra(g,'A')
    print("Distancias desde A:", dist)
    h = lambda u,v: 0.0  # heurística trivial
    cost, path = a_star(g,'A','F', h)
    print("A* A->F: costo", cost, "camino", path)
def demo_knapsack():
    print("== Mochila 0/1 ==")
    w = [3, 2, 4, 5]
    v = [4, 3, 5, 6]
    W = 5
    val, idx = knapsack_01(w, v, W)
    print(f"Capacidad {W}, valor máximo {val}, items {idx}")
def demo_lis():
    print("== LIS ==")
    seq = [10, 9, 2, 5, 3, 7, 101, 18]
    print("Secuencia:", seq)
    print("LIS:", lis(seq))
def demo_stats():
    print("== Estadística ==")
    xs = [1,2,3,4,5,6,7,8,9]
    ys = [2,4,5,4,5,7,8,9,10]
    print("media(xs)=", mean(xs))
    print("var(xs)=", variance(xs))
    m,b,r2 = linear_regression(xs, ys)
    print(f"y = {m:.3f} x + {b:.3f}; R^2={r2:.3f}")
def demo_text():
    print("== Texto y KMP ==")
    t = "ababcabcabababd"
    p = "ababd"
    print("texto:", t)
    print("patrón:", p)
    print("posiciones:", kmp_search(t,p))
    wc = word_count("Hola hola, mundo! Mundo... hola?")
    print("Word count:", dict(wc))
def demo_sim():
    print("== Simulaciones ==")
    print("Caminata 100 pasos:", random_walk(100, seed=42))
    print("Pi ~", monte_carlo_pi(10000, seed=0))
def demo_scheduler():
    print("== Scheduler 1s por 3s ==")
    s = Scheduler()
    s.every(1.0, "tick", lambda: print("tick"))
    s.run_for(3.1)
DEMO_OPTIONS: Dict[str, Tuple[str, Callable[[], None]]] = {
    '1': ("Primos", demo_primes),
    '2': ("Grafos", demo_graph),
    '3': ("Mochila", demo_knapsack),
    '4': ("LIS", demo_lis),
    '5': ("Estadística", demo_stats),
    '6': ("Texto/KMP", demo_text),
    '7': ("Simulaciones", demo_sim),
    '8': ("Scheduler", demo_scheduler),
}
def menu():
    print("\n=== AlgoPlayground ===")
    for k,(name,_) in DEMO_OPTIONS.items():
        print(f" {k}. {name}")
    print(" 9. Salir")
def run_cli():
    while True:
        menu()
        try:
            choice = input("> ").strip()
        except EOFError:
            print()
            return
        if choice == '9':
            print("Adiós")
            return
        fn = DEMO_OPTIONS.get(choice)
        if fn:
            try:
                fn[1]()
            except Exception as e:
                print("Ocurrió un error:", e)
        else:
            print("Opción inválida")
def _self_test() -> None:
    """Pequeña batería de aserciones rápidas."""
    assert clamp(10,0,5) == 5
    assert clamp(-1,0,5) == 0
    assert is_prime(2) and is_prime(97) and not is_prime(1) and not is_prime(100)
    assert primes_up_to(10) == [2,3,5,7]
    g = Graph(); g.add_edge(1,2,1); g.add_edge(2,3,2)
    dist = bfs(g,1)
    assert dist[3] == 2
    order = dfs(g,1)
    assert order[0] == 1 and 3 in order
    dj = dijkstra(g,1)
    assert dj[3] == 3
    cost, path = a_star(g,1,3, lambda u,v: 0)
    assert cost == 3 and path == [1,2,3]
    val, idx = knapsack_01([1,3,4],[15,20,30],4)
    assert val == 35 and idx == [0,2]
    assert lis([3,10,2,1,20]) == [3,10,20]
    xs = [1,2,3]
    assert mean(xs) == 2
    assert round(variance(xs),6) == 1.0
    m,b,r2 = linear_regression([1,2,3],[2,4,6])
    assert round(m,6) == 2 and round(b,6) == 0
    assert kmp_search("abcabcd", "abcd") == [3]
    wc = word_count("Hola hola")
    assert wc['hola'] == 2
    assert random_walk(0) == (0,0)
    print("[self_test] OK")
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _self_test()
    else:
        run_cli()


from __future__ import annotations
import argparse, json, time, os, sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.expanduser("~"), ".todo100.json")

@dataclass
class Task:
    id: int
    text: str
    created_at: float
    done_at: Optional[float] = None
    tags: List[str] = None
    def to_row(self) -> List[str]:
        status = "✓" if self.done_at else "·"
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.created_at))
        tg = ",".join(self.tags or [])
        return [str(self.id), status, when, self.text + (f"  #{tg}" if tg else "")]

def _now() -> float:
    return time.time()

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_PATH):
        return {"seq": 0, "tasks": []}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # backup corrupt DB
        backup = DB_PATH + ".bak"
        try: os.replace(DB_PATH, backup)
        except Exception: pass
        return {"seq": 0, "tasks": []}

def save_db(db: Dict[str, Any]) -> None:
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_PATH)

def add_task(text: str, tags: List[str]) -> Task:
    db = load_db()
    db["seq"] += 1
    t = Task(id=db["seq"], text=text, created_at=_now(), tags=tags or [])
    db["tasks"].append(asdict(t))
    save_db(db)
    return t

def list_tasks(show_all: bool = False) -> List[Task]:
    db = load_db()
    items = [Task(**t) for t in db["tasks"]]
    return items if show_all else [t for t in items if not t.done_at]

def mark_done(tid: int) -> bool:
    db = load_db()
    for t in db["tasks"]:
        if t["id"] == tid:
            if t.get("done_at"): return False
            t["done_at"] = _now()
            save_db(db)
            return True
    return False

def clear_done() -> int:
    db = load_db()
    before = len(db["tasks"])
    db["tasks"] = [t for t in db["tasks"] if not t.get("done_at")]
    save_db(db)
    return before - len(db["tasks"])

def stats() -> Dict[str, Any]:
    items = list_tasks(show_all=True)
    total = len(items)
    done = sum(1 for t in items if t.done_at)
    open_ = total - done
    if done:
        cycle = [t.done_at - t.created_at for t in items if t.done_at]
        avg_cycle = sum(cycle) / len(cycle)
    else:
        avg_cycle = None
    tag_counter: Dict[str, int] = {}
    for t in items:
        for tag in t.tags or []:
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    top_tags = sorted(tag_counter.items(), key=lambda x: (-x[1], x[0]))[:5]
    return {"total": total, "open": open_, "done": done, "avg_cycle_sec": avg_cycle, "top_tags": top_tags}

def print_table(rows: List[List[str]]) -> None:
    if not rows:
        print("(sin resultados)"); return
    widths = [max(len(str(x)) for x in col) for col in zip(*rows)]
    for i, r in enumerate(rows):
        line = " | ".join(str(x).ljust(widths[j]) for j, x in enumerate(r))
        print(line)
        if i == 0:
            sep = "-+-".join("-" * w for w in widths)
            print(sep)

def parse_tags(text: str) -> (str, List[str]):
    # tags estilo "#iot #hydroleaf"
    parts = text.split()
    tags = [p[1:] for p in parts if p.startswith("#") and len(p) > 1]
    core = " ".join(p for p in parts if not p.startswith("#"))
    return core.strip(), tags

def main(argv=None):
    p = argparse.ArgumentParser(prog="todo100", description="Pequeño gestor de pendientes (JSON)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Agregar tarea (se aceptan tags con #)")
    p_add.add_argument("text", nargs="+", help="Descripción de la tarea")

    p_list = sub.add_parser("list", help="Listar tareas")
    p_list.add_argument("--all", action="store_true", help="Incluir hechas")

    p_done = sub.add_parser("done", help="Marcar tarea como hecha")
    p_done.add_argument("id", type=int)

    sub.add_parser("clear", help="Eliminar tareas hechas")
    sub.add_parser("stats", help="Estadísticas")

    args = p.parse_args(argv)

    if args.cmd == "add":
        raw = " ".join(args.text)
        text, tags = parse_tags(raw)
        t = add_task(text, tags)
        print(f"[+] #{t.id} agregado: {t.text}" + (f"  tags={','.join(tags)}" if tags else ""))
    elif args.cmd == "list":
        items = list_tasks(show_all=args.all)
        header = [["ID", "S", "Creado", "Texto"]]
        rows = header + [t.to_row() for t in items]
        print_table(rows)
    elif args.cmd == "done":
        ok = mark_done(args.id)
        print("✓ marcado" if ok else "No encontrado o ya estaba hecho")
    elif args.cmd == "clear":
        n = clear_done()
        print(f"Eliminadas {n} tareas hechas")
    elif args.cmd == "stats":
        s = stats()
        print(json.dumps(s, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

