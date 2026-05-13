/**
 * UNIT TEST
 * File: res_orders.test.js
 *
 * Chức năng test:
 * - addItem()
 * - changeQty()
 * - renderOrder()
 * - createOrder()
 * - payOrder()
 * - loadMenu()
 */

// MOCK DOM

document.body.innerHTML = `
    <div id="menu-list"></div>
    <ul id="order-list"></ul>
    <span id="total"></span>
    <div id="table-id"></div>
`;


// MOCK URL PARAM
delete window.location;

window.history.pushState(
    {},
    "",
    "/orders.html?table_id=1"
);
// IMPORT MODULE
const {
    addItem,
    changeQty,
    renderOrder,
    createOrder,
    payOrder,
    loadMenu
} = require("../static/js/res_orders");


// MOCK GLOBAL
global.fetch = jest.fn();
global.alert = jest.fn();
global.confirm = jest.fn();


// MOCK localStorage
Storage.prototype.getItem = jest.fn((key) => {

    if (key === "token") {
        return "fake_token";
    }

    return null;
});

Storage.prototype.setItem = jest.fn();

Storage.prototype.removeItem = jest.fn();

// TEST addItem()
describe("addItem()", () => {

    test("Thêm món mới vào order", () => {

        addItem("F1", "Cơm chiên", 50000, "img.jpg");

        expect(
            document.getElementById("order-list").innerHTML
        ).toContain("Cơm chiên");
    });


    test("Tăng số lượng khi món đã tồn tại", () => {

        addItem("F1", "Cơm chiên", 50000, "img.jpg");

        expect(
            document.getElementById("order-list").innerHTML
        ).toContain("2");
    });

});


// TEST changeQty()
describe("changeQty()", () => {

    test("Tăng số lượng món", () => {

        changeQty("F1", 1);

        expect(
            document.getElementById("order-list").innerHTML
        ).toContain("3");
    });


    test("Giảm số lượng món", () => {

        changeQty("F1", -1);

        expect(
            document.getElementById("order-list").innerHTML
        ).toContain("2");
    });

});


// TEST renderOrder()
describe("renderOrder()", () => {

    test("Hiển thị tổng tiền", () => {

        renderOrder();

        expect(
            document.getElementById("total").innerText
        ).not.toBe("");
    });

});


// TEST loadMenu()
describe("loadMenu()", () => {

    beforeEach(() => {
        fetch.mockClear();
    });
    test("Load menu thành công", async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ([
                {
                    id: "F1",
                    name: "Pizza",
                    price: 100000,
                    image: "pizza.jpg"
                }
            ])
        });

        await loadMenu();
        expect(
            document.getElementById("menu-list").innerHTML
        ).toContain("Pizza");
    });

});


// TEST createOrder()
describe("createOrder()", () => {

    beforeEach(() => {
        fetch.mockClear();
    });


    test("Tạo order thành công", async () => {

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                message: "Success"
            })
        });

        await createOrder();

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/orders"),
            expect.objectContaining({
                method: "POST"
            })
        );

        expect(alert).toHaveBeenCalledWith("Đã gửi order");
    });


    test("Tạo order thất bại", async () => {

        fetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({
                message: "Error"
            })
        });

        await createOrder();

        expect(alert).toHaveBeenCalledWith("Lỗi gửi order");
    });

});


// TEST payOrder()
describe("payOrder()", () => {

    beforeEach(() => {
        fetch.mockClear();
    });


    test("Thanh toán thành công", async () => {

        confirm.mockReturnValue(true);

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                message: "Paid"
            })
        });

        await payOrder();

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/orders/pay/1"),
            expect.objectContaining({
                method: "PUT"
            })
        );

        expect(alert).toHaveBeenCalledWith(
            "Thanh toán thành công"
        );
    });


    test("User hủy thanh toán", async () => {

        confirm.mockReturnValue(false);

        await payOrder();

        expect(fetch).not.toHaveBeenCalled();
    });


    test("Thanh toán thất bại", async () => {

        confirm.mockReturnValue(true);

        fetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({
                message: "Fail"
            })
        });

        await payOrder();

        expect(alert).toHaveBeenCalledWith(
            "Lỗi thanh toán"
        );
    });

});