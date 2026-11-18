"""Apply manually reviewed duplicate decisions; no similarity score deletes cards."""
import json
from pathlib import Path
from build_reviewed_bank import question_id, source_id, PRACTICE_TITLE

ROOT=Path(__file__).resolve().parents[1]
PRACTICE=ROOT/'data-src/practice'
QA=ROOT/'qa/2026-11-18-next200'

def pid(ch,kind,n):return question_id([PRACTICE_TITLE,'A',ch,kind,n])

# Each decision was checked against the complete conditions and requested outputs.
# Numerical changes (e.g. +1 vs +12 constants) are deliberately retained as distinct.
DECISIONS=[
 (2,'分析题',44,1001474573925,'reuse','same two-cart forces and both transfer functions'),
 (2,'分析题',47,671244741789,'reuse','same RLC network; retained card also has state model'),
 (2,'分析题',55,258182817708,'reuse','same RC/mechanical analogy; variable names exchanged'),
 (2,'分析题',59,178475581439,'reuse','same high-pass RC network and differential equation'),
 (3,'分析题',6,226586557319,'reuse','identical response and three questions; book school attribution differs'),
 (3,'分析题',9,334277758298,'reuse','same quartic parameter stability question'),
 (3,'分析题',10,995149599723,'reuse','same fourth-order gain and error constraints'),
 (3,'分析题',13,866246799262,'reuse','same 30-second level sensor and 0.2 cm/s ramp'),
 (3,'分析题',14,957422569642,'reuse','same three speed feedback design cases'),
 (3,'分析题',22,942475191835,'reuse','same integral controller and derivative feedback disturbance problem'),
 (3,'分析题',44,50167009334,'reuse','same fifth-degree polynomial and imaginary roots'),
 (3,'分析题',46,879330766515,'reuse','same model; retained card explicitly uses 3-coefficient settling estimate'),
 (3,'分析题',48,894973933039,'reuse','same cubic gain stability and ramp error'),
 (3,'分析题',59,542475020921,'reuse','same unstable-object PI loop and reference/disturbance inputs'),
 (3,'分析题',80,537506726399,'reuse','same 2 rad/s critical oscillation design'),
 (3,'分析题',90,829021614992,'reuse','same fourth-order transfer function after factor reordering'),
 (3,'分析题',92,159579944272,'reuse','same zeta and peak time; retained card includes both bands'),
 (3,'分析题',97,322505411825,'upgrade','same model; add complete-model transient question and answer'),
 (3,'分析题',101,817203494036,'reuse','same quartic with zero-pivot Routh table'),
 (3,'分析题',107,322891934382,'upgrade','same coefficient condition theorem; include ramp case'),
 (3,'分析题',110,499007699165,'reuse','same mass-spring-damper and 3 N final displacement'),
 (3,'选择题',23,34868443644,'reuse','same closed-loop function and false DC-gain option'),
 (3,'填空题',6,1024707168126,'reuse','same impulse response of unity feedback loop'),
 (3,'填空题',15,493761234925,'upgrade','same step response; add damping and natural frequency'),
 (3,'填空题',17,297843523329,'reuse','same 60-second thermometer response'),
 (3,'填空题',20,578176230489,'reuse','identical two-exponential impulse response'),
 (3,'填空题',22,460877991948,'reuse','same first-order response point (20,0.98)'),
 (3,'填空题',26,580777786413,'reuse','identical DC-preserving reduction'),
 (3,'简答题',2,1309217566,'reuse','same dominant pole definition and conditions'),
 (3,'选择题',15,pid(3,'选择题',12),'reuse','same dominant-pole distance and decay-rate question'),
 (3,'选择题',21,pid(3,'选择题',12),'reuse','same dominant-pole distance and decay-rate question'),
 (3,'填空题',31,pid(3,'选择题',12),'reuse','same dominant-pole distance and decay-rate question'),
 (2,'分析题',62,pid(2,'分析题',50),'upgrade','same two-RC topology; combine requested derivation'),
 (3,'分析题',98,pid(3,'分析题',15),'append','same loop and pole -5; add step response to retained problem'),
 (3,'分析题',99,pid(3,'分析题',53),'append','equivalent reference feedforward placement; preserve parameter conversion'),
 (3,'分析题',27,957422569642,'append','same parameter model and first case; add the sector constraint'),
 (3,'填空题',18,pid(3,'分析题',83),'append','same step response; add the frequency response task'),
    (4,'选择题',11,pid(4,'选择题',7),'reuse','same additional left-half-plane pole and root-locus trend'),
]

def main():
    files={p:json.loads(p.read_text('utf-8-sig')) for p in PRACTICE.glob('qd1000-*.json')}
    src={pid(q['chapter'],q['kind'],q['number']):(p,q) for p,rows in files.items() for q in rows}
    reviewed={p:json.loads(p.read_text('utf-8-sig')) for p in (ROOT/'data-src/reviewed').glob('*.json')}
    old={source_id(q):(p,q) for p,rows in reviewed.items() for q in rows}
    changed=set();log=[]
    for ch,kind,n,target,mode,reason in DECISIONS:
        identifier=pid(ch,kind,n);_,q=src[identifier]
        q['sameAs']=target
        if mode!='reuse':
            p,retained=(old|src)[target]
            if mode=='upgrade':
                for key in ('stem','answer','explanation'):retained[key]=q[key]
                changed.add(p)
            elif mode=='append':
                marker=f'**书册补充：第{ch}章{kind}{n}。**'
                if marker not in retained['stem']:
                    if n==98:
                        task='求同一参数下的零初值单位阶跃响应。'
                        ans=q['answer'].split('第二问',1)[-1]
                    elif n==99:
                        task=q['stem']
                        ans=q['answer']
                    elif n==27:
                        task=r'再求使复极点满足 $1\le|s|\le2$、与负实轴夹角介于 $30^\circ$ 与 $60^\circ$ 的 $K,a$ 范围。'
                        ans=r'$1\le K\le4$，$\sqrt K\le2+aK\le\sqrt{3K}$。'
                    elif kind=='填空题' and n==18:
                        task='再求该系统的闭环频率特性。';ans=q['answer']
                    retained['stem']+='\n\n'+marker+' '+task
                    retained['answer']+='\n\n'+marker+' '+ans
                    retained['explanation']+='\n\n'+marker+'\n\n'+q['explanation']
                    changed.add(p)
        log.append(dict(identity=['A',ch,kind,n],id=identifier,retainedId=target,action=mode,reason=reason))
    # Resolve aliases to their final live card, so old links never form chains.
    aliases={pid(q['chapter'],q['kind'],q['number']):q['sameAs'] for rows in files.values() for q in rows if q.get('sameAs')}
    for rows in files.values():
        for q in rows:
            if 'sameAs' in q:
                seen=set();target=q['sameAs']
                while target in aliases:
                    assert target not in seen;seen.add(target);target=aliases[target]
                q['sameAs']=target
    for p,rows in files.items():p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for p in changed:
        if p in reviewed:p.write_text(json.dumps(reviewed[p],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    QA.mkdir(parents=True,exist_ok=True)
    (QA/'dedup-decisions.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    current=[q for p,rows in files.items() if p.name!='qd1000-a-001-100.json' for q in rows]
    print('source entries',len(current),'merged',sum('sameAs' in q for q in current),'new cards',sum('sameAs' not in q for q in current))

if __name__=='__main__':main()
