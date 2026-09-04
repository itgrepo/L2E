const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();
  
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  page.on('response', response => console.log('RESPONSE:', response.url(), response.status()));

  const baseUrl = 'http://134.185.172.127:3003';
  
  console.log('Testing Catalog View...');
  await page.goto(`${baseUrl}/catalog`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000); 
  
  await browser.close();
})();
