const { test, expect } = require('@playwright/test');

test.describe('Login Feature', () => {
  test('Customer login successfully', async ({ page }) => {
    await page.goto('/templates/auth/login.html');
    await page.fill('input[name="username"]', 'Quyen');
    await page.fill('input[name="password"]', '12345');

    page.on('dialog', async dialog => {
      console.log(dialog.message());
      await dialog.accept();
    });

    await page.click('input[type="submit"]');

    await expect(page).toHaveURL(/customer\/home\.html/);
  });

});