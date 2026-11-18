"""Independent algebra, pole and full-response checks for difficult book items."""
import ast,json,math
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import root,brentq
from qd1000_metrics import metrics

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa/2026-11-18-next200'
s,t=sp.symbols('s t',real=True)
checks=[]
def equal(name,lhs,rhs):
    assert sp.cancel(lhs-rhs)==0,name
    checks.append({'name':name,'method':'independent symbolic residual','passed':True})
def close(name,actual,expected,tol=5e-5):
    assert abs(actual-expected)<tol,(name,actual,expected)
    checks.append({'name':name,'actual':float(actual),'expected':expected,'tolerance':tol,'passed':True})

def main():
    # Numeric roots are independent of the Routh implementation used in authoring.
    for path in (ROOT/'tools').glob('author_qd1000_*.py'):
        for node in ast.walk(ast.parse(path.read_text('utf-8'))):
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and getattr(node.value.func,'id','')=='routh':
                try: coeff=ast.literal_eval(node.value.args[0])
                except (ValueError,TypeError):continue
                nxt=next((n for n in ast.walk(ast.parse(path.read_text('utf-8'))) if isinstance(n,ast.Assert) and n.lineno==node.end_lineno),None)
                expected=nxt.test.comparators[0].value if nxt and isinstance(nxt.test,ast.Compare) else None
                if expected is not None:
                    actual=sum(z.real>1e-6 for z in np.roots(coeff))
                    close(f'{path.name}:{node.lineno}: RHP roots',actual,expected,.1)
    # Shifted-pole intervals: test both sides of each strict boundary.
    cases=[('A3-5',lambda k:[1,1,1,k-14],[(13,False),(14.1,True),(14.9,True),(16,False)]),
           ('A3-12',lambda k:[1,4,1,12*k-6],[(.49,False),(.51,True),(.83,True),(.84,False)]),
           ('A3-fill14',lambda k:[1,9,18,k,k],[(72,True),(80.99,True),(81.01,False)]),
           ('A3-85',lambda k:[1,7,47,64*k-55],[(.85,False),(.87,True),(5.99,True),(6.01,False)])]
    for label,poly,points in cases:
        for k,expected in points:
            actual=bool(np.max(np.roots(poly(k)).real)<-1e-8)
            assert actual==expected,(label,k)
            checks.append({'name':f'{label}, K={k}','stable':actual,'passed':True})
    # Nonzero initial states: ODE residuals and both initial conditions.
    y=1-11*sp.exp(-2*t)+8*sp.exp(-3*t)
    equal('A3-2 ODE',sp.diff(y,t,2)+5*sp.diff(y,t)+6*y,6)
    equal('A3-2 initial y',y.subs(t,0),-2);equal('A3-2 initial derivative',sp.diff(y,t).subs(t,0),-2)
    y=1-4*sp.exp(-t)+2*sp.exp(-2*t)
    equal('A3-8 ODE',sp.diff(y,t,2)+3*sp.diff(y,t)+2*y,2)
    equal('A3-8 initial y',y.subs(t,0),-1);equal('A3-8 initial derivative',sp.diff(y,t).subs(t,0),0)
    y=sp.Rational(7,8)*sp.exp(t)-sp.exp(-t)/4+sp.Rational(3,8)*sp.exp(-3*t)
    equal('A3-93 ODE',sp.diff(y,t,2)+2*sp.diff(y,t)-3*y,sp.exp(-t))
    equal('A3-93 initial y',y.subs(t,0),1);equal('A3-93 initial derivative',sp.diff(y,t).subs(t,0),0)
    y=1-sp.Rational(17,15)*sp.exp(-t/2)+sp.Rational(7,30)*sp.exp(-2*t)
    equal('A3-112 ODE',sp.diff(y,t,2)+sp.Rational(5,2)*sp.diff(y,t)+y,1)
    equal('A3-112 initial y',y.subs(t,0),sp.Rational(1,10));equal('A3-112 initial derivative',sp.diff(y,t).subs(t,0),sp.Rational(1,10))
    R1,R2,R3,C1,C2,C3=sp.symbols('R1 R2 R3 C1 C2 C3',positive=True)
    va,vb,vc=sp.symbols('va vb vc')
    network=sp.solve([(va-1)/R1+C1*s*va+(va-vb)/R2,(vb-va)/R2+C2*s*(vb-vc),C2*s*(vc-vb)+vc/R3+C3*s*vc],[va,vb,vc])
    a3=R1*R2*R3*C1*C2*C3
    a2=R1*R2*C1*C2+R1*R3*C1*C2+R1*R3*C1*C3+R1*R3*C2*C3+R2*R3*C2*C3
    a1=R1*C1+R1*C2+R2*C2+R3*C2+R3*C3
    equal('A2-57 three-node KCL',(network[vb]-network[vc]),(1+R3*C3*s)/(a3*s**3+a2*s**2+a1*s+1))
    G1,G2,G3=sp.symbols('G1 G2 G3');x,y,u,c,r=sp.symbols('x y u c r')
    sol=sp.solve([u-G3*(r-c),x-G1*(-u+y),y-G2*(u-x),c-x-y],[u,x,y,c])
    P=G2-G1+2*G1*G2
    equal('A3-68 coupled node elimination',sol[c]/r,G3*P/(1+G1*G2+G3*P))
    G=(s*s+2*s+sp.Rational(221,100))*(s+10)/((s*s+2*s+2)*(s+2)*(s+sp.Rational(221,20)))
    response=t/2-sp.Rational(647,2210)+sp.Rational(221,905)*sp.exp(-2*t)+21*sp.exp(-t)*(925*sp.cos(t)+904*sp.sin(t))/408010+sp.Rational(1554000,1632080801)*sp.exp(-sp.Rational(221,20)*t)
    equal('A3-52 ramp transform',sp.laplace_transform(response,t,s,noconds=True),G/s**2)
    equal('A3-15 comparator acceleration error',sp.limit((s+10)/(s**3+10*s*s+27*s+10),s,0),1)
    loop=(s+2)*(s+6)/(s*(s+3)*(s+4))
    equal('Errata A3-41 actual ramp error limit',sp.limit(2/(s*(1+loop)),s,0),2)
    kval=sp.symbols('K',positive=True)
    equal('Errata A3-64 parameter equation',sp.solve(sp.Eq(4/(1+kval),sp.Rational(2,5)),kval)[0],9)
    # Full responses retain every numerator zero, rather than importing textbook estimates.
    results={}
    systems={
        'A3-42-base':([2],[1,2,2],.05,4.3213918,2.071714),
        'A3-42-zero':([10,2],[1,2,2],.05,261.361,5.1460),
        'A3-42-pole':([2],[1,7,12,10],.05,4.1018167,2.3047),
        'A3-52':([1,12,22.21,22.1],np.polymul(np.polymul([1,2,2],[1,2]),[1,11.05]),.02,.231326,2.3859866),
        'A3-65':([4],[1,1.56,4],.05,26.432,3.843747),
        'A3-68':([2],[1,1,3],.05,None,6.013189),
        'A3-70':([8,32],[1,9,100],.05,104.224,.696281),
        'A3-97':([10],[1,7,12,10],.02,4.1018167,4.4202773),
        'A3-100':([12],[1,7,24],.05,4.0447975,.604505),
    }
    for label,(num,den,band,mp,ts) in systems.items():
        m=metrics(num,den,band);results[label]=m
        if mp is not None:close(label+' overshoot percent',m['overshoot_percent'],mp,.001)
        close(label+' settling time',m['settling_time'],ts,.0001)
    def pd_constraints(v):
        kc,td=np.exp(v);m=metrics([kc*td,kc],[1,kc*td,kc-.8],.05)
        return [m['overshoot_percent']/100-math.exp(-1),m['settling_time']-.8]
    fit=root(pd_constraints,np.log([81,.0865]));assert fit.success
    kc,td=np.exp(fit.x);close('A3-74 Kc',kc,81.00266775);close('A3-74 T',td,.08652843324)
    results['A3-74']=metrics([kc*td,kc],[1,kc*td,kc-.8],.05)
    kval=brentq(lambda k:metrics([2,24],[3,4+k,12],.02)['overshoot_percent']-9.5,3,3.5)
    close('A3-77 full model K',kval,3.226313418)
    results['A3-77 T0']=metrics([2,24],[3,4+kval,12],.02)
    results['A3-77 T1']=metrics([2,24],np.polymul([1,1],[3,4+kval,12]),.02)
    close('A3-77 T1 overshoot',results['A3-77 T1']['overshoot_percent'],0)
    alpha=-math.log(.44)/6.49;b=math.pi/6.49;k=3*(alpha*alpha+b*b)
    results['A3-102']=metrics([k],[1,2*alpha,k/3],.02)
    close('A3-102 settling time',results['A3-102']['settling_time'],28.17837)
    QA.mkdir(parents=True,exist_ok=True)
    (QA/'independent-math-checks.json').write_text(json.dumps({'checks':checks,'fullResponses':results,'pdDesign':{'Kc':kc,'T':td},'referenceFilterK':kval},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(checks)} independent symbolic/numeric assertions passed; {len(results)} full response models checked.')

if __name__=='__main__':main()
