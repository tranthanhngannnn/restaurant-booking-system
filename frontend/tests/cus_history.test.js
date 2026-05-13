/**
 * @jest-environment jsdom
 */

import * as historyModule from "../static/js/cus_history";

describe("Customer History Module", () => {

    beforeEach(() => {

        // RESET DOM
        document.body.innerHTML = `
            <input id="searchInput" />
            <select id="statusFilter">
                <option value="">All</option>
                <option value="Confirmed">Confirmed</option>
                <option value="Cancelled">Cancelled</option>
            </select>

            <div id="historyContainer"></div>

            <div id="reviewBox" style="display:none"></div>

            <input id="rating" value="5" />
            <textarea id="comment"></textarea>

            <a id="historyLink"></a>
        `;

        // MOCK LOCAL STORAGE
        Storage.prototype.getItem = jest.fn((key) => {
            if (key === "token") return "fake_token";
            return null;
        });

        Storage.prototype.removeItem = jest.fn();

        // MOCK ALERT
        window.alert = jest.fn();

        // MOCK FETCH
        global.fetch = jest.fn((url) => {

            // CHECK REVIEW
            if (url.includes("/review/check")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        reviewed: false,
                        rating: 5,
                        comment: "Good"
                    })
                });
            }

            // HISTORY
            if (url.includes("/history")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([
                        {
                            CustomerName: "Quyen",
                            RestaurantName: "Nhà hàng A",
                            ReservationID: 1,
                            RestaurantID: 10,
                            Status: "Confirmed",
                            BookingDate: "2024-01-01",
                            BookingTime: "18:00",
                            GuestCount: 2
                        }
                    ])
                });
            }

            // LOGIN CHECK
            if (url.includes("/me")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        name: "Quyen"
                    })
                });
            }

            // SUBMIT REVIEW
            if (url.includes("/review")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        message: "Đánh giá thành công"
                    })
                });
            }

            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({})
            });
        });

    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    /**
     * FILTER TEST
     */
    test("Filter theo tên + status", async () => {

        const data = [
            {
                CustomerName: "Quyen",
                RestaurantName: "Nhà hàng A",
                ReservationID: 1,
                RestaurantID: 10,
                Status: "Confirmed",
                BookingDate: "2024",
                BookingTime: "18:00",
                GuestCount: 2
            },
            {
                CustomerName: "An",
                RestaurantName: "Nhà hàng B",
                ReservationID: 2,
                RestaurantID: 20,
                Status: "Cancelled",
                BookingDate: "2024",
                BookingTime: "19:00",
                GuestCount: 4
            }
        ];

        historyModule.__setBookings(data);

        document.getElementById("searchInput").value = "quyen";
        document.getElementById("statusFilter").value = "Confirmed";

        historyModule.filterData();

        await new Promise(r => setTimeout(r, 0));

        const html = document.getElementById("historyContainer").innerHTML;

        expect(html).toContain("Nhà hàng A");
        expect(html).not.toContain("Nhà hàng B");
    });

    /**
     * RENDER SUCCESS
     */
    test("Render booking thành công", async () => {

        const data = [
            {
                RestaurantName: "Nhà hàng Test",
                ReservationID: 1,
                RestaurantID: 5,
                Status: "Cancelled",
                BookingDate: "2024",
                BookingTime: "18:00",
                GuestCount: 2
            }
        ];

        await historyModule.renderTable(data);

        const html = document.getElementById("historyContainer").innerHTML;

        expect(html).toContain("Nhà hàng Test");
        expect(html).toContain("Cancelled");
    });

    /**
     * OPEN REVIEW
     */
    test("Mở popup review", () => {

        historyModule.openReview(1, 2, 5, "Good");

        expect(document.getElementById("reviewBox").style.display)
            .toBe("flex");

        expect(document.getElementById("rating").value)
            .toBe("5");

        expect(document.getElementById("comment").value)
            .toBe("Good");
    });

    /**
     * CLOSE REVIEW
     */
    test("Đóng popup review", () => {

        document.getElementById("reviewBox").style.display = "flex";

        historyModule.closeReview();

        expect(document.getElementById("reviewBox").style.display)
            .toBe("none");
    });

    /**
     * HANDLE CLICK CANCELLED
     */
    test("Handle click với trạng thái Cancelled", async () => {

        await historyModule.handleClick("Cancelled", 1, 1);

        expect(window.alert)
            .toHaveBeenCalledWith("Đơn đã bị hủy");
    });

    /**
     * HANDLE CLICK PENDING
     */
    test("Handle click với trạng thái Pending", async () => {

        await historyModule.handleClick("Pending", 1, 1);

        expect(window.alert)
            .toHaveBeenCalledWith("Chưa sử dụng dịch vụ");
    });

    /**
     * CHECK REVIEW
     */
    test("Check review thành công", async () => {

        const data = await historyModule.checkReview(1);

        expect(data.reviewed).toBe(false);
        expect(data.rating).toBe(5);
    });


//LOAD HISTORY
   test("Load history thành công", async () => {

        await historyModule.loadHistory();
        // chờ renderTable async chạy xong
        await new Promise(resolve => setTimeout(resolve, 0));

        const html = document.getElementById("historyContainer").innerHTML;

        expect(html).toContain("Nhà hàng A");
    });

    /**
     * SUBMIT REVIEW WITHOUT TOKEN
     */
    test("Submit review khi chưa login", () => {

        Storage.prototype.getItem = jest.fn(() => null);

        historyModule.submitReview();

        expect(window.alert)
            .toHaveBeenCalledWith("Vui lòng đăng nhập lại!");
    });

    /**
     * SUBMIT REVIEW SUCCESS
     */
    test("Submit review thành công", async () => {

        historyModule.openReview(1, 1);

        document.getElementById("rating").value = "5";
        document.getElementById("comment").value = "Excellent";

        historyModule.submitReview();

        await new Promise(r => setTimeout(r, 0));

        expect(window.alert)
            .toHaveBeenCalledWith("Đánh giá thành công");
    });

    /**
     * INIT PAGE SUCCESS
     */
    test("Init page thành công", async () => {

        await historyModule.initPage();

        await new Promise(r => setTimeout(r, 0));

        expect(fetch).toHaveBeenCalled();
    });

});