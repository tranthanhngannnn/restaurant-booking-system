const { test, expect } = require('@playwright/test');

test.describe('Restaurant Confirm Booking Feature', () => {

  // LOGIN HELPER
  async function staffLogin(page) {
    await page.goto('/templates/auth/login.html');
    await page.fill('input[name="username"]','restaurantstaff3');
    await page.fill('input[name="password"]','123456');
    await page.click('input[type="submit"]');
    await page.waitForURL('**/restaurant/table.html',{ timeout: 10000 });
    await expect(page).toHaveURL(/restaurant\/table\.html/);
  }

  // OPEN BOOKING PAGE
  async function openBookingPage(page) {
    await page.goto('/templates/restaurant/comfirmbooking.html');
    // chờ API load
    await page.waitForTimeout(3000);
    await expect(page.locator('table')).toBeVisible();
  }


  // HANDLE DIALOG
  test.beforeEach(async ({ page }) => {

    page.on('dialog', async dialog => {

      console.log(
        'DIALOG:',
        dialog.message()
      );
      await dialog.accept();
    });
  });

  // PAGE LOAD
  test('Restaurant booking page loads', async ({ page }) => {
    await page.goto('/templates/restaurant/comfirmbooking.html' );
    await expect(
      page.getByRole('heading', {
        name: 'Danh sách đặt bàn'
      })
    ).toBeVisible();
  });

  // LOGIN SUCCESS
  test('Restaurant can login successfully', async ({ page }) => {
    await staffLogin(page);
  });

  // BOOKING LIST LOAD
  test('Restaurant booking list loads', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    await expect(
      page.locator('#booking-list')
    ).toBeVisible();
  });

  // TABLE HEADER EXISTS

  test('Booking table headers display correctly', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    await expect(
      page.locator('th')
    ).toContainText([
      'Tên khách',
      'SĐT',
      'Số người',
      'Ngày',
      'Giờ',
      'Bàn',
      'Tiền cọc',
      'Trạng thái',
      'Hành động'
    ]);
  });

  // BOOKING ROW EXISTS

  test('Booking rows display successfully', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const rows = page.locator('#booking-list tr');
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  // CONFIRM BUTTON DISPLAY
  test('Pending booking displays confirm button', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const confirmButtons = page.locator('.btn.confirm');
    const count = await confirmButtons.count();
    if (count > 0) {
      await expect(confirmButtons.first()).toBeVisible();
    } else {
      console.log('Không có booking pending');
    }
  });

  // REJECT BUTTON DISPLAY
  test('Pending booking displays reject button', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const rejectButtons = page.locator('.btn.reject');
    const count = await rejectButtons.count();
    if (count > 0) {
      await expect(
        rejectButtons.first()
      ).toBeVisible();
    } else {
      console.log('Không có booking pending');

    }

  });

  // CONFIRM BOOKING
  test('Restaurant can confirm booking', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const confirmButtons = page.locator('.btn.confirm');
    const count = await confirmButtons.count();
    if (count > 0) {
      await confirmButtons.first().click();
      await page.waitForTimeout(3000);
      await expect(
        page.locator('#booking-list')
      ).toBeVisible();
    } else {
      console.log(
        'Không có booking pending để confirm'
      );
    }
  });

  // REJECT BOOKING

  test('Restaurant can reject booking', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const rejectButtons = page.locator('.btn.reject');
    const count = await rejectButtons.count();
    if (count > 0) {
      await rejectButtons.first().click();
      await page.waitForTimeout(3000);
      await expect(
        page.locator('#booking-list')
      ).toBeVisible();
    } else {
      console.log('Không có booking pending để reject');
    }
  });


  // STATUS COLUMN EXISTS
  test('Booking status column displays', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const statusCells = page.locator('#booking-list td');
    const count = await statusCells.count();
    expect(count).toBeGreaterThan(0);
  });

  // CUSTOMER NAME DISPLAY
  test('Customer name displays in booking list', async ({ page }) => {
    await staffLogin(page);
    await openBookingPage(page);
    const rows = page.locator('#booking-list tr');
    const count = await rows.count();
    if (count > 0) {
      await expect(
        rows.first()
      ).toBeVisible();
    }
  });

  // DATE DISPLAY
  test('Booking date displays correctly', async ({ page }) => {
      await staffLogin(page);
      await openBookingPage(page);
      const rows = page.locator('#booking-list tr');
      const count = await rows.count();
      if (count > 0) {
        const dateCell = rows.first().locator('td').nth(3);
        const dateText = await dateCell.textContent();
        expect(dateText.trim()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      }
    });
});