from __future__ import annotations
import math, random, sys, time, json, csv, statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any, Optional, Iterable
from collections import deque, defaultdict, Counter

"""
DataToolkit600: script compacto de 600 líneas.
Incluye utilidades numéricas, álgebra lineal ligera, grafos, cadenas,
probabilidad, ML básico, parser de expresiones, E/S CSV-JSON y un CLI.
Usa:  python toolkit600.py           # menú
      python toolkit600.py --test    # pruebas rápidas
"""

# ---------- Utilidades generales ----------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def chunked(seq: Iterable[Any], size: int) -> Iterable[List[Any]]:
    buf = []
    for x in seq:
        buf.append(x)
        if len(buf) == size:
            yield buf; buf = []
    if buf: yield buf

def argmax(items: Iterable[Any], key: Callable[[Any], float]) -> Any:
    best, bestv = None, -float("inf")
    for it in items:
        v = key(it)
        if v > bestv: best, bestv = it, v
    return best

# ---------- Álgebra lineal (listas) ----------
def zeros(n: int, m: int) -> List[List[float]]:
    return [[0.0]*m for _ in range(n)]

def eye(n: int) -> List[List[float]]:
    I = zeros(n,n)
    for i in range(n): I[i][i] = 1.0
    return I

def matvec(A: List[List[float]], x: List[float]) -> List[float]:
    n, m = len(A), len(A[0]); assert m == len(x)
    y = [0.0]*n
    for i in range(n):
        s = 0.0; Ai = A[i]
        for j in range(m): s += Ai[j]*x[j]
        y[i] = s
    return y

def matmul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    n, p, m = len(A), len(A[0]), len(B[0]); assert p == len(B)
    C = zeros(n,m)
    for i in range(n):
        Ai = A[i]
        for k in range(p):
            aik = Ai[k]; Bk = B[k]
            for j in range(m): C[i][j] += aik*Bk[j]
    return C

def transpose(A: List[List[float]]) -> List[List[float]]:
    n, m = len(A), len(A[0])
    return [[A[i][j] for i in range(n)] for j in range(m)]

