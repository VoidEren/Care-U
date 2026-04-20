from __future__ import annotations
import math, random, sys, time, json, csv, statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from collections import defaultdict, deque, Counter

# ========== Utils ==========
def timing(fn: Callable) -> Callable:
    def wrapper(*a, **k):
        t0 = time.perf_counter()
        r = fn(*a, **k)
        t1 = time.perf_counter()
        print(f"[timing] {fn.__name__}: {(t1-t0):.6f}s")
        return r
    return wrapper

def memoize(fn: Callable) -> Callable:
    cache = {}
    def wrap(*a):
        if a in cache: return cache[a]
        cache[a] = fn(*a)
        return cache[a]
    return wrap

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def chunked(seq: Iterable[Any], n: int) -> Iterable[List[Any]]:
    buf: List[Any] = []
    for x in seq:
        buf.append(x)
        if len(buf) == n:
            yield buf; buf=[]
    if buf: yield buf

# ========== RNG ==========
class RNG:
    def __init__(self, seed: Optional[int]=None):
        self.r = random.Random(seed)
    def choice(self, xs: Sequence[Any]) -> Any: return self.r.choice(xs)
    def uniform(self, a: float, b: float) -> float: return self.r.uniform(a,b)
    def randint(self, a: int, b: int) -> int: return self.r.randint(a,b)
    def rand(self) -> float: return self.r.random()

# ========== LRU Cache ==========
class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: Dict[Any, Any] = {}
        self.order: deque = deque()
    def get(self, key: Any) -> Any:
        if key not in self.map: return None
        self.order.remove(key)
        self.order.appendleft(key)
        return self.map[key]
    def put(self, key: Any, val: Any) -> None:
        if key in self.map:
            self.order.remove(key)
        elif len(self.order) >= self.cap:
            old = self.order.pop(); self.map.pop(old, None)
        self.map[key] = val; self.order.appendleft(key)

# ========== DSU / Union-Find ==========
class DSU:
    def __init__(self):
        self.p: Dict[Any, Any] = {}
        self.r: Dict[Any, int] = {}
    def find(self, x: Any) -> Any:
        if x not in self.p: self.p[x]=x; self.r[x]=0; return x
        if self.p[x]!=x: self.p[x]=self.find(self.p[x])
        return self.p[x]
    def union(self, a: Any, b: Any):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return
        if self.r[ra] < self.r[rb]: ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]: self.r[ra] += 1

# ========== Trie ==========
class Trie:
    def __init__(self):
        self.nxt: Dict[int, Dict[str,int]] = {0:{}}
        self.end: Dict[int,bool] = defaultdict(bool)
        self._id = 1
    def _node(self) -> int:
        self.nxt[self._id] = {}; self._id += 1; return self._id - 1
    def insert(self, s: str) -> None:
        u = 0
        for ch in s:
            if ch not in self.nxt[u]:
                self.nxt[u][ch] = self._node()
            u = self.nxt[u][ch]
        self.end[u] = True
    def search(self, s: str) -> bool:
        u=0
        for ch in s:
            if ch not in self.nxt[u]: return False
            u = self.nxt[u][ch]
        return self.end[u]
    def starts_with(self, p: str) -> bool:
        u=0
        for ch in p:
            if ch not in self.nxt[u]: return False
            u = self.nxt[u][ch]
        return True

# ========== Grafos ==========
class Graph:
    def __init__(self):
        self.adj: Dict[Any, List[Tuple[Any, float]]] = defaultdict(list)
    def add(self, u: Any, v: Any, w: float=1.0, bidir: bool=True):
        self.adj[u].append((v,w))
        if bidir: self.adj[v].append((u,w))
    def neighbors(self, u: Any) -> List[Tuple[Any, float]]:
        return self.adj.get(u, [])

def bfs(graph: Graph, start: Any) -> Dict[Any,int]:
    dist={start:0}; q=deque([start])
    while q:
        u=q.popleft()
        for v,_ in graph.neighbors(u):
            if v not in dist: dist[v]=dist[u]+1; q.append(v)
    return dist

def topo_sort_dag(n: int, edges: List[Tuple[int,int]]) -> List[int]:
    g=[[] for _ in range(n)]; indeg=[0]*n
    for u,v in edges: g[u].append(v); indeg[v]+=1
    q=deque([i for i in range(n) if indeg[i]==0]); out=[]
    while q:
        u=q.popleft(); out.append(u)
        for v in g[u]:
            indeg[v]-=1
            if indeg[v]==0: q.append(v)
    if len(out)!=n: raise ValueError("graph has cycles")
    return out

def dijkstra(graph: Graph, start: Any) -> Dict[Any, float]:
    import heapq
    dist=defaultdict(lambda: float("inf")); dist[start]=0.0
    pq=[(0.0,start)]
    while pq:
        d,u=heapq.heappop(pq)
        if d!=dist[u]: continue
        for v,w in graph.neighbors(u):
            nd=d+w
            if nd<dist[v]:
                dist[v]=nd; heapq.heappush(pq,(nd,v))
    return dict(dist)

