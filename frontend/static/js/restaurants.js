const RES_API = 'http://127.0.0.1:5000/api/v1/admin/restaurants';
const CUISINE_API = 'http://127.0.0.1:5000/api/v1/admin/cuisines';
const USER_API = 'http://127.0.0.1:5000/api/v1/admin/users';
const userRole = localStorage.getItem('role');
let listRes = [];

// 1. Quản lý Đóng/Mở
function getScrollbarWidth() {
    return window.innerWidth - document.documentElement.clientWidth;
}

function prepareAdd() {
    document.getElementById('appResForm').reset();
    document.getElementById('form-res-id').value = '';
    document.getElementById('appModalTitle').innerText = "Đăng ký Nhà Hàng";
    openResModal();
}

function openResModal() {
    const modal = document.getElementById('appModalWrapper');

    // Tính và bù đắp độ rộng thanh cuộn
    const sw = getScrollbarWidth();
    document.documentElement.style.setProperty('--scrollbar-width', sw + 'px');

    modal.classList.add('is-visible');
    document.body.classList.add('modal-open');

    const adminField = document.getElementById('adminFieldContainer');
    if (adminField) adminField.style.display = (userRole === 'ADMIN') ? 'flex' : 'none';
}

function closeResModal() {
    const modal = document.getElementById('appModalWrapper');
    modal.classList.remove('is-visible');
    document.body.classList.remove('modal-open');
    // Reset lại padding sau khi đóng (delay nhẹ để mượt)
    setTimeout(() => {
        document.documentElement.style.setProperty('--scrollbar-width', '0px');
    }, 300);
}

function handleOverlayClick(e) {
    if (e.target.id === 'appModalWrapper') closeResModal();
}

async function loadDropdowns() {
    try {
        const token = localStorage.getItem('token');
        const headers = {'Authorization': `Bearer ${token}`};

        // Đổ dữ liệu Loại ẩm thực
        const resC = await fetch(CUISINE_API, {headers});
        const cuisines = await resC.json();
        const cuisineSelect = document.getElementById('res-cuisine');
        cuisineSelect.innerHTML = '<option value="">-- Chọn loại ẩm thực --</option>';
        cuisines.forEach(c => {
            console.log("Dữ liệu của một loại ẩm thực:", c); //lệnh để xem console in ra gì
            cuisineSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });

        // Đổ dữ liệu Chủ nhà hàng (Admin mới thấy)
        if (userRole === 'ADMIN') {
            const resU = await fetch('http://127.0.0.1:5000/api/v1/admin/users', {headers});
            const users = await resU.json();
            const userSelect = document.getElementById('res-user');
            userSelect.innerHTML = '<option value="">-- Chọn chủ nhà hàng --</option>';
            users.forEach(u => {
                console.log("Dữ liệu của user:", u);
                userSelect.innerHTML += `<option value="${u.id}">${u.username}</option>`;
            });
        }
    } catch (err) {
        console.error("Lỗi load dropdown:", err);
    }
}

// Load danh sách & Hiển thị
async function fetchRestaurants() {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(RES_API, {headers: {'Authorization': `Bearer ${token}`}});
        const data = await res.json();
        listRes = data;
        const tbody = document.getElementById('res-list-body');

        tbody.innerHTML = data.map(r => `
    <tr>
        <td>${r.RestaurantID}</td>
        <td title="${r.RestaurantName}"><strong>${r.RestaurantName}</strong></td>
        <td title="${r.Address || ''}">${r.Address || ''}</td>
        <td>${r.Phone || 'N/A'}</td>
        <td title="${r.Email || ''}"><small>${r.Email || ''}</small></td>
        <td>${r.Opentime || '--:--'}</td>
        <td>${r.Closetime || '--:--'}</td>
        <td title="${r.description || ''}">${r.description || ''}</td>
        <td>User: ${r.UserID}</td>
        <td>${r.CuisineID || 'N/A'}</td>
        <td><span class="status-tag ${r.status == 'Đang hoạt động' ? 'active' : 'pending'}">${r.status}</span></td>
        <td class="col-action">
            <button class="btn-edit" onclick="prepareEdit(${r.RestaurantID})">Sửa</button>
            <button class="btn-delete" onclick="handleDelete(${r.RestaurantID})">Xóa</button>
        </td>
    </tr>`).join('');
    } catch (err) {
        console.error("Lỗi load danh sách:", err);
    }
}

// --- HÀM THÊM MỚI ---
async function addRestaurant(formData) {
    try {
        const res = await fetch(RES_API, {
            method: 'POST',
            headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`},
            body: formData
        });
        handleResponse(res);
    } catch (err) {
        alert("Lỗi kết nối khi thêm!");
    }
}

// --- HÀM CẬP NHẬT ---
async function updateRestaurant(id, formData) {
    try {
        const res = await fetch(`${RES_API}/${id}`, {
            method: 'PUT',
            headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`},
            body: formData
        });
        handleResponse(res);
    } catch (err) {
        alert("Lỗi kết nối khi sửa!");
    }
}

// sự kiện submit
document.getElementById('appResForm').onsubmit = async (e) => {
    e.preventDefault(); // Ngăn trang web load lại

    const id = document.getElementById('form-res-id').value;
    const formData = new FormData(e.target); // Lấy dữ liệu từ các thẻ có thuộc tính 'name'

    // log ra để kiểm tra xem đã lấy được data chưa
    console.log("Dữ liệu gửi đi:");
    for (let [key, value] of formData.entries()) {
        console.log(key, value);
    }

    if (id) {
        await updateRestaurant(id, formData);
    } else {
        await addRestaurant(formData);
    }
};

// Hàm xử lý kết quả trả về chung
async function handleResponse(res) {
    if (res.ok) {
        alert("Thành công!");
        closeResModal();
        fetchRestaurants();
    } else {
        const err = await res.json();
        alert("Lỗi: " + (err.message || "Không xác định"));
    }
}

// Hàm PrepareEdit cho nút Sửa
function prepareEdit(id) {
    const r = listRes.find(item => item.RestaurantID == id);
    if (r) {
        openResModal();
        document.getElementById('appModalTitle').innerText = "Cập nhật Nhà Hàng";
        document.getElementById('form-res-id').value = r.RestaurantID;
        document.getElementById('res-name').value = r.RestaurantName;
        document.getElementById('res-address').value = r.Address || '';
        document.getElementById('res-phone').value = r.Phone || '';
        document.getElementById('res-email').value = r.Email || '';
        document.getElementById('res-open').value = r.Opentime?.slice(0, 5) || '';
        document.getElementById('res-close').value = r.Closetime?.slice(0, 5) || '';
        document.getElementById('res-desc').value = r.description || '';
        document.getElementById('res-status').value = r.status || 'ACTIVE';

        if (r.CuisineID) document.getElementById('res-cuisine').value = r.CuisineID;
        if (r.UserID) document.getElementById('res-user').value = r.UserID;

        // Sau khi fill xong mới hiện modal để tránh "nháy" form trống
        openResModal();
    }
}

//hàm xóa
async function handleDelete(id) {
    if (confirm("Xóa nhà hàng này?")) {
        await fetch(`${RES_API}/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
        });
        fetchRestaurants();
    }
}

window.onload = () => {
    loadDropdowns();
    fetchRestaurants();
    fetchCuisines();
};