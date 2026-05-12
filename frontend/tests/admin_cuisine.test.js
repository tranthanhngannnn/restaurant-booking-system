const fs = require('fs');
const path = require('path');

// Mock các hàm toàn cục
global.fetch = jest.fn();
global.alert = jest.fn();
global.confirm = jest.fn();
global.console.error = jest.fn();
global.console.log = jest.fn();

// Mock window.mockReload để thay thế location.reload()
window.mockReload = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = { 'token': 'mock-token' };
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
    removeItem: jest.fn((key) => { delete store[key]; }),
    clear: jest.fn(() => { store = { 'token': 'mock-token' }; }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Kiểm thử Admin Cuisine Frontend', () => {
  beforeEach(() => {
    // Thiết lập DOM giả lập
    document.body.innerHTML = `
            <table>
                <tbody id="cuisine-list-body"></tbody>
            </table>
            
            <div id="cuisineModal" style="display: none;">
                <h2 id="modal-title"></h2>
                <input type="hidden" id="form-id" />
                <input id="form-name" value="default" />
                <select id="form-status">
                    <option value="Available">Available</option>
                    <option value="Unavailable">Unavailable</option>
                </select>
                <button id="btn-submit">Lưu</button>
            </div>
        `;

    // Reset các mock
    jest.clearAllMocks();
    fetch.mockReset();
    window.mockReload.mockClear();

    // Mặc định fetch trả về mảng rỗng để tránh lỗi .map()
    fetch.mockResolvedValue({
      ok: true,
      json: async () => []
    });

    localStorageMock.clear();

    // Đọc và thực thi script
    const scriptPath = path.resolve(__dirname, '../static/js/admin_cuisine.js');
    let scriptCode = fs.readFileSync(scriptPath, 'utf8');

    // Thay const/let bằng var
    scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');

    // Thay thế location.reload() bằng window.mockReload() để tránh lỗi JSDOM
    scriptCode = scriptCode.replace(/location\.reload\(\)/g, 'window.mockReload()');

    // Gán hàm vào window
    scriptCode += `
            window.fetchCuisines = fetchCuisines;
            window.handleAdd = handleAdd;
            window.handleUpdate = handleUpdate;
            window.handleDelete = handleDelete;
            window.openAddModal = openAddModal;
            window.openEditModal = openEditModal;
            window.closeModal = closeModal;
            window.finishAction = finishAction;
            window.handleLogout = handleLogout;
        `;

    eval(scriptCode);
  });

  const flushPromises = () => new Promise(resolve => setTimeout(resolve, 100));

  test('1. fetchCuisines() gọi API GET kèm token Authorization', async () => {
    await window.fetchCuisines();
    expect(fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:5000/api/v1/admin/cuisines',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
      })
    );
  });

  test('2. fetchCuisines() hiển thị danh sách cuisine lên bảng', async () => {
    const mockData = [
      { id: 1, name: 'Việt Nam', status: 'Available' }
    ];
    fetch.mockResolvedValue({ ok: true, json: async () => mockData });

    await window.fetchCuisines();

    const tbody = document.getElementById('cuisine-list-body');
    expect(tbody.innerHTML).toContain('Việt Nam');
  });

  test('3. fetchCuisines() render bảng rỗng khi API trả []', async () => {
    fetch.mockResolvedValue({ ok: true, json: async () => [] });
    await window.fetchCuisines();
    expect(document.getElementById('cuisine-list-body').innerHTML).toBe('');
  });

  test('4. openAddModal() reset form và đổi tiêu đề modal', () => {
    document.getElementById('form-id').value = '123';
    document.getElementById('form-name').value = 'Old Name';

    window.openAddModal();

    expect(document.getElementById('form-id').value).toBe('');
    expect(document.getElementById('form-name').value).toBe('');
    expect(document.getElementById('modal-title').innerText).toBe('Thêm Cuisine');
    expect(document.getElementById('cuisineModal').style.display).toBe('flex');
  });

  test('5. handleAdd() thêm cuisine thành công: API POST, alert và reload', async () => {
    document.getElementById('form-name').value = 'Món mới';
    fetch.mockResolvedValue({ ok: true, json: async () => [] });

    await window.handleAdd();

    expect(fetch).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'POST' }));
    expect(alert).toHaveBeenCalledWith("Thêm thành công!");
    expect(window.mockReload).toHaveBeenCalled();
  });

  test('6. handleAdd() gửi đúng FormData có CuisineName', async () => {
    document.getElementById('form-name').value = 'Ý';
    fetch.mockResolvedValue({ ok: true, json: async () => [] });

    await window.handleAdd();

    const callArgs = fetch.mock.calls.find(c => c[1]?.method === 'POST');
    expect(callArgs[1].body.get('CuisineName')).toBe('Ý');
  });

  test('7. handleAdd() thất bại có message thì alert đúng message', async () => {
    fetch.mockResolvedValue({
      ok: false,
      json: async () => ({ message: 'Cuisine đã tồn tại' })
    });

    await window.handleAdd();

    expect(alert).toHaveBeenCalledWith(expect.stringContaining('Cuisine đã tồn tại'));
  });

  test('8. handleAdd() thất bại không có message thì alert "Thất bại"', async () => {
    fetch.mockResolvedValue({ ok: false, json: async () => ({}) });
    await window.handleAdd();
    expect(alert).toHaveBeenCalledWith(expect.stringContaining('Thất bại'));
  });

  test('9. openEditModal() đổ dữ liệu vào form và gán handleUpdate', () => {
    window.openEditModal(5, 'Trung Quốc', 'Unavailable');

    expect(document.getElementById('form-id').value).toBe('5');
    expect(document.getElementById('form-name').value).toBe('Trung Quốc');
    expect(document.getElementById('form-status').value).toBe('Unavailable');
    expect(document.getElementById('btn-submit').onclick).toBeDefined();
  });

  test('10. handleUpdate() thành công: API PUT, alert, đóng modal, reload', async () => {
    document.getElementById('form-id').value = '5';
    document.getElementById('form-name').value = 'Trung Hoa';
    document.getElementById('form-status').value = 'Available';
    fetch.mockResolvedValue({ ok: true, json: async () => ({ message: 'Xong' }) });

    await window.handleUpdate();

    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/5'), expect.objectContaining({ method: 'PUT' }));
    expect(alert).toHaveBeenCalledWith(expect.stringMatching(/Xong|Cập nhật thành công/));
    expect(window.mockReload).toHaveBeenCalled();
  });

  test('11. handleUpdate() gửi đúng FormData có CuisineName và Status', async () => {
    document.getElementById('form-id').value = '5';
    document.getElementById('form-name').value = 'Nhật';
    document.getElementById('form-status').value = 'Unavailable';
    fetch.mockResolvedValue({ ok: true, json: async () => [] });

    await window.handleUpdate();

    const putCall = fetch.mock.calls.find(c => c[1]?.method === 'PUT');
    expect(putCall[1].body.get('CuisineName')).toBe('Nhật');
    expect(putCall[1].body.get('Status')).toBe('Unavailable');
  });

  test('12. handleUpdate() thất bại có message báo lỗi từ server', async () => {
    document.getElementById('form-id').value = '99';
    fetch.mockResolvedValue({
      ok: false,
      json: async () => ({ message: 'Không tìm thấy cuisine' })
    });

    await window.handleUpdate();

    expect(alert).toHaveBeenCalledWith(expect.stringContaining('Không tìm thấy cuisine'));
  });

  test('13. handleUpdate() fetch bị reject thì alert lỗi kết nối', async () => {
    fetch.mockRejectedValue(new Error('Down'));

    await window.handleUpdate();

    expect(alert).toHaveBeenCalledWith(expect.stringContaining('Lỗi kết nối server'));
  });

  test('14. handleDelete() bấm Cancel thì không gọi API', async () => {
    confirm.mockReturnValue(false);
    await window.handleDelete(1);
    expect(fetch).not.toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'DELETE' }));
  });

  test('15. handleDelete() bấm OK thành công: gọi DELETE, alert và reload bảng', async () => {
    confirm.mockReturnValue(true);
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Đã xóa' }) });
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });

    await window.handleDelete(1);

    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/1'), expect.objectContaining({ method: 'DELETE' }));
    expect(alert).toHaveBeenCalledWith(expect.stringMatching(/Đã xóa|Đã xóa xong/));
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  test('16. handleDelete() API lỗi thì báo lỗi cụ thể', async () => {
    confirm.mockReturnValue(true);
    fetch.mockResolvedValue({
      ok: false,
      json: async () => ({ message: 'Không thể xóa' })
    });

    await window.handleDelete(1);

    expect(alert).toHaveBeenCalledWith(expect.stringContaining('Không thể xóa'));
  });

  test('17. closeModal() ẩn modal', () => {
    const modal = document.getElementById('cuisineModal');
    modal.style.display = 'flex';
    window.closeModal();
    expect(modal.style.display).toBe('none');
  });

  test('18. finishAction() đóng modal và reload bảng', () => {
    window.finishAction();
    expect(document.getElementById('cuisineModal').style.display).toBe('none');
    expect(fetch).toHaveBeenCalled();
  });

  test('19. handleLogout() bấm OK thì xóa token', () => {
    confirm.mockReturnValue(true);
    window.handleLogout();
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
  });

  test('20. handleLogout() bấm Cancel thì không xóa token', () => {
    confirm.mockReturnValue(false);
    window.handleLogout();
    expect(localStorageMock.removeItem).not.toHaveBeenCalled();
  });
});
