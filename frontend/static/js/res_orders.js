//  INIT
const tableId = new URLSearchParams(window.location.search).get("table_id");
const tableDisplay = document.getElementById("table-id");
if (tableDisplay) tableDisplay.innerText = tableId;

let order = [];

// localStorage Key for persistence
const STORAGE_KEY = `cart_table_${tableId}`;

// Save cart to localStorage
function saveToLocalStorage() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
}

// Load cart from localStorage
function loadFromLocalStorage() {
    const savedOrder = localStorage.getItem(STORAGE_KEY);
    if (savedOrder) {
        order = JSON.parse(savedOrder);
        renderOrder();
    }
}

// LOAD MENU
async function loadMenu() {
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/restaurant/menu`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.length > 0) {
            renderMenu(data);
        } else {
            console.log("Không có món hoặc lỗi!");
        }

    } catch (error) {
        console.error("Lỗi fetch menu:", error);
    }
}

//  RENDER MENU
function renderMenu(data) {
    const menuContainer = document.getElementById('menu-list');
    if (!menuContainer) return;

    const html = data.map(item => {
        const image = item.image || 'https://via.placeholder.com/150?text=No+Image';

        return `
            <div class="menu-item">
                <div class="item-image">
                    <img src="${image}" onerror="this.src='https://via.placeholder.com/150?text=No+Image';">
                </div>
                <div class="item-info">
                    <h3>${item.name}</h3>
                    <p class="price">${Number(item.price).toLocaleString()}đ</p>
                    <button class="btn-add"
                        onclick="addItem('${item.id}', '${item.name}', ${item.price}, '${image}')">
                        Thêm
                    </button>
                </div>
            </div>
        `;
    }).join('');

    menuContainer.innerHTML = html;
}

//  ADD ITEM
function addItem(food_id, name, price, image) {
    const item = order.find(i => i.food_id === food_id);

    if (item) {
        item.qty++;
    } else {
        order.push({
            food_id,
            name,
            price: parseFloat(price),
            qty: 1,
            image
        });
    }

    renderOrder();
    saveToLocalStorage(); // Lưu vào localStorage mỗi khi thêm món
}

//  RENDER ORDER
function renderOrder() {
    const list = document.getElementById("order-list");
    if (!list) return;

    list.innerHTML = "";
    let total = 0;

    order.forEach(i => {
        total += i.price * i.qty;

        const li = document.createElement("li");
        li.innerHTML = `
            ${i.name}
            <button onclick="changeQty('${i.food_id}', -1)">-</button>
            ${i.qty}
            <button onclick="changeQty('${i.food_id}', 1)">+</button>
            - ${(i.price * i.qty).toLocaleString()}đ
        `;
        list.appendChild(li);
    });

    document.getElementById("total").innerText = total.toLocaleString();
}

function changeQty(food_id, delta) {
    const item = order.find(i => i.food_id === food_id);
    if (!item) return;

    item.qty += delta;

    if (item.qty <= 0) {
        order = order.filter(i => i.food_id !== food_id);
    }

    renderOrder();
    saveToLocalStorage(); // Lưu vào localStorage mỗi khi thay đổi số lượng
}

//  CREATE ORDER
async function createOrder() {
    if (order.length === 0) {
        alert("Chưa có món");
        return;
    }

    const res = await fetch("http://127.0.0.1:5000/api/v1/restaurant/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            table_id: parseInt(tableId),
            items: order.map(i => ({
                food_id: i.food_id,
                qty: i.qty
            }))
        })
    });

    const data = await res.json();

    console.log("CREATE ORDER:", data);

    if (res.ok) {
        alert("Đã gửi order");
    } else {
        alert("Lỗi gửi order");
    }
}

// PAY ORDER
async function payOrder() {
    if (!confirm("Thanh toán bàn này?")) return;

    const res = await fetch(
        `http://127.0.0.1:5000/api/v1/restaurant/orders/pay/${tableId}`,
        { method: "PUT" }
    );

    const data = await res.json();
    console.log("PAY:", data);

    if (res.ok) {
        alert("Thanh toán thành công");

        // XÓA LOCALSTORAGE KHI THANH TOÁN THÀNH CÔNG
        localStorage.removeItem(`cart_table_${tableId}`);

        order = []; // clear UI
        renderOrder();
        localStorage.removeItem(STORAGE_KEY); // Xóa localStorage sau khi thanh toán thành công

        window.location.href = "table.html";
    } else {
        alert("Lỗi thanh toán");
    }
}

async function loadOrderFromServer() {
    try {
        const res = await fetch(
            `http://127.0.0.1:5000/api/v1/restaurant/orders/${tableId}`
        );

        const data = await res.json();
        console.log("ORDER DATA:", data);

        // Nếu server có dữ liệu cũ, ta load nó
        if (data.items && data.items.length > 0) {
            order = data.items;
            renderOrder();
            saveToLocalStorage();
        }

    } catch (err) {
        console.log("Lỗi load order:", err);
        loadFromLocalStorage();
    }
}

function handleLogout() {
    if (!confirm("Bạn có chắc muốn đăng xuất không?")) return;
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "../auth/login.html";
}

window.onload = () => {
    loadMenu();

    // Ưu tiên load từ localStorage (draft)
    const savedOrder = localStorage.getItem(`cart_table_${tableId}`);
    if (savedOrder && JSON.parse(savedOrder).length > 0) {
        console.log("Loading order from localStorage");
        order = JSON.parse(savedOrder);
        renderOrder();
    } else {
        // Nếu không có draft, mới load từ server
        loadOrderFromServer();
    }
};
module.exports = {
    loadMenu,
    renderMenu,
    addItem,
    renderOrder,
    changeQty,
    createOrder,
    payOrder,
    loadOrderFromServer,
    saveToLocalStorage,
    loadFromLocalStorage
};