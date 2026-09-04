const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const baseUrl = 'http://134.185.172.127:3003';
  await page.goto(baseUrl + '/login');
  
  const mockUser = {
    user_id: 1,
    username: 'admin',
    role_id: 3,
    previlage_id: 3,
    isAdmin: 'true',
    firstname: 'Admin',
    apikey: 'mock_key'
  };
  await page.evaluate((user) => {
    localStorage.setItem('user', JSON.stringify(user));
  }, mockUser);

  await page.goto(baseUrl + '/catalog');
  await page.waitForTimeout(2000);
  
  // Type in search box
  await page.fill('input[placeholder*="ค้นหา"]', 'สถิติวิเคราะห์');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/Users/natthawutjantakul/.gemini/antigravity/brain/922529c0-c12e-4424-b378-50d7bfb37fa2/scratch/test_catalog_search.png', fullPage: true });
  await browser.close();
})();
