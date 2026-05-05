const REPORT_API = 'http://127.0.0.1:5000/api/v1/admin/report';
const RESTAURANT_API = 'http://127.0.0.1:5000/api/v1/admin/restaurants';
const restaurantSelect = document.getElementById('restaurant_id');
const monthInput = document.getElementById('report_month');
const loadButton = document.getElementById('loadReportBtn');
const totalReportLabel = document.getElementById('total_report');
const totalSixMonthsLabel = document.getElementById('total_6_months');
const restaurantCountLabel = document.getElementById('restaurant_count');
const statusLabel = document.getElementById('status_text');
const statusNoteLabel = document.getElementById('status_note');
const tableStatusLabel = document.getElementById('table_status');
const tableCaption = document.getElementById('table_caption');
const tableHead = document.getElementById('report_table_head');
const tableBody = document.getElementById('report_table_body');

function formatCurrency(value) {
    return Number(value || 0).toLocaleString('vi-VN') + 'đ';
}

function getCurrentMonthValue() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    return year + '-' + month;
}

function setLoadingState(isLoading, message) {
    loadButton.disabled = isLoading;
    statusLabel.textContent = message;
    tableStatusLabel.textContent = message;
}

async function loadRestaurants() {
    try {
        const response = await fetch(RESTAURANT_API);
        const restaurants = await response.json();
        restaurantSelect.innerHTML = '<option value="">Tất cả nhà hàng</option>';

        restaurants.forEach((restaurant) => {
            const option = document.createElement('option');
            option.value = restaurant.RestaurantID;
            option.textContent = restaurant.RestaurantName;
            restaurantSelect.appendChild(option);
        });
    } catch (error) {
        restaurantSelect.innerHTML = '<option value="">Không tải được danh sách</option>';
        statusLabel.textContent = 'Lỗi dữ liệu';
        statusNoteLabel.textContent = 'Không thể tải danh sách nhà hàng.';
        console.error(error);
    }
}

function renderTable(months, restaurants) {
    // Tạo header cho bảng: Nhà hàng + Tháng chọn + Tổng 6 tháng + 6 tháng chi tiết
    const headCells = [
        '<th>Nhà hàng</th>',
        '<th>Tháng chọn</th>',
        '<th>Tổng 6 tháng</th>',
        ...months.map((month) => `<th>${month.label}</th>`)
    ];
    tableHead.innerHTML = headCells.join('');

    // Kiểm tra nếu không có dữ liệu doanh thu
    if (!restaurants.length) {
        tableBody.innerHTML = '<tr><td class="admin-report-empty" colspan="' + headCells.length + '">Không có dữ liệu doanh thu trong giai đoạn đã chọn.</td></tr>';
        return;
    }

    // Render danh sách nhà hàng theo thứ tự doanh thu từ cao xuống thấp
    // restaurants đã được sắp xếp ở BE theo total_6_months giảm dần
    tableBody.innerHTML = restaurants.map((restaurant, index) => {
        // Tạo các ô hiển thị doanh thu từng tháng
        const monthCells = restaurant.monthly_revenue.map((item) => {
            return `<td class="admin-report-money">${formatCurrency(item.revenue)}</td>`;
        }).join('');

        return `
            <tr>
                <td>
                    <div class="admin-report-restaurant-name">${restaurant.restaurant_name}</div>
                    <div class="admin-report-restaurant-sub">Chi nhánh #${restaurant.restaurant_id} · Top ${index + 1}</div>
                </td>
                <td class="admin-report-money">${formatCurrency(restaurant.selected_month_revenue)}</td>
                <td class="admin-report-money">${formatCurrency(restaurant.total_6_months)}</td>
                ${monthCells}
            </tr>
        `;
    }).join('');
}

async function loadReport() {
    // Lấy thông tin từ form
    const token = localStorage.getItem('token');
    const month = monthInput.value;
    const restaurantId = restaurantSelect.value;

    // Kiểm tra đăng nhập
    if (!token) {
        statusLabel.textContent = 'Chưa đăng nhập';
        statusNoteLabel.textContent = 'Không tìm thấy token admin trong localStorage.';
        tableStatusLabel.textContent = 'Thiếu token';
        return;
    }

    // Kiểm tra tháng đã chọn
    if (!month) {
        statusLabel.textContent = 'Thiếu tháng';
        statusNoteLabel.textContent = 'Vui lòng chọn tháng để xem báo cáo.';
        tableStatusLabel.textContent = 'Thiếu bộ lọc';
        return;
    }

    setLoadingState(true, 'Loading...');
    statusNoteLabel.textContent = 'Hệ thống đang tổng hợp doanh thu theo tháng...';

    // Chuẩn bị dữ liệu gửi đến API
    const formData = new FormData();
    formData.append('restaurant_id', restaurantId);  // ID nhà hàng (null = tất cả)
    formData.append('report_month', month);          // Tháng báo cáo (YYYY-MM)

    try {
        // Gọi API để lấy báo cáo doanh thu từ bảng Payment
        const response = await fetch(REPORT_API, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            body: formData
        });

        if (response.status === 401 || response.status === 403) {
            throw new Error('Phiên làm việc hết hạn');
        }

        const data = await response.json();

        if (data.status !== 'success') {
            throw new Error(data.message || 'Không thể tải báo cáo.');
        }

        totalReportLabel.textContent = formatCurrency(data.total_report);
        totalSixMonthsLabel.textContent = formatCurrency(data.total_6_months);
        restaurantCountLabel.textContent = data.restaurant_count || 0;
        statusLabel.textContent = 'Hoàn tất';
        statusNoteLabel.textContent = 'Dữ liệu đã được cập nhật cho tháng ' + month + '.';
        tableStatusLabel.textContent = 'Đã tải ' + (data.restaurant_count || 0) + ' nhà hàng';
        tableCaption.textContent = restaurantId
            ? 'Đang hiển thị chi tiết doanh thu của nhà hàng đã chọn trong 6 tháng gần nhất.'
            : 'Đang hiển thị doanh thu theo tháng của toàn bộ nhà hàng có giao dịch.';

        renderTable(data.months || [], data.restaurants || []);
    } catch (error) {
        totalReportLabel.textContent = formatCurrency(0);
        totalSixMonthsLabel.textContent = formatCurrency(0);
        restaurantCountLabel.textContent = '0';
        statusLabel.textContent = 'Lỗi kết nối';
        statusNoteLabel.textContent = error.message || 'Không thể tải báo cáo doanh thu.';
        tableStatusLabel.textContent = 'Tải thất bại';
        tableBody.innerHTML = '<tr><td class="admin-report-empty" colspan="9">Không thể tải dữ liệu báo cáo. Vui lòng kiểm tra API hoặc dữ liệu thanh toán.</td></tr>';
        console.error(error);
    } finally {
        loadButton.disabled = false;
    }
}


window.onload = async function () {
    monthInput.value = getCurrentMonthValue();
    await loadRestaurants();
    await loadReport();
};

export {
    formatCurrency,
    renderTable,
    loadReport,
    restaurantSelect,
    monthInput,
    loadButton,
    totalReportLabel,
    totalSixMonthsLabel,
    restaurantCountLabel,
    statusLabel,
    statusNoteLabel,
    tableStatusLabel,
    tableCaption,
    tableHead,
    tableBody
};

window.loadReport = loadReport;

function handleLogout() {
        if (confirm("Bạn có chắc muốn đăng xuất không?")) {
            localStorage.removeItem('token');
            window.location.href = "../auth/login.html";
        }
    }

window.handleLogout = handleLogout;
