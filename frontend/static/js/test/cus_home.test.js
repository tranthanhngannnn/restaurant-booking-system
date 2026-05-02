/**
 * @jest-environment jsdom
 */

import { checkLogin, logout } from "../cus_home";

global.fetch = jest.fn();

describe("Home JS", () => {

    beforeEach(() => {
        document.body.innerHTML = `
            <div class="auth-buttons"></div>
            <div id="logoutBtn" style="display:none;"></div>
            <div id="historyLink" style="display:none;"></div>
            <div id="historyCard" style="display:none;"></div>
        `;

        localStorage.clear();
        fetch.mockClear();
    });

    test("Không có token -> không gọi API", () => {
        checkLogin();
        expect(fetch).not.toHaveBeenCalled();
    });

    test("Có token hợp lệ -> hiển thị UI user", async () => {
        localStorage.setItem("token", "abc");

        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ logged_in: true })
        });

        await checkLogin();

        expect(document.querySelector(".auth-buttons").style.display).toBe("none");
        expect(document.getElementById("logoutBtn").style.display).toBe("block");
    });

    test("Token lỗi -> bị xóa", async () => {
        localStorage.setItem("token", "abc");

        fetch.mockResolvedValue({
            ok: false
        });

        await checkLogin();

        expect(localStorage.getItem("token")).toBe(null);
    });

   test("Logout -> xóa token", async () => {
        localStorage.setItem("token", "abc");

        fetch.mockResolvedValue({});

        await logout();

        expect(localStorage.getItem("token")).toBe(null);
    });

});