<<<<<<< HEAD
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
   { id: "RSAK", name: 'Rau Sống Ăn Kèm', restaurant_id: 2, category_id: 5, price: 90000, description:'Rau sống tươi ăn kèm các món nướng', image: '/static/images/Food/Nuong/rausongankem.jpg' },
   { id: "CMN", name: 'Combo Nấm', restaurant_id: 2, category_id: 1, price: 100000, description:'Combo nhiều loại nấm tươi ăn kèm món nướng', image: '/static/images/Food/Nuong/combonam.png' },
   { id: "TNST", name: 'Tôm Nướng Sa Tế', restaurant_id: 2, category_id: 6, price: 240000, description:'Tôm tươi nướng sa tế cay thơm', image: '/static/images/Food/Nuong/tomnuongsate.jpg' },
   { id: "NVH", name: 'Nạc Vai Heo', restaurant_id: 2, category_id: 5, price: 100000, description:'Thịt nạc vai heo mềm, thích hợp nướng BBQ', image: '/static/images/Food/Nuong/nacvaiheo.jpg' },
   { id: "TCTH", name: 'Trái Cây Tổng Hợp', restaurant_id: 2, category_id: 7, price: 100000, description:'Đĩa trái cây tươi theo mùa tráng miệng', image: '/static/images/Food/Nuong/traicaytonghop.jpg' }
   ];