def gauss_jordan(A: List[List[float]], b: List[float]) -> List[float]:
    n = len(A)
    M = [row[:] + [b[i]] for i,row in enumerate(A)]
    for c in range(n):
        piv = max(range(c,n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-12: raise ValueError("singular")
        M[c], M[piv] = M[piv], M[c]
        f = M[c][c]
        for j in range(c, n+1): M[c][j] /= f
        for r in range(n):
            if r==c: continue
            fac = M[r][c]
            for j in range(c, n+1): M[r][j] -= fac*M[c][j]
    return [M[i][n] for i in range(n)]

def power_method(A: List[List[float]], iters: int=100, tol: float=1e-10) -> Tuple[float, List[float]]:
    n = len(A); x = [1.0/n]*n; lam = 0.0
    for _ in range(iters):
        y = matvec(A,x); lam_new = max(abs(v) for v in y) or 1.0
        x = [v/lam_new for v in y]
        if abs(lam_new - lam) < tol: break
        lam = lam_new
    return lam, x

# ---------- Métodos numéricos ----------
def bisection(f: Callable[[float], float], a: float, b: float, tol: float=1e-8, maxit: int=100) -> float:
    fa, fb = f(a), f(b)
    if fa*fb > 0: raise ValueError("f(a)*f(b)>0")
    for _ in range(maxit):
        c = 0.5*(a+b); fc = f(c)
        if abs(fc) < tol or (b-a)/2 < tol: return c
        if fa*fc < 0: b, fb = c, fc
        else: a, fa = c, fc
    return 0.5*(a+b)

def newton(f: Callable[[float], float], df: Callable[[float], float], x0: float, tol: float=1e-10, maxit: int=100) -> float:
    x = x0
    for _ in range(maxit):
        fx, dfx = f(x), df(x)
        if abs(dfx) < 1e-14: break
        xn = x - fx/dfx
        if abs(xn - x) < tol: return xn
        x = xn
    return x

def trapezoid(f: Callable[[float], float], a: float, b: float, n: int=1000) -> float:
    h = (b-a)/n; s = 0.5*(f(a)+f(b)); x=a+h
    for _ in range(1,n): s += f(x); x += h
    return s*h

def simpson(f: Callable[[float], float], a: float, b: float, n: int=1000) -> float:
    if n%2: n+=1
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n):
        x=a+i*h; s += (4 if i%2 else 2)*f(x)
    return s*h/3

def rk4(f: Callable[[float, float], float], t0: float, y0: float, h: float, steps: int) -> List[Tuple[float,float]]:
    t,y=t0,y0; out=[(t,y)]
    for _ in range(steps):
        k1=f(t,y); k2=f(t+0.5*h,y+0.5*h*k1)
        k3=f(t+0.5*h,y+0.5*h*k2); k4=f(t+h,y+h*k3)
        y = y + (h/6)*(k1+2*k2+2*k3+k4); t += h
        out.append((t,y))
    return out

# ---------- Probabilidad y combinatoria ----------
def factorial(n: int) -> int:
    if n<0: raise ValueError("n>=0")
    r=1
    for k in range(2,n+1): r*=k
    return r

def nCr(n: int, r: int) -> int:
    if r<0 or r>n: return 0
    r=min(r,n-r); num=1; den=1
    for k in range(1,r+1): num*=n-r+k; den*=k
    return num//den

def bernoulli_pmf(k:int,p:float)->float:
    return p if k==1 else (1-p if k==0 else 0.0)

def binomial_pmf(k:int,n:int,p:float)->float:
    return nCr(n,k)*(p**k)*((1-p)**(n-k))

def poisson_pmf(k:int,lam:float)->float:
    return (lam**k)*math.exp(-lam)/factorial(k)

def normal_pdf(x:float,mu:float=0.0,sigma:float=1.0)->float:
    z=(x-mu)/sigma; return math.exp(-0.5*z*z)/(sigma*math.sqrt(2*math.pi))

def normal_cdf(x:float,mu:float=0.0,sigma:float=1.0)->float:
    z=(x-mu)/(sigma*math.sqrt(2)); t=1/(1+0.3275911*abs(z))
    a1,a2,a3,a4,a5=0.254829592,-0.284496736,1.421413741,-1.453152027,1.061405429
    erf=1-(((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*math.exp(-z*z)
    if z<0: erf=-erf
    return 0.5*(1+erf)

# ---------- Estructuras básicas ----------
@dataclass(order=True)
class PQItem:
    priority: float
    value: Any=field(compare=False)

class MinPQ:
    def __init__(self):
        import heapq; self._h=heapq; self._heap: List[PQItem]=[]
    def push(self,priority:float,value:Any): self._h.heappush(self._heap,PQItem(priority,value))
    def pop(self)->Any: return self._h.heappop(self._heap).value
    def __len__(self)->int: return len(self._heap)

class DSU:
    def __init__(self): self.p:Dict[Any,Any]={}; self.r:Dict[Any,int]={}
    def find(self,x:Any)->Any:
        if x not in self.p: self.p[x]=x; self.r[x]=0; return x
        if self.p[x]!=x: self.p[x]=self.find(self.p[x])
        return self.p[x]
    def union(self,a:Any,b:Any):
        ra,rb=self.find(a),self.find(b)
        if ra==rb: return
        if self.r[ra]<self.r[rb]: ra,rb=rb,ra
        self.p[rb]=ra
        if self.r[ra]==self.r[rb]: self.r[ra]+=1

# ---------- Grafos ----------
class Graph:
    def __init__(self): self.adj:Dict[Any,List[Tuple[Any,float]]]=defaultdict(list)
    def add(self,u:Any,v:Any,w:float=1.0,bidir:bool=True):
        self.adj[u].append((v,w)); 
        if bidir: self.adj[v].append((u,w))
    def neighbors(self,u:Any)->List[Tuple[Any,float]]: return self.adj.get(u,[])

def bfs(graph:Graph,start:Any)->Dict[Any,int]:
    dist={start:0}; q=deque([start])
    while q:
        u=q.popleft()
        for v,_ in graph.neighbors(u):
            if v not in dist: dist[v]=dist[u]+1; q.append(v)
    return dist

def dijkstra(graph:Graph,start:Any)->Dict[Any,float]:
    import heapq
    dist:Dict[Any,float]=defaultdict(lambda:float("inf")); dist[start]=0.0
    pq=[(0.0,start)]
    while pq:
        d,u=heapq.heappop(pq)
        if d!=dist[u]: continue
        for v,w in graph.neighbors(u):
            nd=d+w
            if nd<dist[v]: dist[v]=nd; heapq.heappush(pq,(nd,v))
    return dict(dist)

def a_star(graph:Graph,start:Any,goal:Any,h:Callable[[Any,Any],float])->Tuple[float,List[Any]]:
    import heapq
    g=defaultdict(lambda:float("inf")); g[start]=0.0
    f=defaultdict(lambda:float("inf")); f[start]=h(start,goal)
    came={start:None}; openq=[(f[start],start)]
    while openq:
        _,u=heapq.heappop(openq)
        if u==goal:
            path=[]; 
            while u is not None: path.append(u); u=came[u]
            path.reverse(); return g[goal], path
        for v,w in graph.neighbors(u):
            tg=g[u]+w
            if tg<g[v]: came[v]=u; g[v]=tg; f[v]=tg+h(v,goal); heapq.heappush(openq,(f[v],v))
    return float("inf"), []

# ---------- Cadenas ----------
def kmp_build(p:str)->List[int]:
    m=len(p); lps=[0]*m; j=0
    for i in range(1,m):
        while j>0 and p[i]!=p[j]: j=lps[j-1]
        if p[i]==p[j]: j+=1
        lps[i]=j
    return lps

def kmp_search(s:str,p:str)->List[int]:
    if not p: return list(range(len(s)+1))
    lps=kmp_build(p); i=j=0; out=[]
    while i<len(s):
        if s[i]==p[j]:
            i+=1; j+=1
            if j==len(p): out.append(i-j); j=lps[j-1]
        else:
            j=lps[j-1] if j>0 else 0; 
            if j==0: i+=1
    return out

def rle_encode(data:str)->str:
    if not data: return ""
    out=[]; cnt=1
    for i in range(1,len(data)):
        if data[i]==data[i-1]: cnt+=1
        else: out.append(f"{data[i-1]}:{cnt};"); cnt=1
    out.append(f"{data[-1]}:{cnt};")
    return "".join(out)

def rle_decode(encoded:str)->str:
    if not encoded: return ""
    out=[]
    for chunk in encoded.split(";"):
        if not chunk: continue
        ch,num=chunk.split(":"); out.append(ch*int(num))
    return "".join(out)

# ---------- IO: JSON/CSV y tabla ----------
def read_json(path:str)->Any:
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def write_json(path:str,obj:Any)->None:
    with open(path,"w",encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)

def read_csv(path:str)->List[Dict[str,str]]:
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def write_csv(path:str,rows:List[Dict[str,Any]])->None:
    if not rows:
        with open(path,"w",newline="",encoding="utf-8") as f: f.write(""); return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def table(rows:List[List[Any]])->str:
    if not rows: return ""
    widths=[max(len(str(x)) for x in col) for col in zip(*rows)]
    out=[]
    for i,r in enumerate(rows):
        line=" | ".join(str(x).ljust(widths[j]) for j,x in enumerate(r)); out.append(line)
        if i==0: out.append("-+-".join("-"*w for w in widths))
    return "\n".join(out)

# ---------- ML mínimo ----------
def euclid(a:List[float],b:List[float])->float:
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def knn_predict(train_X:List[List[float]],train_y:List[Any],x:List[float],k:int=3)->Any:
    d=[(euclid(x,xi),yi) for xi,yi in zip(train_X,train_y)]; d.sort(key=lambda t:t[0])
    top=d[:k]; return Counter(yi for _,yi in top).most_common(1)[0][0]

class NaiveBayes:
    def __init__(self): self.priors:Dict[Any,float]={}; self.means:Dict[Any,List[float]]={}; self.vars:Dict[Any,List[float]]={}
    def fit(self,X:List[List[float]],y:List[Any])->None:
        for c in sorted(set(y)):
            Xc=[xi for xi,yi in zip(X,y) if yi==c]; self.priors[c]=len(Xc)/len(X)
            cols=list(zip(*Xc)); self.means[c]=[statistics.mean(col) for col in cols]
            self.vars[c]=[statistics.pvariance(col)+1e-9 for col in cols]
    def predict_one(self,x:List[float])->Any:
        best,blp=None,-float("inf")
        for c in self.priors:
            lp=math.log(self.priors[c])
            for i,xi in enumerate(x):
                mu=self.means[c][i]; var=self.vars[c][i]
                lp += -0.5*math.log(2*math.pi*var) - 0.5*((xi-mu)**2)/var
            if lp>blp: blp, best = lp, c
        return best
    def predict(self,X:List[List[float]])->List[Any]: return [self.predict_one(x) for x in X]

# ---------- Parser de expresiones ----------
def tokenize_expr(s:str)->List[str]:
    toks=[]; i=0
    while i<len(s):
        c=s[i]
        if c.isspace(): i+=1; continue
        if c in "+-*/()": toks.append(c); i+=1; continue
        if c.isdigit() or c==".":
            j=i+1
            while j<len(s) and (s[j].isdigit() or s[j]=="."): j+=1
            toks.append(s[i:j]); i=j; continue
        raise ValueError(f"Caracter no válido: {c}")
    return toks

class Parser:
    def __init__(self,toks:List[str]): self.t=toks; self.i=0
    def peek(self)->str: return self.t[self.i] if self.i<len(self.t) else "\0"
    def eat(self,tok:str=None)->str:
        cur=self.peek()
        if tok and cur!=tok: raise ValueError(f"Esperaba {tok} y vi {cur}")
        self.i+=1; return cur
    def parse(self)->float:
        v=self.expr()
        if self.peek()!="\0": raise ValueError("Tokens extra")
        return v
    def expr(self)->float:
        v=self.term()
        while self.peek() in ("+","-"):
            op=self.eat(); w=self.term(); v=v+w if op=="+" else v-w
        return v
    def term(self)->float:
        v=self.factor()
        while self.peek() in ("*","/"):
            op=self.eat(); w=self.factor(); v=v*w if op=="*" else v/w
        return v
    def factor(self)->float:
        tok=self.peek()
        if tok=="(": self.eat("("); v=self.expr(); self.eat(")"); return v
        if tok=="-": self.eat("-"); return -self.factor()
        self.eat(); return float(tok)

# ---------- Demos ----------
def demo_linear_algebra():
    A=[[3,2,0],[1,-1,0],[0,5,1]]; b=[2,4,-1]; x=gauss_jordan(A,b)
    lam,vec=power_method([[2,1],[1,3]])
    print("x =",[round(xi,4) for xi in x])
    print("lambda_max ~",round(lam,4),"vec ~",[round(v,4) for v in vec])

def demo_numerics():
    f=lambda x:x*math.cos(x)-0.25; df=lambda x:math.cos(x)-x*math.sin(x)
    root_b=bisection(f,0,2); root_n=newton(f,df,1.0)
    area=simpson(lambda x:math.sin(x),0,math.pi,1000)
    traj=rk4(lambda t,y:-2*y,0.0,1.0,0.1,10)
    print("bisection ~",round(root_b,6),"newton ~",round(root_n,6),"area sin ~",round(area,6))
    print("rk4 last:",traj[-1])

def demo_strings():
    s="ababcabcabababd"; p="ababd"
    print("KMP:",kmp_search(s,p))
    enc=rle_encode("aaaabbbbccccddaa"); dec=rle_decode(enc)
    print("RLE:",enc, dec=="aaaabbbbccccddaa")    

def demo_graphs():
    g=Graph(); g.add("A","B",4); g.add("A","C",2); g.add("C","D",7); g.add("B","D",1)
    print("BFS:",bfs(g,"A")); print("Dijkstra:",dijkstra(g,"A"))
    rnd=random_graph(6,0.4); print("Rnd Dijkstra 0->:", dijkstra(rnd,0))

def demo_ml():
    X=[[0,0],[0,1],[1,0],[1,1]]; y=["neg","pos","pos","pos"]
    pred=knn_predict(X,y,[0.2,0.9],k=3); nb=NaiveBayes(); nb.fit(X,y)
    print("kNN:",pred,"NB:",nb.predict([[0,0],[1,1],[0.3,0.8]]))

def demo_parser():
    expr="3 + 4*(2-1) - 5/2"; toks=tokenize_expr(expr); val=Parser(toks).parse(); print(expr,"=",val)

def demo_table():
    rows=[["Name","Score"],["Ana",9.1],["Luis",8.7],["Khalid",9.5]]; print(table(rows))

def random_graph(n:int,density:float=0.2,wmin:float=1.0,wmax:float=10.0)->Graph:
    g=Graph()
    for i in range(n):
        for j in range(i+1,n):
            if random.random()<density:
                w=random.uniform(wmin,wmax); g.add(i,j,w,True)
    return g

# ---------- CLI ----------
COMMANDS:Dict[str,Tuple[str,Callable[[],None]]]={
    "la":("Álgebra lineal", demo_linear_algebra),
    "num":("Métodos numéricos", demo_numerics),
    "str":("Cadenas", demo_strings),
    "gra":("Grafos", demo_graphs),
    "ml": ("ML básico", demo_ml),
    "par":("Parser expr", demo_parser),
    "tab":("Tabla", demo_table),
}

def menu():
    print("\n=== DataToolkit600 ===")
    for k,(name,_) in COMMANDS.items(): print(f" {k:>3} : {name}")
    print("  ext : salir")

def run_cli():
    while True:
        menu()
        try: op=input("> ").strip()
        except EOFError: print(); break
        if op=="ext": print("Adiós"); break
        fn=COMMANDS.get(op)
        if fn:
            try: fn[1]()
            except Exception as e: print("Error:",e)
        else: print("Opción inválida")

# ---------- Pruebas (--test) ----------
def _test_all():
    # álgebra
    assert matvec([[1,2],[3,4]],[5,6])==[17,39]
    x=gauss_jordan([[2,1],[1,3]],[4,5])
    for a,b in zip(x,[1.0,1.3333333333]): assert abs(a-b)<1e-6
    lam,_=power_method([[2,1],[1,3]],iters=50); assert 3.6<lam<3.7
    # numéricos
    root=bisection(lambda v:v-2,0,5); assert abs(root-2)<1e-8
    rootn=newton(lambda t:t*t-2,lambda t:2*t,1.0); assert abs(rootn-math.sqrt(2))<1e-6
    area=trapezoid(lambda z:z,0,1,1000); assert abs(area-0.5)<1e-3
    # prob
    assert factorial(5)==120 and nCr(5,2)==10
    assert abs(normal_pdf(0)-1/math.sqrt(2*math.pi))<1e-9
    assert 0.49<normal_cdf(0)<0.51
    # estructuras
    pq=MinPQ(); pq.push(2,"b"); pq.push(1,"a"); assert pq.pop()=="a"
    dsu=DSU(); dsu.union(1,2); dsu.union(2,3); assert dsu.find(1)==dsu.find(3)
    # grafos
    g=Graph(); g.add(0,1,1); g.add(1,2,2)
    assert bfs(g,0)[2]==2
    dj=dijkstra(g,0); assert dj[2]==3
    c,p=a_star(g,0,2,lambda u,v:0); assert c==3 and p==[0,1,2]
    # cadenas
    assert kmp_search("abcabcd","abcd")==[3]
    enc=rle_encode("aaabb"); assert rle_decode(enc)=="aaabb"
    # io
    t=table([["A","B"],[1,22],[333,4]]); assert "|" in t and "-+-" in t
    # ml
    pred=knn_predict([[0,0],[1,1]],[0,1],[0.2,0.2],k=1); assert pred==0
    nb=NaiveBayes(); nb.fit([[0,0],[1,1]],[0,1]); assert nb.predict([[0,0],[1,1]])==[0,1]
    # parser
    expr="1+2*3-(4/2)"; val=Parser(tokenize_expr(expr)).parse(); assert abs(val-(1+6-2))<1e-9
    print("[self_test] OK")

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--test": _test_all()
    else: run_cli()

# ---------- Algoritmos adicionales ----------
def insertion_sort(a: List[Any]) -> List[Any]:
    a = a[:]
    for i in range(1, len(a)):
        x = a[i]; j = i-1
        while j >= 0 and a[j] > x:
            a[j+1] = a[j]; j -= 1
        a[j+1] = x
    return a

def merge_sort(a: List[Any]) -> List[Any]:
    if len(a) <= 1: return a[:]
    mid = len(a)//2
    left = merge_sort(a[:mid]); right = merge_sort(a[mid:])
    i = j = 0; out = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: out.append(left[i]); i += 1
        else: out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out

def _partition(a: List[Any], lo: int, hi: int) -> int:
    pivot = a[hi]; i = lo
    for j in range(lo, hi):
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]
    return i

def quickselect(a: List[Any], k: int) -> Any:
    a = a[:]; lo, hi = 0, len(a)-1
    while True:
        p = _partition(a, lo, hi)
        if p == k: return a[p]
        if k < p: hi = p-1
        else: lo = p+1

def heapsort(a: List[Any]) -> List[Any]:
    import heapq
    h = a[:]; heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

def lis(seq: List[int]) -> List[int]:
    if not seq: return []
    tails = []; prev = [-1]*len(seq); idx = []
    def lower_bound(arr, x):
        lo, hi = 0, len(arr)
        while lo < hi:
            mid = (lo+hi)//2
            if arr[mid] < x: lo = mid+1
            else: hi = mid
        return lo
    for i,x in enumerate(seq):
        j = lower_bound(tails, x)
        if j == len(tails): tails.append(x); idx.append(i)
        else: tails[j] = x; idx[j] = i
        if j > 0: prev[i] = idx[j-1]
    k = idx[len(tails)-1]; out = []
    while k != -1: out.append(seq[k]); k = prev[k]
    return out[::-1]

def edit_distance(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if a[i-1]==b[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[n][m]

def random_walk(steps: int, seed: Optional[int]=None) -> Tuple[int,int]:
    if seed is not None: random.seed(seed)
    x = y = 0
    for _ in range(steps):
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        x += dx; y += dy
    return x, y

def monte_carlo_pi(n: int, seed: Optional[int]=None) -> float:
    if seed is not None: random.seed(seed)
    inside = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1: inside += 1
    return 4*inside/n if n>0 else float("nan")

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: Dict[Any, Any] = {}
        self.order: deque = deque()
    def get(self, key: Any) -> Any:
        if key not in self.map: return None
        self.order.remove(key); self.order.appendleft(key)
        return self.map[key]
    def put(self, key: Any, value: Any) -> None:
        if key in self.map:
            self.order.remove(key)
        elif len(self.order) >= self.cap:
            old = self.order.pop(); self.map.pop(old, None)
        self.map[key] = value; self.order.appendleft(key)

class Scheduler:
    def __init__(self): self.tasks: List[Tuple[float, Callable[[],None], float]] = []
    def every(self, seconds: float, fn: Callable[[],None]): self.tasks.append((time.perf_counter()+seconds, fn, seconds))
    def run_for(self, seconds: float):
        end = time.perf_counter()+seconds
        while time.perf_counter() < end:
            now = time.perf_counter()
            for i,(t,fn,period) in enumerate(self.tasks):
                if now >= t:
                    fn()
                    self.tasks[i] = (now+period, fn, period)
            time.sleep(0.01)
# pad 1
# pad 2
# pad 3
# pad 4
# pad 5
# pad 6
# pad 7
# pad 8
# pad 9
# pad 10
# pad 11
# pad 12
# pad 13
# pad 14
# pad 15
# pad 16
# pad 17
# pad 18
# pad 19
# pad 20
# pad 21
# pad 22
# pad 23
