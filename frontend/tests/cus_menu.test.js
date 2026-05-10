/**
 * @jest-environment jsdom
 */

import { renderMenu, goBooking, goHome } from "../static/js/cus_menu";

describe("Menu JS", () => {

    beforeEach(() => {
        document.body.innerHTML = `<div id="menu"></div>`;

        global.MENU_DATA = [
            {
                restaurant_id: 1,
                name: "Phở",
                price: 50000,
                image: "img.jpg",
                description: "Ngon"
            },
            {
                restaurant_id: 2,
                name: "Bún",
                price: 40000,
                image: "bun.jpg"
            }
        ];
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    //  RENDER

    test("Không có id -> hiển thị lỗi", () => {
        window.history.pushState({}, "", "");

        renderMenu();

        expect(document.getElementById("menu").innerHTML)
            .toContain("Lỗi: không có nhà hàng");
    });

    test("Render đúng menu theo id", () => {
        window.history.pushState({}, "", "?id=1");

        renderMenu();

        const html = document.getElementById("menu").innerHTML;

        expect(html).toContain("Phở");
        expect(html).not.toContain("Bún");
    });

    test("Không có dữ liệu -> không render gì", () => {
        window.history.pushState({}, "", "?id=999");

        renderMenu();

        const html = document.getElementById("menu").innerHTML;

        expect(html).toBe("");
    });

    // LOGIC

    test("goBooking lấy đúng id từ URL", () => {
        window.history.pushState({}, "", "?id=3");

        const spy = jest.spyOn(URLSearchParams.prototype, "get");

        goBooking();

        expect(spy).toHaveBeenCalledWith("id");
    });

    test("goHome chạy không lỗi", () => {
        expect(() => goHome()).not.toThrow();
    });

});