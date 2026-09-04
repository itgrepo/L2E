const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();
  
  const baseUrl = 'http://134.185.172.127:3003';
  const outDir = '/Users/natthawutjantakul/.gemini/antigravity/brain/922529c0-c12e-4424-b378-50d7bfb37fa2/scratch/';
  
  // Set window size
  await page.setViewportSize({ width: 1440, height: 900 });

  console.log('1. Testing Contact View...');
  await page.goto(`${baseUrl}/contact`);
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: `${outDir}contact.png`, fullPage: true });

  console.log('2. Testing Register View...');
  await page.goto(`${baseUrl}/register`);
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: `${outDir}register.png` });

  console.log('3. Setting mock admin user...');
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
  
  console.log('4. Testing Catalog View...');
  await page.goto(`${baseUrl}/catalog`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000); 
  await page.screenshot({ path: `${outDir}catalog.png` });
  
  // Test Search
  await page.fill('input[type="text"]', 'L2E');
  await page.click('.btn-search');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${outDir}catalog_search.png` });

  console.log('5. Testing API Management View...');
  await page.goto(`${baseUrl}/api-management`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${outDir}api_management.png` });

  console.log('6. Testing Dataset Config View (Create Mode)...');
  await page.goto(`${baseUrl}/dataset-config`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${outDir}dataset_config.png` });

  await browser.close();
  console.log('Done!');
})();
