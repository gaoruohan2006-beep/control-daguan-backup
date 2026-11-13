"""Exercise the published question bank with a real Chromium browser."""
import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
CHROME = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")


async def verify():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=CHROME)
        page = await browser.new_page(viewport={"width": 1380, "height": 950})
        page.set_default_timeout(8000)
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        await page.goto(BASE)
        await page.wait_for_selector(".card")
        library = await page.evaluate("fetch('data/library.json').then(r => r.json())")
        questions = library["questions"]
        ids = {q["id"] for q in questions}
        assert questions and len(ids) == len(questions)
        assert all(q["sourceType"] == "reviewed" for q in questions)
        assert [entry["id"] for entry in library["lists"]] == ["complete", "by-school"]
        assert all(set(entry["questionIds"]) == ids for entry in library["lists"])
        assert await page.locator('.node[data-path="历年真题"]').count() == 0
        await page.locator("#listBtn").click()
        await page.locator('[data-list="by-school"]').click()
        assert len(await page.locator("#tree .node.top").all()) == len({q["school"] for q in questions})
        await page.locator("#search").fill(questions[0]["school"])
        await page.wait_for_function("(school) => document.querySelectorAll('#tree .node.top').length === 1 && document.querySelector('.card .src').textContent.includes(school)", arg=questions[0]["school"])
        await page.locator("#search").fill("")
        await page.locator("#listBtn").click()
        await page.locator('[data-list="complete"]').click()

        for q in questions:
            identifier = q["id"]
            await page.goto(f"{BASE}?question={identifier}", wait_until="domcontentloaded")
            card = page.locator(f'.card[data-id="{identifier}"]')
            await card.wait_for()
            await card.get_by_role("button", name="答案", exact=True).click()
            await card.get_by_role("button", name="解析", exact=True).click()
            await card.locator('.box[data-kind="exp"] .body > :first-child').wait_for()
            assert await card.locator(".katex-error").count() == 0, q["source"]
            bad = await card.evaluate("""async card => {
                const images = [...card.querySelectorAll('img')];
                await Promise.all(images.map(img => { img.loading = 'eager'; return img.decode().catch(() => {}); }));
                return images.filter(img => !img.naturalWidth || !img.getAttribute('src').endsWith('.svg'))
                    .map(img => img.getAttribute('src'));
            }""")
            assert not bad, (q["source"], bad)
            body = await card.inner_text()
            assert not any(ad in body for ad in ("公众号", "二维码", "真橙", "考研群", "讲义", "题本 PDF", "参考答案 PDF", "答案本 PDF")), q["source"]

        q = next(q for q in questions if q["hasFigure"])
        await page.goto(f"{BASE}?question={q['id']}")
        await page.locator(".stem img").first.click()
        assert await page.locator("#lightbox").is_visible()
        await page.keyboard.press("Escape")
        await page.locator('button[data-act="fav"]').click()
        await page.locator('button[data-mark="shaky"]').click()
        await page.locator('button[data-act="note"]').click()
        await page.locator('button[data-act="nedit"]').click()
        await page.locator(".note-input").fill("审核测试")
        await page.wait_for_function(f"CDGStore.get('rec').then(r => r?.notes?.['{q['id']}']?.text === '审核测试')")
        await page.locator('#tabs button[data-tab="fav"]').click()
        assert await page.locator(f'.card[data-id="{q["id"]}"]').count() == 1

        mobile = await browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await mobile.goto(f"{BASE}?question={q['id']}")
        await mobile.locator(".card").wait_for()
        await mobile.locator("#tocBtn").click()
        assert await mobile.locator("#sidebar").is_visible()
        await mobile.locator("#tree .node.top .nm").first.click()
        assert not await mobile.locator("#app").evaluate("node => node.classList.contains('drawer-open')")
        if target := os.environ.get("BANK_SCREENSHOT"):
            await page.goto(f"{BASE}?question={q['id']}")
            await page.locator(".stem img").first.evaluate("img => img.decode()")
            await page.screenshot(path=Path(target))
        assert not errors, errors
        print(f"Verified {len(questions)} question cards, LaTeX rendering, SVGs, topics, schools, notes, favorites and mobile navigation.")


if __name__ == "__main__":
    asyncio.run(verify())
