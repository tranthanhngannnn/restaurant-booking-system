/**
 * Unit Test cho Admin Report (admin_report.js)
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
    let store = { 'token': 'mock-token' };
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
        removeItem: jest.fn((key) => { delete store[key]; }),
        clear: jest.fn(() => { store = { 'token': 'mock-token' }; }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock window.mockReload
window.mockReload = jest.fn();

describe('Kiểm thử Admin Report Frontend', () => {
    beforeEach(() => {
        // Thiết lập DOM giả lập
        document.body.innerHTML = `
      <select id="restaurant_id">
        <option value="">Tất cả</option>
        <option value="1">Res 1</option>
        <option value="10">Res 10</option>
      </select>
      <input id="report_month" />
      <button id="loadReportBtn">Load</button>
      <div id="total_report"></div>
      <div id="total_6_months"></div>
      <div id="restaurant_count"></div>
      <div id="status_text"></div>
      <div id="status_note"></div>
      <div id="table_status"></div>
      <div id="table_caption"></div>
      <table>
        <thead id="report_table_head"></thead>
        <tbody id="report_table_body"></tbody>
      </table>
    `;

        // Reset các mock
        jest.clearAllMocks();
        fetch.mockReset();
        localStorageMock.clear();
        window.mockReload.mockClear();

        // Mặc định fetch trả về mảng rỗng
        fetch.mockResolvedValue({
            ok: true,
            json: async () => []
        });

        // Đọc và thực thi script
        const scriptPath = path.resolve(__dirname, '../static/js/admin_report.js');
        let scriptCode = fs.readFileSync(scriptPath, 'utf8');

        // Xử lý export và thay const/let bằng var
        scriptCode = scriptCode.replace(/export\s*\{[\s\S]*?\}\s*;?/g, '');
        scriptCode = scriptCode.replace(/\bconst\b /g, 'var ').replace(/\blet\b /g, 'var ');
        scriptCode = scriptCode.replace(/location\.reload\(\)/g, 'window.mockReload()');

        // Đảm bảo các hàm được gắn vào window
        scriptCode += `
      window.formatCurrency = formatCurrency;
      window.getCurrentMonthValue = getCurrentMonthValue;
      window.loadRestaurants = loadRestaurants;
      window.renderTable = renderTable;
      window.loadReport = loadReport;
      window.setLoadingState = setLoadingState;
      window.handleLogout = handleLogout;
    `;

        eval(scriptCode);
    });

    const flushPromises = () => new Promise(resolve => setTimeout(resolve, 50));

    test('1. formatCurrency() format 1.000.000đ', () => {
        const formatted = window.formatCurrency(1000000).replace(/\u00a0/g, ' ').replace(/\s/g, '');
        expect(formatted).toContain('1.000.000đ');
    });

    test('2. formatCurrency() với null/undefined trả 0đ', () => {
        expect(window.formatCurrency(null)).toBe('0đ');
        expect(window.formatCurrency(undefined)).toBe('0đ');
    });

    test('3. getCurrentMonthValue() trả đúng định dạng YYYY-MM', () => {
        const val = window.getCurrentMonthValue();
        expect(val).toMatch(/^\d{4}-\d{2}$/);
    });

    test('4. loadRestaurants() gọi API danh sách nhà hàng', async () => {
        await window.loadRestaurants();
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/admin/restaurants'));
    });

    test('5. loadRestaurants() đổ option vào dropdown', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => [{ RestaurantID: 1, RestaurantName: 'Nha Hang A' }]
        });
        await window.loadRestaurants();
        const select = document.getElementById('restaurant_id');
        expect(select.innerHTML).toContain('Tất cả nhà hàng');
        expect(select.innerHTML).toContain('Nha Hang A');
    });

    test('6. loadRestaurants() lỗi thì báo lỗi UI', async () => {
        fetch.mockRejectedValue(new Error('Fail'));
        await window.loadRestaurants();
        expect(document.getElementById('restaurant_id').innerHTML).toContain('Không tải được danh sách');
        expect(document.getElementById('status_text').textContent).toBe('Lỗi dữ liệu');
    });

    test('7. setLoadingState() cập nhật UI khi đang tải', () => {
        window.setLoadingState(true, 'Đang quét...');
        expect(document.getElementById('loadReportBtn').disabled).toBe(true);
        expect(document.getElementById('status_text').textContent).toBe('Đang quét...');
    });

    test('8. renderTable() render header bảng đúng cấu trúc', () => {
        const months = [{ label: 'Tháng 1' }, { label: 'Tháng 2' }];
        window.renderTable(months, []);
        const thead = document.getElementById('report_table_head');
        expect(thead.innerHTML).toContain('Nhà hàng');
        expect(thead.innerHTML).toContain('Tháng 1');
    });

    test('9. renderTable() render dữ liệu doanh thu', () => {
        const months = [{ label: 'T1' }];
        const data = [{
            restaurant_id: 1,
            restaurant_name: 'Res 1',
            selected_month_revenue: 100,
            total_6_months: 600,
            monthly_revenue: [{ revenue: 100 }]
        }];
        window.renderTable(months, data);
        const tbody = document.getElementById('report_table_body');
        expect(tbody.innerHTML).toContain('Res 1');
        expect(tbody.innerHTML).toContain('100đ');
    });

    test('10. renderTable() render dòng trống khi không có dữ liệu', () => {
        window.renderTable([], []);
        expect(document.getElementById('report_table_body').textContent).toContain('Không có dữ liệu doanh thu');
    });

    test('11. loadReport() không có token báo lỗi', async () => {
        localStorageMock.getItem.mockReturnValue(null);
        await window.loadReport();
        expect(document.getElementById('status_text').textContent).toBe('Chưa đăng nhập');
    });

    test('12. loadReport() thiếu tháng báo lỗi', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '';
        await window.loadReport();
        expect(document.getElementById('status_text').textContent).toBe('Thiếu tháng');
    });

    test('13. loadReport() gửi đúng FormData lên API', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        document.getElementById('restaurant_id').value = '10';
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'success', total_report: 0, months: [], restaurants: [] })
        });

        await window.loadReport();

        const call = fetch.mock.calls.find(c => c[1]?.method === 'POST');
        expect(call[1].body.get('report_month')).toBe('2024-05');
        expect(call[1].body.get('restaurant_id')).toBe('10');
    });

    test('14. loadReport() thành công cập nhật tổng quát', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        document.getElementById('restaurant_id').value = '';
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                status: 'success',
                total_report: 1000,
                total_6_months: 5000,
                restaurant_count: 3,
                months: [],
                restaurants: []
            })
        });

        await window.loadReport();

        const totalText = document.getElementById('total_report').textContent.replace(/\u00a0/g, ' ').replace(/\s/g, '');
        expect(totalText).toContain('1.000đ');
        expect(document.getElementById('restaurant_count').textContent).toBe('3');
    });

    test('15. loadReport() thành công cho 1 nhà hàng hiện caption chi tiết', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        document.getElementById('restaurant_id').value = '1';
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'success', months: [], restaurants: [] })
        });

        await window.loadReport();
        expect(document.getElementById('table_caption').textContent).toContain('chi tiết doanh thu của nhà hàng đã chọn');
    });

    test('16. loadReport() API trả error thì reset dữ liệu', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'error', message: 'Lỗi định dạng' })
        });

        await window.loadReport();
        const totalText = document.getElementById('total_report').textContent;
        expect(totalText).toBe('0đ');
        expect(document.getElementById('status_text').textContent).toBe('Lỗi kết nối');
    });

    test('17. loadReport() 401 báo lỗi kết nối', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        fetch.mockResolvedValue({ status: 401 });

        await window.loadReport();
        expect(document.getElementById('status_text').textContent).toBe('Lỗi kết nối');
    });

    test('18. loadReport() fetch bị reject báo lỗi kết nối', async () => {
        localStorageMock.getItem.mockReturnValue('valid-token');
        document.getElementById('report_month').value = '2024-05';
        fetch.mockRejectedValue(new Error('Network Error'));

        await window.loadReport();
        expect(document.getElementById('status_text').textContent).toBe('Lỗi kết nối');
        expect(document.getElementById('table_status').textContent).toBe('Tải thất bại');
    });

    test('19. window.onload khởi tạo dữ liệu (kiểm tra qua fetch)', async () => {
        fetch.mockReset();
        fetch.mockResolvedValue({ ok: true, json: async () => [] });

        await window.onload();

        expect(document.getElementById('report_month').value).toBe(window.getCurrentMonthValue());
        expect(fetch).toHaveBeenCalledTimes(2);
    });

    test('20. handleLogout() xóa token khi bấm OK', () => {
        confirm.mockReturnValue(true);
        window.handleLogout();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });
});
