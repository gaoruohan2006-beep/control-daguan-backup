"""Reproducible response and pole illustrations for the second book batch."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import step, TransferFunction
from qd1000_next_graph import graph,mason
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/img/reviewed'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'path',
                     'axes.spines.top':False,'axes.spines.right':False})
images={}

def chart(n, systems, end, title, normalize=False, band=None):
    fig,ax=plt.subplots(figsize=(8,3.8),layout='constrained')
    times=np.linspace(0,end,2500)
    for label,num,den in systems:
        tt,yy=step(TransferFunction(num,den),T=times)
        if normalize: yy=yy/(num[-1]/den[-1])
        ax.plot(tt,yy,lw=1.8,label=label)
    if band:
        ax.axhspan(1-band,1+band,color='#8fa6ad',alpha=.15,label=f'{band:.0%} band')
    ax.set(xlabel='Time t (s)',ylabel='Normalized output' if normalize else 'Output c(t)',title=title)
    ax.grid(alpha=.22);ax.legend(loc='best',fontsize=9)
    name=f'qd1000-next-response-{n}.svg';fig.savefig(OUT/name);plt.close(fig)
    images[n]=f'![第3章分析题{n}的响应比较](img/reviewed/{name})'

def main():
    model_path=ROOT/'data-src/practice/qd1000-a-models-041-068.json'
    model_cards=json.loads(model_path.read_text('utf-8'))
    structures={
        43:('Ui I1 Ua I2 Uo','Ui:I1:1/R1 Ua:I1:-1/R1 I1:Ua:1/(C1*s) I2:Ua:-1/(C1*s) Ua:I2:1/R2 Uo:I2:-1/R2 I2:Uo:1/(C2*s)','Ui','Uo'),
        52:('Va E Tm M L','Va:E:1 M:E:-Kb*s E:Tm:KT/Ra Tm:M:A/D M:L:KL/A','Va','L'),
        56:('U1 I1 U3 I2 U2','U1:I1:1/R1 U3:I1:-1/R1 I1:U3:1/(C*s) I2:U3:-1/(C*s) U3:I2:1/(L*s) U2:I2:-1/(L*s) I2:U2:R2','U1','U2'),
        65:('U1 E V I M W','U1:E:1 W:E:-K3 E:V:K1 W:V:-Ce V:I:1/(L*s+R) I:M:Cm M:W:1/(J*s+f)','U1','W'),
    }
    for n,(names,edges,inp,out) in structures.items():
        nodes=names.split();links=[tuple(e.split(':')) for e in edges.split()]
        image=graph(f'2-{n}-solution',nodes,links)
        solved,_,_=mason(nodes,links,[(inp,out)])
        sx=sp.Symbol('s')
        if n==43:
            R1,R2,C1,C2=sp.symbols('R1 R2 C1 C2')
            expected=1/(R1*R2*C1*C2*sx*sx+(R1*C1+R1*C2+R2*C2)*sx+1)
            assert sp.cancel(solved[inp,out]-expected)==0
        card=next(q for q in model_cards if q['number']==n)
        caption='**等价信号流结构图。** 节点为求和点，支路标出对应环节；负号已包含在反馈增益中。'
        if n==52:caption+=' 图中M、L分别表示电机与负载角位移，A、D同上。'
        if n==65:caption+=' 图中W表示角速度，V表示扣除反电动势后的电枢电压。'
        if image not in card['explanation']:card['explanation']+='\n\n'+caption+'\n\n'+image
    model_path.write_text(json.dumps(model_cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    chart(42,[('Original',[2],[1,2,2]),('Added zero',[10,2],[1,2,2]),('Added pole',[2],[1,7,12,10])],8,'Complete models: normalized step responses',True,.05)
    full=np.polymul(np.polymul([1,2,2],[1,2]),[1,11.05])
    chart(52,[('Complete model',[1,12,22.21,22.1],full),('Reduced model',[1],[1,2])],7,'Near cancellation: full and reduced models',True,.02)
    kc=81.00266775;td=.08652843324
    chart(74,[('PD zero retained',[kc*td,kc],[1,kc*td,kc-.8])],1.7,'Design verified with the closed-loop zero',True,.05)
    d=4+3.226313418
    chart(77,[('T = 0',[2,24],[3,d,12]),('T = 1',[2,24],np.polymul([1,1],[3,d,12]))],7,'Reference filter and complete step responses')
    chart(86,[(f'K = {k}, tau = {tau}',[k],[1,1+k*tau,k]) for k,tau in [(2,.2),(10,.5),(10,.2)]],8,'Rate feedback: three parameter sets')
    fig,(ax,px)=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
    times=np.linspace(0,14,1800)
    for z in [0,.5,1,2]:
        tt,yy=step(TransferFunction([1],[1,2*z,1]),T=times)
        line,=ax.plot(tt,yy,label=rf'$\zeta={z}$')
        poles=np.roots([1,2*z,1]);px.scatter(poles.real,poles.imag,marker='x',s=60,color=line.get_color(),label=rf'$\zeta={z}$')
        if z==1:px.annotate('double',(-1,0),xytext=(-1.8,.4),arrowprops={'arrowstyle':'->','color':'#555'})
    ax.set(xlabel='Normalized time t/T',ylabel='Output c(t)',title='Four damping regimes');ax.legend();ax.grid(alpha=.2)
    px.axhline(0,color='#888',lw=.7);px.axvline(0,color='#888',lw=.7);px.set(xlabel='Re(sT)',ylabel='Im(sT)',title='Normalized closed-loop poles');px.grid(alpha=.2)
    name='qd1000-next-response-81.svg';fig.savefig(OUT/name);plt.close(fig)
    images[81]=f'![四种阻尼的归一响应与极点](img/reviewed/{name})'
    path=ROOT/'data-src/practice/qd1000-a-time-analysis.json'
    cards=json.loads(path.read_text('utf-8'))
    for q in cards:
        if q['number'] in images:
            marker=images[q['number']]
            if marker not in q['explanation']:q['explanation']+='\n\n'+marker
    path.write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Response illustrations:',len(images))

if __name__=='__main__':main()
