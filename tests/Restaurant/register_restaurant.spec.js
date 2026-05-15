import { test, expect } from '@playwright/test';
test.describe('Restaurant Registration Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://127.0.0.1:5500/templates/auth/login.html');
    await page.locator('input[name="username"]').fill('restaurantstaff3');
    await page.locator('input[name="password"]').fill('123456');

    await page.locator('.submit').click();
    await page.waitForLoadState('networkidle');
    // Vào trang đăng ký
    await page.goto('http://127.0.0.1:5500/templates/restaurant/register_restaurant.html');
    await page.waitForLoadState('networkidle');
  });
  test('Cuisine dropdown loads successfully', async ({ page }) => {
    await page.waitForFunction(() => {
      const select = document.querySelector(
        '#register-restaurant-cuisine'
      );
      return select && select.options.length > 1;
    });
    const optionCount = await page.locator(
      '#register-restaurant-cuisine option'
    ).count();
    expect(optionCount).toBeGreaterThan(1);
  });

  test('Register restaurant successfully', async ({ page }) => {
    const restaurantName = 'Playwright Restaurant ' + Date.now();
    await page.fill('#register-restaurant-name',restaurantName);
    await page.fill('#register-restaurant-address','123 Nguyen Hue' );
    await page.fill('#register-restaurant-phone','0912345678' );
    await page.fill('#register-restaurant-email',`playwright${Date.now()}@gmail.com`);
    await page.selectOption('#register-restaurant-cuisine',{ index: 1 });
    await page.fill('#register-restaurant-open','08:00');
    await page.fill('#register-restaurant-close','22:00');
    await page.fill('#register-restaurant-description','Nhà hàng test automation playwright');
    await page.click('#register-submit-button');
    await expect(
      page.locator('#restaurant-page-message')
    ).toContainText(
      'Đăng ký thành công'
    );
  });

  test('Cannot register with empty restaurant name', async ({ page }) => {
    await page.fill('#register-restaurant-address','456 Le Loi');
    await page.fill('#register-restaurant-phone','0912345678' );
    await page.fill('#register-restaurant-email','emptyname@gmail.com');
    await page.selectOption('#register-restaurant-cuisine',{ index: 1 } );
    await page.fill('#register-restaurant-open','09:00');
    await page.fill('#register-restaurant-close','21:00');
    await page.fill('#register-restaurant-description','Test validate');
    await page.click('#register-submit-button' );

    const isValid = await page.$eval(
      '#register-restaurant-name',
      (el) => el.checkValidity()
    );
    expect(isValid).toBeFalsy();
  });

  test('Cannot register without login token', async ({ page }) => {
      await page.evaluate(() => {localStorage.removeItem('token');});
      await page.reload();
      await expect(
        page.locator('#restaurant-page-message')
      ).toContainText(
        'Không tải được loại ẩm thực'
      );
    });

  test('Cancel registration redirects to table page', async ({ page }) => {
    await page.fill('#register-restaurant-name','Temp Restaurant');
    await page.fill( '#register-restaurant-address','Cancel Address'  );
    await page.click('#register-cancel-button' );
    await expect(page).toHaveURL( /table\.html/ );
  });
});