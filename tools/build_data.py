# 生成 public/data/library.json 与 public/data/questions/<id>.json
import json, os, re, sys, importlib.util
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'public','data'); os.makedirs(os.path.join(OUT,'questions'),exist_ok=True)
CN='一二三四五六七八九十'
# 数据源：一个 Python 模块 + 每题图片映射（crops.json）。新年份追加到这里即可。
SOURCES=[dict(module='questions_2023_2025.py', crops='crops.json',
              qpages={2023:'47–50',2024:'51–54',2025:'55–57'}, apages={2023:'170–180',2024:'181–191',2025:'192–202'})]
questions=[]; details={}
for src in SOURCES:
  spec=importlib.util.spec_from_file_location('m',os.path.join(ROOT,'tools',src['module'])); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  crops=json.load(open(os.path.join(ROOT,'tools',src['crops'])))
  for d in m.Q:
    key=f"{d['year']}-{d['no']}"; qid=d['year']*100+d['no']
    figs=crops['figs'].get(key,[])
    stem=d['stem']
    used=set()
    def rep(mo):
      i=int(mo.group(1)); used.add(i)
      from PIL import Image
      w=Image.open(os.path.join(ROOT,'public',figs[i-1])).width
      return f'![图{i}|{round(w*0.55)}]({figs[i-1]})'
    stem=re.sub(r'\[\[fig:(\d+)\]\]',rep,stem)
    assert len(used)==len(figs), (key, used, figs)
    cats=[f"历年真题 / {d['year']}"]+d['cats']
    plain=re.sub(r'\$+[^$]*\$+',' ',stem)
    source=f"{d['year']}重大844 · 第{CN[d['no']-1]}题"+(f"（{d['score']}分）" if d['score'] else '')
    questions.append(dict(id=qid,year=d['year'],number=d['no'],score=d['score'],source=source,
        categories=cats,tags=[c.split(' / ')[0] for c in d['cats']],hasFigure=bool(figs),
        stem=stem,pdfPage=src['qpages'][d['year']],
        search=' '.join([str(qid),source,*cats,stem])))
    details[qid]=dict(answer=d['answer'],explanation=d['explanation'],
        originalImages=[dict(src=a,w=round(__import__('PIL.Image',fromlist=['x']).open(os.path.join(ROOT,'public',a)).width*0.6)) for a in crops['ans'].get(key,[])],answerPdfPages=src['apages'][d['year']])
# JSON 数据源：data-src/<年份>/questions.json（格式见 incoming/SPEC.md）
import glob, shutil
from PIL import Image
for qf in sorted(glob.glob(os.path.join(ROOT,'data-src','*','questions.json'))):
  src=json.load(open(qf)); y=src['year']; base=os.path.dirname(qf)
  os.makedirs(os.path.join(ROOT,'public','img'),exist_ok=True)
  def pub(rel):
    fn=os.path.basename(rel); shutil.copy(os.path.join(base,rel),os.path.join(ROOT,'public','img',fn)); return 'img/'+fn
  for d in src['questions']:
    qid=y*100+d['no']; assert qid not in details,(qid,'duplicate')
    figs=[pub(f) for f in d['figures']]
    stem=d['stem']; used=set()
    def rep(mo):
      i=int(mo.group(1)); used.add(i); w=Image.open(os.path.join(ROOT,'public',figs[i-1])).width
      return f'![图{i}|{round(w*0.55)}]({figs[i-1]})'
    stem=re.sub(r'\[\[fig:(\d+)\]\]',rep,stem)
    assert len(used)==len(figs),(qid,used,figs)
    # 统一不同录入者的分类命名（不改源数据）
    ALIAS={'离散系统 / 输出响应':'离散系统 / 时间响应','建模 / 机电系统传递函数':'建模 / 机电系统 / 传递函数','建模 / 机电系统 / 直流电动机':'建模 / 机电系统 / 传递函数'}
    d['cats']=list(dict.fromkeys(ALIAS.get(c,c) for c in d['cats']))
    cats=[f"历年真题 / {y}"]+d['cats']
    source=f"{y}重大844 · 第{CN[d['no']-1]}题"+(f"（{d['score']}分）" if d.get('score') else '')
    questions.append(dict(id=qid,year=y,number=d['no'],score=d.get('score'),source=source,categories=cats,
        tags=[c.split(' / ')[0] for c in d['cats']],hasFigure=bool(figs),stem=stem,pdfPage=src.get('questionPages',''),
        contributor=src.get('contributor',''),search=' '.join([str(qid),source,*cats,stem])))
    ans=[pub(a) for a in d['answerImages']]
    details[qid]=dict(answer=d.get('answer',''),explanation=d.get('explanation',''),notes=d.get('notes',''),
        originalImages=[dict(src=a,w=round(Image.open(os.path.join(ROOT,'public',a)).width*0.6)) for a in ans],
        answerPdfPages=src.get('answerPages',''))
questions.sort(key=lambda x:(-x['year'],x['number']))
years=sorted({q['year'] for q in questions},reverse=True)
TOPIC_ORDER=['建模','时域分析','根轨迹','频域分析','校正','离散系统','非线性系统','状态空间']
def lst(id,name,qs,catfn):
  return dict(id=id,name=name,questionIds=[q['id'] for q in qs],categoryByQuestion={str(q['id']):catfn(q) for q in qs})
def topic_cats(q): return [c for c in q['categories'] if not c.startswith('历年真题')]
def year_cat(q): return [f"历年真题 / {q['year']}"]
lists=[lst('complete','完整题库',questions,lambda q:topic_cats(q)+year_cat(q)),
       lst('exam-by-year','真题按年',questions,year_cat),
       lst('by-topic','专题分类',questions,topic_cats)]
for y in years: lists.append(lst(f'exam-{y}',f'{y} 真题',[q for q in questions if q['year']==y],lambda q:topic_cats(q)))
for t in TOPIC_ORDER:
  qs=[q for q in questions if t in q['tags']]
  if qs: lists.append(lst(f'topic-{t}',f'专题·{t}',qs,lambda q:[c for c in topic_cats(q)]))
lib=dict(subject='自动控制原理（重庆大学 844）',source=f'重庆大学 {min(q["year"] for q in questions)}–{max(q["year"] for q in questions)} 初试真题',
         topicOrder=['历年真题']+TOPIC_ORDER,years=years,lists=lists,questions=questions)
json.dump(lib,open(os.path.join(OUT,'library.json'),'w'),ensure_ascii=False)
for k,v in details.items(): json.dump(v,open(os.path.join(OUT,'questions',f'{k}.json'),'w'),ensure_ascii=False)
print(len(questions),'questions;',{y:sum(1 for q in questions if q['year']==y) for y in years},
      'with figures',sum(q['hasFigure'] for q in questions),'with answers',sum(1 for v in details.values() if v['answer']),
      'answer images',sum(len(v['originalImages']) for v in details.values()))
