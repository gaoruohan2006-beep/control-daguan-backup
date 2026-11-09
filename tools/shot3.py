import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=await b.new_page(viewport={'width':1440,'height':900})
    await pg.goto('http://localhost:8765/',wait_until='networkidle'); await pg.wait_for_timeout(600); await pg.screenshot(path='shots/01-home-list.png')
    await pg.goto('http://localhost:8765/?list=complete&question=202306',wait_until='networkidle'); await pg.wait_for_timeout(600); await pg.screenshot(path='shots/02-question-formula-figure.png')
    await pg.goto('http://localhost:8765/?list=complete&question=202407',wait_until='networkidle')
    await pg.get_by_role('button',name='答案',exact=True).click(); await pg.get_by_role('button',name='解析',exact=True).click(); await pg.wait_for_selector('.orig img')
    await pg.locator('.box').first.evaluate('e=>e.scrollIntoView({block:"start"})'); await pg.wait_for_timeout(800); await pg.screenshot(path='shots/03-answer-shown.png')
    await pg.locator('.orig').evaluate('e=>e.scrollIntoView({block:"start"})'); await pg.wait_for_timeout(800); await pg.screenshot(path='shots/04-original-solution.png')
    await pg.goto('http://localhost:8765/?list=complete&question=202404',wait_until='networkidle'); await pg.locator('#gearBtn').click(); await pg.wait_for_timeout(300); await pg.screenshot(path='shots/05-settings.png')
    await pg.keyboard.press('Escape'); await pg.locator('#listBtn').click(); await pg.wait_for_timeout(300); await pg.screenshot(path='shots/06-list-select.png')
    m=await b.new_page(viewport={'width':390,'height':844}); await m.goto('http://localhost:8765/?list=complete&question=202501',wait_until='networkidle'); await m.wait_for_timeout(500); await m.screenshot(path='shots/07-mobile.png')
    await b.close()
asyncio.run(main())
