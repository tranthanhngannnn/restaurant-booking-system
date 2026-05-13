const registerForm = document.getElementById('registerForm');

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Kiểm tra mật khẩu có khớp nhau không
        const pass = document.getElementById('pass').value;
        const confirmPass = document.getElementById('confirm_pass').value;

        if (pass !== confirmPass) {
            alert("Mật khẩu xác nhận không khớp!");
            return;
        }

        // 2. Lấy data
        const formData = new FormData(registerForm);

        // Đảm bảo restaurant_id được xử lý đúng (lấy trực tiếp từ element nếu FormData không bắt được do nested tags)
        const resId = document.getElementById('restaurantSelect').value;
        if (resId && resId !== "") {
            formData.set('restaurant_id', resId);
        } else {
            formData.delete('restaurant_id');
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/auth/registerRequest', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                alert("Chúc mừng! Đăng ký thành công.");
                window.location.href = "login.html"; 
            } else {
                // Hiển thị lỗi từ Backend (như Username đã tồn tại, sai định dạng...)
                alert("Lỗi đăng ký: " + (result.message || "Vui lòng kiểm tra lại"));
            }

        } catch (error) {
            console.error("Lỗi:", error);
            alert("Không kết nối được với Server Flask! Hãy chắc chắn Backend đang chạy.");
        }
    });
}

/**
 * Hàm ẩn/hiện ô chọn nhà hàng dựa vào Role
 * Để ở scope ngoài (global) để HTML onchange="toggleRestaurantDropdown()" có thể gọi được
 */
async function toggleRestaurantDropdown() {
    const roleSelect = document.getElementById("roleSelect");
    if (!roleSelect) return;
    
    const role = roleSelect.value;
    const resDiv = document.getElementById("restaurantDiv");
    const select = document.getElementById("restaurantSelect");

    if (role === "STAFF") {
        resDiv.style.display = "block";

        // Chỉ load nếu dropdown đang trống (để tránh load đi load lại)
        if (select.options.length <= 1) {
            try {
                // Gọi API lấy danh sách nhà hàng đã được duyệt
                const res = await fetch("http://127.0.0.1:5000/api/v1/restaurant/list");
                const data = await res.json();

                if (Array.isArray(data)) {
                    data.forEach(r => {
                        const option = document.createElement("option");
                        option.value = r.id; 
                        option.textContent = r.name;
                        select.appendChild(option);
                    });
                }
            } catch (err) {
                console.error("Không lấy được danh sách nhà hàng:", err);
            }
        }
    } else {
        resDiv.style.display = "none";
        select.value = ""; // Clear selection if not staff
    }
}
