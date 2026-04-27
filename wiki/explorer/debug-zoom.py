import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        await page.goto("http://localhost:8081/wiki/explorer/index.html?preset=power_system", wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        
        await page.evaluate("""() => {
            document.querySelectorAll('.pane.left, .pane.center, .splitter').forEach(el => el.style.display = "none");
            const right = document.querySelector('.pane.right');
            if (right) {
                right.style.position = "fixed"; right.style.top = "39px"; right.style.left = "0";
                right.style.width = "100vw"; right.style.height = "calc(100vh - 39px)"; right.style.zIndex = "9999";
            }
            const lp = document.getElementById("layer-panel"); if (lp) lp.style.display = "none";
            const pb = document.getElementById("preset-bar"); if (pb) pb.style.display = "none";
            if (window._explorer && window._explorer.map) window._explorer.map.invalidateSize();
        }""")
        await page.wait_for_timeout(1000)
        
        await page.evaluate("""() => { window._explorer.map.setView([28.2, 84.0], 8); }""")
        await page.wait_for_timeout(4000)
        
        meta = await page.evaluate("""() => {
            const ex = window._explorer;
            return {
                activeLayers: ex.lm.activeKeys(),
                badgeCount: document.querySelectorAll(".np-marker-badge").length,
                zoom: ex.map.getZoom()
            };
        }""")
        print(meta)
        await browser.close()

asyncio.run(test())
