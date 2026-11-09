import asyncio,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=await b.new_page(viewport={'width':1440,'height':900})
    errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto('http://localhost:8765/',wait_until='networkidle'); await pg.wait_for_timeout(800)
    await pg.screenshot(path='shots/home.png')
    await pg.goto('http://localhost:8765/?list=complete&question=202402',wait_until='networkidle'); await pg.wait_for_timeout(800)
    await pg.screenshot(path='shots/q-figure.png')
    await pg.get_by_role('button',name='答案',exact=True).click(); await pg.get_by_role('button',name='解析',exact=True).click(); await pg.wait_for_timeout(1200)
    await pg.screenshot(path='shots/answer.png',full_page=False)
    print('errors',errs)
    await b.close()
asyncio.run(main())
