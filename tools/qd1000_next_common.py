"""Authoring helpers for the second reviewed Qidian batch (2026-11-18)."""
import json
from html import escape
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'public/img/reviewed'
cards = []
s, t = sp.symbols('s t', real=True)

def label(x, y, text):
    return f'<text x="{x}" y="{y}" text-anchor="middle">{escape(text)}</text>'

def fig(name, title, body, width=640, height=240):
    path = FIG / f'{name}.svg'
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title><defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 1L10 5 0 9z" fill="#20384d"/></marker></defs>
<style>text{{fill:#142f45;font:15px "Times New Roman",SimSun,serif}}.wire,.arr{{fill:none;stroke:#20384d;stroke-width:1.65;stroke-linecap:round;stroke-linejoin:round}}.arr{{marker-end:url(#ar)}}.box{{fill:#fff;stroke:#20384d;stroke-width:1.6}}.node{{fill:#20384d}}</style><rect width="100%" height="100%" fill="white"/>{body}</svg>''', encoding='utf-8')
    return f'![{title}](img/reviewed/{name}.svg)'

def D(tex): return '$$'+tex.strip()+'$$'
def L(expr): return sp.latex(sp.factor(expr))

def routh(coeff):
    """Exact Routh table, including auxiliary polynomials and zero pivots."""
    eps=sp.Symbol('\\varepsilon',positive=True)
    n=len(coeff)-1; width=(n+2)//2
    rows=[[sp.S(0)]*width for _ in range(n+1)]
    for j,v in enumerate(coeff[::2]):rows[0][j]=sp.sympify(v)
    for j,v in enumerate(coeff[1::2]):rows[1][j]=sp.sympify(v)
    special=[]
    for i in range(2,n+1):
        if all(v==0 for v in rows[i-1]):
            power=n-i+2
            rows[i-1]=[sp.simplify(v*(power-2*j)) for j,v in enumerate(rows[i-2])]
            special.append(f'$s^{{{n-i+1}}}$ 行全零，使用上一行辅助多项式的导数替换。')
        if rows[i-1][0]==0:
            rows[i-1][0]=eps
            special.append('首项为零而非全零行时，用正的 $\\varepsilon$ 代替并取右极限。')
        for j in range(width-1):
            rows[i][j]=sp.cancel((rows[i-1][0]*rows[i-2][j+1]-rows[i-2][0]*rows[i-1][j+1])/rows[i-1][0])
    first=[r[0] for r in rows]
    signs=[sp.sign(sp.limit(x,eps,0,dir='+')) for x in first]
    assert all(x in [-1,0,1] for x in signs)
    clean=[x for x in signs if x]
    changes=sum(a!=b for a,b in zip(clean,clean[1:]))
    table='\\begin{array}{c|'+'c'*width+'}'+'\\\\'.join('s^{'+str(n-i)+'}&'+'&'.join(sp.latex(v) for v in row) for i,row in enumerate(rows))+'\\end{array}'
    text='**列劳斯表。**\n'+D(table)+'\n\n'+' '.join(dict.fromkeys(special))
    text+='\n\n首列符号依次为 $'+','.join('+' if x>0 else '-' if x<0 else '0' for x in signs)+'$，有 '+str(changes)+' 次变号，故右半平面根有 '+str(changes)+' 个。'
    return text, changes

def C(ch, kind, n, origin, qp, ap, stem, answer, exp, topic, notes=''):
    item = dict(volume='A',chapter=ch,kind=kind,number=n,origin=origin,
                questionPages=str(qp),answerPages=str(ap),topics=[topic],
                stem=stem.strip(),answer=answer.strip(),explanation=exp.strip(),notes=notes)
    assert all(item[k] for k in ('stem','answer','explanation','origin'))
    assert not any(ord(c)<32 and c not in '\n\r\t' for k in ('stem','answer','explanation') for c in item[k]), (ch,kind,n,'control character')
    assert not any((q['chapter'],q['kind'],q['number']) == (ch,kind,n) for q in cards)
    cards.append(item)
    return item

def save(name):
    (ROOT/'data-src/practice'/name).write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def circuit(name, positions, components, inp='Ui', out='Uo'):
    """Draw an explicit electrical net, with components specified between nodes."""
    body=[]
    for a,b,typ,txt in components:
        x1,y1=positions[a];x2,y2=positions[b];dx=x2-x1;dy=y2-y1
        length=(dx*dx+dy*dy)**.5; ux=dx/length;uy=dy/length
        midx=(x1+x2)/2;midy=(y1+y2)/2
        if typ=='wire':body.append(f'<path class="wire" d="M{x1} {y1}L{x2} {y2}"/>');continue
        aa=(midx-ux*18,midy-uy*18);bb=(midx+ux*18,midy+uy*18)
        body.append(f'<path class="wire" d="M{x1} {y1}L{aa[0]} {aa[1]}M{bb[0]} {bb[1]}L{x2} {y2}"/>')
        if typ=='C':
            for d in (-4,4):
                px=midx+ux*d;py=midy+uy*d
                body.append(f'<path class="wire" d="M{px-uy*13} {py+ux*13}L{px+uy*13} {py-ux*13}"/>')
            body.append(f'<path class="wire" d="M{aa[0]} {aa[1]}L{midx-ux*4} {midy-uy*4}M{midx+ux*4} {midy+uy*4}L{bb[0]} {bb[1]}"/>')
        else:
            body.append(f'<rect class="box" x="{midx-18}" y="{midy-9}" width="36" height="18" transform="rotate({90 if dy else 0} {midx} {midy})"/>')
        body.append(label(midx+(24 if dy else 0),midy+(5 if dy else -17),txt))
    for key,(x,y) in positions.items():body.append(f'<circle class="node" cx="{x}" cy="{y}" r="2.7"/>')
    body.extend([label(40,140,inp),label(560,140,out)])
    return fig(name,'电路元件与接线关系',''.join(body),600,240)
