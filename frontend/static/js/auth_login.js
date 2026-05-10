const loginForm = document.querySelector('form');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Chặn load lại trang

    // Tự động hốt hết data từ các ô input có "name"
    const formData = new FormData(loginForm);

    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
            method: 'POST',
            body: formData // Gửi trực tiếp FormData
        });

        const result = await response.json();
        if (response.ok) {
            // Lưu token vào máy để các trang sau kiểm tra quyền đăng nhập
            localStorage.setItem('token', result.access_token);
            localStorage.setItem('role', result.role);
            localStorage.setItem('user_id', result.user_info?.id)

            alert("Đăng nhập thành công!");

            const role = result.role; // Lấy role từ Flask trả về

            if (role === 'ADMIN') {
                window.location.href = "../admin/homepage.html";
            } else if (role === 'STAFF') {
                window.location.href = "../restaurant/table.html"; // Đường dẫn tới trang nhà hàng
            } else if (role === 'CUSTOMER') {
                window.location.href = "../customer/home.html"; // Đường dẫn tới trang khách hàng
            }

        } else {
            // Flask trả về lỗi (như sai mật khẩu) thì hiện thông báo
            alert("Lỗi: " + (result.message || "Đăng nhập thất bại"));
        }

    } catch (error) {
        console.error("Lỗi:", error);
        alert("Kiểm tra lại Flask đã chạy chưa!");
    }
});