//  Toàn bộ dữ liệu menu
const MENU_DATA = [
   { id: "LT", name: 'Lẩu Thái', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu chua cay kiểu Thái với hải sản tươi và rau', image: '/static/images/Food/Lau/lauthai.jpg' },
   { id: "LM", name: 'Lẩu Mala', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cay tê đặc trưng Tứ Xuyên với nhiều loại topping', image: '/static/images/Food/Lau/laumala.jpg' },
   { id: "LCD", name: 'Lẩu Cua Đồng', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cua đồng đậm vị truyền thống ăn kèm rau tươi', image: '/static/images/Food/Lau/cuadong.webp' },
   { id: "LKC", name: 'Lẩu Kimchi', restaurant_id: 1, category_id: 3, price: 60000, description:'Lẩu kimchi Hàn Quốc cay nhẹ với thịt và đậu hũ', image: '/static/images/Food/Lau/laukimchi.webp' },
   { id: "LTX", name: 'Lẩu Tứ Xuyên', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cay nồng đậm vị tiêu hoa Tứ Xuyên', image: '/static/images/Food/Lau/lautuxuyen.jpg' },
   { id: "LBNG", name: 'Lẩu Bò Nhúng Giấm', restaurant_id: 1, category_id: 3, price: 50000, description:'Thịt bò tươi nhúng giấm chua nhẹ ăn kèm rau', image: '/static/images/Food/Lau/laubonhunggiam.jpg' },
   { id: "STN", name: 'Set Thịt Nhỏ', restaurant_id: 1, category_id: 1, price: 120000, description:'Set thịt nhỏ gồm bò, heo và rau ăn kèm', image: '/static/images/Food/Lau/setthitnho.jpg' },
   { id: "HSTH", name: 'Hải Sản Tổng Hợp', restaurant_id: 1, category_id: 1, price: 150000, description:'Combo hải sản gồm tôm, mực, nghêu tươi', image: '/static/images/Food/Lau/haisantonghop.jpg' },
   { id: "CBRN", name: 'Combo Rau Nấm', restaurant_id: 1, category_id: 1, price: 100000, description:'Combo rau và nấm tươi ăn kèm lẩu', image: '/static/images/Food/Lau/comboraunam.jpg' },
   { id: "STL", name: 'Set Thịt Lớn', restaurant_id: 1, category_id: 1, price: 240000, description:'Set thịt lớn tẩm ướp đậm vị dùng với lẩu', image: '/static/images/Food/Lau/setthitlon.jpg' },
   { id: "SVTL", name: 'Set Viên Thả Lẩu', restaurant_id: 1, category_id: 1, price: 100000, description:'Các loại viên thả lẩu như bò viên, cá viên', image: '/static/images/Food/Lau/setvienthalau.jpg' },
   { id: "BFTM", name: 'Buffet Tráng Miệng', restaurant_id: 1, category_id: 7, price: 50000, description:'Buffet trái cây và nước tráng miệng', image: '/static/images/Food/Lau/buffettrangmieng.jpg' },


   //dữ liệu món nướng
   { id: "BCBM", name: 'Ba Chỉ Bò Mỹ', restaurant_id: 2, category_id: 5, price: 90000, description:'Thịt ba chỉ bò Mỹ mềm, thích hợp nướng', image: '/static/images/Food/Nuong/bachibomy.png' },
   { id: "LVB", name: 'Lõi Vai Bò', restaurant_id: 2, category_id: 5, price: 90000, description:'Phần lõi vai bò mềm, ít mỡ, nướng rất đậm vị', image: '/static/images/Food/Nuong/loivaibo.jpg' },
   { id: "THI", name: 'Thịt Heo Iberico', restaurant_id: 2, category_id: 5, price: 70000, description:'Thịt heo Iberico cao cấp, mềm ngọt tự nhiên', image: '/static/images/Food/Nuong/thitheoiberico.jpg' },
   { id: "KC", name: 'Kimchi', restaurant_id: 2, category_id: 8, price: 25000, description:'Kimchi cải thảo chua cay kiểu Hàn Quốc', image: '/static/images/Food/Nuong/kimchi.jpg' },
   { id: "BTM", name: 'Bạch Tuộc Mini', restaurant_id: 2, category_id: 2, price: 85000, description:'Bạch tuộc mini tươi giòn thích hợp nướng', image: '/static/images/Food/Nuong/bachtuocmini.jpg' },
   { id: "SDMH", name: 'Sò Điệp Mỡ Hành', restaurant_id: 2, category_id: 6, price: 85000, description:'Sò điệp tươi nướng mỡ hành thơm béo', image: '/static/images/Food/Nuong/sodiepnuongmohanh.jpg' },
   { id: "SNMO", name: 'Sườn Non Ướp Mật Ong', restaurant_id: 2, category_id: 6, price: 120000, description:'Sườn non tẩm mật ong nướng thơm ngọt', image: '/static/images/Food/Nuong/suonnonuopmatong.jpg' },
   { id: "RSAK", name: 'Rau Sống Ăn Kèm', restaurant_id: 2, category_id: 5, price: 90000, description:'Rau sống tươi ăn kèm các món nướng', image: '/static/images/Food/Nuong/rausongankem' },
   { id: "CMN", name: 'Combo Nấm', restaurant_id: 2, category_id: 1, price: 100000, description:'Combo nhiều loại nấm tươi ăn kèm món nướng', image: '/static/images/Food/Nuong/combonam.png' },
   { id: "TNST", name: 'Tôm Nướng Sa Tế', restaurant_id: 2, category_id: 6, price: 240000, description:'Tôm tươi nướng sa tế cay thơm', image: '/static/images/Food/Nuong/tomnuongsate.jpg' },
   { id: "NVH", name: 'Nạc Vai Heo', restaurant_id: 2, category_id: 5, price: 100000, description:'Thịt nạc vai heo mềm, thích hợp nướng BBQ', image: '/static/images/Food/Nuong/nacvaiheo.jpg' },
   { id: "TCTH", name: 'Trái Cây Tổng Hợp', restaurant_id: 2, category_id: 7, price: 100000, description:'Đĩa trái cây tươi theo mùa tráng miệng', image: '/static/images/Food/Nuong/traicaytonghop.jpg' }
   ];


