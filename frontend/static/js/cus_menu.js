

export function renderMenu() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    if (!id) {
        document.getElementById("menu").innerHTML = "<p>Lỗi: không có nhà hàng</p>";
        return;
    }

    let html = "";
    const filtered = MENU_DATA.filter(m => m.restaurant_id == id);

    filtered.forEach(m => {
        html += `
            <div class="food-item">
                <img src="${m.image}" class="food-img">
                <h3>${m.name}</h3>
                <p> ${m.price} VND</p>
                <div class="desc">${m.description || ""}</div>
            </div>
        `;
    });

    document.getElementById("menu").innerHTML = html;
}

export function goBooking() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    window.location.href = `booking.html?id=${id}`;
}

export function goHome() {
    window.location.href = `search.html`;
}