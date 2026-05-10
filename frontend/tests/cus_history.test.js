/**
 * @jest-environment jsdom
 */

import * as historyModule from "../static/js/cus_history";

describe("History filter", () => {

    beforeEach(() => {
        document.body.innerHTML = `
            <input id="searchInput" />
            <select id="statusFilter"></select>
            <div id="historyContainer"></div>
        `;

        // mock fetch
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({
                    reviewed: false,
                    rating: 5,
                    comment: "ok"
                })
            })
        );
    });

    test("Filter theo tên + status", async () => {
        const data = [
            {
                CustomerName: "Quyen",
                RestaurantName: "Nhà hàng A",
                ReservationID: 1,
                Status: "Confirmed",
                BookingDate: "2024",
                BookingTime: "18:00",
                GuestCount: 2
            },
            {
                CustomerName: "An",
                RestaurantName: "Nhà hàng B",
                ReservationID: 2,
                Status: "Cancelled",
                BookingDate: "2024",
                BookingTime: "19:00",
                GuestCount: 4
            }
        ];

        // inject dữ liệu
        historyModule.__setBookings(data);

        document.getElementById("searchInput").value = "quyen";
        document.getElementById("statusFilter").value = "Confirmed";

        historyModule.filterData();

        // chờ render async xong
        await new Promise(r => setTimeout(r, 0));

        const html = document.getElementById("historyContainer").innerHTML;

        expect(html).toContain("Nhà hàng A");
        expect(html).not.toContain("Nhà hàng B");
    });

});