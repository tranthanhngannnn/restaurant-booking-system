const REGISTER_API = "http://127.0.0.1:5000/api/v1/restaurants/registerRestaurant";
const CUISINE_API = "http://127.0.0.1:5000/api/v1/admin/cuisines";

const messageBox = document.getElementById("restaurant-page-message");
const registerPanel = document.getElementById("restaurant-registration-panel");
const registerForm = document.getElementById("restaurant-register-form");
const registerCuisine = document.getElementById("register-restaurant-cuisine");
const registerSubmitButton = document.getElementById("register-submit-button");
const logoutButton = document.getElementById("logoutButton");
const navButtons = document.querySelectorAll("[data-panel-target]");
const registerCancelButton = document.getElementById("register-cancel-button");

function getAuthHeaders(includeJson = true) {
    const token = localStorage.getItem("token");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    if (includeJson) {
        headers["Content-Type"] = "application/json";
    }
    return headers;
}

function showPageMessage(message, type = "info") {
    if (!messageBox) return;
    messageBox.hidden = false;
    messageBox.textContent = message;
    messageBox.className = `staff-restaurant-message ${type}`;
}

function clearPageMessage() {
    if (!messageBox) return;
    messageBox.hidden = true;
    messageBox.textContent = "";
    messageBox.className = "staff-restaurant-message";
}

function setActivePanel(panelName) {
    // Navigation redirection
    if (panelName === "tables") {
        window.location.href = "table.html";
        return;
    }

    const showRegister = panelName === "register";
    if (registerPanel) registerPanel.hidden = !showRegister;

    navButtons.forEach((button) => {
        const isActive = button.dataset.panelTarget === panelName;
        button.classList.toggle("is-active", isActive);
    });

    if (!showRegister) {
        clearPageMessage();
    }
}

async function loadCuisines() {
    try {
        const response = await fetch(CUISINE_API, {
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token") || ""}`
            }
        });

        if (!response.ok) {
            throw new Error("Không tải được loại ẩm thực.");
        }

        const cuisines = await response.json();
        registerCuisine.innerHTML = '<option value="">-- Chọn loại ẩm thực --</option>';
        cuisines.forEach((cuisine) => {
            registerCuisine.innerHTML += `<option value="${cuisine.id}">${cuisine.name}</option>`;
        });
    } catch (error) {
        registerCuisine.innerHTML = '<option value="">Không tải được dữ liệu</option>';
        showPageMessage(error.message || "Lỗi tải loại ẩm thực.", "error");
    }
}

async function submitRestaurantRegistration(event) {
    event.preventDefault();
    clearPageMessage();

    const token = localStorage.getItem("token");
    if (!token) {
        showPageMessage("Bạn chưa đăng nhập.", "error");
        return;
    }

    registerSubmitButton.disabled = true;

    try {
        const formData = new FormData(registerForm);
        const response = await fetch(REGISTER_API, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || "Đăng ký nhà hàng thất bại.");
        }

        registerForm.reset();
        showPageMessage("Đăng ký thành công, chờ admin duyệt", "success");
        setActivePanel("register");
    } catch (error) {
        showPageMessage(error.message || "Có lỗi xảy ra khi đăng ký nhà hàng.", "error");
    } finally {
        registerSubmitButton.disabled = false;
    }
}

function cancelRestaurantRegistration() {
    registerForm.reset();
    clearPageMessage();
    setActivePanel("tables");
}

function handleLogout() {
    if (!confirm("Bạn có chắc muốn đăng xuất không?")) return;
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "../auth/login.html";
}

navButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setActivePanel(button.dataset.panelTarget);
    });
});

if (registerForm) registerForm.addEventListener("submit", submitRestaurantRegistration);
if (registerCancelButton) registerCancelButton.addEventListener("click", cancelRestaurantRegistration);
if (logoutButton) logoutButton.addEventListener("click", handleLogout);

window.onload = async () => {
    setActivePanel("register");
    await loadCuisines();
};
