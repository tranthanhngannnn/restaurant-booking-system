const RES_API = 'http://127.0.0.1:5000/api/v1/admin/restaurants';
const CUISINE_API = 'http://127.0.0.1:5000/api/v1/admin/cuisines';
const USER_API = 'http://127.0.0.1:5000/api/v1/admin/users';
const APPROVE_API_SUFFIX = '/approve';
const REJECT_API_SUFFIX = '/reject';
const userRole = localStorage.getItem('role');

let listRes = [];
let cuisineMap = {};
let userMap = {};
let currentApprovalRestaurant = null;

const restaurantMessage = document.getElementById('restaurant-admin-message');
const approvalModal = document.getElementById('approvalModal');
const approvalName = document.getElementById('approval-restaurant-name');
const approvalUser = document.getElementById('approval-restaurant-user');
const approvalCuisine = document.getElementById('approval-restaurant-cuisine');
const approvalStatus = document.getElementById('approval-restaurant-status');
const approvalNote = document.getElementById('approval-note');
const approvalApproveButton = document.getElementById('approvalApproveButton');
const approvalRejectButton = document.getElementById('approvalRejectButton');

function getScrollbarWidth() {
    return window.innerWidth - document.documentElement.clientWidth;
}

function showRestaurantMessage(message, type = 'info') {
    if (!restaurantMessage) return;
    restaurantMessage.hidden = false;
    restaurantMessage.textContent = message;
    restaurantMessage.className = `admin-restaurants-message ${type}`;
}

function clearRestaurantMessage() {
    if (!restaurantMessage) return;
    restaurantMessage.hidden = true;
    restaurantMessage.textContent = '';
    restaurantMessage.className = 'admin-restaurants-message';
}

function normalizeText(value) {
    return (value || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
}

function getStatusVariant(status) {
    const normalized = normalizeText(status);
    if (normalized.includes('dang hoat dong')) return 'active';
    if (normalized.includes('cho duyet')) return 'pending';
    if (normalized.includes('tu choi')) return 'rejected';
    if (normalized.includes('ngung')) return 'inactive';
    return 'neutral';
}

function getCuisineName(cuisineId) {
    return cuisineMap[cuisineId] || cuisineId || 'N/A';
}

function getUserName(userId) {
    return userMap[userId] || `User: ${userId || 'N/A'}`;
}

function prepareAdd() {
    document.getElementById('appResForm').reset();
    document.getElementById('form-res-id').value = '';
    document.getElementById('appModalTitle').innerText = 'Đăng ký Nhà Hàng';
    document.getElementById('res-status').value = 'Đang hoạt động';
    openResModal();
}

function openResModal() {
    const modal = document.getElementById('appModalWrapper');
    const sw = getScrollbarWidth();
    document.documentElement.style.setProperty('--scrollbar-width', `${sw}px`);
    modal.classList.add('is-visible');
    document.body.classList.add('modal-open');

    const adminField = document.getElementById('adminFieldContainer');
    if (adminField) adminField.style.display = userRole === 'ADMIN' ? 'flex' : 'none';
}

function closeResModal() {
    const modal = document.getElementById('appModalWrapper');
    modal.classList.remove('is-visible');
    document.body.classList.remove('modal-open');
    setTimeout(() => {
        document.documentElement.style.setProperty('--scrollbar-width', '0px');
    }, 300);
}

function handleOverlayClick(event) {
    if (event.target.id === 'appModalWrapper') {
        closeResModal();
    }
}

function openApprovalModal(restaurantId) {
    const restaurant = listRes.find((item) => item.RestaurantID === restaurantId || item.RestaurantID == restaurantId);
    if (!restaurant) {
        showRestaurantMessage('Không tìm thấy thông tin nhà hàng cần duyệt.', 'error');
        return;
    }

    currentApprovalRestaurant = restaurant;
    approvalName.textContent = restaurant.RestaurantName || '-';
    approvalUser.textContent = getUserName(restaurant.UserID);
    approvalCuisine.textContent = getCuisineName(restaurant.CuisineID);
    approvalStatus.textContent = restaurant.status || '-';
    approvalNote.value = '';
    approvalModal.classList.add('is-visible');
}

function closeApprovalModal() {
    approvalModal.classList.remove('is-visible');
    currentApprovalRestaurant = null;
    approvalNote.value = '';
}

function handleApprovalOverlayClick(event) {
    if (event.target.id === 'approvalModal') {
        closeApprovalModal();
    }
}

async function loadDropdowns() {
    try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };

        const cuisineResponse = await fetch(CUISINE_API, { headers });
        const cuisines = await cuisineResponse.json();
        cuisineMap = {};

        const cuisineSelect = document.getElementById('res-cuisine');
        cuisineSelect.innerHTML = '<option value="">-- Chọn loại ẩm thực --</option>';
        cuisines.forEach((cuisine) => {
            cuisineMap[cuisine.id] = cuisine.name;
            cuisineSelect.innerHTML += `<option value="${cuisine.id}">${cuisine.name}</option>`;
        });

        if (userRole === 'ADMIN') {
            const userResponse = await fetch(USER_API, { headers });
            const users = await userResponse.json();
            userMap = {};

            const userSelect = document.getElementById('res-user');
            userSelect.innerHTML = '<option value="">-- Chọn chủ nhà hàng --</option>';
            users.forEach((user) => {
                userMap[user.id] = user.username;
                userSelect.innerHTML += `<option value="${user.id}">${user.username}</option>`;
            });
        }
    } catch (error) {
        showRestaurantMessage('Không tải được dữ liệu dropdown.', 'error');
        console.error(error);
    }
}

