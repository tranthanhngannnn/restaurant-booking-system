const API = "http://127.0.0.1:5000/api/v1/customer";

export function search() {
    const address = document.getElementById("address").value;
    const cuisine = document.getElementById("cuisine").value;

    return fetch(`${API}/search?address=${encodeURIComponent(address)}&cuisine=${cuisine}`)
        .then(res => res.json())
        .then(data => {
            let html = "";

            if (data.length === 0) {
                html = "<p>Không tìm thấy nhà hàng</p>";
            }

            data.forEach(r => {
                html += `
                    <div style="border:1px solid #ccc; margin:10px; padding:10px">
                        <h3>${r.RestaurantName}</h3>
                        <p>📍 ${r.Address}</p>
                        <p>📞 ${r.Phone}</p>
                        <p>${r.Available}</p>

                        <button onclick="goMenu(${r.RestaurantID})">
                            Xem chi tiết
                        </button>

                        <button onclick="goBooking(${r.RestaurantID})">
                            Đặt bàn
                        </button>
                    </div>
                `;
            });

            document.getElementById("result").innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            alert("Lỗi gọi API");
        });
}
export function redirect(url) {
    window.location.href = url;
}

export function goMenu(id, redirectFn = redirect) {
    return redirectFn(`menu.html?id=${id}`);
}

export function goBooking(id, redirectFn = redirect) {
    return redirectFn(`booking.html?id=${id}`);
}

export function initPage() {
    const historyLink = document.getElementById("historyLink");

    return fetch(`${API}/me`, {
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.logged_in) {
                historyLink.style.display = "block";
            }
        });
}