def a_star(graph: Graph, start: Any, goal: Any, h: Callable[[Any,Any],float]) -> Tuple[float,List[Any]]:
    import heapq
    g=defaultdict(lambda: float("inf")); g[start]=0.0
    f=defaultdict(lambda: float("inf")); f[start]=h(start,goal)
    came={start:None}; openq=[(f[start],start)]
    while openq:
        _,u=heapq.heappop(openq)
        if u==goal:
            path=[]; 
            while u is not None: path.append(u); u=came[u]
            return g[goal], path[::-1]
        for v,w in graph.neighbors(u):
            tg=g[u]+w
            if tg<g[v]:
                g[v]=tg; f[v]=tg+h(v,goal); came[v]=u; heapq.heappush(openq,(f[v],v))
    return float("inf"), []

# ========== Strings ==========
def tokenize(text: str) -> List[str]:
    tok=[]; buf=[]
    for ch in text.lower():
        if ch.isalnum(): buf.append(ch)
        else:
            if buf: tok.append("".join(buf)); buf=[]
    if buf: tok.append("".join(buf))
    return tok

def word_count(text: str) -> Counter:
    return Counter(tokenize(text))

def kmp_build(p: str) -> List[int]:
    lps=[0]*len(p); j=0
    for i in range(1,len(p)):
        while j>0 and p[i]!=p[j]: j=lps[j-1]
        if p[i]==p[j]: j+=1
        lps[i]=j
    return lps

def kmp_search(s: str, p: str) -> List[int]:
    if not p: return list(range(len(s)+1))
    lps=kmp_build(p); i=j=0; out=[]
    while i<len(s):
        if s[i]==p[j]:
            i+=1; j+=1
            if j==len(p): out.append(i-j); j=lps[j-1]
        else:
            j=lps[j-1] if j>0 else 0
            if j==0: i+=1
    return out

def rle_encode(s: str) -> str:
    if not s: return ""
    out=[]; cnt=1
    for i in range(1,len(s)):
        if s[i]==s[i-1]: cnt+=1
        else: out.append(f"{s[i-1]}:{cnt};"); cnt=1
    out.append(f"{s[-1]}:{cnt};"); return "".join(out)

def rle_decode(enc: str) -> str:
    if not enc: return ""
    out=[]
    for t in enc.split(";"):
        if not t: continue
        ch,k=t.split(":"); out.append(ch*int(k))
    return "".join(out)

# ========== Edición/LIS/Sorts ==========
def edit_distance(a: str, b: str) -> int:
    n,m=len(a),len(b)
    dp=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0]=i
    for j in range(m+1): dp[0][j]=j
    for i in range(1,n+1):
        for j in range(1,m+1):
            cost=0 if a[i-1]==b[j-1] else 1
            dp[i][j]=min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[n][m]

def lis(seq: List[int]) -> List[int]:
    if not seq: return []
    tails=[]; prev=[-1]*len(seq); idx=[]
    def lb(arr,x):
        lo,hi=0,len(arr)
        while lo<hi:
            md=(lo+hi)//2
            if arr[md]<x: lo=md+1
            else: hi=md
        return lo
    for i,x in enumerate(seq):
        j=lb(tails,x)
        if j==len(tails): tails.append(x); idx.append(i)
        else: tails[j]=x; idx[j]=i
        if j>0: prev[i]=idx[j-1]
    k=idx[len(tails)-1]; out=[]
    while k!=-1: out.append(seq[k]); k=prev[k]
    return out[::-1]

def insertion_sort(a: List[Any]) -> List[Any]:
    a=a[:]
    for i in range(1,len(a)):
        x=a[i]; j=i-1
        while j>=0 and a[j]>x:
            a[j+1]=a[j]; j-=1
        a[j+1]=x
    return a

def merge_sort(a: List[Any]) -> List[Any]:
    if len(a)<=1: return a[:]
    m=len(a)//2
    L=merge_sort(a[:m]); R=merge_sort(a[m:])
    i=j=0; out=[]
    while i<len(L) and j<len(R):
        if L[i]<=R[j]: out.append(L[i]); i+=1
        else: out.append(R[j]); j+=1
    out.extend(L[i:]); out.extend(R[j:])
    return out

# ========== Estadística / Regresión ==========
def mean(xs: Iterable[float]) -> float:
    xs=list(xs); return sum(xs)/len(xs) if xs else float("nan")

def variance(xs: Iterable[float], sample: bool=True) -> float:
    xs=list(xs); n=len(xs)
    if n<2: return float("nan")
    mu=mean(xs); ss=sum((x-mu)**2 for x in xs)
    return ss/(n-1 if sample else n)

