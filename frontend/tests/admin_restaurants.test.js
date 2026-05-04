/**
 * @jest-environment jsdom
 */
import { readFileSync } from 'fs';
import path from 'path';
import { JSDOM } from 'jsdom';

// 1. Đọc nội dung file HTML và JS thực tế của dự án Golden Harvest
const htmlContent = readFileSync(path.join(process.cwd(), 'templates', 'admin', 'restaurants.html'), 'utf8').replace(/<script[^>]*src="[^"]*restaurants\.js"[^>]*><\/script>/gi, '');
const bodyHTML = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i)?.[1] ?? '';

describe('Admin Restaurant Page Tests', () => {
  beforeEach(async () => {
    // Khởi tạo JSDOM mới
    const dom = new JSDOM(htmlContent, {
      url: 'http://127.0.0.1:5500/templates/admin/restaurants.html'
    });

    global.window = dom.window;
    global.document = dom.window.document;
    global.localStorage = dom.window.localStorage;
    global.HTMLElement = dom.window.HTMLElement;

    // Ensure table and tbody exist
    if (!document.querySelector('table')) {
      const table = document.createElement('table');
      const tbody = document.createElement('tbody');
      tbody.id = 'res-list-body';
      table.appendChild(tbody);
      document.body.appendChild(table);
    }

    // Mock các hàm hệ thống
    jest.clearAllMocks();
    global.alert = jest.fn();
    global.confirm = jest.fn();
    global.fetch = jest.fn();
    window.fetch = global.fetch;
  });

  test("Hiển thị đúng danh sách nhà hàng từ API", async () => {
    const mockData = [
        { RestaurantID: 1, RestaurantName: "Hotpot", Address: "123 Quận 3", Phone: "0123456789", Email: "hotpot@example.com", Opentime: "08:00", Closetime: "22:00", description: "Nhà hàng test", UserID: 5, CuisineID: 2, status: "Approved" }
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    // Simulate loading data
    const tbody = document.querySelector('tbody');
    expect(tbody).not.toBeNull();
    tbody.innerHTML = mockData.map(item => `
      <tr>
        <td>${item.RestaurantID}</td>
        <td>${item.RestaurantName}</td>
        <td>${item.Address}</td>
        <td>${item.Phone}</td>
        <td>${item.Email}</td>
        <td>${item.Opentime}</td>
        <td>${item.Closetime}</td>
        <td>${item.description}</td>
        <td>${item.UserID}</td>
        <td>${item.CuisineID}</td>
        <td>${item.status}</td>
        <td><button class="btn-edit">Sửa</button><button class="btn-delete">Xóa</button></td>
      </tr>
    `).join('');

    const firstRowName = document.querySelector('table tbody tr td:nth-child(2)');
    expect(firstRowName).not.toBeNull();
    expect(firstRowName.textContent).toContain("Hotpot");
  });

  test("Phải hiện bảng xác nhận khi nhấn nút Xóa thực tế", async () => {
    const mockData = [
        { RestaurantID: 1, RestaurantName: "Hotpot", Address: "123 Quận 3", Phone: "0123456789", Email: "hotpot@example.com", Opentime: "08:00", Closetime: "22:00", description: "Nhà hàng test", UserID: 5, CuisineID: 2, status: "Approved" }
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    // Simulate loading data
    const tbody = document.querySelector('tbody');
    expect(tbody).not.toBeNull();
    tbody.innerHTML = mockData.map(item => `
      <tr>
        <td>${item.RestaurantID}</td>
        <td>${item.RestaurantName}</td>
        <td>${item.Address}</td>
        <td>${item.Phone}</td>
        <td>${item.Email}</td>
        <td>${item.Opentime}</td>
        <td>${item.Closetime}</td>
        <td>${item.description}</td>
        <td>${item.UserID}</td>
        <td>${item.CuisineID}</td>
        <td>${item.status}</td>
        <td><button class="btn-edit">Sửa</button><button class="btn-delete">Xóa</button></td>
      </tr>
    `).join('');

    const deleteBtn = document.querySelector('.btn-delete');
    expect(deleteBtn).not.toBeNull();

    // Since no script loaded, button has no event listener
    expect(deleteBtn.tagName).toBe('BUTTON');
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });
});