=======
// File này chứa toàn bộ dữ liệu menu
const MENU_DATA = [
   { id: "LT", name: 'Lẩu Thái', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu chua cay kiểu Thái với hải sản tươi và rau', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001564-lau-thai_1_1.jpg' },
   { id: "LM", name: 'Lẩu Mala', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cay tê đặc trưng Tứ Xuyên với nhiều loại topping', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001563-lau-mala-dai-loan_1_2.jpg' },
   { id: "LCD", name: 'Lẩu Cua Đồng', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cua đồng đậm vị truyền thống ăn kèm rau tươi', image: 'https://tiki.vn/blog/wp-content/uploads/2023/07/thanh-pham-lau-cua-dong-5-nguoi-an-1-1536x1030.jpg' },
   { id: "LKC", name: 'Lẩu Kimchi', restaurant_id: 1, category_id: 3, price: 60000, description:'Lẩu kimchi Hàn Quốc cay nhẹ với thịt và đậu hũ', image: 'https://thichlaunuong.com/uploads/files/2021/05/21/gyu-kimchi-nabe-lau-bo-kim-chi1537556147.jpg' },
   { id: "LTX", name: 'Lẩu Tứ Xuyên', restaurant_id: 1, category_id: 3, price: 50000, description:'Lẩu cay nồng đậm vị tiêu hoa Tứ Xuyên', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/l/a/lau-hong-ngoc_1.jpg' },
   { id: "LBNG", name: 'Lẩu Bò Nhúng Giấm', restaurant_id: 1, category_id: 3, price: 50000, description:'Thịt bò tươi nhúng giấm chua nhẹ ăn kèm rau', image: 'https://i.pinimg.com/1200x/84/2f/c8/842fc899420614cf55de8b8e7481d8d2.jpg' },
   { id: "STN", name: 'Set Thịt Nhỏ', restaurant_id: 1, category_id: 1, price: 120000, description:'Set thịt nhỏ gồm bò, heo và rau ăn kèm', image: 'https://i.pinimg.com/1200x/10/84/9a/10849a51b3a4716655ab197944a1d995.jpg' },
   { id: "HSTH", name: 'Hải Sản Tổng Hợp', restaurant_id: 1, category_id: 1, price: 150000, description:'Combo hải sản gồm tôm, mực, nghêu tươi', image: 'https://i.pinimg.com/736x/f2/c0/41/f2c04156507b638dd7710a393405840e.jpg' },
   { id: "CBRN", name: 'Combo Rau Nấm', restaurant_id: 1, category_id: 1, price: 100000, description:'Combo rau và nấm tươi ăn kèm lẩu', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/r/a/rau_nam_tong_hop.jpg' },
   { id: "STL", name: 'Set Thịt Lớn', restaurant_id: 1, category_id: 1, price: 240000, description:'Set thịt lớn tẩm ướp đậm vị dùng với lẩu', image: 'https://i.pinimg.com/736x/cd/2f/59/cd2f59d1d3406af4e0c80cbe8b726799.jpg' },
   { id: "SVTL", name: 'Set Viên Thả Lẩu', restaurant_id: 1, category_id: 1, price: 100000, description:'Các loại viên thả lẩu như bò viên, cá viên', image: 'http://anvatngon.vn/upload/images/set-vien-tha-lau-eb-steamboat-5in1-nk-malaysia-mon-an-che-bien-tai-nha-hotline-093-8828-553.jpg' },
   { id: "BFTM", name: 'Buffet Tráng Miệng', restaurant_id: 1, category_id: 7, price: 50000, description:'Buffet trái cây và nước tráng miệng', image: 'https://i.pinimg.com/736x/93/21/0c/93210c9b608c619be5495e4253d95fbd.jpg' },


   //dữ liệu món nướng
   { id: "BCBM", name: 'Ba Chỉ Bò Mỹ', restaurant_id: 2, category_id: 5, price: 90000, description:'Thịt ba chỉ bò Mỹ mềm, thích hợp nướng hoặc nhúng lẩu', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/t/h/thitbonhuy.png' },
   { id: "LVB", name: 'Lõi Vai Bò', restaurant_id: 2, category_id: 5, price: 90000, description:'Phần lõi vai bò mềm, ít mỡ, nướng rất đậm vị', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/2/8/2865-loi-vai-wagyu.jpg' },
   { id: "THI", name: 'Thịt Heo Iberico', restaurant_id: 2, category_id: 5, price: 70000, description:'Thịt heo Iberico cao cấp, mềm ngọt tự nhiên', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001584-ba-chi-heo-iberico_2_1.jpg' },
   { id: "KC", name: 'Kimchi', restaurant_id: 2, category_id: 8, price: 25000, description:'Kimchi cải thảo chua cay kiểu Hàn Quốc', image: 'https://i.pinimg.com/1200x/88/5e/d9/885ed9d3194e58c01b3c2865a943691a.jpg' },
   { id: "BTM", name: 'Bạch Tuộc Mini', restaurant_id: 2, category_id: 2, price: 85000, description:'Bạch tuộc mini tươi giòn thích hợp nướng', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001591-bach-tuoc-baby_1_1.jpg' },
   { id: "SDMH", name: 'Sò Điệp Mỡ Hành', restaurant_id: 2, category_id: 6, price: 85000, description:'Sò điệp tươi nướng mỡ hành thơm béo', image: 'https://i.pinimg.com/1200x/c4/b6/34/c4b634ee4f04c0cf4fe83a9fba39dd19.jpg' },
   { id: "SNMO", name: 'Sườn Non Ướp Mật Ong', restaurant_id: 2, category_id: 6, price: 120000, description:'Sườn non tẩm mật ong nướng thơm ngọt', image: 'https://i.pinimg.com/736x/3e/58/15/3e58156f6d4f5efba5ec8c72f52d5ff3.jpg' },
   { id: "RSAK", name: 'Rau Sống Ăn Kèm', restaurant_id: 2, category_id: 5, price: 90000, description:'Rau sống tươi ăn kèm các món nướng', image: 'https://cdn.yeutre.vn/medias/uploads/228/228658-rau-an-do-nuong-han-quoc.jpg' },
   { id: "CMN", name: 'Combo Nấm', restaurant_id: 2, category_id: 1, price: 100000, description:'Combo nhiều loại nấm tươi ăn kèm lẩu', image: 'https://image.foodbook.vn/upload/20220503/1651551345115_blob.png' },
   { id: "TNST", name: 'Tôm Nướng Sa Tế', restaurant_id: 2, category_id: 6, price: 240000, description:'Tôm tươi nướng sa tế cay thơm', image: 'https://i.pinimg.com/1200x/94/03/bf/9403bf0a4317828cc0d50e30d493c189.jpg' },
   { id: "NVH", name: 'Nạc Vai Heo', restaurant_id: 2, category_id: 5, price: 100000, description:'Thịt nạc vai heo mềm, thích hợp nướng BBQ', image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/3/1/31_1.jpg' },
   { id: "TCTH", name: 'Trái Cây Tổng Hợp', restaurant_id: 2, category_id: 7, price: 100000, description:'Đĩa trái cây tươi theo mùa tráng miệng', image: 'https://i.pinimg.com/1200x/51/e9/00/51e90025e4f0f776b454617976400147.jpg' }
   ];

>>>>>>> origin/main
