/**
 * Unit Test cho Restaurant Menu Management (res_menu_mgmt.js)
 * Sử dụng Jest + JSDOM
 */

const fs = require('fs');
const path = require('path');

// Mock các hàm toàn cục
global.fetch = jest.fn();
global.alert = jest.fn();
global.confirm = jest.fn();
global.prompt = jest.fn();
global.console.error = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
    let store = { 'token': 'mock-token', 'role': 'STAFF' };
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
        removeItem: jest.fn((key) => { delete store[key]; }),
        clear: jest.fn(() => { store = { 'token': 'mock-token', 'role': 'STAFF' }; }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Kiểm thử Restaurant Menu Management', () => {
    const baseHTML = `
        <div id="menuContainer"></div>
        <div id="addFoodForm" style="display: none;"></div>
        <input id="name" value="" />
        <input id="price" value="" />
        <input id="image" value="" />
        <input id="category" value="" />
        <input id="editImageInput" type="file" />
    `;

    beforeEach(() => {
        document.body.innerHTML = baseHTML;
        jest.clearAllMocks();
        fetch.mockReset();
        localStorageMock.clear();

        // Reset implementation to default
        localStorageMock.getItem.mockImplementation((key) => {
            if (key === 'token') return 'mock-token';
            if (key === 'role') return 'STAFF';
            return null;
        });

        // Mặc định fetch trả về mảng rỗng
        fetch.mockResolvedValue({
            ok: true,
            json: async () => []
        });

        // Đọc và thực thi script
        const scriptPath = path.resolve(__dirname, '../static/js/res_menu_mgmt.js');
        let scriptCode = fs.readFileSync(scriptPath, 'utf8');

        scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
        scriptCode = scriptCode.replace(/loadMenu\(\);?\s*$/, '');

        scriptCode += `
            window.loadMenu = loadMenu;
            window.renderMenu = renderMenu;
            window.addFood = addFood;
            window.deleteFood = deleteFood;
            window.editFood = editFood;
            window.toggleAddForm = toggleAddForm;
            window.handleLogout = handleLogout;
        `;

        eval(scriptCode);
    });

    const flushPromises = () => new Promise(resolve => setTimeout(resolve, 50));

    // --- LOAD MENU ---
    test('1. loadMenu() không có token báo lỗi', async () => {
        localStorageMock.getItem.mockReturnValueOnce(null);
        await window.loadMenu();
        expect(alert).toHaveBeenCalledWith("Bạn chưa đăng nhập!");
    });

    test('2. loadMenu() thành công gọi API và render', async () => {
        const mockData = [{ id: 1, name: 'Phở', price: 50000, Visible: true }];
        fetch.mockResolvedValue({ ok: true, json: async () => mockData });

        await window.loadMenu();

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/menu/admin'), expect.any(Object));
        expect(document.getElementById('menuContainer').innerHTML).toContain('Phở');
    });

    test('3. loadMenu() lỗi 401/403 báo hết hạn', async () => {
        fetch.mockResolvedValue({ ok: false, status: 401 });
        await window.loadMenu();
        expect(alert).toHaveBeenCalledWith(expect.stringContaining("phiên đăng nhập đã hết hạn"));
    });

    test('4. loadMenu() lỗi khác ghi console', async () => {
        fetch.mockResolvedValue({ ok: false, status: 500 });
        await window.loadMenu();
        expect(console.error).toHaveBeenCalled();
    });

    // --- RENDER MENU ---
    test('5. renderMenu() hiển thị đủ thông tin món', () => {
        const data = [{ id: 'f1', name: 'Món A', price: 10000, image: 'img.png', visible: true }];
        window.renderMenu(data);
        const container = document.getElementById('menuContainer');
        expect(container.innerHTML).toContain('Món A');
        expect(container.innerHTML).toContain('10.000');
        expect(container.querySelector('img').src).toContain('img.png');
    });

    test('6. renderMenu() dùng placeholder nếu không có ảnh', () => {
        window.renderMenu([{ id: 'f1', name: 'Món B', price: 0, image: '', visible: true }]);
        expect(document.querySelector('img').src).toContain('placeholder');
    });

    test('7. renderMenu() món hiển thị có opacity 1', () => {
        window.renderMenu([{ id: 'f1', name: 'Món C', price: 0, visible: true }]);
        expect(document.querySelector('.menu-item').style.opacity).toBe("1");
        expect(document.querySelector('.toggle-btn').textContent).toBe("Ẩn món");
    });

    test('8. renderMenu() món ẩn có opacity 0.4', () => {
        window.renderMenu([{ id: 'f1', name: 'Món D', price: 0, visible: false }]);
        expect(document.querySelector('.menu-item').style.opacity).toBe("0.4");
        expect(document.querySelector('.toggle-btn').textContent).toBe("Hiện món");
    });

    test('9. Click toggle visible gọi API và cập nhật UI', async () => {
        window.renderMenu([{ id: 'f1', name: 'Món E', price: 0, visible: true }]);
        fetch.mockResolvedValue({ ok: true, json: async () => ({ visible: false }) });

        const btn = document.querySelector('.toggle-btn');
        btn.click();
        await flushPromises();

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/f1/toggle'), expect.objectContaining({ method: 'PUT' }));
        expect(document.querySelector('.menu-item').style.opacity).toBe("0.4");
        expect(btn.textContent).toBe("Hiện món");
    });

    test('10. Click toggle visible thất bại báo lỗi', async () => {
        window.renderMenu([{ id: 'f1', name: 'Món E', price: 0, visible: true }]);
        fetch.mockResolvedValue({ ok: false });
        document.querySelector('.toggle-btn').click();
        await flushPromises();
        expect(alert).toHaveBeenCalledWith("Thao tác thất bại!");
    });

    // --- ADD FOOD ---
    test('11. addFood() thiếu tên/giá báo lỗi', async () => {
        document.getElementById('name').value = '';
        await window.addFood();
        expect(alert).toHaveBeenCalledWith("Vui lòng nhập tên món và giá!");
    });

    test('12-13. addFood() thành công gọi API POST JSON và reset form', async () => {
        document.getElementById('name').value = 'Phở';
        document.getElementById('price').value = '50000';
        document.getElementById('category').value = 'Main';
        fetch.mockResolvedValue({ ok: true, json: async () => ({ id: 2 }) });

        await window.addFood();

        const call = fetch.mock.calls.find(c => c[1]?.method === 'POST');
        const body = JSON.parse(call[1].body);
        expect(body.name).toBe('Phở');
        expect(body.price).toBe(50000);
        expect(alert).toHaveBeenCalledWith("Thêm món thành công!");
        expect(document.getElementById('name').value).toBe('');
    });

    test('14. addFood() API lỗi báo lỗi', async () => {
        document.getElementById('name').value = 'A'; document.getElementById('price').value = '10';
        fetch.mockResolvedValue({ ok: false, text: async () => 'Error' });
        await window.addFood();
        expect(alert).toHaveBeenCalledWith(expect.stringContaining("Thêm thất bại"));
    });

    test('15. addFood() reject báo lỗi kết nối', async () => {
        document.getElementById('name').value = 'A'; document.getElementById('price').value = '10';
        fetch.mockRejectedValue(new Error('Network Fail'));
        await window.addFood();
        expect(alert).toHaveBeenCalledWith("Lỗi kết nối server!");
    });

    // --- DELETE FOOD ---
    test('16. deleteFood() Cancel không gọi API', async () => {
        confirm.mockReturnValue(false);
        await window.deleteFood(123);
        expect(fetch).not.toHaveBeenCalled();
    });

    test('17. deleteFood() OK thành công load lại menu', async () => {
        confirm.mockReturnValue(true);
        fetch.mockResolvedValue({ ok: true });
        await window.deleteFood(123);
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/123'), expect.objectContaining({ method: 'DELETE' }));
    });

    test('18. deleteFood() lỗi báo lỗi', async () => {
        confirm.mockReturnValue(true);
        fetch.mockResolvedValue({ ok: false });
        await window.deleteFood(123);
        expect(alert).toHaveBeenCalledWith("Xoá thất bại");
    });

    // --- EDIT FOOD ---
    test('19. editFood() Cancel prompt không làm gì', async () => {
        prompt.mockReturnValue(null);
        await window.editFood('f1', 'A', 10);
        expect(fetch).not.toHaveBeenCalled();
    });

    test('20. editFood() dữ liệu rỗng/sai báo lỗi', async () => {
        prompt.mockReturnValueOnce('').mockReturnValueOnce('abc');
        await window.editFood('f1', 'A', 10);
        expect(alert).toHaveBeenCalledWith("Dữ liệu không hợp lệ!");
    });

    test('21. editFood() sửa không đổi ảnh dùng FormData không có image', async () => {
        prompt.mockReturnValueOnce('Tên mới').mockReturnValueOnce('20000');
        confirm.mockReturnValueOnce(false);
        fetch.mockResolvedValue({ ok: true });

        await window.editFood('f1', 'A', 10000);

        const call = fetch.mock.calls.find(c => c[1]?.method === 'PUT');
        expect(call[1].body.get('name')).toBe('Tên mới');
        expect(call[1].body.get('image')).toBeNull();
    });

    test('22-23. editFood() sửa có đổi ảnh và thành công', async () => {
        prompt.mockReturnValueOnce('Tên mới').mockReturnValueOnce('20000');
        confirm.mockReturnValueOnce(true);
        fetch.mockResolvedValue({ ok: true });

        const mockFile = new File([''], 'new.jpg', { type: 'image/jpeg' });
        const fileInput = document.getElementById('editImageInput');

        const editPromise = window.editFood('f1', 'A', 10000);

        Object.defineProperty(fileInput, 'files', { value: [mockFile] });
        fileInput.onchange();

        await editPromise;

        const call = fetch.mock.calls.find(c => c[1]?.method === 'PUT');
        expect(call[1].body.get('image')).not.toBeNull();
        expect(alert).toHaveBeenCalledWith("Sửa thành công");
    });

    test('24. editFood() lỗi báo thất bại', async () => {
        prompt.mockReturnValueOnce('A').mockReturnValueOnce('1');
        confirm.mockReturnValueOnce(false);
        fetch.mockResolvedValue({ ok: false });
        await window.editFood('f1', 'A', 10);
        expect(alert).toHaveBeenCalledWith("Sửa thất bại");
    });

    // ---  UI & LOGOUT ---
    test('25. toggleAddForm() hiển thị form', () => {
        const form = document.getElementById('addFoodForm');
        form.style.display = 'none';
        window.toggleAddForm();
        expect(form.style.display).toBe('block');
    });

    test('26. toggleAddForm() ẩn form', () => {
        const form = document.getElementById('addFoodForm');
        form.style.display = 'block';
        window.toggleAddForm();
        expect(form.style.display).toBe('none');
    });

    test('27. handleLogout() Cancel không xóa storage', () => {
        confirm.mockReturnValue(false);
        window.handleLogout();
        expect(localStorageMock.removeItem).not.toHaveBeenCalled();
    });

    test('28. handleLogout() OK xóa token/role', () => {
        confirm.mockReturnValue(true);
        window.handleLogout();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('role');
    });
});
