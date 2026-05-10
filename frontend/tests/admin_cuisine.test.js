/**
 * @jest-environment jsdom
 */
import { readFileSync } from 'fs';
import path from 'path';

const htmlContent = readFileSync(path.join(process.cwd(), 'templates', 'admin', 'cuisine.html'), 'utf8');
const bodyHTML = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i)?.[1] ?? '';
const scriptContent = readFileSync(path.join(process.cwd(), 'static', 'js', 'admin_cuisine.js'), 'utf8');

describe('Admin Cuisine Page Tests', () => {
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

    document.getElementById('form-id').value = '123';
    document.getElementById('form-name').value = 'Test Cuisine';
    document.getElementById('form-status').value = 'Ngưng hoạt động';
    document.getElementById('cuisineModal').style.display = 'none';
  });

  test('Modal thêm cuisine reset dữ liệu cũ', () => {
    openAddModal();

    expect(document.getElementById('form-id').value).toBe('');
    expect(document.getElementById('form-name').value).toBe('');
    expect(document.getElementById('modal-title').innerText).toBe('Thêm Cuisine');
    expect(document.getElementById('cuisineModal').style.display).toBe('flex');
  });

  test('Đóng modal cuisine không lưu', () => {
    openAddModal();
    closeModal();

    expect(document.getElementById('cuisineModal').style.display).toBe('none');
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
