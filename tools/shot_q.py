import asyncio,sys
from playwright.async_api import async_playwright
async def main(base,qid,out,full='1'):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':1400,'height':1000})
        await pg.goto(f'{base}?list=complete&question={qid}',wait_until='networkidle')
        await pg.click('button[aria-label="答案"]'); await pg.wait_for_timeout(800)
        await pg.screenshot(path=out,full_page=full=='1'); await b.close()
asyncio.run(main(*sys.argv[1:]))
