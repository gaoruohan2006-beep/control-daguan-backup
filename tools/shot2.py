import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=await b.new_page(viewport={'width':1440,'height':900})
    await pg.goto('http://localhost:8765/?list=complete&question=202304',wait_until='networkidle')
    await pg.get_by_role('button',name='答案',exact=True).click(); await pg.get_by_role('button',name='解析',exact=True).click(); await pg.wait_for_timeout(1500)
    await pg.screenshot(path='shots/answer.png')
    await pg.locator('.orig').scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
    await pg.screenshot(path='shots/answer-original.png')
    await b.close()
asyncio.run(main())
