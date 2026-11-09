import json,re,subprocess,os
from PIL import Image, ImageDraw
import numpy as np
DPI=200; S=DPI/72; D=1654/720  # display->px
OUT='/workspace/control-daguan/public/img'; os.makedirs(OUT,exist_ok=True)
def page(p): return Image.open(f'pages/p-{p:03d}.png').convert('RGB')
def trim(im,pad=12,thr=235):
  a=np.asarray(im.convert('L'))<thr
  ys=np.where(a.any(1))[0]; xs=np.where(a.any(0))[0]
  if len(ys)==0: return None
  y0,y1,x0,x1=max(0,ys[0]-pad),min(im.height,ys[-1]+pad),max(0,xs[0]-pad),min(im.width,xs[-1]+pad)
  return im.crop((x0,y0,x1,y1))
def save(im,name):
  im.save(f'{OUT}/{name}.png',optimize=True); return f'img/{name}.png'
# question figures: display coords
QF={
 '2023-1':[(47,(250,290,440,428))],
 '2023-2':[(47,(170,640,540,815))],
 '2023-5':[(48,(225,655,500,735))],
 '2023-6':[(49,(200,120,530,200)),(49,(220,235,510,392))],
 '2024-1':[(51,(100,328,630,532)),(51,(220,540,470,742))],
 '2024-2':[(52,(240,120,480,262)),(52,(240,275,480,472))],
 '2024-4':[(53,(150,140,570,262))],
 '2024-5':[(53,(195,520,520,802))],
 '2024-6':[(54,(150,118,560,238))],
 '2024-8':[(54,(180,650,545,760))],
 '2025-1':[(55,(255,400,470,552))],
 '2025-2':[(55,(195,655,530,748))],
 '2025-5':[(56,(195,795,535,862))],
 '2025-6':[(57,(205,515,520,588))],
}
figs={}
for k,lst in QF.items():
  figs[k]=[]
  for i,(p,b) in enumerate(lst):
    im=trim(page(p).crop(tuple(int(v*D) for v in b)))
    figs[k].append(save(im,f'q{k}-{i+1}'))
# answer segments
B={2023:[(170,127),(170,722),(172,82),(174,212),(175,661),(178,82),(179,305),(180,163),(181,0)],
   2024:[(181,120),(181,661),(183,82),(184,547),(186,82),(187,696),(189,151),(190,388),(192,0)],
   2025:[(192,131),(193,546),(195,359),(196,669),(198,253),(199,310),(200,554),(201,530),(203,0)]}
TOP,BOT=57,764
# word boxes for whiting out the 【万人教育解析】 label
bb=subprocess.run(['pdftotext','-bbox','-f','170','-l','202','book.pdf','-'],capture_output=True,text=True).stdout.split('<page ')[1:]
words={170+i:[(float(a),float(b),float(c),float(d),t) for a,b,c,d,t in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',pg)] for i,pg in enumerate(bb)}
def whiteout(im,p):
  dr=ImageDraw.Draw(im); ws=words[p]; on=False
  for x0,y0,x1,y1,t in ws:
    if '【' in t: on=True
    if on:
      # only white the bracket part of the word
      dr.rectangle([x0*S-2,y0*S-2,x1*S+2,y1*S+2],fill='white')
    if '】' in t: on=False
  return im
# Need words that merge label+content (e.g. "【万人教育解析】（1）"): handle by splitting proportional
def whiteout2(im,p):
  dr=ImageDraw.Draw(im)
  ws=words[p]; i=0
  while i<len(ws):
    x0,y0,x1,y1,t=ws[i]
    if '【' in t:
      # collect until 】
      j=i; seg=[]
      while j<len(ws):
        seg.append(ws[j])
        if '】' in ws[j][4]: break
        j+=1
      for (a,b,c,d,tt) in seg:
        n=len(tt); s=tt.find('【'); e=tt.find('】')
        s=0 if s<0 else s; e=n-1 if e<0 else e
        cw=(c-a)/max(n,1)
        dr.rectangle([(a+cw*s)*S-1,b*S-1,(a+cw*(e+1))*S+1,d*S+1],fill='white')
      i=j+1
    else: i+=1
  return im
ans={}
for y,bl in B.items():
  for q in range(8):
    (p0,y0),(p1,y1)=bl[q],bl[q+1]
    segs=[]
    for p in range(p0,p1+1):
      if p>202: break
      top=max(TOP,y0-3) if p==p0 else TOP
      bot=(y1-3) if p==p1 else BOT
      if p==p1 and y1==0: continue
      if bot-top<8: continue
      im=whiteout2(page(p),p).crop((int(60*S/ (S/ S)) if False else 0,int(top*S),1654,int(bot*S)))
      im=im.crop((150,0,1654-150,im.height))
      t=trim(im,pad=10)
      if t is None or t.height<30: continue
      segs.append(save(t,f'a{y}-{q+1}-{len(segs)+1}'))
    ans[f'{y}-{q+1}']=segs
json.dump({'figs':figs,'ans':ans},open('crops.json','w'),indent=1)
print({k:len(v) for k,v in ans.items()})