function renderStatusCell(restaurant) {
    const variant = getStatusVariant(restaurant.status);
    const isPending = variant === 'pending';

    if (isPending) {
        return `<button type="button" class="admin-restaurants-status-button pending" onclick="openApprovalModal(${restaurant.RestaurantID})">
            ${restaurant.status}
        </button>`;
    }

    return `<span class="admin-restaurants-status-badge ${variant}">${restaurant.status || 'N/A'}</span>`;
}

async function fetchRestaurants() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(RES_API, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('Không tải được danh sách nhà hàng.');
        }

        const data = await response.json();
        listRes = data;

        const tbody = document.getElementById('res-list-body');
        tbody.innerHTML = data.map((restaurant) => `
            <tr>
                <td>${restaurant.RestaurantID}</td>
                <td title="${restaurant.RestaurantName || ''}"><strong>${restaurant.RestaurantName || ''}</strong></td>
                <td title="${restaurant.Address || ''}">${restaurant.Address || ''}</td>
                <td>${restaurant.Phone || 'N/A'}</td>
                <td title="${restaurant.Email || ''}"><small>${restaurant.Email || ''}</small></td>
                <td>${restaurant.Opentime || '--:--'}</td>
                <td>${restaurant.Closetime || '--:--'}</td>
                <td title="${restaurant.description || ''}">${restaurant.description || ''}</td>
                <td>${getUserName(restaurant.UserID)}</td>
                <td>${getCuisineName(restaurant.CuisineID)}</td>
                <td>${renderStatusCell(restaurant)}</td>
                <td class="col-action">
                    <button class="btn-edit" onclick="prepareEdit(${restaurant.RestaurantID})">Sửa</button>
                    <button class="btn-delete" onclick="handleDelete(${restaurant.RestaurantID})">Xóa</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        showRestaurantMessage(error.message || 'Lỗi tải danh sách.', 'error');
        console.error(error);
    }
}

async function addRestaurant(formData) {
    const response = await fetch(RES_API, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: formData
    });
    await handleResponse(response, 'Thêm nhà hàng thành công!');
}

async function updateRestaurant(id, formData) {
    const response = await fetch(`${RES_API}/${id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: formData
    });
    await handleResponse(response, 'Cập nhật nhà hàng thành công!');
}

