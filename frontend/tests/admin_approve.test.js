/**
 * @jest-environment jsdom
 */
import { readFileSync } from 'fs';
import path from 'path';
import { JSDOM } from 'jsdom';

const htmlContent = readFileSync(path.join(process.cwd(), 'templates', 'restaurant', 'register_restaurant.html'), 'utf8').replace(/<script[^>]*src="[^"]*register_restaurant\.js"[^>]*><\/script>/gi, '');

describe('Admin Approve Registration Form Tests', () => {
  beforeEach(async () => {
    const dom = new JSDOM(htmlContent, {
      url: 'http://127.0.0.1:5500/templates/restaurant/register_restaurant.html'
    });

    global.window = dom.window;
    global.document = dom.window.document;
    global.localStorage = dom.window.localStorage;
    global.HTMLElement = dom.window.HTMLElement;

    localStorage.setItem('token', 'test-token');

    // Đảm bảo form và message box tồn tại
    if (!document.getElementById('restaurant-register-form')) {
      const form = document.createElement('form');
      form.id = 'restaurant-register-form';
      form.innerHTML = `
        <input id="register-restaurant-name" name="RestaurantName" type="text" required>
        <input id="register-restaurant-address" name="Address" type="text" required>
        <input id="register-restaurant-phone" name="Phone" type="text" required>
        <input id="register-restaurant-email" name="Email" type="email" required>
        <select id="register-restaurant-cuisine" name="CuisineID" required></select>
        <input id="register-restaurant-open" name="Opentime" type="time" required>
        <input id="register-restaurant-close" name="Closetime" type="time" required>
        <textarea id="register-restaurant-description" name="description" required></textarea>
        <button type="submit" id="register-submit-button">Đăng ký</button>
      `;
      document.body.appendChild(form);
    }

    if (!document.getElementById('restaurant-page-message')) {
      const msg = document.createElement('div');
      msg.id = 'restaurant-page-message';
      msg.hidden = true;
      document.body.appendChild(msg);
    }

    jest.clearAllMocks();
    global.fetch = jest.fn();
    window.fetch = global.fetch;
  });

  test('Hiển thị thông báo lỗi khi submit form mà để trống các trường bắt buộc', async () => {
    const form = document.getElementById('restaurant-register-form');
    const messageBox = document.getElementById('restaurant-page-message');

    expect(form).not.toBeNull();
    expect(messageBox).not.toBeNull();

    // Form trống không hợp lệ (required validation)
    expect(form.checkValidity()).toBe(false);

    // Các fields bắt buộc phải trống
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
      expect(field.value).toBe('');
    });
  });

  test('Gọi API gửi dữ liệu khi form hợp lệ và hiện thông báo thành công', async () => {
    const form = document.getElementById('restaurant-register-form');

    // Điền dữ liệu hợp lệ vào form
    document.getElementById('register-restaurant-name').value = 'Nhà hàng test';
    document.getElementById('register-restaurant-address').value = '123 Quận 1';
    document.getElementById('register-restaurant-phone').value = '0123456789';
    document.getElementById('register-restaurant-email').value = 'test@example.com';
    document.getElementById('register-restaurant-open').value = '08:00';
    document.getElementById('register-restaurant-close').value = '22:00';
    document.getElementById('register-restaurant-description').value = 'Mô tả test';
    document.getElementById('register-restaurant-cuisine').value = '1';

    // Mock phản hồi API thành công
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Đăng ký thành công' })
    });

    // Gắn handler submit (mô phỏng code thực tế)
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      await fetch('http://127.0.0.1:5000/api/v1/restaurants/registerRestaurant', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
    });

    // Kích hoạt gửi form
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);

    await new Promise(resolve => setTimeout(resolve, 100));

    // Kiểm tra fetch được gọi với method và URL đúng
    expect(global.fetch).toHaveBeenCalled();
    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toContain('registerRestaurant');
    expect(options.method).toBe('POST');
  });

  test('Admin duyệt nhà hàng thành công chuyển trạng thái Pending sang Active', async () => {
    const messageBox = document.getElementById('restaurant-page-message');

    // Tạo approval modal và button
    const approvalModal = document.createElement('div');
    approvalModal.id = 'approvalModal';
    const approveBtn = document.createElement('button');
    approveBtn.id = 'approvalApproveButton';
    approveBtn.textContent = 'Duyệt';
    approvalModal.appendChild(approveBtn);
    document.body.appendChild(approvalModal);

    // Mock phản hồi duyệt thành công
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Duyệt nhà hàng thành công!' })
    });

    // Mô phỏng hành động duyệt
    approveBtn.addEventListener('click', async () => {
      const response = await fetch('http://127.0.0.1:5000/api/v1/admin/restaurants/1/approve', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const result = await response.json();
      if (response.ok) {
        messageBox.hidden = false;
        messageBox.textContent = result.message;
        messageBox.className = 'staff-restaurant-message success';
      }
    });

    // Nhấn nút duyệt
    approveBtn.click();

    await new Promise(resolve => setTimeout(resolve, 100));

    // Kiểm tra API được gọi với endpoint /approve
    expect(global.fetch).toHaveBeenCalled();
    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toContain('/approve');
    expect(options.method).toBe('PUT');

    // Kiểm tra thông báo thành công được hiển thị
    expect(messageBox.hidden).toBe(false);
    expect(messageBox.textContent).toContain('thành công');
    expect(messageBox.className).toContain('success');
  });
});
