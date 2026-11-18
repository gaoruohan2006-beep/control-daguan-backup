"""Inspect rational step responses using residues and bracketed scalar roots."""
import numpy as np
from scipy.signal import residue
from scipy.optimize import brentq

def metrics(num, den, delta=.05):
    poles=np.roots(den)
    assert all(p.real < -1e-8 for p in poles)
    final=float(num[-1]/den[-1])
    rr,pp,kk=residue(num,np.polymul(den,[1,0]))
    assert len(kk)==0
    assert min(abs(a-b) for i,a in enumerate(pp) for b in pp[i+1:])>1e-7
    def val(t,order=0):
        arr=np.asarray(t)
        return np.real(sum(r*p**order*np.exp(p*arr) for r,p in zip(rr,pp)))
    end=32/min(-p.real for p in poles)
    samples=max(20000,int(end*max(1,max(abs(p.imag) for p in poles))*60))
    ts=np.linspace(0,end,samples)
    def roots(fun):
        yy=fun(ts);ii=np.where(yy[:-1]*yy[1:]<0)[0]
        return [brentq(fun,ts[i],ts[i+1],xtol=1e-12) for i in ii]
    stationary=roots(lambda t:val(t,1))
    values=[(float(val(x)),x) for x in [0,*stationary]]
    peak=max(values+[(final,float('inf'))])
    crossings=roots(lambda t:abs(val(t)/final-1)-delta)
    first95=roots(lambda t:val(t)/final-.95)
    ten=roots(lambda t:val(t)/final-.1);ninety=roots(lambda t:val(t)/final-.9)
    return dict(final=final,overshoot_percent=max(0,(peak[0]/final-1)*100),
                peak_time=None if not np.isfinite(peak[1]) else peak[1],
                settling_time=max(crossings) if crossings else 0,
                first_95_time=first95[0] if first95 else None,
                rise_10_90=ninety[0]-ten[0] if ten and ninety else None,
                step_residues=[dict(residue=[float(r.real),float(r.imag)],pole=[float(p.real),float(p.imag)]) for r,p in zip(rr,pp)])

if __name__=='__main__':
    import json
    results={
      'A3-analysis30':metrics([2],[1,6,4]),
      'A3-analysis37-open':metrics([10000],[1,60,600,5000]),
      'A3-analysis39':metrics([35],[1,13,47,35]),
      'A3-analysis42-base':metrics([2],[1,2,2]),
      'A3-analysis42-zero':metrics([10,2],[1,2,2]),
      'A3-analysis42-pole':metrics([2],[1,7,12,10]),
      'A3-analysis52':metrics([1,12,22.21,22.1],np.polymul(np.polymul([1,2,2],[1,2]),[1,11.05]),.02),
    }
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/'qa/2026-11-18-next200'
    out.mkdir(parents=True,exist_ok=True)
    (out/'response_metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for key,value in results.items():print(key,{k:v for k,v in value.items() if k!='step_residues'})
