import { test, expect } from '@playwright/test';

test.describe('Admin Restaurant Management Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Login admin
    await page.goto('http://127.0.0.1:5500/templates/auth/login.html');
    await page.locator('input[name="username"]').fill( 'admin');
    await page.locator('input[name="password"]').fill('123456' );
    await page.locator('.submit').click();
    await page.waitForLoadState('networkidle');
    // Vào trang quản lý nhà hàng
    await page.goto('http://127.0.0.1:5500/templates/admin/restaurants.html' );
    await page.waitForLoadState('networkidle');

  });

  test('Load restaurant management page successfully', async ({ page }) => {
    await expect(
      page.locator('h2')
    ).toContainText(
      'Quản Lý Nhà Hàng'
    );
    await expect(page.locator('.res-table')).toBeVisible();
  });

  test('Restaurant list loads successfully', async ({ page }) => {
    await page.waitForSelector('#res-list-body tr');
    const rowCount = await page.locator('#res-list-body tr').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('Open add restaurant modal successfully', async ({ page }) => {
    await page.click('.btn-add');
    await expect(page.locator('#appModalWrapper')).toHaveClass(/is-visible/);
    await expect(page.locator('#appModalTitle')).toContainText('Đăng ký Nhà Hàng');
  });

  test('Add restaurant successfully', async ({ page }) => {
      await page.click('.btn-add');
      // CHỜ dropdown load xong
      await page.waitForFunction(() => {
        const cuisine = document.querySelector('#res-cuisine');
        const user = document.querySelector('#res-user');

        return cuisine &&
               cuisine.options.length > 1 &&
               user &&
               user.options.length > 1;
      });

      const restaurantName = 'Playwright Restaurant ' + Date.now();
      await page.fill('#res-name', restaurantName);
      await page.fill('#res-address','123 Nguyen Hue');
      await page.fill(  '#res-phone',  '0912345678' );
      await page.fill('#res-email',`playwright${Date.now()}@gmail.com`);
      // chọn cuisine thật
      await page.selectOption('#res-cuisine',{ index: 1 });
      // chọn user thật
      await page.selectOption('#res-user', { index: 1 });
      await page.fill('#res-open','08:00');
      await page.fill('#res-close', '22:00');
      await page.fill('#res-desc','Nhà hàng test playwright');
      await page.click('.app-btn-save');
      await expect(
        page.locator('#restaurant-admin-message')
      ).toContainText(
        'Thêm nhà hàng thành công'
      );
    });

  test('Cannot add restaurant with empty name', async ({ page }) => {
    await page.click('.btn-add');
    await page.fill('#res-address','456 Le Loi');
    await page.fill('#res-phone','0912345678');
    await page.click('.app-btn-save');
    const isValid = await page.$eval('#res-name',(el) => el.checkValidity());
    expect(isValid).toBeFalsy();
  });

  test('Edit restaurant successfully', async ({ page }) => {
    await page.waitForSelector('.btn-edit');
    await page.locator('.btn-edit').first().click();
    const updatedName ='Updated Restaurant ' + Date.now();
    await page.fill('#res-name',updatedName);
    await page.click('.app-btn-save');
    await expect(
      page.locator('#restaurant-admin-message')
    ).toContainText(
      'Cập nhật nhà hàng thành công'
    );
  });
  test('Delete restaurant successfully', async ({ page }) => {
    page.on('dialog', dialog => dialog.accept());
    await page.waitForSelector('.btn-delete');
    await page.locator('.btn-delete').last().click();
    await expect(page.locator('#restaurant-admin-message')).toBeVisible();
  });

  test('Open approval modal successfully', async ({ page }) => {
    const pendingButton = page.locator('.admin-restaurants-status-button.pending');
    const count = await pendingButton.count();
    if (count > 0) {
      await pendingButton.first().click();
      await expect(page.locator('#approvalModal')).toHaveClass(/is-visible/);
      await expect(page.locator('#approval-restaurant-name')).toBeVisible();
    }
  });

  test('Approve restaurant successfully', async ({ page }) => {
    const pendingButton = page.locator('.admin-restaurants-status-button.pending');
    const count = await pendingButton.count();
    if (count > 0) {
      await pendingButton.first().click();
      await page.click('#approvalApproveButton');
      await expect(page.locator('#restaurant-admin-message')).toBeVisible();
    }
  });

  test('Reject restaurant successfully', async ({ page }) => {
    const pendingButton = page.locator('.admin-restaurants-status-button.pending');
    const count = await pendingButton.count();
    if (count > 0) {
      await pendingButton.first().click();
      await page.click('#approvalRejectButton');
      await expect(
        page.locator('#restaurant-admin-message')
      ).toBeVisible();
    }
  });

  test('Close modal successfully', async ({ page }) => {
    await page.click('.btn-add');
    await page.click('.app-btn-cancel');
    await expect(
      page.locator('#appModalWrapper')
    ).not.toHaveClass(/is-visible/);
  });

  test('Logout successfully', async ({ page }) => {
    page.on('dialog', dialog => dialog.accept());
    await page.click('.btn-logout');
    await expect(page).toHaveURL(
      /login\.html/
    );
  });
});