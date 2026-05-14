const { test, expect } = require('@playwright/test');

test.describe('Customer History Feature', () => {


  // LOGIN HELPER
  async function customerLogin(page) {
    await page.goto('/templates/auth/login.html');
    await page.waitForSelector('input[name="username"]');

    await page.fill('input[name="username"]', 'Quyen' );
    await page.fill('input[name="password"]', '12345' );
    await page.click('input[type="submit"]');
    await page.waitForLoadState('networkidle');
    console.log('CURRENT URL:',await page.url());
    await expect(page).toHaveURL(/customer\/home\.html/ );
  }

  // HANDLE ALERT
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
  test('History page loads successfully', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.waitForLoadState('networkidle' );
    await expect(
      page.getByRole('heading', {
        name: 'Lịch sử đặt bàn'
      })
    ).toBeVisible();

  });

  // HISTORY CONTAINER LOAD
  test('History list loads', async ({ page }) => {
    await customerLogin(page);
    await page.goto( '/templates/customer/history.html' );
    await page.waitForSelector('#historyContainer');
    await expect(page.locator('#historyContainer')).toBeVisible();});


  // HISTORY LINK VISIBLE
  test('History link visible after login', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html' );
    await expect(page.locator('#historyLink')).toBeVisible();
  });

  // REDIRECT IF NO TOKEN
  test('Redirect to login when token missing', async ({ page }) => {
    await page.goto( '/templates/customer/history.html');
    await page.waitForURL('**/auth/login.html');
    await expect(page).toHaveURL(/auth\/login\.html/ );
  });


  // EMPTY HISTORY
  test('Display no data message when history empty', async ({ page }) => {
    await customerLogin(page);
    await page.route(
      '**/api/v1/customer/history',
      async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });

      }
    );
    await page.goto( '/templates/customer/history.html');
    await expect(page.locator('#historyContainer')).toContainText('Không có dữ liệu' );});
  // SEARCH BOOKING
  test('Search booking history', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html' );
    await page.waitForSelector('#searchInput');
    await page.fill('#searchInput','1');
    await page.waitForTimeout(1000);
    await expect(page.locator('#historyContainer')).toBeVisible();
  });


  // SEARCH CUSTOMER NAME
  test('Search booking by customer name', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.fill('#searchInput','Quyen');
    await page.waitForTimeout(1000);
    await expect(page.locator('#historyContainer')).toBeVisible();
  });


  // FILTER CONFIRMED
  test('Filter booking status Confirmed', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.waitForSelector('#statusFilter',{ timeout: 10000 } );
    await page.selectOption('#statusFilter','Confirmed');
    await page.waitForTimeout(1000);
    await expect(page.locator('#historyContainer')).toBeVisible();
  });


  // FILTER PENDING
  test('Filter Pending booking', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html' );
    await page.selectOption( '#statusFilter','Pending' );
    await page.waitForTimeout(1000);
    await expect(page.locator('#historyContainer')).toBeVisible();
  });

  // FILTER CANCELLED
  test('Filter Cancelled booking', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.selectOption('#statusFilter','Cancelled');
    await page.waitForTimeout(1000);
    await expect(page.locator('#historyContainer')).toBeVisible();
  });


  // OPEN REVIEW POPUP
  test('Open review popup', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.waitForSelector('#historyContainer');
    await page.waitForTimeout(3000);
    const reviewButtons = page.locator('button:text("⭐ Đánh giá")');
    const count =await reviewButtons.count();

    if (count > 0) {
      await reviewButtons
        .first()
        .click();
      await expect( page.locator('#reviewBox')).toBeVisible();
    } else {
      console.log('Không có booking confirmed để review');
    }
  });

  // CLOSE REVIEW POPUP
  test('Close review popup', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.waitForTimeout(3000);
    const reviewButtons = page.locator('button:text("⭐ Đánh giá")' );
    const count = await reviewButtons.count();
    if (count > 0) {
      await reviewButtons
        .first()
        .click();
      await expect(page.locator('#reviewBox')).toBeVisible();
      await page.locator('#reviewBox button').last().click();
      await expect(page.locator('#reviewBox')).toBeHidden();
    } else {
      console.log('Không có booking để đóng popup');
    }
  });


  // SUBMIT REVIEW
  test('Submit review successfully', async ({ page }) => {
    await customerLogin(page);
    await page.goto('/templates/customer/history.html');
    await page.waitForSelector('#historyContainer');
    await page.waitForTimeout(3000);
    const reviewButtons = page.locator('button:text("⭐ Đánh giá")');
    const count =await reviewButtons.count();

    if (count > 0) {
      await reviewButtons
        .first()
        .click();

      await page.waitForSelector('#reviewBox');
      await page.fill('#rating','5' );
      await page.fill('#comment','Playwright automation review test');
      await page.click('button:text("Gửi")');
      await page.waitForTimeout(3000);
      await expect(page.locator('#historyContainer')).toBeVisible();
    } else {
      console.log('Không có booking để review');
    }
  });

  // SUBMIT REVIEW WITHOUT TOKEN
  test('Cannot submit review without token', async ({ page }) => {
    await customerLogin(page);
    await page.goto( '/templates/customer/history.html' );
    await page.evaluate(() => {localStorage.removeItem('token');});
    await page.evaluate(() => {
      const reviewBox =document.getElementById('reviewBox');
      if (reviewBox) {
        reviewBox.style.display = 'flex';
      }
    });
    await page.waitForTimeout(1000);
  });

  // GO HOME BUTTON
  test('Go home button works', async ({ page }) => {
    await customerLogin(page);
    await page.goto( '/templates/customer/history.html');
    await page.click( '.btn-closehst' );
    await page.waitForURL('**/customer/home.html' );
    await expect(page).toHaveURL( /customer\/home\.html/);
  });
});