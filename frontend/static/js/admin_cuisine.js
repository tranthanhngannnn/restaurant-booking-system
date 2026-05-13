const API_URL = 'http://127.0.0.1:5000/api/v1/admin/cuisines';

// 1. GET
async function fetchCuisines() {
    const token = localStorage.getItem('token');
    const res = await fetch(API_URL, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    const data = await res.json();
    const body = document.getElementById('cuisine-list-body');

    body.innerHTML = data.map(item => `
            <tr class="list-row">
                <td class="col-id">${item.id}</td>
                <td class="col-name">${item.name}</td>
                <td class="col-status">${item.status}</td>
                <td class="col-action">
                    <button class="btn-edit" onclick="openEditModal(${item.id},'${item.name}','${item.status}')">Sửa</button>
                    <button class="btn-delete" onclick="handleDelete(${item.id})">Xóa</button>
                </td>
            </tr>
        `).join('');
}

// 2. POST - Thêm mới
async function handleAdd() {
    const name = document.getElementById('form-name').value;
    const token = localStorage.getItem('token');

    const formData = new FormData();
    formData.append('CuisineName', name);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert("Thêm thành công!");
            location.reload();
        } else {
            alert("Lỗi từ Server: " + (result.message || "Thất bại"));
        }
    } catch (err) {
        console.error("Lỗi kết nối:", err);
    }
}

// Logic mở Modal Thêm mới (Reset sạch sẽ dữ liệu cũ)
function openAddModal() {
    document.getElementById('form-id').value = '';
    document.getElementById('form-name').value = '';
    document.getElementById('modal-title').innerText = 'Thêm Cuisine';
    document.getElementById('btn-submit').onclick = handleAdd;
    document.getElementById('cuisineModal').style.display = 'flex';
}

// 3. PUT
async function handleUpdate() {
    const id = document.getElementById('form-id').value;
    const name = document.getElementById('form-name').value;
    const status = document.getElementById('form-status').value;
    const token = localStorage.getItem('token');

    const formData = new FormData();
    formData.append('CuisineName', name);
    formData.append('Status', status);

    console.log("Đang gửi Form Data để cập nhật ID:", id);

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || "Cập nhật thành công!");
            closeModal();
            location.reload();
        } else {
            alert("Lỗi server: " + (result.message || "Không thể cập nhật"));
        }
    } catch (err) {
        console.error("Lỗi kết nối:", err);
        alert("Lỗi kết nối server, kiểm tra lại console!");
    }
}

// 4. DELETE
async function handleDelete(id) {
    if (confirm('Chắc chắn xóa món này không?')) {
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${API_URL}/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message || "Đã xóa xong!");
                fetchCuisines();
            } else {
                alert("Lỗi khi xóa: " + (result.message || "Không thể xóa"));
            }
        } catch (err) {
            console.error("Lỗi kết nối khi xóa:", err);
        }
    }
}

// Logic UI Modal
function openEditModal(id, name, status) {
    document.getElementById('form-id').value = id;
    document.getElementById('form-name').value = name;
    document.getElementById('form-status').value = status;

    document.getElementById('cuisineModal').style.display = 'flex';

    const btn = document.getElementById('btn-submit');
    btn.onclick = handleUpdate;
}

function showModal(title, name, actionFunc) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('form-name').value = name;
    document.getElementById('btn-submit').onclick = actionFunc;
    document.getElementById('cuisineModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('cuisineModal').style.display = 'none';
}

function finishAction() {
    closeModal();
    fetchCuisines();
}

window.onload = async function () {
    fetchCuisines();
};

// Logic đăng xuất
function handleLogout() {
    if (confirm("Bạn có chắc muốn đăng xuất không?")) {
        localStorage.removeItem('token');
        window.location.href = "../auth/login.html";
    }
}