document.getElementById('appResForm').onsubmit = async (event) => {
    event.preventDefault();
    clearRestaurantMessage();

    const id = document.getElementById('form-res-id').value;
    const formData = new FormData(event.target);
    formData.set('status', document.getElementById('res-status').value);

    try {
        if (id) {
            await updateRestaurant(id, formData);
        } else {
            await addRestaurant(formData);
        }
    } catch (error) {
        showRestaurantMessage(error.message || 'Không lưu được nhà hàng.', 'error');
    }
};

async function handleResponse(response, successMessage) {
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.message || 'Không xác định');
    }

    showRestaurantMessage(successMessage || result.message || 'Thành công!', 'success');
    closeResModal();
    await fetchRestaurants();
}

function prepareEdit(id) {
    const restaurant = listRes.find((item) => item.RestaurantID == id);
    if (!restaurant) return;

    document.getElementById('appModalTitle').innerText = 'Cập nhật Nhà Hàng';
    document.getElementById('form-res-id').value = restaurant.RestaurantID;
    document.getElementById('res-name').value = restaurant.RestaurantName || '';
    document.getElementById('res-address').value = restaurant.Address || '';
    document.getElementById('res-phone').value = restaurant.Phone || '';
    document.getElementById('res-email').value = restaurant.Email || '';
    document.getElementById('res-open').value = restaurant.Opentime ? restaurant.Opentime.slice(0, 5) : '';
    document.getElementById('res-close').value = restaurant.Closetime ? restaurant.Closetime.slice(0, 5) : '';
    document.getElementById('res-desc').value = restaurant.description || '';
    document.getElementById('res-status').value = restaurant.status || 'Đang hoạt động';

    if (restaurant.CuisineID) {
        document.getElementById('res-cuisine').value = restaurant.CuisineID;
    }
    if (restaurant.UserID) {
        document.getElementById('res-user').value = restaurant.UserID;
    }

    openResModal();
}

async function handleDelete(id) {
    if (!confirm('Xóa nhà hàng này?')) return;

    try {
        const response = await fetch(`${RES_API}/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || 'Không xóa được nhà hàng.');
        }

        showRestaurantMessage(result.message || 'Đã xóa nhà hàng.', 'success');
        await fetchRestaurants();
    } catch (error) {
        showRestaurantMessage(error.message || 'Lỗi khi xóa nhà hàng.', 'error');
    }
}

async function submitApproval(action) {
    if (!currentApprovalRestaurant) return;

    const endpoint = action === 'approve' ? APPROVE_API_SUFFIX : REJECT_API_SUFFIX;
    const button = action === 'approve' ? approvalApproveButton : approvalRejectButton;
    const defaultText = button.textContent;
    button.disabled = true;
    button.textContent = action === 'approve' ? 'Đang duyệt...' : 'Đang từ chối...';

    try {
        const response = await fetch(`${RES_API}/${currentApprovalRestaurant.RestaurantID}${endpoint}`, {
            method: 'PUT',
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            }
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || 'Không xử lý được yêu cầu.');
        }

        closeApprovalModal();
        showRestaurantMessage(result.message || 'Đã cập nhật trạng thái nhà hàng.', 'success');
        await fetchRestaurants();
    } catch (error) {
        showRestaurantMessage(error.message || 'Xử lý duyệt nhà hàng thất bại.', 'error');
    } finally {
        button.disabled = false;
        button.textContent = defaultText;
    }
}

approvalApproveButton.addEventListener('click', () => submitApproval('approve'));
approvalRejectButton.addEventListener('click', () => submitApproval('reject'));

window.prepareAdd = prepareAdd;
window.closeResModal = closeResModal;
window.handleOverlayClick = handleOverlayClick;
window.prepareEdit = prepareEdit;
window.handleDelete = handleDelete;
window.openApprovalModal = openApprovalModal;
window.closeApprovalModal = closeApprovalModal;
window.handleApprovalOverlayClick = handleApprovalOverlayClick;

window.onload = async () => {
    await loadDropdowns();
    await fetchRestaurants();
};

function handleLogout() {
    if (confirm("Bạn có chắc muốn đăng xuất không?")) {
        localStorage.removeItem('token');
        window.location.href = "../auth/login.html";
    }
}
