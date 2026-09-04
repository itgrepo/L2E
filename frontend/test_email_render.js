const fs = require('fs');
const { chromium } = require('playwright');

const htmlContent = `
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333; padding: 20px; border: 1px solid #eee;">
    <h2 style="color: #10b981;">Verify Your Email Address</h2>
    <p>Hi Admin User,</p>
    <p>Thank you for signing up with DataX Portal.</p>
    <p>Please click the button below to verify your email address and activate your account:</p>
    <br>
    <a href="#" style="display: inline-block; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Verify Email</a>
    <br><br>
    <p style="font-size: 12px; color: #777;">If you did not register for an account, please ignore this email.</p>
</div>
`;

fs.writeFileSync('email_preview.html', htmlContent);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/email_preview.html');
  await page.screenshot({ path: 'email_preview.png' });
  await browser.close();
})();
