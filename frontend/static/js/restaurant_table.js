const TABLE_API = "http://127.0.0.1:5000/api/v1/restaurant/tables";

const messageBox = document.getElementById("restaurant-page-message");

const tablePanel = document.getElementById("table-management-panel");
const logoutButton = document.getElementById("logoutButton");
const navButtons = document.querySelectorAll("[data-panel-target]");

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

// hiển thị thông báo
function showPageMessage(message, type = "info") {
    if (!messageBox) return;
    messageBox.hidden = false;
    messageBox.textContent = message;
    messageBox.className = `staff-restaurant-message ${type}`;
}

// ẩn thông báo
function clearPageMessage() {
    if (!messageBox) return;
    messageBox.hidden = true;
    messageBox.textContent = "";
    messageBox.className = "staff-restaurant-message";
}

// chuyển panel
function setActivePanel(panelName) {
    if (panelName === "register") {
        window.location.href = "register_restaurant.html";
        return;
    }

    const showRegister = panelName === "register";
    if (tablePanel) tablePanel.hidden = showRegister;

    navButtons.forEach((button) => {
        const isActive = button.dataset.panelTarget === panelName;
        button.classList.toggle("is-active", isActive);
    });

    if (!showRegister) {
        clearPageMessage();
    }
}

// render bàn
function renderTableCard(table) {
    let capacity = table.capacity;
    let extraClass = "";

    if (table.id % 9 === 0) {
        capacity = 8;
        extraClass = "double";
    }

    if (
        table.status === "available" ||
        table.status === "Trống" ||
        table.status === "Available"
    ) {
       return `<div class="card available ${extraClass}" onclick="openOrder(${table.id})">
            <div class="icon">🍽️</div>
            <h3>Bàn ${table.id}</h3>
            <p>Trống</p>
            <p>${capacity} người</p>
        </div>`;
    }

    if (table.status === "Reserved" || table.status === "Confirmed") {
        return `<div class="card reserved ${extraClass}" onclick="openOrder(${table.id})">
            <div class="icon">🍽️</div>
            <h3>Bàn ${table.id}</h3>
            <p>👤 ${table.customer_name || ""}</p>
            <p>${capacity} người</p>
            <div class="actions">
                <button onclick="cancelBooking(event, ${table.id})">Hủy</button>
            </div>
        </div>`;
    }

    return `<div class="card ${extraClass}">
        <div class="icon">🍽️</div>
        <h3>Bàn ${table.id}</h3>
        <p>Trạng thái: ${table.status}</p>
    </div>`;
}



// load bàn
async function loadTables() {
    try {
        const response = await fetch(TABLE_API, {
            method: "GET",
            headers: getAuthHeaders(true)
        });

        if (!response.ok) {
            throw new Error("Không tải được danh sách bàn.");
        }

        const tables = await response.json();
        const middle = Math.ceil(tables.length / 2);

        document.getElementById("left-side").innerHTML =
            tables.slice(0, middle).map(renderTableCard).join("");

        document.getElementById("right-side").innerHTML =
            tables.slice(middle).map(renderTableCard).join("");

    } catch (error) {
        showPageMessage(error.message || "Lỗi tải dữ liệu bàn.", "error");
    }

}

// update trạng thái
async function updateTableStatus(tableId, payload) {
    const response = await fetch(`${TABLE_API}/${tableId}/status`, {
        method: "PUT",
        headers: getAuthHeaders(true),
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error("Không cập nhật được trạng thái bàn.");
    }

    return response.json();
}

// hủy đặt bàn
async function cancelBooking(event, id) {
    event.stopPropagation();
    if (!confirm("Hủy đặt bàn này?")) return;

    try {
        await updateTableStatus(id, {
            Status: "Available",
            customer_name: "",
            customer_count: 0
        });
        await loadTables();
        showPageMessage("Đã hủy đặt bàn.", "success");
    } catch (error) {
        showPageMessage(error.message || "Hủy đặt bàn thất bại.", "error");
    }
}

// thêm bàn
async function addTable() {
    const capacity = parseInt(prompt("Nhập số chỗ ngồi:"), 10);
    if (!capacity || capacity <= 0) {
        showPageMessage("Số chỗ không hợp lệ.", "error");
        return;
    }

    try {
        const listResponse = await fetch(TABLE_API, {
            method: "GET",
            headers: getAuthHeaders(true)
        });
        const tables = await listResponse.json();
        const newNumber = tables.length + 1;

        const createResponse = await fetch(TABLE_API, {
            method: "POST",
            headers: getAuthHeaders(true),
            body: JSON.stringify({
                TableNumber: `B${newNumber}`,
                Capacity: capacity,
                Status: "Available"
            })
        });

        if (createResponse.ok) {
            showPageMessage("Đã thêm bàn mới thành công!", "success");
            await loadTables();
        } else {
            const errorData = await createResponse.json();
            throw new Error(errorData.error || "Không thêm được bàn mới.");
        }

    } catch (err) {
        console.error("Lỗi addTable:", err);
        showPageMessage(err.message || "Lỗi hệ thống khi thêm bàn.", "error");
    }
}

// mở order
function openOrder(id) {
    window.location.href = `./orders.html?table_id=${id}`;
}

// logout
function handleLogout() {
    if (!confirm("Bạn có chắc muốn đăng xuất không?")) return;
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "../auth/login.html";
}

// event
navButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setActivePanel(button.dataset.panelTarget);
    });
});

if (logoutButton) logoutButton.addEventListener("click", handleLogout);

window.cancelBooking = cancelBooking;
window.addTable = addTable;
window.openOrder = openOrder;

// load lần đầu
window.onload = async () => {
    setActivePanel("tables");
    await loadTables();
};

// quay lại tab reload
window.addEventListener("focus", () => {
    loadTables();
});

module.exports = {
    renderTableCard,
    loadTables,
    updateTableStatus,
    cancelBooking,
    getAuthHeaders,
    showPageMessage,
    clearPageMessage
};