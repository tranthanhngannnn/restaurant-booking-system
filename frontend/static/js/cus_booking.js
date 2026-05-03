const API = "http://127.0.0.1:5000/api/v1/customer";

let params = new URLSearchParams(window.location.search);
let restaurant_id = params.get("restaurant_id") || params.get("id");

let selectedTable = null;
let reservationId = null;
let bookingData = {};

export function initPage() {
    const historyLink = document.getElementById("historyLink");

    fetch(`${API}/me`, {
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

    fetch(`${API}/restaurants`)
        .then(res => res.json())
        .then(data => {
            restaurantSelect.innerHTML = `<option value="">-- Chọn nhà hàng --</option>`;

            data.forEach(r => {
                const option = document.createElement("option");
                option.value = r.RestaurantID;
                option.textContent = r.RestaurantName;

                if (restaurant_id && r.RestaurantID == restaurant_id) {
                    option.selected = true;
                }

                restaurantSelect.appendChild(option);
            });

            if (restaurant_id) {
                loadRestaurantInfo(restaurant_id);
            }
        });
}

// CHANGE RESTAURANT
export function changeRestaurant(id) {
    restaurant_id = id;
    loadRestaurantInfo(id);
}

// LOAD INFO
export function loadRestaurantInfo(id) {
    fetch(`${API}/restaurant/${id}`)
        .then(res => res.json())
        .then(data => {
            const open = data.Opentime.substring(0, 5);
            const close = data.Closetime.substring(0, 5);

            timeInput.min = open;
            timeInput.max = close;

            openTime.innerText = open;
            closeTime.innerText = close;
        });
}

// TIME HELPER
export function toMinutes(t) {
    const [h, m] = t.split(":").map(Number);
    return h * 60 + m;
}

// CHECK TABLE
export function check() {
    const name = nameInput.value.trim();
    const phone = phoneInput.value.trim();
    const date = dateInput.value;
    const time = timeInput.value;
    const people = peopleInput.value;
    const open = timeInput.min;
    const close = timeInput.max;

    if (!name || !phone || !date || !time || !people) {
        alert("Vui lòng nhập đầy đủ thông tin!");
        return;
    }
    if (!/^0\d{9}$/.test(phone)) {
        alert("SĐT phải gồm 10 số và bắt đầu bằng 0");
        return;
    }

    const now = new Date();
    const inputDate = new Date(date + "T" + time);

    if (inputDate < now) {
        alert("Không thể đặt ngày trong quá khứ");
        return;
    }

    if (!restaurant_id) {
        alert("Vui lòng chọn nhà hàng!");
        return;
    }
    if (!open || !close) {
        alert("Chưa load giờ nhà hàng!");
        return;
    }

    const timeVal = toMinutes(time);
    const openVal = toMinutes(open);
    const closeVal = toMinutes(close);

    if (timeVal < openVal || timeVal > closeVal) {
        alert(`Chỉ được đặt từ ${open} đến ${close}`);
        return;
    }

    fetch(`${API}/check?restaurant_id=${restaurant_id}&date=${date}&time=${time}&people=${people}`)
        .then(async res => {
            const data = await res.json();

            if (!res.ok) {
                alert(data.error || "Có lỗi xảy ra!");
                return;
            }

            let html = "";
            data.forEach(t => {
                html += `<button onclick="selectTable(${t.TableID})">
                        Bàn ${t.TableID} (${t.Capacity})
                     </button>`;
            });

            tables.innerHTML = html;
        });
}

// SELECT TABLE
export function selectTable(id) {
    selectedTable = id;
    createBooking();
}

// CREATE BOOKING
export function createBooking() {
    const note = noteInput.value.trim();
    if (note.length > 300) {
        alert("Ghi chú tối đa 300 ký tự!");
        return;
    }
    fetch(`${API}/book`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({
            name: nameInput.value,
            phone: phoneInput.value,
            restaurant_id,
            table_id: selectedTable,
            date: dateInput.value,
            time: timeInput.value,
            people: peopleInput.value,
            note: noteInput.value
        })
    })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                alert(data.error || "Có lỗi xảy ra!");
                return;
            }

            reservationId = data.reservation_id;
            bookingData = data;
            openPayment();
        });
}

// PAYMENT
export function openPayment() {
    paymentBox.style.display = "flex";
    resId.innerText = reservationId;
    cusName.innerText = nameInput.value;
    cusPhone.innerText = phoneInput.value;
    cusDate.innerText = dateInput.value;
    cusTime.innerText = timeInput.value;
    cusPeople.innerText = peopleInput.value;
    depositText.innerText = bookingData.deposit + " VND";
    qrImg.src = bookingData.qr;
}

export function closePayment() {
    paymentBox.style.display = "none";
}

// CONFIRM
export function confirmPayment() {
    fetch(`${API}/payment`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({
            reservation_id: reservationId,
            amount: bookingData.deposit
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            closePayment();
            showSuccess();
        });
}

// SUCCESS
export function showSuccess() {
    const successBox = document.getElementById("successBox");
    successBox.style.display = "flex";
}

export function goHome() {
    window.location.href = "home.html";
}

export function logout() {
    localStorage.removeItem("token");
    window.location.href = "home.html";
}