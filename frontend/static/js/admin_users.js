    const API_URL = 'http://127.0.0.1:5000/api/v1/admin/users';
    const RESTAURANT_LIST_API = 'http://127.0.0.1:5000/api/v1/restaurants/list';

    // Xử lý sự kiện thay đổi Role
    document.getElementById('user-field-role').addEventListener('change', function() {
        const role = this.value;
        const restaurantGroup = document.getElementById('restaurant-select-group');
        if (role === 'STAFF') {
            restaurantGroup.style.display = 'block';
            fetchRestaurants();
        } else {
            restaurantGroup.style.display = 'none';
        }
    });

    // Lấy danh sách nhà hàng
    async function fetchRestaurants() {
        try {
            const res = await fetch(RESTAURANT_LIST_API);
            const data = await res.json();
            const select = document.getElementById('user-field-restaurant');
            
            const currentValue = select.value;
            select.innerHTML = '<option value="">-- Chọn nhà hàng --</option>';
            data.forEach(r => {
                const option = document.createElement('option');
                option.value = r.id;
                option.textContent = r.name;
                select.appendChild(option);
            });
            select.value = currentValue;
        } catch (err) {
            console.error("Lỗi fetch nhà hàng:", err);
        }
    }

    //READ: Đổ data vào bảng
    async function fetchUsers() {
        const token = localStorage.getItem('token');
        const res = await fetch(API_URL, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        const users = await res.json();

        const tbody = document.getElementById('user-list-body');

        tbody.innerHTML = users.map(u => `
            <tr>
            <td class="cell-id">${u.id}</td>
            <td class="cell-info"><strong>${u.username}</strong></td>
            <td class="cell-email">${u.email}</td>
            <td class="cell-phone">${u.phone || 'Chưa có số'}</td>
            <td class="cell-role">${u.role}</td>
            <td class="cell-action">
                <button onclick="openEditModal(${u.id}, '${u.username}', '${u.email}', '${u.phone}', '${u.role}', ${u.restaurant_id})">Sửa</button>
                <button onclick="handleDelete(${u.id})">Xóa</button>
            </td>
            </tr>
        `).join('');
    }

    //PUT
    async function updateUser(id) {
        const token = localStorage.getItem('token');
        const formData = new FormData();

        const role = document.getElementById('user-field-role').value;
        formData.append('Username', document.getElementById('user-field-name').value);
        formData.append('Email', document.getElementById('user-field-email').value);
        formData.append('Phone', document.getElementById('user-field-phone').value);
        formData.append('Role', role);

        if (role === 'STAFF') {
            const restaurantId = document.getElementById('user-field-restaurant').value;
            if (!restaurantId) {
                alert("Vui lòng chọn nhà hàng cho STAFF!");
                return;
            }
            formData.append('RestaurantID', restaurantId);
        }


        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {'Authorization': `Bearer ${token}`},
            body: formData
        });

        if (response.ok) {
            alert("Cập nhật thành công!");
            closeUserEntry();
            fetchUsers();
        } else {
            const error = await response.json();
            alert("Lỗi cập nhật: " + (error.message || "Không xác định"));
        }
    }

    //DELETE
    async function handleDelete(id) {
        if (confirm("Xóa user này?")) {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/${id}`, {
                method: 'DELETE',
                headers: {'Authorization': `Bearer ${token}`}
            });
            fetchUsers();
        }
    }

    // UI LOGIC
    // Hàm tổng để quyết định là Thêm hay Sửa
    function handleSaveUser() {
        const id = document.getElementById('form-id').value;

        if (id) {
            updateUser(id); // Chỉ chạy hàm này khi có ID (tức là đang sửa)
        } else {
            console.warn("Không tìm thấy ID user để cập nhật!");
            alert("Lỗi: Không xác định được người dùng cần sửa.");
        }
    }


    function openAddModal() {
        document.getElementById('form-id').value = '';
        document.getElementById('user-title').innerText = "Thêm User";
        document.getElementById('button-submit').onclick = handleSaveUser;
        document.getElementById('restaurant-select-group').style.display = 'none';
        document.getElementById('userModal').style.display = 'flex';
    }

    async function openEditModal(id, name, email, phone, role, restaurant_id) {
        document.getElementById('form-id').value = id;
        document.getElementById('user-field-name').value = name;
        document.getElementById('user-field-email').value = email;
        document.getElementById('user-field-phone').value = phone;
        document.getElementById('user-field-role').value = role;
        
        const restaurantGroup = document.getElementById('restaurant-select-group');
        if (role === 'STAFF') {
            restaurantGroup.style.display = 'block';
            await fetchRestaurants();
            document.getElementById('user-field-restaurant').value = restaurant_id || '';
        } else {
            restaurantGroup.style.display = 'none';
        }

        document.getElementById('user-title').innerText = "Sửa User";
        document.getElementById('button-submit').onclick = handleSaveUser;
        document.getElementById('userModal').style.display = 'flex';
    }

    function closeUserEntry() {
        document.getElementById('userModal').style.display = 'none';
    }

    window.onload = fetchUsers;


    // Logic đăng xuất
    function handleLogout() {
        if (confirm("Bạn có chắc muốn đăng xuất không?")) {
            localStorage.removeItem('token');
            window.location.href = "../auth/login.html";
        }
    }