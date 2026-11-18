"""Typeset book fractions vertically without changing the algebra or identifiers."""
import json,re
from pathlib import Path
from merge_qd1000_next import DECISIONS,pid
from build_reviewed_bank import source_id

ROOT=Path(__file__).resolve().parents[1]
FORMULA=re.compile(r'\$\$([\s\S]+?)\$\$|\$([^$]+?)\$')
BREAK=re.compile(r'\\(?:quad|qquad|approx|sim|leq?|geq?|neq?|to|in|times|cdot|Rightarrow|Longrightarrow|equiv|begin|end)(?![A-Za-z])|\\[,;! ]|\\\\')
OP=set('+-=<>;,&:/')
PAIRS={')':'(',']':'[','}':'{'}

def bounds(text,slash,direction):
    stack=[];i=slash+direction
    stops={m.start():m.end() for m in BREAK.finditer(text)}
    while 0<=i<len(text):
        c=text[i]
        if direction<0:
            if c in PAIRS:stack.append(PAIRS[c])
            elif c in '([{':
                if not stack:break
                assert stack.pop()==c,(text,i)
        else:
            if c in '([{':stack.append(c)
            elif c in PAIRS:
                if not stack:break
                assert stack.pop()==PAIRS[c],(text,i)
        if not stack:
            if c in OP:break
            if direction>0 and i in stops and i>slash+1:break
            if direction<0 and any(i==end-1 for end in stops.values()):break
        i+=direction
    return i+1 if direction<0 else i

def unwrap(value):
    value=value.strip()
    if len(value)>1 and value[0] in '([' and value[-1] in ')]':
        level=0
        for i,c in enumerate(value):
            if c==value[0]:level+=1
            elif c==value[-1]:level-=1
            if level==0 and i<len(value)-1:return value
        return value[1:-1]
    return value

def fraction_tex(text):
    # Work from the most deeply nested slash outwards.
    while '/' in text:
        level=0;slashes=[]
        for i,c in enumerate(text):
            if c in '([{':level+=1
            elif c in ')]}':level-=1
            elif c=='/':slashes.append((level,-i,i))
        if not slashes:break
        pos=max(slashes)[2];a=bounds(text,pos,-1);b=bounds(text,pos,1)
        numerator=text[a:pos].strip();denominator=text[pos+1:b].strip()
        assert numerator and denominator,(text,pos,a,b)
        text=text[:a]+r'\frac{'+unwrap(numerator)+'}{'+unwrap(denominator)+'}'+text[b:]
    return text

def polish(text):
    # Correct two non-raw Python literals detected by the full-bank KaTeX check.
    text=text.replace('\x07pprox',r'\approx').replace('\x07rccos',r'\arccos')
    assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',text)
    def replace(m):
        delimiter='$$' if m.group(1) is not None else '$'
        return delimiter+fraction_tex(m.group(1) or m.group(2))+delimiter
    return FORMULA.sub(replace,text)

def main():
    changed=0
    paths=list((ROOT/'data-src/practice').glob('qd1000-*.json'))
    # Included retained cards with new subquestions must follow the same typography.
    paths += [ROOT/'data-src/reviewed'/name for name in ['reviewed-211-bupt.json','reviewed-211-hfut.json','reviewed-211-ncepu.json','reviewed-scu.json']]
    for path in paths:
        rows=json.loads(path.read_text('utf-8-sig'))
        retained={target for _,_,_,target,mode,_ in DECISIONS if mode!='reuse'}
        for q in rows:
            if path.name=='qd1000-a-001-100.json' and pid(q['chapter'],q['kind'],q['number']) not in retained:continue
            if 'reviewed' in path.parts and source_id(q) not in retained:continue
            for key in ('stem','answer','explanation'):
                if key not in q:continue
                new=polish(q[key])
                changed+=new!=q[key];q[key]=new
            if path.name=='qd1000-a-time-analysis.json' and q['number']==81:
                q['answer']=r'''令归一时间 $u=\frac tT$。

无阻尼 $\zeta=0$：
$$c=1-\cos u.$$

欠阻尼 $0<\zeta<1$，记 $\beta=\sqrt{1-\zeta^2}$、$\varphi=\arccos\zeta$：
$$c=1-\frac{e^{-\zeta u}}\beta\sin(\beta u+\varphi).$$

临界阻尼 $\zeta=1$：
$$c=1-(1+u)e^{-u}.$$

过阻尼 $\zeta>1$，记 $v=\sqrt{\zeta^2-1}$：
$$\begin{aligned}c&=1-e^{-\zeta u}A(u),\\A(u)&=\cosh(vu)+\frac\zeta v\sinh(vu).\end{aligned}$$'''
            if path.name=='qd1000-a-time-analysis.json' and q['number']==102:
                q['answer']=q['answer'].replace(r'$h=\frac{1}{3},a=',r'$h=\frac{1}{3}$，$a=').replace(r'0.252999,K=',r'0.252999$，$K=')
            if path.name=='qd1000-a-time-analysis.json' and q['number']==42:
                q['answer']=r'''各完整模型按各自终值计算精确指标：

**原系统。** 峰值时间3.1416秒，相对超调4.321%，5%调节时间2.0717秒。

**增加零点。** 峰值时间0.8961秒，相对超调261.361%，5%调节时间5.1460秒。

**增加极点。** 峰值时间3.3866秒，相对超调4.102%，5%调节时间2.3047秒。

（3）开环 $G_{new}=\frac{8}{s(s+4)}$。原系统调节时间的常用工程估算另为3秒。'''
        path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Fields typeset:',changed)

if __name__=='__main__':main()
