/**
 * @jest-environment jsdom
 */

import * as searchModule from "../static/js/cus_search";

global.fetch = jest.fn();

describe("Customer Search Module", () => {

    beforeEach(() => {

        document.body.innerHTML = `
            <input id="address" value="HCM" />

            <select id="cuisine">
                <option value="1" selected>Lẩu</option>
            </select>

            <div id="result"></div>

            <div id="historyLink" style="display:none;"></div>
        `;

        fetch.mockClear();

        localStorage.clear();

        window.alert = jest.fn();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    /**
     * SEARCH API
     */
    test("Search API được gọi đúng", async () => {

        fetch.mockResolvedValue({
            json: async () => []
        });

        await searchModule.search();

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/search?")
        );
    });

    /**
     * EMPTY RESULT
     */
    test("Hiển thị khi không có kết quả", async () => {

        fetch.mockResolvedValue({
            json: async () => []
        });

        await searchModule.search();

        expect(document.getElementById("result").innerHTML)
            .toContain("Không tìm thấy nhà hàng");
    });

    /**
     * RENDER RESTAURANT
     */
    test("Hiển thị danh sách nhà hàng", async () => {

        fetch.mockResolvedValue({
            json: async () => ([
                {
                    RestaurantID: 1,
                    RestaurantName: "Test Restaurant",
                    Address: "HCM",
                    Phone: "123456",
                    Available: "Available"
                }
            ])
        });

        await searchModule.search();

        const html = document.getElementById("result").innerHTML;

        expect(html).toContain("Test Restaurant");
        expect(html).toContain("HCM");
        expect(html).toContain("123456");
    });

    /**
     * SEARCH API ERROR
     */
    test("Hiển thị alert khi API lỗi", async () => {

        fetch.mockRejectedValue(new Error("API ERROR"));

        await searchModule.search();

        expect(window.alert)
            .toHaveBeenCalledWith("Lỗi gọi API");
    });

    /**
     * goMenu
     */
    test("goMenu gọi redirect đúng", () => {

        const mockRedirect = jest.fn();

        searchModule.goMenu(5, mockRedirect);

        expect(mockRedirect)
            .toHaveBeenCalledWith("menu.html?id=5");
    });

    /**
     * goBooking
     */
    test("goBooking gọi redirect đúng", () => {

        const mockRedirect = jest.fn();

        searchModule.goBooking(10, mockRedirect);

        expect(mockRedirect)
            .toHaveBeenCalledWith("booking.html?id=10");
    });

    /**
     * redirect
     * jsdom không hỗ trợ navigation thật
     * nên chỉ verify function tồn tại
     */
    test("redirect function tồn tại", () => {

        expect(typeof searchModule.redirect)
            .toBe("function");
    });

    /**
     * INIT PAGE LOGIN
     */
    test("initPage hiển thị history khi login", async () => {

        localStorage.setItem("token", "abc");

        fetch.mockResolvedValue({
            json: async () => ({
                logged_in: true
            })
        });

        await searchModule.initPage();

        expect(document.getElementById("historyLink").style.display)
            .toBe("block");
    });

    /**
     * INIT PAGE NOT LOGIN
     */
    test("initPage không hiển thị history khi chưa login", async () => {

        fetch.mockResolvedValue({
            json: async () => ({
                logged_in: false
            })
        });

        await searchModule.initPage();

        expect(document.getElementById("historyLink").style.display)
            .toBe("none");
    });

});