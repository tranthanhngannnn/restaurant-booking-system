// Mock các hàm toàn cục trước khi chạy test
global.fetch = jest.fn();
global.alert = jest.fn();
global.console.error = jest.fn();
global.console.log = jest.fn();

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => {
            store[key] = (value === null || value === undefined) ? "" : value.toString();
        }),
        clear: jest.fn(() => { store = {}; }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock window.location đúng cách cho JSDOM
const mockLocation = {
    href: 'http://localhost/',
    assign: jest.fn((url) => { mockLocation.href = url; }),
    replace: jest.fn((url) => { mockLocation.href = url; }),
    toString: () => mockLocation.href
};
delete window.location;
window.location = mockLocation;

describe('Kiểm thử Login Frontend', () => {
    beforeEach(() => {
        // Thiết lập DOM giả lập
        document.body.innerHTML = `
            <form id="loginForm">
                <input name="username" value="admin" />
                <input name="password" value="123456" />
                <button type="submit">Đăng nhập</button>
            </form>
        `;

        // Reset tất cả các mock
        jest.clearAllMocks();
        fetch.mockClear();
        localStorageMock.clear();
        mockLocation.href = 'http://localhost/'; // Reset URL về mặc định
        global.console.error.mockClear();

        // Import file script cần test
        jest.isolateModules(() => {
            require('../static/js/auth_login.js');
        });
    });

    // Chờ xử lý async
    const flushPromises = () => new Promise(resolve => setTimeout(resolve, 300));

    test('1. Chặn reload trang khi submit form (preventDefault)', async () => {
        const form = document.querySelector('form');
        const event = new window.Event('submit', { cancelable: true });
        const spy = jest.spyOn(event, 'preventDefault');

        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ role: 'ADMIN', access_token: 't' })
        });

        form.dispatchEvent(event);
        expect(spy).toHaveBeenCalled();
    });

    test('2. Gọi đúng API POST /api/v1/auth/login', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ role: 'ADMIN', access_token: 't' })
        });

        form.dispatchEvent(new window.Event('submit'));

        expect(fetch).toHaveBeenCalledWith(
            'http://127.0.0.1:5000/api/v1/auth/login',
            expect.objectContaining({
                method: 'POST',
                body: expect.any(FormData)
            })
        );
    });

    test('3. ADMIN: lưu token, role, user_id khi đăng nhập thành công', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                access_token: 'token_admin',
                role: 'ADMIN',
                user_info: { id: 1 }
            })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(localStorage.setItem).toHaveBeenCalledWith('token', 'token_admin');
        expect(localStorage.setItem).toHaveBeenCalledWith('role', 'ADMIN');
        expect(localStorage.setItem).toHaveBeenCalledWith('user_id', 1);
        expect(alert).toHaveBeenCalledWith("Đăng nhập thành công!");
    });

    test('4. STAFF: lưu token, role, user_id khi đăng nhập thành công', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ 
                role: 'STAFF', 
                access_token: 'token_staff',
                user_info: { id: 2 }
            })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(localStorage.setItem).toHaveBeenCalledWith('token', 'token_staff');
        expect(localStorage.setItem).toHaveBeenCalledWith('role', 'STAFF');
        expect(localStorage.setItem).toHaveBeenCalledWith('user_id', 2);
        expect(alert).toHaveBeenCalledWith("Đăng nhập thành công!");
    });

    test('5. CUSTOMER: lưu token, role, user_id khi đăng nhập thành công', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ 
                role: 'CUSTOMER', 
                access_token: 'token_cus',
                user_info: { id: 3 }
            })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(localStorage.setItem).toHaveBeenCalledWith('token', 'token_cus');
        expect(localStorage.setItem).toHaveBeenCalledWith('role', 'CUSTOMER');
        expect(localStorage.setItem).toHaveBeenCalledWith('user_id', 3);
        expect(alert).toHaveBeenCalledWith("Đăng nhập thành công!");
    });

    test('6. Hiển thị alert khi đăng nhập thành công', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ role: 'ADMIN', access_token: 't' })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Đăng nhập thành công!");
    });

    test('7. Hiển thị lỗi khi API trả status 401 (Sai mật khẩu)', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: false,
            json: async () => ({ message: 'Sai tài khoản hoặc mật khẩu' })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Lỗi: Sai tài khoản hoặc mật khẩu");
    });

    test('8. Hiển thị lỗi mặc định khi API không trả về message', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: false,
            json: async () => ({}) // Trống message
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Lỗi: Đăng nhập thất bại");
    });

    test('9. Hiển thị lỗi khi gặp sự cố mạng (fetch bị reject)', async () => {
        const form = document.querySelector('form');
        fetch.mockRejectedValue(new Error('Network Error'));

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(alert).toHaveBeenCalledWith("Kiểm tra lại Flask đã chạy chưa!");
    });

    test('10. Lưu user_id vào localStorage sau khi thành công', async () => {
        const form = document.querySelector('form');
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                role: 'ADMIN',
                access_token: 't',
                user_info: { id: 99 }
            })
        });

        form.dispatchEvent(new window.Event('submit'));
        await flushPromises();

        expect(localStorage.setItem).toHaveBeenCalledWith('user_id', 99);
    });
});
