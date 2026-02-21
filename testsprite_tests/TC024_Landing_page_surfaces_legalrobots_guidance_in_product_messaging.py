import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> Navigate to http://localhost:3000/incidents
        await page.goto("http://localhost:3000/incidents", wait_until="commit", timeout=10000)
        
        # -> Navigate to http://localhost:3000/ (home) and then check the landing page content for visible text containing 'robots.txt', 'permission', and 'crawl'.
        await page.goto("http://localhost:3000/", wait_until="commit", timeout=10000)
        
        # --> Assertions to verify final state
        frame = context.pages[-1]
        # Verify landing page contains guidance about crawling permissions and robots.txt behavior
        xpaths = [
            '/html/body/div/nav/div/a[1]',
            '/html/body/div/nav/div/a[2]',
            '/html/body/div/section[1]/div[3]/a[1]',
            '/html/body/div/section[1]/div[3]/svg',
            '/html/body/div/section[1]/div[3]/a[2]',
            '/html/body/div/section[2]/div[2]/div/div[1]/div[1]',
            '/html/body/div/section[2]/div[2]/div/div[2]/div[1]',
            '/html/body/div/section[2]/div[2]/div/div[3]/div[1]',
            '/html/body/div/section[3]/div/a',
        ]
        available_texts = {}
        for xp in xpaths:
            locator = frame.locator(f"xpath={xp}")
            count = await locator.count()
            if count:
                try:
                    text = await locator.inner_text()
                except Exception:
                    text = ''
            else:
                text = ''
            available_texts[xp] = text
        
        missing = []
        for term in ['robots.txt', 'permission', 'crawl']:
            found = any((t or '').lower().find(term.lower()) != -1 for t in available_texts.values())
            if not found:
                missing.append(term)
        
        if missing:
            raise AssertionError(f"Landing page missing expected guidance about crawling permissions/robots.txt: could not find text(s): {', '.join(missing)}. Available elements and their texts: {available_texts}")
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    