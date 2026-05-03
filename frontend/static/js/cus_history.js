const API = "http://127.0.0.1:5000";

let bookings = [];

let currentReviewReservationID = null;
let currentReviewRestaurantID = null;
export function __setBookings(data) {
    bookings = data;
}
export function initPage() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Bạn chưa đăng nhập!");
        window.location.href = "../auth/login.html";
        return;
    }

    fetch(`${API}/api/v1/customer/me`, {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
    })
        .then(res => {
            if (!res.ok) {
                alert("Phiên đăng nhập hết hạn hoặc Token sai. Vui lòng đăng nhập lại!");
                localStorage.removeItem("token");
                window.location.href = "../auth/login.html";
                throw new Error("Token invalid");
            }
            return res.json();
        })
        .then(() => {
            const historyLink = document.getElementById("historyLink");
            if (historyLink) historyLink.style.display = "block";

            loadHistory();

            const searchInput = document.getElementById("searchInput");
            const statusFilter = document.getElementById("statusFilter");

            if (searchInput) searchInput.addEventListener("keyup", filterData);
            if (statusFilter) statusFilter.addEventListener("change", filterData);
        })
        .catch(err => console.log("Lỗi check token:", err));
}

export function loadHistory() {
    const token = localStorage.getItem("token");

    return fetch(`${API}/api/v1/customer/history`, {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
    })
        .then(res => res.json())
        .then(data => {
            if (!Array.isArray(data)) {
                data = data.data || [];
            }
            bookings = data;
            renderTable(data);
        })
        .catch(err => {
            console.error("Lỗi fetch history:", err);
        });
}

export function filterData() {
    const searchInput = document.getElementById("searchInput");
    const statusFilter = document.getElementById("statusFilter");

    const key = searchInput ? searchInput.value.toLowerCase() : "";
    const status = statusFilter ? statusFilter.value : "";

    let filtered = bookings.filter(b =>
        (b.CustomerName && b.CustomerName.toLowerCase().includes(key)) ||
        String(b.ReservationID).includes(key)
    );

    if (status) {
        filtered = filtered.filter(b => b.Status === status);
    }

    renderTable(filtered);
}

export async function renderTable(data) {
    const historyContainer = document.getElementById("historyContainer");
    let html = "";

    if (!data || data.length === 0) {
        if (historyContainer) historyContainer.innerHTML = "<p>Không có dữ liệu</p>";
        return;
    }

    for (const b of data) {
        let reviewHtml = "";

        if (b.Status === "Confirmed") {
            const reviewData = await checkReview(b.ReservationID);

            if (reviewData.reviewed) {
                reviewHtml = `
                    <div class="review-box">
                        <div class="stars">
                            ${"⭐".repeat(Math.round(reviewData.rating || 0))}
                            <span class="rating-number">(${reviewData.rating}/5)</span>
                        </div>
                        <div class="review-text">
                            ${reviewData.comment || "Không có nhận xét"}
                        </div>
                    </div>`;
            } else {
                reviewHtml = `<button onclick="event.stopPropagation(); openReview(${b.RestaurantID || b.restaurant_id}, ${b.ReservationID})">⭐ Đánh giá</button>`;
            }
        }

        html += `
        <div class="history-card ${b.Status}" onclick="handleClick('${b.Status}', ${b.RestaurantID || b.restaurant_id}, ${b.ReservationID})">
            <div class="card-header">
                <h3>🍲 ${b.RestaurantName || "Nhà hàng"}</h3>
                <span class="status ${b.Status}">${b.Status}</span>
            </div>
            <div class="card-body">
                <p>📅 ${b.BookingDate} - ${b.BookingTime}</p>
                <p>👤 ${b.GuestCount} người</p>
                <p>🪑 Bàn: ${b.TableNumber || "Chưa xếp"}</p>
            </div>
            <div class="card-footer">
                ${reviewHtml}
            </div>
        </div>`;
    }

    if (historyContainer) historyContainer.innerHTML = html;
}

export async function handleClick(status, restaurantID, reservationID) {
    if (status === "Confirmed") {
        const reviewData = await checkReview(reservationID);
        openReview(restaurantID, reservationID, reviewData.rating, reviewData.comment);

    } else if (status === "Cancelled") {
        alert("Đơn đã bị hủy");
    } else {
        alert("Chưa sử dụng dịch vụ");
    }
}

export async function checkReview(reservationId) {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API}/api/v1/customer/review/check?reservation_id=${reservationId}`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    return await res.json();
}

export function goHome() {
    window.location.href = "home.html";
}

export function openReview(restaurantID, reservationID, oldRating, oldComment) {
    const reviewBox = document.getElementById("reviewBox");
    if (reviewBox) reviewBox.style.display = "flex";

    currentReviewRestaurantID = restaurantID;
    currentReviewReservationID = reservationID;

    const ratingInput = document.getElementById("rating");
    const commentInput = document.getElementById("comment");
    if (comment.length > 255) {
        alert("Bình luận tối đa 255 ký tự!");
        return;
    }
    if (ratingInput) ratingInput.value = oldRating || "";
    if (commentInput) commentInput.value = oldComment || "";
}

export function closeReview() {
    const reviewBox = document.getElementById("reviewBox");
    if (reviewBox) reviewBox.style.display = "none";
}

export function submitReview() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Vui lòng đăng nhập lại!");
        return;
    }

    if (!currentReviewRestaurantID || !currentReviewReservationID) {
        alert("Thiếu mã nhà hàng hoặc mã đơn đặt bàn! Hãy load lại trang.");
        return;
    }

    const ratingInput = document.getElementById("rating");
    const commentInput = document.getElementById("comment");

    fetch(`${API}/api/v1/customer/review`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            RestaurantID: parseInt(currentReviewRestaurantID),
            ReservationID: parseInt(currentReviewReservationID),
            Rating: parseInt(ratingInput ? ratingInput.value : 5),
            Comment: commentInput ? commentInput.value : ""
        })
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message || data.error);
            if (data.message) {
                closeReview();
                loadHistory();
            }
        })
        .catch(err => {
            console.error("Lỗi gửi review:", err);
        });
}