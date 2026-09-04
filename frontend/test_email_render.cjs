const fs = require('fs');
const { chromium } = require('playwright');

const htmlContent = `
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333; padding: 20px; border: 1px solid #eee;">
    <h2 style="color: #10b981;">Verify Your Email Address</h2>
    <p>Hi QA Engineer,</p>
    <p>Thank you for signing up with DataX Portal.</p>
    <p>Please click the button below to verify your email address and activate your account:</p>
    <br>
    <div style="text-align: center;">
        <a href="#" style="margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #10b981;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;font-weight:bold;">Verify Email</a>
    </div>
    <br><br>
    <p style="font-size: 12px; color: #777;">If you did not register for an account, please ignore this email.</p>
</div>
`;

fs.writeFileSync('email_preview.html', htmlContent);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/email_preview.html');
  await page.screenshot({ path: '/Users/natthawutjantakul/.gemini/antigravity/brain/922529c0-c12e-4424-b378-50d7bfb37fa2/scratch/email_preview.png' });
  await browser.close();
})();
