const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();
  
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));

  const baseUrl = 'http://134.185.172.127:3003';
  
  // Go to login first to establish origin and set localstorage
  await page.goto(`${baseUrl}/login`);
  await page.evaluate(() => {
    localStorage.setItem('user', JSON.stringify({
      user_id: 1,
      username: 'admin',
      role_id: 3,
      previlage_id: 3,
      isAdmin: 'true',
      firstname: 'Admin',
      apikey: 'mock_key'
    }));
  });

  console.log('Testing Catalog View...');
  await page.goto(`${baseUrl}/catalog`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000); 
  
  const h1 = await page.$eval('h1', el => el.innerText).catch(() => 'no h1');
  console.log('H1:', h1);
  
  await browser.close();
})();
