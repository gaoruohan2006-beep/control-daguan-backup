"""Check every second-batch source and upgraded card at six reading sizes."""
import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright
from build_reviewed_bank import question_id,PRACTICE_TITLE

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa/2026-11-18-next200'
BASE='http://127.0.0.1:8765/'

async def main():
    sources=[]
    for p in sorted((ROOT/'data-src/practice').glob('qd1000-*.json')):
        if p.name!='qd1000-a-001-100.json':sources+=json.loads(p.read_text('utf-8'))
    library=json.loads((ROOT/'public/data/library.json').read_text('utf-8'))
    aliases=library['questionAliases'];by_id={q['id']:q for q in library['questions']}
    identifiers={aliases.get(str(i),i) for q in sources for i in [question_id([PRACTICE_TITLE,q['volume'],q['chapter'],q['kind'],q['number']])]}
    data=[]
    for i in sorted(identifiers):
        q=by_id[i];detail=json.loads((ROOT/f'public/data/questions/{i}.json').read_text('utf-8'))
        data.append({**q,**detail})
    issues=[];sizes=[];scrollable=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('CHROME_PATH','C:/Program Files/Google/Chrome/Application/chrome.exe'))
        page=await browser.new_page(viewport={'width':1380,'height':1000})
        async def instrument(route):
            response=await route.fetch()
            source=await response.text()
            source=source.rsplit('})();',1)[0]+'window.__layoutQA={md,layoutCardMath};\n})();'
            await route.fulfill(response=response,body=source)
        await page.route('**/app.js*',instrument)
        await page.goto(BASE);await page.locator('.card').wait_for()
        for width,scale in [(1380,1),(1380,1.3),(1024,1),(1024,1.3),(390,1),(390,1.3)]:
            print('Checking',width,scale,flush=True)
            await page.set_viewport_size({'width':width,'height':1000})
            for off in range(0,len(data),12):
                batch=data[off:off+12]
                found=await page.evaluate('''async ({batch,scale})=>{
                    document.documentElement.style.setProperty('--fs',scale);
                    const cards=document.querySelector('#cards');
                    const {md,layoutCardMath}=window.__layoutQA;
                    cards.innerHTML=batch.map(q=>`<article class="card" data-id="${q.id}"><div class="stem">${md(q.stem)}</div><section class="box" data-kind="answer"><div class="body">${md(q.answer)}</div></section><section class="box" data-kind="exp"><div class="body">${md(q.explanation)}</div></section></article>`).join('');
                    await Promise.all([...cards.querySelectorAll('img')].map(i=>{i.loading='eager';return Promise.race([i.decode(),new Promise((_,reject)=>setTimeout(()=>reject(new Error('image timeout '+i.src)),10000))]);}));
                    await layoutCardMath(cards);
                    const issues=[];
                    for(const card of cards.children){
                        for(const e of card.querySelectorAll('.katex-display,.math-wide')){
                            if(e.scrollWidth>e.clientWidth+2)issues.push({id:card.dataset.id,type:'math',tex:e.querySelector('annotation')?.textContent,width:e.scrollWidth,available:e.clientWidth});
                        }
                        for(const e of card.querySelectorAll('img'))if(!e.naturalWidth)issues.push({id:card.dataset.id,type:'image'});
                    }
                    if(document.documentElement.scrollWidth>innerWidth+1)issues.push({type:'page',width:document.documentElement.scrollWidth});
                    return issues;
                }''',{'batch':batch,'scale':scale})
                for x in found:
                    item={**x,'viewport':width,'scale':scale}
                    if width<600 and x['type']=='math':scrollable.append(item)
                    else:issues.append(item)
            sizes.append({'width':width,'fontScale':scale,'cards':len(data)})
        # Representative actual interactive cards, with every answer and solution expanded.
        examples=[(3,'分析题',42),(3,'分析题',52),(3,'分析题',74),(3,'分析题',81),(2,'分析题',68),(2,'分析题',52)]
        for ch,kind,n in examples:
            i=question_id([PRACTICE_TITLE,'A',ch,kind,n])
            await page.set_viewport_size({'width':1380,'height':1000})
            await page.goto(f'{BASE}?question={i}');await page.locator('.card').wait_for()
            await page.get_by_role('button',name='答案',exact=True).click()
            await page.get_by_role('button',name='解析',exact=True).click()
            await page.locator('.box[data-kind="exp"] .body > :first-child').wait_for()
            await page.evaluate('document.fonts.ready.then(()=>true)')
            await page.screenshot(path=QA/f'desktop-A{ch}-{n}.png',full_page=True)
            figure=page.locator('.box[data-kind="exp"] .fig img').last
            if await figure.count():
                await figure.scroll_into_view_if_needed()
                await figure.evaluate('img=>img.decode()')
                await page.screenshot(path=QA/f'figure-A{ch}-{n}.png')
        await browser.close()
    report={'sourceEntries':len(sources),'retainedCardsExercised':len(data),'sizes':sizes,'issues':issues,'mobileScrollableFormulas':scrollable,
            'mobilePolicy':'Long formulas retain normal reading size and scroll inside their formula container; page width and image loading are enforced.'}
    (QA/'layout-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cards':len(data),'sizes':len(sizes),'issues':len(issues)}))
    if issues:print(json.dumps(issues[:30],ensure_ascii=False,indent=2))
    assert not issues,'See layout-checks.json'

if __name__=='__main__':asyncio.run(main())
