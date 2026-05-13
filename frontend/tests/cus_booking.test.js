/**
 * @jest-environment jsdom
 */

import * as booking from "../static/js/cus_booking";

import {
    toMinutes,
    check,
    createBooking,
    closePayment,
    showSuccess,
    logout,
    loadRestaurantInfo,
    changeRestaurant,
    selectTable,
    confirmPayment
} from "../static/js/cus_booking";



// BOOKING UTILS
describe("Booking Utils", () => {

    test("toMinutes hoạt động đúng", () => {

        expect(toMinutes("10:30")).toBe(630);
        expect(toMinutes("00:00")).toBe(0);
        expect(toMinutes("23:59")).toBe(1439);

    });

});


// BOOKING VALIDATION
describe("Booking Validation", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <select id="restaurantSelect">
                <option value="1" selected>Restaurant</option>
            </select>
            <input id="nameInput" value="Nguyen Van A">
            <input id="phoneInput" value="0123456789">
            <input id="dateInput" value="2099-01-01">
            <input id="timeInput" value="10:00" min="08:00" max="22:00">
            <input id="peopleInput" value="2">
            <textarea id="noteInput"></textarea>

            <div id="tables"></div>

            <div id="paymentBox" style="display:none"></div>
            <div id="successBox" style="display:none"></div>

            <span id="resId"></span>
            <span id="cusName"></span>
            <span id="cusPhone"></span>
            <span id="cusDate"></span>
            <span id="cusTime"></span>
            <span id="cusPeople"></span>
            <span id="depositText"></span>

            <span id="openTime"></span>
            <span id="closeTime"></span>

            <img id="qrImg">
        `;

        global.nameInput =document.getElementById("nameInput");
        global.phoneInput =document.getElementById("phoneInput");
        global.dateInput =document.getElementById("dateInput");
        global.timeInput =document.getElementById("timeInput");
        global.peopleInput =document.getElementById("peopleInput");
        global.restaurantSelect = document.getElementById("restaurantSelect");
        global.noteInput =document.getElementById("noteInput");
        global.tables =document.getElementById("tables");
        global.paymentBox =document.getElementById("paymentBox");
        global.successBox =document.getElementById("successBox");
        global.resId =document.getElementById("resId");
        global.cusName =document.getElementById("cusName");
        global.cusPhone =document.getElementById("cusPhone");
        global.cusDate =document.getElementById("cusDate");
        global.cusTime =document.getElementById("cusTime");
        global.cusPeople =document.getElementById("cusPeople");
        global.depositText =document.getElementById("depositText");
        global.qrImg =document.getElementById("qrImg");
        global.openTime =document.getElementById("openTime");
        global.closeTime =document.getElementById("closeTime");
        global.alert = jest.fn();

        global.fetch = jest.fn((url) => {

            if (url.includes("/restaurant/")) {

                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        Opentime: "08:00:00",
                        Closetime: "22:00:00"
                    })
                });

            }

            if (url.includes("/check")) {

                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([])
                });

            }

            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({})
            });

        });

    });


    // CHECK VALIDATION
    test("Thiếu input -> báo lỗi", async () => {

        nameInput.value = "";

        await check();

        expect(alert).toHaveBeenCalled();

    });

    test("Phone sai format", async () => {

        phoneInput.value = "123";

        await check();

        expect(alert).toHaveBeenCalledWith(
            "SĐT phải gồm 10 số và bắt đầu bằng 0"
        );

    });

    test("Ngày giờ quá khứ -> báo lỗi", async () => {

        dateInput.value = "2000-01-01";

        await check();

        expect(alert).toHaveBeenCalledWith(
            "Không thể đặt ngày, giờ trong quá khứ"
        );

    });

    test("Đặt bàn dưới 30 phút -> báo lỗi", async () => {

        const now = new Date();

        const future = new Date(
            now.getTime() + 10 * 60 * 1000
        );

        const date = future
            .toISOString()
            .split("T")[0];

        const time =
            future.getHours()
                .toString()
                .padStart(2, "0")
            + ":" +
            future.getMinutes()
                .toString()
                .padStart(2, "0");

        dateInput.value = date;
        timeInput.value = time;

        await check();

        expect(alert).toHaveBeenCalledWith(
            "Phải đặt trước ít nhất 30 phút"
        );

    });

    test("Đặt ngoài giờ mở cửa -> báo lỗi", async () => {

        timeInput.value = "23:00";

        await check();

        expect(alert).toHaveBeenCalled();

    });
});


// CHANGE RESTAURANT
describe("Change Restaurant", () => {

    test("changeRestaurant hoạt động", () => {

        expect(() => changeRestaurant(5))
            .not.toThrow();

    });

});


describe("Select Table", () => {

    test("selectTable hoạt động", () => {

        expect(() => selectTable(2))
            .not.toThrow();

    });

});


// CREATE BOOKING
describe("Create Booking", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <textarea id="noteInput"></textarea>

            <input id="nameInput" value="Nguyen Van A">
            <input id="phoneInput" value="0123456789">
            <input id="dateInput" value="2099-01-01">
            <input id="timeInput" value="10:00">
            <input id="peopleInput" value="2">

            <div id="paymentBox"></div>
            <div id="successBox"></div>

            <span id="resId"></span>
            <span id="cusName"></span>
            <span id="cusPhone"></span>
            <span id="cusDate"></span>
            <span id="cusTime"></span>
            <span id="cusPeople"></span>
            <span id="depositText"></span>

            <img id="qrImg">
        `;

        global.noteInput =
            document.getElementById("noteInput");

        global.nameInput =
            document.getElementById("nameInput");

        global.phoneInput =
            document.getElementById("phoneInput");

        global.dateInput =
            document.getElementById("dateInput");

        global.timeInput =
            document.getElementById("timeInput");

        global.peopleInput =
            document.getElementById("peopleInput");

        global.paymentBox =
            document.getElementById("paymentBox");

        global.successBox =
            document.getElementById("successBox");

        global.resId =
            document.getElementById("resId");

        global.cusName =
            document.getElementById("cusName");

        global.cusPhone =
            document.getElementById("cusPhone");

        global.cusDate =
            document.getElementById("cusDate");

        global.cusTime =
            document.getElementById("cusTime");

        global.cusPeople =
            document.getElementById("cusPeople");

        global.depositText =
            document.getElementById("depositText");

        global.qrImg =
            document.getElementById("qrImg");

        global.alert = jest.fn();

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({
                    reservation_id: 1,
                    deposit: 100000,
                    qr: "QR_LINK"
                })
            })
        );

    });

    test("Note vượt 300 ký tự -> báo lỗi", async () => {

        noteInput.value = "A".repeat(301);

        await createBooking();

        expect(alert).toHaveBeenCalled();

    });

    test("createBooking gọi API thành công", async () => {

        noteInput.value = "Test";

        await createBooking();

        expect(fetch).toHaveBeenCalled();

    });

});

// PAYMENT
describe("Payment", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <div id="successBox" style="display:none"></div>
            <div id="paymentBox" style="display:flex"></div>
        `;

        global.successBox =
            document.getElementById("successBox");

        global.paymentBox =
            document.getElementById("paymentBox");

        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({})
            })
        );

    });

    test("confirmPayment gọi payment API", async () => {

        await confirmPayment();

        expect(fetch).toHaveBeenCalled();

    });

});



// PAYMENT UI

describe("Payment UI", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <div id="paymentBox" style="display:none"></div>
            <div id="successBox" style="display:none"></div>
        `;

        global.paymentBox =
            document.getElementById("paymentBox");

        global.successBox =
            document.getElementById("successBox");

    });

    test("closePayment ẩn popup", () => {

        closePayment();

        expect(paymentBox.style.display)
            .toBe("none");

    });

    test("showSuccess hiển thị popup success", () => {

        showSuccess();

        expect(successBox.style.display)
            .toBe("flex");

    });

});


// LOGOUT
describe("Logout", () => {

    test("logout xóa token", () => {

        Storage.prototype.removeItem = jest.fn();

        expect(() => logout())
            .not.toThrow();

        expect(localStorage.removeItem)
            .toHaveBeenCalledWith("token");

    });

});