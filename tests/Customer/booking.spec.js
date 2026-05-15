const { test, expect } = require('@playwright/test');

test.describe('Customer Booking Feature', () => {

  // HELPER: CAPTURE ALERT
  async function captureAlert(page) {
    return new Promise(resolve => {
      page.once('dialog', async dialog => {
        const message = dialog.message();
        await dialog.accept();
        resolve(message);
      });
    });
  }

  // HELPER: FILL VALID FORM
  async function fillValidBookingForm(page) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const date = tomorrow.toISOString().split('T')[0];
    // Chờ dropdown load
    await page.waitForTimeout(1500);
    const options = page.locator('#restaurantSelect option');
    const count = await options.count();
    expect(count).toBeGreaterThan(1);
    // Chọn restaurant đầu tiên
    const value = await options.nth(1).getAttribute('value');
    await page.selectOption('#restaurantSelect', value);
    // Fill form
    await page.fill('#nameInput', 'Nguyen Van A');
    await page.fill('#phoneInput', '0123456789');
    await page.fill('#dateInput', date);
    await page.fill('#timeInput', '18:00');
    await page.fill('#peopleInput', '4');
  }

  // BEFORE EACH
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates/customer/booking.html');
    await page.waitForLoadState('networkidle');
  });


  // SMOKE TEST
  test('Booking page loads successfully', async ({ page }) => {
    await expect(page.locator('h2')).toContainText('Đặt bàn');
    await expect(page.locator('#restaurantSelect')).toBeVisible();
    await expect(page.locator('#nameInput')).toBeVisible();
    await expect(page.locator('#phoneInput')).toBeVisible();
  });

  test('Restaurant dropdown loads successfully', async ({ page }) => {
    await page.waitForTimeout(2000);
    const count = await page.locator('#restaurantSelect option').count();
    expect(count).toBeGreaterThan(1);
  });


  // VALIDATION TEST
  test('Validate empty booking form', async ({ page }) => {
    const alertPromise = captureAlert(page);
    await page.click('button:text("Kiểm tra bàn")');
    const alertMessage = await alertPromise;
    expect(alertMessage).toContain('Vui lòng nhập đầy đủ thông tin');
  });

  test('Validate invalid phone number', async ({ page }) => {
    await page.fill('#nameInput', 'Nguyen Van A');
    await page.fill('#phoneInput', '123');
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const date = tomorrow.toISOString().split('T')[0];
    await page.fill('#dateInput', date);
    await page.fill('#timeInput', '18:00');
    await page.fill('#peopleInput', '4');
    const alertPromise = captureAlert(page);
    await page.click('button:text("Kiểm tra bàn")');
    const alertMessage = await alertPromise;
    expect(alertMessage).toContain('SĐT phải gồm 10 số');

  });

  test('Validate booking in the past', async ({ page }) => {
    await page.fill('#nameInput', 'Nguyen Van A');
    await page.fill('#phoneInput', '0123456789');
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const date = yesterday.toISOString().split('T')[0];
    await page.fill('#dateInput', date);
    await page.fill('#timeInput', '10:00');
    await page.fill('#peopleInput', '4');
    const alertPromise = captureAlert(page);
    await page.click('button:text("Kiểm tra bàn")');
    const alertMessage = await alertPromise;
    expect(alertMessage).toContain('Không thể đặt ngày, giờ trong quá khứ');
  });

  test('Validate booking less than 30 minutes', async ({ page }) => {
      await page.fill('#nameInput', 'Nguyen Van A');
      await page.fill('#phoneInput', '0123456789');
      // Lấy thời gian hiện tại
      const now = new Date();
      // +25 phút
      const future = new Date(now.getTime() + 25 * 60 * 1000);
      const year = future.getFullYear();
      const month = String(future.getMonth() + 1).padStart(2, '0');
      const day = String(future.getDate()).padStart(2, '0');
      const hours = String(future.getHours()).padStart(2, '0');
      const minutes = String(future.getMinutes()).padStart(2, '0');
      const date = `${year}-${month}-${day}`;
      const time = `${hours}:${minutes}`;
      await page.fill('#dateInput', date);
      await page.fill('#timeInput', time);
      await page.fill('#peopleInput', '4');
      // Chọn restaurant
      await page.waitForTimeout(1000);
      const value = await page
        .locator('#restaurantSelect option')
        .nth(1)
        .getAttribute('value');
      await page.selectOption('#restaurantSelect', value);
      const alertPromise = captureAlert(page);
      await page.click('button:text("Kiểm tra bàn")');
      const alertMessage = await alertPromise;
      expect(alertMessage).toContain('Phải đặt trước ít nhất 30 phút');
    });

  test('Validate note exceeds 300 characters', async ({ page }) => {
    await fillValidBookingForm(page);
    const longNote = 'A'.repeat(301);
    await page.fill('#noteInput', longNote);
    // Check bàn
    await page.click('button:text("Kiểm tra bàn")');
    const tableButtons = page.locator('#tables button');
    await expect(tableButtons.first()).toBeVisible();
    const alertPromise = captureAlert(page);
    // Chọn bàn
    await tableButtons.first().click();
    const alertMessage = await alertPromise;
    expect(alertMessage).toContain('Ghi chú tối đa 300 ký tự');

  });

  // BOOKING FLOW
  test('Customer can check available tables', async ({ page }) => {
    await fillValidBookingForm(page);
    await page.click('button:text("Kiểm tra bàn")');
    const tableButtons = page.locator('#tables button');
    await expect(tableButtons.first())
      .toBeVisible();
  });
  test('Customer can book successfully', async ({ page }) => {
    // LOGIN
    await page.goto('/templates/auth/login.html');
    await page.fill('input[name="username"]', 'Quyen');
    await page.fill('input[name="password"]', '12345');
    await page.click('input[type="submit"]');
    await page.waitForURL('**/customer/home.html');
    // BOOKING PAGE
    await page.goto('/templates/customer/booking.html');
    await page.waitForLoadState('networkidle');
    await fillValidBookingForm(page);
    await page.fill('#noteInput','Playwright automation test');
    // CHECK TABLe
    await page.click('button:text("Kiểm tra bàn")');
    const tableButtons = page.locator('#tables button');
    await expect(tableButtons.first()).toBeVisible();
    // SELECT TABLE
    await tableButtons.first().click();
    // PAYMENT POPUP
    await expect(page.locator('#paymentBox')).toBeVisible();
    // Verify payment info
    await expect(page.locator('#cusName')).toContainText('Nguyen Van A');
    await expect(page.locator('#cusPhone')).toContainText('0123456789');
    // CONFIRM PAYMENT
    await page.click('button:text("Đã chuyển khoản")');
    // SUCCESS POPUP
    await expect(page.locator('#successBox')).toBeVisible();
    await expect(page.locator('#successBox')).toContainText('Đặt bàn thành công');
  });
});