const { test, expect } = require('@playwright/test');

test.describe('Admin Report Feature', () => {

  // LOGIN HELPER
  async function adminLogin(page) {
    await page.goto('/templates/auth/login.html');
    await page.waitForSelector('input[name="username"]');
    await page.fill('input[name="username"]','admin');
    await page.fill('input[name="password"]','123456');
    await page.click('input[type="submit"]');
    await page.waitForLoadState('networkidle');
  }

  test.beforeEach(async ({ page }) => {
    page.on('dialog', async dialog => {
      console.log('DIALOG:',dialog.message());
      await dialog.accept();
    });
  });

  // LOAD PAGE
  test('Report page loads successfully', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await expect(
      page.locator('.admin-report-title')
    ).toContainText(
      'Báo cáo doanh thu nhà hàng'
    );
  });

  // LOAD RESTAURANT DROPDOWN
  test('Restaurant dropdown loads', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.waitForFunction(() => {
      const select = document.querySelector('#restaurant_id');
      return select && select.options.length > 1;
    });
    const options = page.locator('#restaurant_id option');
    const count = await options.count();
    expect(count).toBeGreaterThan(0);
  });

  // DEFAULT MONTH EXISTS
  test('Current month auto selected', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.waitForSelector('#report_month');
    const value = await page.inputValue('#report_month');
    expect(value).not.toBe('');
  });

  // LOAD REPORT SUCCESS
  test('Load report successfully', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.waitForSelector('#loadReportBtn');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    await expect(page.locator('#status_text')).toContainText('Hoàn tất');
  });


  // REPORT TABLE LOADS
  test('Report table loads data', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');

    await page.waitForTimeout(4000);
    await expect(
      page.locator('#report_table_body')
    ).toBeVisible();

  });

  // TOTAL REPORT DISPLAY
  test('Total revenue displays', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    const total = await page.locator('#total_report').textContent();
    expect(total).not.toBeNull();
  });

  // TOTAL 6 MONTHS DISPLAY
  test('Total 6 months revenue displays', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    const total = await page.locator('#total_6_months').textContent();
    expect(total).not.toBeNull();
  });

  // RESTAURANT COUNT DISPLAY
  test('Restaurant count displays', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    const count = await page.locator('#restaurant_count').textContent();
    expect(count).not.toBe('');
  });

  // FILTER BY RESTAURANT
  test('Filter report by restaurant', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.waitForFunction(() => {
      const select = document.querySelector('#restaurant_id');
      return select && select.options.length > 1;
    });

    const options = page.locator('#restaurant_id option');
    const count = await options.count();
    // option đầu là "Tất cả"
    if (count > 1) {
      const value = await options.nth(1).getAttribute('value');
      await page.selectOption('#restaurant_id',value);
      await page.click('#loadReportBtn');
      await page.waitForTimeout(4000);
      await expect(
        page.locator('#status_text')
      ).toContainText(
        'Hoàn tất'
      );
    } else {
      console.log(
        'Không có nhà hàng để filter'
      );
    }
  });

  // CHANGE MONTH
  test('Change report month', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.fill('#report_month','2026-05');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    await expect(page.locator('#status_note')).toContainText('2026-05');
  });


  // TABLE HEADER LOADS
  test('Report table header renders', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    await expect(
      page.locator('#report_table_head')
    ).toContainText(
      'Nhà hàng'
    );
  });

  // TABLE BODY LOADS
  test('Report table body renders', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('#loadReportBtn');
    await page.waitForTimeout(4000);
    const rows = page.locator('#report_table_body tr' );
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });

  // LOGOUT
  test('Admin can logout', async ({ page }) => {
    await adminLogin(page);
    await page.goto('/templates/admin/report.html');
    await page.click('.btn-logout');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(
      /login\.html/
    );
  });
});