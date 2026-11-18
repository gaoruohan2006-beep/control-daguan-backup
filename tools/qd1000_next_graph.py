import itertools,json
from collections import defaultdict
import networkx as nx
import sympy as m
from qd1000_next_common import fig,label

PAGE_START=[18,20,21,22,23,25,27,28,29,31,32,33,34,34,35,37,37,39,40,41,42,43,45,46,47,48,49,50,52,53,53,55,56,57,58,60,61,64,65,67,68]
def ap(n):
    a=PAGE_START[n-1]-2
    b=max(a,PAGE_START[n]-3)
    return f'{a}–{b}' if a!=b else a
def tex(x):return '$'+m.latex(x)+'$'
def inl(x):return '$'+x+'$'
def disp(x):return '$$'+x+'$$'
def ind(base,i):return f'{base}_{{{i}}}'
def pretty(t):
    import re
    return re.sub(r'(?<=[A-Za-z])[0-9]+',lambda s:s[0].translate(str.maketrans('0123456789','₀₁₂₃₄₅₆₇₈₉')),t.replace('**2','²').replace('-', '−').replace('*','·'))
def frac(a,b):return rf'\frac{{{a}}}{{{b}}}'

def graph(n,nodes,links):
    pos={name:i for i,name in enumerate(nodes)}
    interval=113
    groups={True:[],False:[]}
    line=[]
    for a,b,g in links:
        i,j=pos[a],pos[b]
        if j==i+1:line.append((i,j,g,None))
        else:
            lo,hi=sorted((i,j))
            side=groups[j>i]
            lane=next((l for l,ranges in enumerate(side) if all(hi<x or lo>y for x,y in ranges)),len(side))
            if lane==len(side):side.append([])
            side[lane].append((lo,hi))
            line.append((i,j,g,lane))
    y=48+32*len(groups[True])
    h=y+48+32*len(groups[False])
    width=80+interval*(len(nodes)-1)
    body=[]
    for i,j,g,lane in line:
        x1,x2=40+i*interval,40+j*interval
        if lane is None:
            body.append(f'<path class="arr" d="M{x1+13} {y}H{x2-13}"/>')
            x,ytext=(x1+x2)/2,y-11
        elif i==j:
            bow=y+35+32*lane
            body.append(f'<path class="arr" d="M{x1+8} {y+10}C{x1+52} {bow} {x1-52} {bow} {x1-8} {y+10}"/>')
            x,ytext=x1,bow+4
        else:
            direct=1 if j>i else -1
            side=-direct
            start=x1+10*direct;end=x2-10*direct
            bend1=x1+40*direct;bend2=x2-40*direct
            level=y+side*(32+32*lane)
            body.append(f'<path class="arr" d="M{start} {y+side*8}Q{x1+22*direct} {level} {bend1} {level}H{bend2}Q{x2-22*direct} {level} {end} {y+side*8}"/>')
            x,ytext=(bend1+bend2)/2,level-7 if side==-1 else level+19
        gain=pretty(g)
        span=10*len(gain)+8
        body.append(f'<rect x="{x-span/2}" y="{ytext-13}" width="{span}" height="17" rx="3" fill="#fff"/>')
        body.append(label(x,ytext,gain))
    for node,i in pos.items():
        x=40+i*interval
        body += [f'<circle class="box" cx="{x}" cy="{y}" r="12"/>',label(x,y+4,pretty(node))]
    return fig(f'qd1000-next-graph-{n}','题中各信号支路及其增益','\n'.join(body),width,h)

