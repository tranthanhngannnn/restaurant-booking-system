const TABLE_API = "http://127.0.0.1:5000/api/v1/restaurant/tables";

const modal = document.getElementById("booking-modal");
const modalClose = document.getElementById("modal-close");
const bookingForm = document.getElementById("booking-form");
const bookingTableId = document.getElementById("booking-table-id");
const customerNameInput = document.getElementById("customer-name");
const customerCountInput = document.getElementById("customer-count");
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

function renderTableCard(table) {
    let capacity = table.capacity;
    let extraClass = "";

    if (table.id % 9 === 0) {
        capacity = 8;
        extraClass = "double";
    }

    if (table.status === "available" || table.status === "Trống" || table.status === "Available") {
        return `<div class="card available ${extraClass}" onclick="openBookingModal(${table.id}, ${capacity})">
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
                <button onclick="editBooking(event, ${table.id}, '${table.customer_name || ""}', ${table.customer_count || 1}, ${capacity})">Sửa</button>
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
        document.getElementById("left-side").innerHTML = tables.slice(0, middle).map(renderTableCard).join("");
        document.getElementById("right-side").innerHTML = tables.slice(middle).map(renderTableCard).join("");
    } catch (error) {
        showPageMessage(error.message || "Lỗi tải dữ liệu bàn.", "error");
    }
}


function openBookingModal(tableId, capacity) {
    bookingTableId.value = tableId;
    customerCountInput.value = capacity;
    customerCountInput.max = capacity;
    customerNameInput.value = "";
    modal.classList.add("show");
    customerNameInput.focus();
}

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

function editBooking(event, id, name, count, capacity) {
    event.stopPropagation();
    bookingTableId.value = id;
    customerNameInput.value = name || "";
    customerCountInput.value = count || 1;
    customerCountInput.max = capacity;
    modal.classList.add("show");
}

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

        if (!createResponse.ok) {
            throw new Error("Không thêm được bàn mới.");
        }

        await loadTables();
        showPageMessage("Đã thêm bàn mới.", "success");
    } catch (error) {
        showPageMessage(error.message || "Lỗi thêm bàn.", "error");
    }
}

function openOrder(id) {
    window.location.href = `./orders.html?table_id=${id}`;
}


function handleLogout() {
    if (!confirm("Bạn có chắc muốn đăng xuất không?")) return;
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "../auth/login.html";
}

bookingForm.onsubmit = async (event) => {
    event.preventDefault();

    const id = bookingTableId.value;
    const customerName = customerNameInput.value.trim();
    const customerCount = parseInt(customerCountInput.value, 10);
    const maxCapacity = Number(customerCountInput.max);

    if (customerCount > maxCapacity) {
        showPageMessage(`Bàn này chỉ tối đa ${maxCapacity} người.`, "error");
        return;
    }

    if (!customerName || !customerCount || customerCount <= 0) {
        showPageMessage("Vui lòng nhập thông tin đặt bàn hợp lệ.", "error");
        return;
    }

    try {
        await updateTableStatus(id, {
            Status: "Reserved",
            customer_name: customerName,
            customer_count: customerCount
        });

        modal.classList.remove("show");
        await loadTables();
        showPageMessage("Đặt bàn thành công.", "success");
    } catch (error) {
        showPageMessage(error.message || "Không kết nối được server.", "error");
    }
};

modalClose.onclick = () => modal.classList.remove("show");
window.onclick = (event) => {
    if (event.target === modal) {
        modal.classList.remove("show");
    }
};

navButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setActivePanel(button.dataset.panelTarget);
    });
});

if (logoutButton) logoutButton.addEventListener("click", handleLogout);

window.openBookingModal = openBookingModal;
window.cancelBooking = cancelBooking;
window.editBooking = editBooking;
window.addTable = addTable;
window.openOrder = openOrder;

window.onload = async () => {
    setActivePanel("tables");
    await loadTables();
};
