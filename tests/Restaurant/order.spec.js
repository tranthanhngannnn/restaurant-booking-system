const { test, expect } = require('@playwright/test');

test.describe('Restaurant Order Feature', () => {

  // LOGIN HELPER
  async function restaurantLogin(page) {
    await page.goto('/templates/auth/login.html');
    await page.fill('input[name="username"]','restaurantstaff3');
    await page.fill('input[name="password"]','123456');
    await page.click('input[type="submit"]');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(
      /restaurant\/table\.html/
    );
  }

  test.beforeEach(async ({ page }) => {
    // HANDLE ALERT + CONFIRM
    page.on('dialog', async dialog => {
      console.log('DIALOG:', dialog.message());
      await dialog.accept();
    });

  });

  test('Order page loads successfully', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await expect(
      page.locator('.title')
    ).toContainText('Bàn 1');

  });

  test('Menu loads successfully', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.menu-item', { timeout: 10000});
    const items = page.locator('.menu-item');
    const count = await items.count();
    expect(count).toBeGreaterThan(0);

  });

  test('Add item to order', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    await expect(
      page.locator('#order-list li')
    ).toHaveCount(1);

  });

  test('Increase quantity', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    // CLICK +
    await page.locator('#order-list button').nth(1).click();
    await expect(
      page.locator('#order-list li').first()
    ).toContainText('2');
  });

  test('Decrease quantity', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    // CLICK +
    await page.locator('#order-list button').nth(1).click();
    // CLICK -
    await page.locator('#order-list button').nth(0).click();
    await expect(
      page.locator('#order-list li').first()
    ).toContainText('1');

  });

  test('Remove item when quantity becomes zero', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    // CLICK -
    await page.locator('#order-list button').nth(0).click();
    await expect(
      page.locator('#order-list li')
    ).toHaveCount(0);
  });

  test('Total price updates correctly', async ({ page }) => {
    await restaurantLogin(page)
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    const total = page.locator('#total');
    await expect(total).not.toHaveText('0');
  });

  test('Create order with empty cart', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto( '/templates/restaurant/orders.html?table_id=1');
    await page.click('button:text("Gửi order")' );
  });

  test('Create order successfully', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    await page.click('button:text("Gửi order")' );
    await page.waitForTimeout(3000);
    await expect( page.locator('#order-list li')).toHaveCount(1);
  });

  test('Pay order successfully', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    await page.click('button:text("Gửi order")');
    await page.waitForTimeout(2000);
    await page.click('button:text("Thanh toán")');
    await page.waitForTimeout(3000);
    await expect(page).toHaveURL(/table\.html/);
  });

  test('Cart persists after reload', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    // SET LOCAL STORAGE
    await page.evaluate(() => {

      localStorage.setItem(
        'cart_table_1',
        JSON.stringify([
          {
            food_id: '1',
            name: 'Cơm chiên',
            price: 50000,
            qty: 1,
            image: ''
          }
        ])
      );
    });
    // RELOAD
    await page.reload();
    await page.waitForTimeout(2000);
    // VERIFY ITEM RESTORED
    await expect(
      page.locator('#order-list li')
    ).toHaveCount(1);
    await expect(
      page.locator('#order-list li').first()
    ).toContainText('Cơm chiên');

  });

  test('Order data still exists after page reload', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    await addButtons.first().click();
    await page.reload();
    await page.waitForTimeout(2000);
    await expect(
      page.locator('#order-list li')
    ).toHaveCount(1);
  });

  test('Multiple items can be added', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.btn-add');
    const addButtons = page.locator('.btn-add');
    const count = await addButtons.count();
    if (count >= 2) {
      await addButtons.nth(0).click();
      await addButtons.nth(1).click();
      await expect( page.locator('#order-list li')).toHaveCount(2);
    }
  });

  test('Menu item displays image', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.waitForSelector('.menu-item img');
    await expect(
      page.locator('.menu-item img').first()
    ).toBeVisible();

  });

  test('Logout button works', async ({ page }) => {
    await restaurantLogin(page);
    await page.goto('/templates/restaurant/orders.html?table_id=1');
    await page.click('.logout-btn');
    await expect(page).toHaveURL(
      /login\.html/
    );

  });

});