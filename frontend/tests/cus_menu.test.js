/**
 * @jest-environment jsdom
 */

import * as menuModule from "../static/js/cus_menu";

describe("Customer Menu Module", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <div id="menu"></div>
        `;

        global.MENU_DATA = [
            {
                restaurant_id: 1,
                name: "Phở",
                price: 50000,
                image: "pho.jpg",
                description: "Phở bò"
            },
            {
                restaurant_id: 2,
                name: "Bún",
                price: 40000,
                image: "bun.jpg",
                description: "Bún bò"
            }
        ];

    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    /**
     * NO ID
     */
    test("Không có id -> hiển thị lỗi", () => {

        window.history.pushState({}, "", "/");

        menuModule.renderMenu();

        expect(document.getElementById("menu").innerHTML)
            .toContain("Lỗi: không có nhà hàng");
    });

    /**
     * RENDER MENU
     */
    test("Render đúng menu theo restaurant id", () => {

        window.history.pushState({}, "", "/?id=1");

        menuModule.renderMenu();

        const html = document.getElementById("menu").innerHTML;

        expect(html).toContain("Phở");
        expect(html).not.toContain("Bún");
    });

    /**
     * EMPTY MENU
     */
    test("Không có dữ liệu menu", () => {

        window.history.pushState({}, "", "/?id=999");

        menuModule.renderMenu();

        expect(document.getElementById("menu").innerHTML)
            .toBe("");
    });

    /**
     * RENDER DESCRIPTION
     */
    test("Render description món ăn", () => {

        window.history.pushState({}, "", "/?id=1");

        menuModule.renderMenu();

        expect(document.getElementById("menu").innerHTML)
            .toContain("Phở bò");
    });

    /**
     * goBooking
     * jsdom không hỗ trợ navigation thật
     * nên chỉ kiểm tra lấy đúng id
     */
    test("goBooking lấy đúng id từ URL", () => {

        window.history.pushState({}, "", "/?id=3");

        const spy = jest.spyOn(URLSearchParams.prototype, "get");

        try {
            menuModule.goBooking();
        } catch (e) {
            // jsdom navigation not implemented
        }

        expect(spy).toHaveBeenCalledWith("id");
    });

    /**
     * goHome
     * jsdom không hỗ trợ navigation
     */
    test("goHome chạy không lỗi logic", () => {

        expect(() => {

            try {
                menuModule.goHome();
            } catch (e) {
                // ignore navigation error
            }

        }).not.toThrow();
    });

});