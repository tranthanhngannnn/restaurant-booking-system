const API = "http://127.0.0.1:5000/api";

// CHECK LOGIN
export function checkLogin() {
    const token = localStorage.getItem("token");
    console.log("TOKEN:", token);

    if (!token) return;

    return fetch(`${API}/v1/customer/me`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })
        .then(res => {
            console.log("STATUS:", res.status);
            if (!res.ok) {
                throw new Error("Token hết hạn hoặc không hợp lệ");
            }
            return res.json();
        })
        .then(data => {
            console.log("DATA:", data);

            if (data.logged_in || data.id) {
                document.querySelector(".auth-buttons").style.display = "none";

                document.getElementById("logoutBtn").style.display = "block";
                document.getElementById("historyLink").style.display = "block";
                document.getElementById("historyCard").style.display = "block";
            }
        })
        .catch(error => {
            console.error("Lỗi xác thực:", error);
            localStorage.removeItem("token");
        });
}

// LOGOUT
export function logout() {
    localStorage.removeItem("token");

    return fetch(`${API}/logout`, {
        credentials: "include"
    })
        .then(() => {
            window.location.href = "home.html";
        })
        .catch(err => {
            console.error("Lỗi đăng xuất:", err);
            window.location.reload();
        });
}

// UI SWITCH
export function closePopup() {
    if (typeof authBox !== 'undefined') {
        authBox.style.display = "none";
    }
}