const { test, expect } = require('@playwright/test');

test.describe('Register Feature', () => {

  // Handle alert chung
  test.beforeEach(async ({ page }) => {
    page.on('dialog', async dialog => {
      console.log('ALERT:', dialog.message());
      await dialog.accept();
    });

    await page.goto('/templates/auth/register.html');
  });

  test('Register page loads successfully', async ({ page }) => {

    await expect(page.locator('header'))
      .toContainText('Đăng ký tài khoản');

  });

  test('Show restaurant dropdown when role is STAFF', async ({ page }) => {

    // Ban đầu hidden
    await expect(page.locator('#restaurantDiv'))
      .toBeHidden();

    // Chọn STAFF
    await page.selectOption('#roleSelect', 'STAFF');

    // Verify dropdown hiện ra
    await expect(page.locator('#restaurantDiv'))
      .toBeVisible();

  });

  test('Password confirmation mismatch', async ({ page }) => {

    await page.fill('#user', 'testuser123');

    await page.fill('input[name="email"]', 'test@gmail.com');

    await page.fill('input[name="phone"]', '0123456789');

    await page.fill('#pass', '123456');

    // Sai confirm password
    await page.fill('#confirm_pass', '654321');

    await page.click('input[type="submit"]');

    // Không redirect
    await expect(page).toHaveURL(/register\.html/);

  });

  test('Register CUSTOMER successfully', async ({ page }) => {

    // random username tránh trùng DB
    const randomUser = `user${Date.now()}`;

    await page.fill('#user', randomUser);

    await page.fill('input[name="email"]',
      `${randomUser}@gmail.com`);

    await page.fill('input[name="phone"]',
      '0123456789');

    await page.fill('#pass', '123456');

    await page.fill('#confirm_pass', '123456');

    await page.selectOption('#roleSelect', 'CUSTOMER');

    await page.click('input[type="submit"]');

    // Chờ redirect về login
    await page.waitForURL('**/login.html');

    // Verify redirect
    await expect(page).toHaveURL(/login\.html/);

  });

});