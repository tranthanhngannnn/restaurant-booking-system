const fs = require('fs');
const path = require('path');

// Mock các hàm toàn cục
global.fetch = jest.fn();
global.alert = jest.fn();
global.console.error = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => { store[key] = value ? value.toString() : ""; }),
        clear: jest.fn(() => { store = {}; }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('Kiểm thử Register Frontend', () => {
    beforeEach(() => {
        // Thiết lập DOM giả lập
        document.body.innerHTML = `
            <form id="registerForm">
                <input id="username" name="username" value="testuser" />
                <input id="pass" name="password" value="123456" />
                <input id="confirm_pass" value="123456" />
                <select id="roleSelect" name="role">
                    <option value="CUSTOMER">Customer</option>
                    <option value="STAFF">Staff</option>
                </select>
                <div id="restaurantDiv" style="display: none;">
                    <select id="restaurantSelect" name="restaurant_id">
                        <option value="">-- Chọn nhà hàng --</option>
                    </select>
                </div>
                <button type="submit">Đăng ký</button>
            </form>
        `;

        // Reset các mock
        jest.clearAllMocks();
        fetch.mockClear();
        global.console.error.mockClear();
        window.location.href = '';

        // Đọc script
        const scriptPath = path.resolve(__dirname, '../static/js/auth_register.js');
        let scriptCode = fs.readFileSync(scriptPath, 'utf8');

        /**
         * HACK: Thay const/let bằng var để cho phép khai báo lại nhiều lần trong JSDOM 
         * khi chạy nhiều test case (tránh lỗi Identifier already declared).
         */
        scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');

        // Đăng ký hàm vào scope global để test có thể gọi
        scriptCode += "\nwindow.toggleRestaurantDropdown = toggleRestaurantDropdown;";

        // Thực thi script
        // Dùng eval đơn giản vì ta đã xử lý việc cho phép khai báo lại bằng var
        eval(scriptCode);
    });

    const flushPromises = () => new Promise(resolve => setTimeout(resolve, 100));

    test('1. Chặn reload trang khi submit (preventDefault)', async () => {
        const form = document.getElementById('registerForm');
        const event = new window.Event('submit', { cancelable: true });
        const spy = jest.spyOn(event, 'preventDefault');

        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ message: 'Success' })
        });

        form.dispatchEvent(event);
        expect(spy).toHaveBeenCalled();
    });

    test('2. Mật khẩu không khớp báo lỗi và không gọi API', async () => {
        document.getElementById('confirm_pass').value = "wrong_pass";
        const form = document.getElementById('registerForm');

        form.dispatchEvent(new window.Event('submit'));

        expect(alert).toHaveBeenCalledWith("Mật khẩu xác nhận không khớp!");
        expect(fetch).not.toHaveBeenCalled();
    });

    test('3. Dữ liệu hợp lệ thì gọi API registerRequest', async () => {
        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({})
        });

        form.dispatchEvent(new window.Event('submit'));

        expect(fetch).toHaveBeenCalledWith(
            'http://127.0.0.1:5000/api/v1/auth/registerRequest',
            expect.objectContaining({
                method: 'POST',
                body: expect.any(FormData)
            })
        );
    });

    test('4. Đăng ký thành công hiển thị alert thông báo', async () => {
        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({})
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Chúc mừng! Đăng ký thành công.");
    });

    test('5. Backend trả lỗi có message thì hiển thị đúng message đó', async () => {
        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({
            ok: false,
            json: async () => ({ message: 'Username đã tồn tại' })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Lỗi đăng ký: Username đã tồn tại");
    });

    test('6. Backend trả lỗi không có message thì hiển thị message mặc định', async () => {
        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({
            ok: false,
            json: async () => ({})
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Lỗi đăng ký: Vui lòng kiểm tra lại");
    });

    test('7. Lỗi network khi fetch thì hiển thị thông báo lỗi kết nối', async () => {
        const form = document.getElementById('registerForm');
        fetch.mockRejectedValue(new Error('Network error'));

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Không kết nối được với Server Flask! Hãy chắc chắn Backend đang chạy.");
        expect(global.console.error).toHaveBeenCalled();
    });

    test('8. Role STAFF có chọn nhà hàng thì FormData phải chứa restaurant_id', async () => {
        document.getElementById('roleSelect').value = "STAFF";
        const resSelect = document.getElementById('restaurantSelect');
        const option = document.createElement("option");
        option.value = "res_123";
        option.textContent = "Nhà hàng A";
        resSelect.appendChild(option);
        resSelect.value = "res_123";

        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({ ok: true, json: async () => ({}) });

        form.dispatchEvent(new window.Event('submit'));

        const callArgs = fetch.mock.calls[0][1];
        const sentFormData = callArgs.body;
        expect(sentFormData.get('restaurant_id')).toBe("res_123");
    });

    test('9. Role CUSTOMER thì FormData không được chứa restaurant_id', async () => {
        document.getElementById('roleSelect').value = "CUSTOMER";
        document.getElementById('restaurantSelect').value = "some_id";

        const form = document.getElementById('registerForm');
        fetch.mockResolvedValue({ ok: true, json: async () => ({}) });

        form.dispatchEvent(new window.Event('submit'));

        const callArgs = fetch.mock.calls[0][1];
        const sentFormData = callArgs.body;
        expect(sentFormData.get('restaurant_id')).toBeNull();
    });

    test('10. toggleRestaurantDropdown STAFF thì hiện div nhà hàng', async () => {
        document.getElementById('roleSelect').value = "STAFF";

        await window.toggleRestaurantDropdown();

        expect(document.getElementById('restaurantDiv').style.display).toBe('block');
    });

    test('11. toggleRestaurantDropdown CUSTOMER thì ẩn div và xóa giá trị select', async () => {
        const resSelect = document.getElementById('restaurantSelect');
        resSelect.value = "old_val";
        document.getElementById('roleSelect').value = "CUSTOMER";

        await window.toggleRestaurantDropdown();

        expect(document.getElementById('restaurantDiv').style.display).toBe('none');
        expect(resSelect.value).toBe("");
    });

    test('12. STAFF gọi API lấy danh sách nhà hàng', async () => {
        document.getElementById('roleSelect').value = "STAFF";
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ([{ id: '1', name: 'Res A' }])
        });

        await window.toggleRestaurantDropdown();

        expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:5000/api/v1/restaurant/list");
        expect(document.getElementById('restaurantSelect').options.length).toBe(2);
    });

    test('13. Dropdown đã có dữ liệu thì không gọi lại API lần nữa', async () => {
        const select = document.getElementById('restaurantSelect');
        const opt = document.createElement("option");
        opt.value = "exist";
        select.appendChild(opt);

        document.getElementById('roleSelect').value = "STAFF";

        await window.toggleRestaurantDropdown();

        expect(fetch).not.toHaveBeenCalledWith("http://127.0.0.1:5000/api/v1/restaurant/list");
    });

    test('14. API nhà hàng lỗi thì log console.error và không crash', async () => {
        document.getElementById('roleSelect').value = "STAFF";
        fetch.mockRejectedValue(new Error("API Fail"));

        await window.toggleRestaurantDropdown();

        expect(global.console.error).toHaveBeenCalledWith("Không lấy được danh sách nhà hàng:", expect.any(Error));
        expect(document.getElementById('restaurantSelect').options.length).toBe(1);
    });
});
