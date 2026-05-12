/**
 * Unit Test cho chức năng Admin User (admin_users.js)
 * Sử dụng Jest + JSDOM
 */

const fs = require('fs');
const path = require('path');

// Mock các hàm toàn cục
global.fetch = jest.fn();
global.alert = jest.fn();
global.confirm = jest.fn();
global.console.error = jest.fn();
global.console.warn = jest.fn();

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

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('Kiểm thử Admin User Frontend', () => {
    beforeEach(() => {
        // Thiết lập DOM giả lập
        document.body.innerHTML = `
            <table id="user-list-table">
                <tbody id="user-list-body"></tbody>
            </table>
            
            <div id="userModal" style="display: none;">
                <h2 id="user-title"></h2>
                <input type="hidden" id="form-id" />
                <input id="user-field-name" value="testname" />
                <input id="user-field-email" value="test@mail.com" />
                <input id="user-field-phone" value="123" />
                <select id="user-field-role">
                    <option value="CUSTOMER">Customer</option>
                    <option value="STAFF">Staff</option>
                    <option value="ADMIN">Admin</option>
                </select>
                
                <div id="restaurant-select-group" style="display: none;">
                    <select id="user-field-restaurant">
                        <option value="">-- Chọn nhà hàng --</option>
                    </select>
                </div>
                
                <button id="button-submit">Lưu</button>
            </div>
        `;

        // Reset các mock
        jest.clearAllMocks();
        fetch.mockReset(); 
        
        // Mặc định fetch trả về mảng rỗng để tránh lỗi .json() hoặc .map()
        fetch.mockResolvedValue({
            ok: true,
            json: async () => []
        });

        localStorageMock.clear();
        window.location.href = '';

        // Đọc và thực thi script
        const scriptPath = path.resolve(__dirname, '../static/js/admin_users.js');
        let scriptCode = fs.readFileSync(scriptPath, 'utf8');
        
        scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
        
        scriptCode += `
            window.fetchUsers = fetchUsers;
            window.fetchRestaurants = fetchRestaurants;
            window.updateUser = updateUser;
            window.handleDelete = handleDelete;
            window.handleSaveUser = handleSaveUser;
            window.openAddModal = openAddModal;
            window.openEditModal = openEditModal;
            window.closeUserEntry = closeUserEntry;
            window.handleLogout = handleLogout;
        `;
        
        eval(scriptCode);
    });

    const flushPromises = () => new Promise(resolve => setTimeout(resolve, 100));

    test('1. fetchUsers() gọi API GET kèm token Authorization', async () => {
        await window.fetchUsers();
        expect(fetch).toHaveBeenCalledWith(
            'http://127.0.0.1:5000/api/v1/admin/users',
            expect.objectContaining({
                headers: { 'Authorization': 'Bearer mock-token' }
            })
        );
    });

    test('2. fetchUsers() hiển thị danh sách user lên bảng', async () => {
        const mockUsers = [
            { id: 1, username: 'user1', email: 'u1@test.com', phone: '0987', role: 'ADMIN' }
        ];
        fetch.mockResolvedValue({ ok: true, json: async () => mockUsers });

        await window.fetchUsers();

        const tbody = document.getElementById('user-list-body');
        expect(tbody.innerHTML).toContain('user1');
        expect(tbody.innerHTML).toContain('ADMIN');
    });

    test('3. User không có phone thì hiển thị "Chưa có số"', async () => {
        const mockUsers = [{ id: 1, username: 'u1', email: 'e', phone: null, role: 'ADMIN' }];
        fetch.mockResolvedValue({ ok: true, json: async () => mockUsers });

        await window.fetchUsers();

        expect(document.getElementById('user-list-body').innerHTML).toContain('Chưa có số');
    });

    test('4. fetchRestaurants() gọi đúng API danh sách nhà hàng', async () => {
        await window.fetchRestaurants();
        expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:5000/api/v1/restaurants/list');
    });

    test('5. fetchRestaurants() đổ danh sách nhà hàng vào dropdown', async () => {
        const mockRes = [{ id: 10, name: 'Res A' }];
        fetch.mockResolvedValue({ ok: true, json: async () => mockRes });

        await window.fetchRestaurants();

        const select = document.getElementById('user-field-restaurant');
        expect(select.options.length).toBe(2); 
        expect(select.options[1].textContent).toBe('Res A');
    });

    test('6. Đổi role sang STAFF thì hiện dropdown và gọi fetchRestaurants', async () => {
        const roleSelect = document.getElementById('user-field-role');
        roleSelect.value = 'STAFF';
        roleSelect.dispatchEvent(new window.Event('change'));

        expect(document.getElementById('restaurant-select-group').style.display).toBe('block');
        expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:5000/api/v1/restaurants/list');
    });

    test('7. Đổi role sang CUSTOMER thì ẩn dropdown nhà hàng', async () => {
        const roleSelect = document.getElementById('user-field-role');
        roleSelect.value = 'CUSTOMER';
        roleSelect.dispatchEvent(new window.Event('change'));

        expect(document.getElementById('restaurant-select-group').style.display).toBe('none');
    });

    test('8. openEditModal() CUSTOMER: mở modal, đổ data, ẩn chọn nhà hàng', async () => {
        await window.openEditModal(1, 'u1', 'e1', 'p1', 'CUSTOMER', null);

        expect(document.getElementById('userModal').style.display).toBe('flex');
        expect(document.getElementById('user-field-name').value).toBe('u1');
        expect(document.getElementById('restaurant-select-group').style.display).toBe('none');
    });

    test('9. openEditModal() STAFF: mở modal, hiện chọn nhà hàng và chọn đúng ID', async () => {
        fetch.mockResolvedValue({ ok: true, json: async () => [{ id: 5, name: 'Res 5' }] });
        
        await window.openEditModal(1, 'u1', 'e1', 'p1', 'STAFF', 5);

        expect(document.getElementById('restaurant-select-group').style.display).toBe('block');
        expect(document.getElementById('user-field-restaurant').value).toBe('5');
    });

    test('10. updateUser() CUSTOMER thành công: gọi API, alert, đóng modal, reload', async () => {
        document.getElementById('form-id').value = '1';
        document.getElementById('user-field-role').value = 'CUSTOMER';
        fetch.mockResolvedValue({ ok: true, json: async () => [] });

        await window.updateUser(1);

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/1'), expect.objectContaining({ method: 'PUT' }));
        expect(alert).toHaveBeenCalledWith("Cập nhật thành công!");
    });

    test('11. updateUser() STAFF chưa chọn nhà hàng thì báo lỗi và dừng lại', async () => {
        document.getElementById('user-field-role').value = 'STAFF';
        document.getElementById('user-field-restaurant').value = '';

        await window.updateUser(1);

        expect(alert).toHaveBeenCalledWith("Vui lòng chọn nhà hàng cho STAFF!");
        expect(fetch).not.toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'PUT' }));
    });

    test('12. updateUser() STAFF có nhà hàng thì FormData có RestaurantID', async () => {
        document.getElementById('user-field-role').value = 'STAFF';
        
        // Thêm option vào select để có thể gán value hợp lệ trong JSDOM
        const select = document.getElementById('user-field-restaurant');
        const opt = document.createElement('option');
        opt.value = '10';
        select.appendChild(opt);
        select.value = '10';
        
        fetch.mockResolvedValue({ ok: true, json: async () => [] });

        await window.updateUser(1);

        const putCall = fetch.mock.calls.find(c => c[1]?.method === 'PUT');
        expect(putCall).toBeDefined();
        expect(putCall[1].body.get('RestaurantID')).toBe('10');
    });

    test('13. updateUser() API lỗi thì hiển thị thông báo lỗi', async () => {
        document.getElementById('user-field-role').value = 'CUSTOMER';
        fetch.mockResolvedValue({
            ok: false,
            json: async () => ({ message: 'Email đã tồn tại' })
        });

        await window.updateUser(1);

        expect(alert).toHaveBeenCalledWith(expect.stringContaining('Email đã tồn tại'));
    });

    test('14. handleDelete() bấm Cancel thì không gọi API', async () => {
        confirm.mockReturnValue(false);
        await window.handleDelete(1);
        expect(fetch).not.toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ method: 'DELETE' }));
    });

    test('15. handleDelete() bấm OK thì gọi API DELETE và reload', async () => {
        confirm.mockReturnValue(true);
        fetch.mockResolvedValue({ ok: true, json: async () => [] });

        await window.handleDelete(1);

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/1'), expect.objectContaining({ method: 'DELETE' }));
        expect(fetch).toHaveBeenCalledTimes(2); 
    });

    test('16. handleSaveUser() có ID thì gọi updateUser', async () => {
        document.getElementById('form-id').value = '123';
        document.getElementById('user-field-role').value = 'CUSTOMER';
        fetch.mockResolvedValue({ ok: true, json: async () => [] });

        window.handleSaveUser();

        await flushPromises();
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/123'), expect.objectContaining({ method: 'PUT' }));
    });

    test('17. handleSaveUser() không có ID thì báo lỗi', () => {
        document.getElementById('form-id').value = '';
        window.handleSaveUser();
        expect(alert).toHaveBeenCalledWith(expect.stringContaining("Không xác định được người dùng"));
    });

    test('18. closeUserEntry() ẩn modal', () => {
        const modal = document.getElementById('userModal');
        modal.style.display = 'flex';
        window.closeUserEntry();
        expect(modal.style.display).toBe('none');
    });

    test('19. handleLogout() bấm Cancel thì không xóa token', () => {
        confirm.mockReturnValue(false);
        window.handleLogout();
        expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    });

    test('20. handleLogout() bấm OK thì xóa token', () => {
        confirm.mockReturnValue(true);
        window.handleLogout();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });
});