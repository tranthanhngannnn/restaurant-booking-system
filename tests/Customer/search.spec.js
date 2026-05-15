const { test, expect } = require('@playwright/test');

test.describe('Customer Search Feature', () => {


  // HELPER: LOGIN
  async function customerLogin(page) {
    await page.goto('/templates/auth/login.html');
    await page.fill('input[name="username"]','Quyen' );
    await page.fill('input[name="password"]', '12345');
    await page.click('input[type="submit"]');
    await page.waitForURL('**/customer/home.html');
  }


  // HELPER: OPEN SEARCH PAGE
  async function openSearchPage(page) {
    await customerLogin(page);
    await page.goto('/templates/customer/search.html');
    await page.waitForLoadState('networkidle');
  }


  // BEFORE EACH
  test.beforeEach(async ({ page }) => {
    // Handle alert dialog
    page.on('dialog', async dialog => {
      console.log('ALERT:', dialog.message());
      await dialog.accept();
    });
  });

  // PAGE LOAD

  test('Search page loads successfully', async ({ page }) => {
    await openSearchPage(page);
    await expect(
      page.getByRole('heading', {
        name: 'Tìm kiếm nhà hàng'
      })
    ).toBeVisible();
    await expect(page.locator('#address')).toBeVisible();
    await expect(page.locator('#cuisine')).toBeVisible();

  });


  // SEARCH TEST
  test('Search restaurant by address', async ({ page }) => {
    await openSearchPage(page);
    await page.fill('#address', 'HCM');
    await page.click('button:text("Tìm kiếm")');
    // Verify result loaded
    await expect(
      page.locator('#result')
    ).not.toBeEmpty();

  });

  test('Search restaurant by cuisine', async ({ page }) => {
    await openSearchPage(page);
    await page.selectOption('#cuisine', '1');
    await page.click('button:text("Tìm kiếm")');
    await expect(
      page.locator('#result')
    ).not.toBeEmpty();

  });

  test('Search restaurant by address and cuisine', async ({ page }) => {
    await openSearchPage(page);
    await page.fill('#address', 'HCM');
    await page.selectOption('#cuisine', '1');
    await page.click('button:text("Tìm kiếm")');
    await expect(
      page.locator('#result')
    ).not.toBeEmpty();

  });

  test('Search restaurant with empty result', async ({ page }) => {
    await openSearchPage(page);
    await page.fill('#address', 'abcdefghxyz123456' );
    await page.click('button:text("Tìm kiếm")');
    await expect(page.locator('#result')).toContainText('Không tìm thấy');
  });

  test('Search with empty input returns results', async ({ page }) => {
    await openSearchPage(page);
    await page.click('button:text("Tìm kiếm")');
    await expect(page.locator('#result')).not.toBeEmpty();
  });


  // RESULT VALIDATION
  test('Search result contains restaurant information', async ({ page }) => {
    await openSearchPage(page);
    await page.fill('#address', 'HCM');
    await page.click('button:text("Tìm kiếm")');
    const result = page.locator('#result');
    await expect(result).toContainText('📍');
    await expect(result).toContainText('📞');
  });

  test('Search result displays booking button', async ({ page }) => {
      await openSearchPage(page);
      // Search all
      await page.click('button:has-text("Tìm kiếm")');
      // Chờ render
      await page.waitForTimeout(2000);
      const bookingButtons = page.locator(
        'button:has-text("Đặt bàn")'
      );
      const count = await bookingButtons.count();
      expect(count).toBeGreaterThan(0);

    });

  test('Search result displays detail button', async ({ page }) => {
      await openSearchPage(page);
      await page.click('button:has-text("Tìm kiếm")');
      await page.waitForTimeout(2000);
      const detailButtons = page.locator('button:has-text("Xem chi tiết")');
      const count = await detailButtons.count();
      expect(count).toBeGreaterThan(0);
    });

  // NAVIGATION TEST
  test('Navigate to booking page from search', async ({ page }) => {
      await openSearchPage(page);
      await page.click('button:has-text("Tìm kiếm")');
      await page.waitForTimeout(2000);
      const bookingButtons = page.locator('button:has-text("Đặt bàn")');
      const count = await bookingButtons.count();
      expect(count).toBeGreaterThan(0);
      await bookingButtons.first().click();
      await expect(page).toHaveURL(/booking\.html/);

    });

  test('Navigate to menu page from search', async ({ page }) => {
      await openSearchPage(page);
      await page.click('button:has-text("Tìm kiếm")');
      await page.waitForTimeout(2000);
      const menuButtons = page.locator(
        'button:has-text("Xem chi tiết")'
      );
      const count = await menuButtons.count();
      expect(count).toBeGreaterThan(0);
      await menuButtons.first().click();
      await expect(page).toHaveURL(/menu\.html/);

    });

  // HISTORY LINK
  test('History link is visible after login', async ({ page }) => {
    await openSearchPage(page);
    await page.waitForTimeout(3000);
    await expect(
      page.locator('#historyLink')
    ).toHaveCSS('display', 'block');
  });
});