def mason(nodes,links,queries):
    G=nx.DiGraph()
    G.add_nodes_from(nodes)
    z=defaultdict(list)
    for a,b,g in links:z[a,b].append(m.sympify(g))
    for (a,b),gs in z.items():G.add_edge(a,b,g=m.Add(*gs))
    def prod(node_path):
        return m.prod(G[a][b]['g'] for a,b in zip(node_path,node_path[1:]))
    cycles=[]
    for cycle in nx.simple_cycles(G):
        first=min(range(len(cycle)),key=lambda i:nodes.index(cycle[i]))
        cycles.append(cycle[first:]+cycle[:first])
    loops=sorted(cycles,key=lambda cycle:(len(cycle),tuple(nodes.index(y) for y in cycle)))
    loop_values=[prod(c+[c[0]]) for c in loops]
    loop_nodes=list(map(set,loops))
    forms=[]
    for k in range(1,len(loops)+1):
        group=[ix for ix in itertools.combinations(range(len(loops)),k)
               if all(not (loop_nodes[i]&loop_nodes[j]) for i,j in itertools.combinations(ix,2))]
        if not group:break
        forms.append(group)
    def d(path=(), symbolic=False):
        loop_terms=[m.Symbol(f'L{i+1}') if symbolic else g for i,g in enumerate(loop_values)]
        omit=set(path)
        return 1+sum((-1)**k*m.prod(loop_terms[i] for i in ix) for k,level in enumerate(forms,1)
                     for ix in level if all(not (omit&loop_nodes[i]) for i in ix))
    D=d()
    unknowns=[m.Symbol(v) for v in nodes if G.in_degree(v)]
    eq=[]
    for u in unknowns:
        ins=sum(m.Symbol(t)*G[t][str(u)]['g'] for t in G.predecessors(str(u)))
        eq.append(disp(m.latex(u)+'='+m.latex(ins)+'.'))
    loop_list=[]
    for i,(loop,g) in enumerate(zip(loops,loop_values),1):
        loop_list.append(inl(ind('L',i)+'='+m.latex(g))+'，对应 '+inl(r'\to '.join(m.latex(m.Symbol(a)) for a in loop+[loop[0]]))+'。')
    pairs=[inl(m.latex(m.prod(m.Symbol(f'L{i+1}') for i in idx))) for group in forms[1:] for idx in group]
    pairs_ex=('互不接触的回路乘积为 '+'、'.join(pairs)+'。') if pairs else '没有互不接触的回路乘积项。'
    if len(loops)>5:
        delta=disp(r'\Delta=1-S_1'+('+S_2' if len(forms)>1 else '')+('-S_3' if len(forms)>2 else '')+'.')+'\n\n'
        delta+='各阶 $S_k$ 是上列每组 $k$ 个互不接触回路的增益乘积之和。$S_1$ 为所有单独回路增益的和。'
        assert len(forms)<=3
    else:delta=disp(r'\Delta='+m.latex(d(symbolic=True))+'.')
    extras=[]
    answers=[]
    solved={}
    for a,b in queries:
        paths=list(nx.all_simple_paths(G,a,b))
        assert paths,(a,b)
        P=[prod(p) for p in paths]
        dg=[d(p) for p in paths]
        numerator=sum(p*x for p,x in zip(P,dg))
        sol=m.factor(numerator/D)
        solved[a,b]=sol
        symbolic_matrix=m.eye(len(unknowns))
        symbolic_input=m.zeros(len(unknowns),1)
        for u,x,g in G.edges.data('g'):
            row=unknowns.index(m.Symbol(x))
            if m.Symbol(u) in unknowns:
                symbolic_matrix[row,unknowns.index(m.Symbol(u))]-=g
            elif u==a:
                symbolic_input[row,0]+=g
        det=symbolic_matrix.det(method="domain-ge")
        replaced=symbolic_matrix.copy()
        replaced[:,unknowns.index(m.Symbol(b))]=symbolic_input
        det_output=replaced.det(method="domain-ge")
        assert m.cancel(det-D)==0,(a,b,"characteristic determinant")
        assert m.cancel(det_output-numerator)==0,(a,b,"transfer numerator")
        variables=sorted(set().union(*(g.free_symbols for gs in z.values() for g in gs)),key=str)
        for j in range(5):
            sub={x:m.Rational((i*7+j*5+1)%19+1,17+(i+j)%4) for i,x in enumerate(variables)}
            A=m.eye(len(unknowns)); B=m.zeros(len(unknowns),1)
            for u,x,g in G.edges.data('g'):
                dest=unknowns.index(m.Symbol(x));gain=g.subs(sub)
                if m.Symbol(u) in unknowns:A[dest,unknowns.index(m.Symbol(u))]-=gain
                elif u==a:B[dest,0]+=gain
            assert A.det()!=0,(a,b)
            assert m.simplify(sol.subs(sub)-(A.inv()*B)[unknowns.index(m.Symbol(b))])==0,(a,b,sol)
        lhs=frac(m.latex(m.Symbol(b)),m.latex(m.Symbol(a)))
        extras.append('**'+inl(lhs)+' 的前向通路。**')
        for i,p in enumerate(paths,1):
            extras.append(inl(r'\to '.join(m.latex(m.Symbol(k)) for k in p))+' 的增益与余因子为\n'+
                          disp(ind('P',i)+'='+m.latex(P[i-1])+r',\qquad '+ind(r'\Delta',i)+'='+m.latex(d(p,True))+'.'))
        groups='+'.join(ind('P',i)+ind(r'\Delta',i) for i in range(1,len(paths)+1))
        extras.append(disp(lhs+'='+frac(groups,r'\Delta')+'.'))
        N=m.latex(m.factor(numerator))
        if len(N)<=115:answers.append(disp(lhs+'='+frac(N,r'\Delta')+'.'))
        else:
            k=r'N_{'+b+a+'}'
            answers.append(disp(lhs+'='+frac(k,r'\Delta')+'.')+'\n\n'+
                '分子 '+inl(k+'='+groups)+'，各通路增益和余因子见解析。')
    exp='\n\n'.join(['**从信号图列方程。** 以下增益省略自变量 $s$。求某一外输入的通道时，其余独立输入置零。',*eq,
                    '**逐条核对回路。**',*loop_list,pairs_ex,delta,*extras])
    return solved,'\n\n'.join(['下式的 $\Delta$ 由解析中的有向回路确定。',*answers]),exp

