/**
 * @jest-environment jsdom
 */
import { readFileSync } from 'fs';
import path from 'path';

const htmlContent = readFileSync(path.join(process.cwd(), 'templates', 'admin', 'users.html'), 'utf8');
const bodyHTML = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i)?.[1] ?? '';
const scriptContent = readFileSync(path.join(process.cwd(), 'static', 'js', 'admin_users.js'), 'utf8');

describe('Admin Users Page Tests', () => {
  beforeAll(() => {
    document.body.innerHTML = bodyHTML;

    const scriptEl = document.createElement('script');
    scriptEl.textContent = scriptContent;
    document.head.appendChild(scriptEl);
    window.onload = null;
  });

  beforeEach(() => {
    document.body.innerHTML = bodyHTML;

    jest.clearAllMocks();
    global.alert = jest.fn();
    global.confirm = jest.fn();
    global.fetch = jest.fn();
    window.fetch = global.fetch;
  });

  test('Không xác định ID khi lưu modal thêm mới', () => {
    openAddModal();

    document.getElementById('user-field-name').value = 'Test User';
    document.getElementById('user-field-email').value = 'test@example.com';
    document.getElementById('user-field-phone').value = '123456789';
    document.getElementById('user-field-role').value = 'CUSTOMER';

    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

    handleSaveUser();

    expect(alert).toHaveBeenCalledWith('Lỗi: Không xác định được người dùng cần sửa.');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('Đóng modal sửa user', () => {
    openEditModal(1, 'Test', 'test@example.com', '123', 'ADMIN');

    expect(document.getElementById('userModal').style.display).toBe('flex');

    closeUserEntry();

    expect(document.getElementById('userModal').style.display).toBe('none');
  });

  test('Danh sách user hiển thị phone rỗng', async () => {
    const mockUsers = [
      { id: 1, username: 'user1', email: 'user1@example.com', phone: null, role: 'CUSTOMER' },
      { id: 2, username: 'user2', email: 'user2@example.com', phone: '', role: 'ADMIN' },
      { id: 3, username: 'user3', email: 'user3@example.com', phone: '123456', role: 'STAFF' }
    ];

    global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockUsers });

    await fetchUsers();

    const tbody = document.getElementById('user-list-body');
    const rows = tbody.querySelectorAll('tr');

    expect(rows.length).toBe(3);
    expect(rows[0].querySelector('.cell-phone').textContent).toBe('Chưa có số');
    expect(rows[1].querySelector('.cell-phone').textContent).toBe('Chưa có số');
    expect(rows[2].querySelector('.cell-phone').textContent).toBe('123456');
  });
});