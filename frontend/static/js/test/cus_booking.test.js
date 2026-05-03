/**
 * @jest-environment jsdom
 */

import { toMinutes, check } from "../cus_booking";

describe("Booking Utils", () => {

    test("toMinutes hoạt động đúng", () => {
        expect(toMinutes("10:30")).toBe(630);
        expect(toMinutes("00:00")).toBe(0);
    });

});

describe("Booking Validation", () => {

    beforeEach(() => {
        document.body.innerHTML = `
            <input id="nameInput" value="A">
            <input id="phoneInput" value="0123456789">
            <input id="dateInput" value="2099-01-01">
            <input id="timeInput" value="10:00">
            <input id="peopleInput" value="2">
        `;

        global.alert = jest.fn();
    });

    test("Thiếu input -> báo lỗi", () => {
        document.getElementById("nameInput").value = "";

        check();

        expect(alert).toHaveBeenCalled();
    });

    test("Phone sai format", () => {
        document.getElementById("phoneInput").value = "123";

        check();

        expect(alert).toHaveBeenCalledWith(
            "SĐT phải gồm 10 số và bắt đầu bằng 0"
        );
    });

});