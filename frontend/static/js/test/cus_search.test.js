/**
 * @jest-environment jsdom
 */

import * as searchModule from "../cus_search";

global.fetch = jest.fn();

describe("Search JS", () => {

    beforeEach(() => {
        document.body.innerHTML = `
            <input id="address" value="HCM">
            <select id="cuisine">
                <option value="1" selected>Lẩu</option>
            </select>
            <div id="result"></div>
            <div id="historyLink" style="display:none;"></div>
        `;

        fetch.mockClear();
        localStorage.clear();
    });

    // SEARCH

    test("Search API được gọi đúng", async () => {
        fetch.mockResolvedValue({
            json: async () => []
        });

        await searchModule.search();

        expect(fetch).toHaveBeenCalled();
    });

    test("Hiển thị khi không có kết quả", async () => {
        fetch.mockResolvedValue({
            json: async () => []
        });

        await searchModule.search();

        expect(document.getElementById("result").innerHTML)
            .toContain("Không tìm thấy nhà hàng");
    });

    test("Hiển thị danh sách nhà hàng", async () => {
        fetch.mockResolvedValue({
            json: async () => ([
                {
                    RestaurantID: 1,
                    RestaurantName: "Test",
                    Address: "HCM",
                    Phone: "123",
                    Available: "Yes"
                }
            ])
        });

        await searchModule.search();

        expect(document.getElementById("result").innerHTML)
            .toContain("Test");
    });

    //  NAVIGATION

    test("goMenu gọi redirect đúng", () => {
        const mockRedirect = jest.fn();

        searchModule.goMenu(5, mockRedirect);

        expect(mockRedirect).toHaveBeenCalledWith("menu.html?id=5");
    });

    test("goBooking gọi redirect đúng", () => {
        const mockRedirect = jest.fn();

        searchModule.goBooking(10, mockRedirect);

        expect(mockRedirect).toHaveBeenCalledWith("booking.html?id=10");
    });
    //  INIT PAGE

    test("initPage hiển thị history khi login", async () => {
        localStorage.setItem("token", "abc");

        fetch.mockResolvedValue({
            json: async () => ({ logged_in: true })
        });

        await searchModule.initPage();

        expect(document.getElementById("historyLink").style.display)
            .toBe("block");
    });

});