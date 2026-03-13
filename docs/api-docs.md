# TÀI LIỆU API
## Restaurant Booking System

---

## 1. Giới thiệu

Hệ thống **Restaurant Booking System** cho phép khách hàng tìm kiếm nhà hàng, xem menu và đặt bàn online.

Hệ thống có **3 vai trò chính**:

- **Khách hàng (Customer)**: tìm nhà hàng, xem menu, đặt bàn
- **Nhà hàng (Restaurant)**: quản lý bàn, menu, xác nhận đặt bàn
- **Admin**: quản lý nhà hàng, duyệt nhà hàng mới, quản lý danh mục cuisine

---

# 2. Customer APIs

## Tìm kiếm nhà hàng

GET /api/restaurants

Query params

location  
cuisine  

Example request

GET /api/restaurants?location=hcm&cuisine=bbq

Response

```json
[
 {
  "id":1,
  "name":"BBQ House",
  "location":"HCM",
  "cuisine":"BBQ"
 }
]
```

Xem menu nhà hàng
```json
GET /api/restaurants/{id}/menu
Example
GET /api/restaurants/1/menu
```
Response
```json
[
 {
  "id":1,
  "name":"Beef BBQ",
  "price":120000
 }
]
```

Đặt bàn
POST /api/reservations
Request body
```json
{
 "restaurant_id":1,
 "date":"2026-04-01",
 "time":"18:00",
 "people":4
 "statue":"pending"
}
```

Response
```json
{
 "message":"Reservation created successfully"
}
```

3. Restaurant APIs
Xem danh sách đặt bàn
GET /api/restaurant/reservations

Xác nhận đặt bàn
PUT /api/reservations/{id}/confirm
Response
```json
{
 "message":"Reservation confirmed"
}
```

Từ chối đặt bàn
PUT /api/reservations/{id}/reject
Response
```json
{
 "message":"Reservation rejected"
}
```

Quản lý menu
Thêm món
POST /api/menu
```json
{
 "name":"Seafood Pizza",
 "price":150000
}
```

Cập nhật món
PUT /api/menu/{id}

Xóa món
DELETE /api/menu/{id}

4. Admin APIs
Duyệt nhà hàng
PUT /api/admin/restaurants/{id}/approve

Quản lý nhà hàng
GET /api/admin/restaurants
POST /api/admin/restaurants
PUT /api/admin/restaurants/{id}
DELETE /api/admin/restaurants/{id}

Quản lý cuisine
GET /api/admin/cuisines
POST /api/admin/cuisines
DELETE /api/admin/cuisines/{id}

5. Luồng hệ thống
Customer → tìm nhà hàng → xem menu → đặt bàn
Restaurant → xác nhận hoặc từ chối đặt bàn
Admin → duyệt nhà hàng → quản lý cuisine

6. API đăng ký / đăng nhập
Nếu hệ thống có người dùng.
Đăng ký
POST /api/register
Request
```json
{
 "name":"Nguyen Van A",
 "email":"a@gmail.com",
 "password":"123456"
}
```

Đăng nhập
POST /api/login
```json
{
 "email":"a@gmail.com",
 "password":"123456"
}
```

Response
```json
{
 "token":"jwt_token_here"
}
```

8. API xem chi tiết nhà hàng
Hiện bạn chỉ có tìm nhà hàng, nên nên thêm:
GET /api/restaurants/{id}
Response
```json
{
 "id":1,
 "name":"BBQ House",
 "location":"HCM",
 "cuisine":"BBQ",
 "rating":4.5
}
```

9. API thêm nhà hàng (business user)
POST /api/restaurants
```json
{
 "name":"Seafood House",
 "location":"HCM",
 "cuisine":"Seafood"
}
```

11. API báo cáo (Admin)
GET /api/admin/reports
Response
```json
{
 "total_restaurants":20,
 "total_reservations":150
}
```
