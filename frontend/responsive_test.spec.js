import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://134.185.172.127:3003';
const VIEWPORTS = [
  { width: 390, height: 844, name: 'Mobile' },
  { width: 768, height: 1024, name: 'Tablet-Portrait' },
  { width: 1024, height: 768, name: 'Tablet-Landscape' },
  { width: 1440, height: 900, name: 'Desktop' }
];

const ROUTES = [
  '/',
  '/login',
  '/dashboard',
  '/catalog',
  '/api-management',
  '/api-monitor',
  '/user-management',
  '/permission-management',
  '/dataset-management',
  '/organization-management'
];

test.describe('Full Responsive UI Audit', () => {

  test.beforeEach(async ({ page }) => {
    // Add fake auth context before going to routes
    await page.goto(`${BASE_URL}/login`);
    await page.evaluate(() => {
      const fakeUser = {
        email: "admin@test.com",
        username: "admin",
        role: "admin",
        permissions: ["full_access"]
      };
      localStorage.setItem('user', JSON.stringify(fakeUser));
    });
  });

  for (const route of ROUTES) {
    test.describe(`Route: ${route}`, () => {
      for (const viewport of VIEWPORTS) {
        test(`Viewport: ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
          await page.setViewportSize({ width: viewport.width, height: viewport.height });
          await page.goto(`${BASE_URL}${route}`, { waitUntil: 'networkidle' });

          await page.waitForTimeout(2000); // Wait for animations/data fetch

          const dir = path.join(process.cwd(), '..', 'docs', 'responsive-audit', 'before', viewport.name);
          if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
          }
          
          const filename = route === '/' ? 'home' : route.substring(1).replace(/\//g, '_');
          await page.screenshot({ path: path.join(dir, `${filename}.png`), fullPage: true });

          const overflowX = await page.evaluate(() => {
            return document.documentElement.scrollWidth > window.innerWidth;
          });

          const bodyOverflow = await page.evaluate(() => {
            return document.body.scrollWidth > window.innerWidth;
          });

          if (overflowX || bodyOverflow) {
            console.warn(`[WARNING] Horizontal overflow detected on ${route} at ${viewport.name}`);
          }
        });
      }
    });
  }
});
