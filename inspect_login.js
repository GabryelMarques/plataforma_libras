const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8000/login/', { waitUntil: 'domcontentloaded' });
  console.log('url', page.url());
  console.log('title', await page.title());
  console.log('count', await page.locator('input[name="email"]').count());
  console.log(await page.content());
  await browser.close();
})();
