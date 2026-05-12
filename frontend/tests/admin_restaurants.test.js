/**
 * Unit Test cho Admin Restaurant & Register Restaurant
 * Sử dụng Jest + JSDOM
 */

const fs = require('fs');
const path = require('path');

// Mock các hàm toàn cục
global.fetch = jest.fn();
global.alert = jest.fn();
global.confirm = jest.fn();
global.console.error = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = { 'token': 'mock-token', 'role': 'ADMIN' };
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
    removeItem: jest.fn((key) => { delete store[key]; }),
    clear: jest.fn(() => { store = { 'token': 'mock-token', 'role': 'ADMIN' }; }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock window.mockReload
window.mockReload = jest.fn();

describe('Kiểm thử Admin Restaurant & Register Restaurant', () => {

  const baseHTML = `
    <!-- Admin Restaurant HTML -->
    <div id="restaurant-admin-message" hidden></div>
    <div id="approvalModal" class="modal">
        <span id="approval-restaurant-name"></span>
        <span id="approval-restaurant-user"></span>
        <span id="approval-restaurant-cuisine"></span>
        <span id="approval-restaurant-status"></span>
        <textarea id="approval-note"></textarea>
        <button id="approvalApproveButton">Duyệt</button>
        <button id="approvalRejectButton">Từ chối</button>
    </div>

    <div id="appModalWrapper" class="modal">
        <h2 id="appModalTitle"></h2>
        <form id="appResForm">
            <input type="hidden" id="form-res-id" />
            <input id="res-name" name="RestaurantName" />
            <input id="res-address" name="Address" />
            <input id="res-phone" name="Phone" />
            <input id="res-email" name="Email" />
            <input id="res-open" name="Opentime" />
            <input id="res-close" name="Closetime" />
            <textarea id="res-desc" name="description"></textarea>
            <select id="res-status" name="status">
                <option value="Đang hoạt động">Đang hoạt động</option>
                <option value="Chờ duyệt">Chờ duyệt</option>
            </select>
            <div id="adminFieldContainer" style="display:none;">
                <select id="res-user" name="UserID"></select>
            </div>
            <select id="res-cuisine" name="CuisineID"></select>
            <button id="btn-save-res" type="submit">Lưu</button>
        </form>
    </div>

    <table><tbody id="res-list-body"></tbody></table>

    <!-- Register Restaurant HTML -->
    <div id="restaurant-page-message" hidden></div>
    <div id="restaurant-registration-panel" hidden></div>
    <form id="restaurant-register-form">
        <select id="register-restaurant-cuisine" name="CuisineID"></select>
        <button id="register-submit-button">Đăng ký</button>
        <button id="register-cancel-button">Hủy</button>
    </form>
    <button id="logoutButton">Logout</button>
    <button data-panel-target="register">Go Register</button>
    <button data-panel-target="tables">Go Tables</button>
  `;

  beforeEach(() => {
    document.body.innerHTML = baseHTML;
    jest.clearAllMocks();
    fetch.mockReset();
    localStorageMock.clear();
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'token') return 'mock-token';
      if (key === 'role') return 'ADMIN';
      return null;
    });
    window.mockReload.mockClear();

    fetch.mockResolvedValue({
      ok: true,
      json: async () => []
    });
  });

  const flushPromises = () => new Promise(resolve => setTimeout(resolve, 50));

  // --- PHẦN 1: ADMIN RESTAURANT (restaurants.js) ---
  describe('Admin Restaurant Logic (restaurants.js)', () => {
    beforeEach(() => {
      const scriptPath = path.resolve(__dirname, '../static/js/restaurants.js');
      let scriptCode = fs.readFileSync(scriptPath, 'utf8');
      scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
      scriptCode = scriptCode.replace(/location\.reload\(\)/g, 'window.mockReload()');
      scriptCode += `
        window.loadDropdowns = loadDropdowns; window.fetchRestaurants = fetchRestaurants;
        window.handleResponse = handleResponse; window.handleLogout = handleLogout;
        window.openResModal = openResModal; window.addRestaurant = addRestaurant;
        window.updateRestaurant = updateRestaurant; window.renderStatusCell = renderStatusCell;
        window.submitApproval = submitApproval; window.prepareEdit = prepareEdit;
        window.prepareAdd = prepareAdd; window.handleDelete = handleDelete;
        window.openApprovalModal = openApprovalModal;
      `;
      eval(scriptCode);
    });

    test('1. loadDropdowns(): ADMIN load thêm danh sách chủ nhà hàng', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [{ id: 1, name: 'Cuisine 1' }] });
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [{ id: 10, username: 'Owner A' }] });
      await window.loadDropdowns();
      expect(document.getElementById('res-user').innerHTML).toContain('Owner A');
    });

    test('2. fetchRestaurants(): Gọi đúng API GET kèm token', async () => {
      await window.fetchRestaurants();
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/admin/restaurants'), expect.objectContaining({
        headers: expect.objectContaining({ 'Authorization': 'Bearer mock-token' })
      }));
    });

    test('3. fetchRestaurants(): Hiển thị đúng danh sách lên bảng', async () => {
      fetch.mockResolvedValue({ ok: true, json: async () => [{ RestaurantID: 1, RestaurantName: 'Res A', status: 'Active' }] });
      await window.fetchRestaurants();
      expect(document.getElementById('res-list-body').innerHTML).toContain('Res A');
    });

    test('4. prepareAdd(): Reset form, title Đăng ký, status mặc định, mở modal', () => {
      document.getElementById('form-res-id').value = '5';
      window.prepareAdd();
      expect(document.getElementById('form-res-id').value).toBe('');
      expect(document.getElementById('appModalTitle').innerText).toBe('Đăng ký Nhà Hàng');
      expect(document.getElementById('res-status').value).toBe('Đang hoạt động');
      expect(document.getElementById('appModalWrapper').classList.contains('is-visible')).toBe(true);
    });

    test('5. openResModal(): ADMIN thấy field chọn chủ nhà hàng', () => {
      window.openResModal();
      expect(document.getElementById('adminFieldContainer').style.display).toBe('flex');
    });

    test('6. openResModal(): Role khác ADMIN ẩn field chọn chủ', () => {
      localStorageMock.getItem.mockImplementation(k => k === 'role' ? 'STAFF' : 'mock-token');
      const scriptPath = path.resolve(__dirname, '../static/js/restaurants.js');
      let scriptCode = fs.readFileSync(scriptPath, 'utf8');
      scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
      scriptCode += `window.openResModal = openResModal;`;
      eval(scriptCode);
      window.openResModal();
      expect(document.getElementById('adminFieldContainer').style.display).toBe('none');
    });

    test('7. appResForm onsubmit: id="" gọi addRestaurant (kiểm tra qua API POST)', async () => {
      document.getElementById('form-res-id').value = '';
      document.getElementById('res-name').value = 'New Res';
      fetch.mockResolvedValue({ ok: true, json: async () => ({ message: 'Thêm thành công!' }) });

      const form = document.getElementById('appResForm');
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flushPromises();

      expect(fetch).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'POST' }));
    });

    test('8. addRestaurant(): Thành công hiện message, đóng modal, reload', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Thêm thành công!' }) });
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
      await window.addRestaurant(new FormData());
      expect(document.getElementById('restaurant-admin-message').textContent).toContain('Thêm nhà hàng thành công!');
    });

    test('9. appResForm onsubmit: id=1 gọi updateRestaurant (kiểm tra qua API PUT)', async () => {
      document.getElementById('form-res-id').value = '1';
      document.getElementById('res-name').value = 'Updated Name';
      fetch.mockResolvedValue({ ok: true, json: async () => ({ message: 'Cập nhật thành công!' }) });

      const form = document.getElementById('appResForm');
      form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      await flushPromises();

      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/1'), expect.objectContaining({ method: 'PUT' }));
    });

    test('10. updateRestaurant(): Thành công hiện message, đóng modal, reload', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Cập nhật thành công!' }) });
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
      await window.updateRestaurant(1, new FormData());
      expect(document.getElementById('restaurant-admin-message').textContent).toContain('Cập nhật nhà hàng thành công!');
    });

    test('11. handleResponse(): Xử lý lỗi khi API trả message lỗi', async () => {
      const res = { ok: false, json: async () => ({ message: 'Lỗi server' }) };
      await expect(window.handleResponse(res)).rejects.toThrow('Lỗi server');
    });

    test('12. prepareEdit(): Đổ dữ liệu hợp lệ vào form và mở modal', async () => {
      fetch.mockResolvedValue({ ok: true, json: async () => [{ RestaurantID: 5, RestaurantName: 'Res 5' }] });
      await window.fetchRestaurants();
      window.prepareEdit(5);
      expect(document.getElementById('res-name').value).toBe('Res 5');
      expect(document.getElementById('appModalTitle').innerText).toBe('Cập nhật Nhà Hàng');
    });

    test('13. handleDelete(): Hủy xóa khi bấm Cancel', async () => {
      confirm.mockReturnValue(false);
      await window.handleDelete(1);
      expect(fetch).not.toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'DELETE' }));
    });

    test('14. handleDelete(): Hiển thị lỗi khi xóa thất bại', async () => {
      confirm.mockReturnValue(true);
      fetch.mockResolvedValue({ ok: false, json: async () => ({ message: 'Không thể xóa' }) });
      await window.handleDelete(1);
      expect(document.getElementById('restaurant-admin-message').textContent).toContain('Không thể xóa');
    });

    test('15. renderStatusCell(): Chờ duyệt hiển thị nút Duyệt', () => {
      const html = window.renderStatusCell({ RestaurantID: 1, status: 'Chờ duyệt' });
      expect(html).toContain('openApprovalModal(1)');
    });

    test('16. openApprovalModal(): ID hợp lệ mở modal thông tin', async () => {
      fetch.mockResolvedValue({ ok: true, json: async () => [{ RestaurantID: 10, RestaurantName: 'Res 10' }] });
      await window.fetchRestaurants();
      window.openApprovalModal(10);
      expect(document.getElementById('approval-restaurant-name').textContent).toBe('Res 10');
      expect(document.getElementById('approvalModal').classList.contains('is-visible')).toBe(true);
    });

    test('17. openApprovalModal(): ID không tồn tại báo lỗi', () => {
      window.openApprovalModal(999);
      expect(document.getElementById('restaurant-admin-message').textContent).toContain('Không tìm thấy thông tin');
    });

    test('18. submitApproval(): Duyệt thành công gọi API approve', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [{ RestaurantID: 1 }] });
      await window.fetchRestaurants();
      window.openApprovalModal(1);
      fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Approved' }) });
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
      await window.submitApproval('approve');
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/approve'), expect.any(Object));
    });

    test('19. submitApproval(): Từ chối thành công gọi API reject', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [{ RestaurantID: 1 }] });
      await window.fetchRestaurants();
      window.openApprovalModal(1);
      fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Rejected' }) });
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
      await window.submitApproval('reject');
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/reject'), expect.any(Object));
    });

    test('20. submitApproval(): Lỗi thì hiện message và bật lại nút', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [{ RestaurantID: 1 }] });
      await window.fetchRestaurants();
      window.openApprovalModal(1);
      fetch.mockResolvedValue({ ok: false, json: async () => ({ message: 'Lỗi duyệt' }) });
      await window.submitApproval('approve');
      expect(document.getElementById('restaurant-admin-message').textContent).toContain('Lỗi duyệt');
      expect(document.getElementById('approvalApproveButton').disabled).toBe(false);
    });
  });

  // --- PHẦN 2: REGISTER RESTAURANT (register_restaurant.js) ---
  describe('Register Restaurant Logic (register_restaurant.js)', () => {
    beforeEach(() => {
      const scriptPath = path.resolve(__dirname, '../static/js/register_restaurant.js');
      let scriptCode = fs.readFileSync(scriptPath, 'utf8');
      scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
      scriptCode += `
        window.loadCuisines = loadCuisines; window.submitRestaurantRegistration = submitRestaurantRegistration;
        window.cancelRestaurantRegistration = cancelRestaurantRegistration;
        window.setActivePanel = setActivePanel; window.handleLogout = handleLogout;
      `;
      eval(scriptCode);
    });

    test('21. loadCuisines(): Đổ dữ liệu vào dropdown khi trang load', async () => {
      fetch.mockResolvedValue({ ok: true, json: async () => [{ id: 1, name: 'Cuisine A' }] });
      await window.loadCuisines();
      expect(document.getElementById('register-restaurant-cuisine').innerHTML).toContain('Cuisine A');
    });

    test('22. loadCuisines(): Lỗi hiện Không tải được dữ liệu', async () => {
      fetch.mockResolvedValue({ ok: false, json: async () => ({}) });
      await window.loadCuisines();
      expect(document.getElementById('register-restaurant-cuisine').innerHTML).toContain('Không tải được dữ liệu');
    });

    test('23. submitRestaurantRegistration(): preventDefault được gọi', async () => {
      const event = { preventDefault: jest.fn(), target: document.getElementById('restaurant-register-form') };
      await window.submitRestaurantRegistration(event);
      expect(event.preventDefault).toHaveBeenCalled();
    });

    test('24. submitRestaurantRegistration(): Không token báo lỗi chưa đăng nhập', async () => {
      localStorageMock.getItem.mockImplementation(k => null);
      const event = { preventDefault: jest.fn(), target: document.getElementById('restaurant-register-form') };
      await window.submitRestaurantRegistration(event);
      expect(document.getElementById('restaurant-page-message').textContent).toContain('Bạn chưa đăng nhập');
    });

    test('25. submitRestaurantRegistration(): Thành công reset form, hiện message', async () => {
      fetch.mockResolvedValue({ ok: true, json: async () => ({}) });
      const form = document.getElementById('restaurant-register-form');
      const spyReset = jest.spyOn(form, 'reset');
      await window.submitRestaurantRegistration({ preventDefault: jest.fn(), target: form });
      expect(spyReset).toHaveBeenCalled();
      expect(document.getElementById('restaurant-page-message').textContent).toContain('Đăng ký thành công');
    });

    test('26. submitRestaurantRegistration(): Lỗi hiện message từ server', async () => {
      fetch.mockResolvedValue({ ok: false, json: async () => ({ message: 'Trùng tên' }) });
      await window.submitRestaurantRegistration({ preventDefault: jest.fn(), target: document.getElementById('restaurant-register-form') });
      expect(document.getElementById('restaurant-page-message').textContent).toContain('Trùng tên');
    });

    test('27. cancelRestaurantRegistration(): Reset form, clear message, switch panel', () => {
      document.getElementById('restaurant-page-message').textContent = 'Old msg';
      window.cancelRestaurantRegistration();
      expect(document.getElementById('restaurant-page-message').textContent).toBe('');
    });

    test('28. handleLogout(): OK xóa token và chuyển trang', () => {
      confirm.mockReturnValue(true);
      window.handleLogout();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });

    test('29. handleLogout(): Cancel không xóa token', () => {
      confirm.mockReturnValue(false);
      window.handleLogout();
      expect(localStorageMock.removeItem).not.toHaveBeenCalledWith('token');
    });

    test('30. setActivePanel(): Chuyển panel đúng', () => {
      const panel = document.getElementById('restaurant-registration-panel');
      window.setActivePanel('register');
      expect(panel.hidden).toBe(false);
      window.setActivePanel('other');
      expect(panel.hidden).toBe(true);
    });
  });
});