def linear_regression(xs: List[float], ys: List[float]) -> Tuple[float,float,float]:
    if len(xs)!=len(ys) or not xs: return float('nan'), float('nan'), float('nan')
    n=len(xs); sx=sum(xs); sy=sum(ys)
    sxx=sum(x*x for x in xs); syy=sum(y*y for y in ys); sxy=sum(x*y for x,y in zip(xs,ys))
    d=n*sxx - sx*sx
    if d==0: return float('nan'), float('nan'), float('nan')
    m=(n*sxy - sx*sy)/d; b=(sy - m*sx)/n
    yhat=[m*x+b for x in xs]
    ss_res=sum((y-yt)**2 for y,yt in zip(ys,yhat))
    ss_tot=sum((y-mean(ys))**2 for y in ys)
    r2=1 - ss_res/ss_tot if ss_tot!=0 else float('nan')
    return m,b,r2

# ========== JSON/CSV ==========
def read_json(path: str) -> Any:
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def write_json(path: str, obj: Any) -> None:
    with open(path,"w",encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)

def read_csv(path: str) -> List[Dict[str,str]]:
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def write_csv(path: str, rows: List[Dict[str,Any]]) -> None:
    if not rows:
        with open(path,"w",newline="",encoding="utf-8") as f: f.write("")
        return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

# ========== Demos ==========
def demo_graphs():
    g=Graph(); g.add("A","B",4); g.add("A","C",2); g.add("C","D",7); g.add("B","D",1)
    print("BFS:", bfs(g,"A"))
    print("Dijkstra:", dijkstra(g,"A"))
    h=lambda u,v: 0.0
    print("A* A->D:", a_star(g,"A","D",h))

def demo_strings():
    s="ababcabcabababd"; p="ababd"
    print("KMP:", kmp_search(s,p))
    enc=rle_encode("aaaabbbbccdaa"); print("RLE:", enc, "->", rle_decode(enc))

def demo_stats():
    xs=[1,2,3,4,5,6,7,8,9]; ys=[2,4,5,4,5,7,8,9,10]
    print("mean(xs)=", mean(xs)); print("var(xs)=", variance(xs))
    m,b,r2=linear_regression(xs,ys); print(f"y={m:.3f}x + {b:.3f}, R2={r2:.3f}")

def demo_algo():
    arr=[5,3,8,1,2,7]
    print("insertion:", insertion_sort(arr))
    print("merge:", merge_sort(arr))
    print("edit('gato','pato'):", edit_distance("gato","pato"))
    print("lis:", lis([10,9,2,5,3,7,101,18]))

def demo_trie_lru():
    t=Trie(); 
    for w in ["hola","holaque","adios"]: t.insert(w)
    print("trie search hola:", t.search("hola"), "starts ho:", t.starts_with("ho"))
    lru=LRUCache(2); lru.put("a",1); lru.put("b",2); lru.get("a"); lru.put("c",3)
    print("LRU get b=None?", lru.get("b"))

# ========== Self-test ==========
def _self_test():
    # DSU
    d=DSU(); d.union(1,2); d.union(2,3); assert d.find(1)==d.find(3)
    # Trie
    t=Trie(); t.insert("abc"); assert t.search("abc") and not t.search("ab") and t.starts_with("ab")
    # Strings
    assert kmp_search("abcabcd","abcd")==[3]
    enc=rle_encode("aaabb"); assert rle_decode(enc)=="aaabb"
    # Graphs
    g=Graph(); g.add(0,1,1); g.add(1,2,2); assert bfs(g,0)[2]==2
    dj=dijkstra(g,0); assert dj[2]==3
    c,p=a_star(g,0,2,lambda u,v:0); assert c==3 and p==[0,1,2]
    # Stats
    xs=[1,2,3]; assert mean(xs)==2 and round(variance(xs),6)==1.0
    m,b,r2=linear_regression([1,2,3],[2,4,6]); assert round(m,6)==2 and round(b,6)==0
    # Algo
    assert insertion_sort([3,1,2])==[1,2,3]
    assert merge_sort([5,3,1,2,4])==[1,2,3,4,5]
    assert edit_distance("kitten","sitting")==3
    assert lis([0,1,0,3,2,3])==[0,1,2,3]
    print("[self_test] OK")

# ========== CLI ==========
CMDS: Dict[str, Tuple[str, Callable[[],None]]] = {
    "gra": ("Grafos (BFS/Dijkstra/A*)", demo_graphs),
    "str": ("Cadenas (KMP/RLE)", demo_strings),
    "sta": ("Estadística (media/var/OLS)", demo_stats),
    "alg": ("Algoritmos (sort/LIS/edit)", demo_algo),
    "tri": ("Trie + LRU", demo_trie_lru),
}

def menu():
    print("\n=== microtoolkit300 ===")
    for k,(name,_) in CMDS.items(): print(f" {k:>3} : {name}")
    print("  ext : salir")

def run_cli():
    while True:
        menu()
        try:
            op=input("> ").strip()
        except EOFError:
            print(); return
        if op=="ext": print("Adiós"); return
        fn=CMDS.get(op)
        if fn:
            try: fn[1]()
            except Exception as e: print("Error:", e)
        else:
            print("Opción inválida")

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        _self_test()
    else:
        run_cli()
