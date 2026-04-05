// File này chứa toàn bộ dữ liệu menu
const MENU_DATA = [
    { id: LT, name: 'Lẩu Thái', category_id: 3, price: 50000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001564-lau-thai_1_1.jpg' },
    { id: LM, name: 'Lẩu Mala', category_id: 3, price: 50000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001563-lau-mala-dai-loan_1_2.jpg' },
    { id: LCD, name: 'Lẩu Cua Đồng', category_id: 3, price: 50000, image: 'https://tiki.vn/blog/wp-content/uploads/2023/07/thanh-pham-lau-cua-dong-5-nguoi-an-1-1536x1030.jpg' },
    { id: LKC, name: 'Lẩu Kimchi', category_id: 3, price: 60000, image: 'https://thichlaunuong.com/uploads/files/2021/05/21/gyu-kimchi-nabe-lau-bo-kim-chi1537556147.jpg' },
    { id: LTX, name: 'Lẩu Tứ Xuyên', category_id: 3, price: 50000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/l/a/lau-hong-ngoc_1.jpg' },
    { id: LBNG, name: 'Lẩu Bò Nhúng Giấm', category_id: 3, price: 50000, image: 'https://i.pinimg.com/1200x/84/2f/c8/842fc899420614cf55de8b8e7481d8d2.jpg' },
    { id: STN, name: 'Set Thịt Nhỏ', category_id: 1, price: 120000, image: 'https://i.pinimg.com/1200x/10/84/9a/10849a51b3a4716655ab197944a1d995.jpg' },
    { id: HSTH, name: 'Hải Sản Tổng Hợp', category_id: 1, price: 150000, image: 'https://i.pinimg.com/736x/f2/c0/41/f2c04156507b638dd7710a393405840e.jpg' },
    { id: CBRN, name: 'Combo Rau Nấm', category_id: 1, price: 100000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/r/a/rau_nam_tong_hop.jpg' },
    { id: STL, name: 'Set Thịt Lớn', category_id: 1, price: 240000, image: 'https://i.pinimg.com/736x/cd/2f/59/cd2f59d1d3406af4e0c80cbe8b726799.jpg' },
    { id: SVTL, name: 'Set Viên Thả Lẩu', category_id: 1, price: 100000, image: 'http://anvatngon.vn/upload/images/set-vien-tha-lau-eb-steamboat-5in1-nk-malaysia-mon-an-che-bien-tai-nha-hotline-093-8828-553.jpg' },
    { id: BFTM, name: 'Buffet Tráng Miệng', category_id: 7, price: 50000, image: 'https://i.pinimg.com/736x/93/21/0c/93210c9b608c619be5495e4253d95fbd.jpg' },

    //dữ liệu món nướng
    { id: BCBM, name: 'Ba Chỉ Bò Mỹ', category_id: 5, price: 90000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/t/h/thitbonhuy.png' },
    { id: LVB, name: 'Lõi Vai Bò', category_id: 5, price: 90000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/2/8/2865-loi-vai-wagyu.jpg' },
    { id: THI, name: 'Thịt Heo Iberico', category_id: 5, price: 70000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001584-ba-chi-heo-iberico_2_1.jpg' },
    { id: KC, name: 'Kimchi', category_id: 8, price: 25000, image: 'https://i.pinimg.com/1200x/88/5e/d9/885ed9d3194e58c01b3c2865a943691a.jpg' },
    { id: BTM, name: 'Bạch Tuộc Mini', category_id: 2, price: 85000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/6/0/60001591-bach-tuoc-baby_1_1.jpg' },
    { id: SDMH, name: 'Sò Điệp Mỡ Hành', category_id: 6, price: 85000, image: 'https://i.pinimg.com/1200x/c4/b6/34/c4b634ee4f04c0cf4fe83a9fba39dd19.jpg' },
    { id: SNMO, name: 'Sườn Non Ướp Mật Ong', category_id: 6, price: 120000, image: 'https://i.pinimg.com/736x/3e/58/15/3e58156f6d4f5efba5ec8c72f52d5ff3.jpg' },
    { id: RSAK, name: 'Rau Sống Ăn Kèm', category_id: 5, price: 90000, image: 'https://cdn.yeutre.vn/medias/uploads/228/228658-rau-an-do-nuong-han-quoc.jpg' },
    { id: CMN, name: 'Combo Nấm', category_id: 1, price: 100000, image: 'https://image.foodbook.vn/upload/20220503/1651551345115_blob.png' },
    { id: TNST, name: 'Tôm Nướng Sa Tế', category_id: 6, price: 240000, image: 'https://i.pinimg.com/1200x/94/03/bf/9403bf0a4317828cc0d50e30d493c189.jpg' },
    { id: NVH, name: 'Nạc Vai Heo', category_id: 5, price: 100000, image: 'https://brand-pcms.ggg.systems/media/catalog/product/cache/fccf9bc1c56510f6f2e84ded9c30a375/3/1/31_1.jpg' },
    { id: TCTH, name: 'Trái Cây Tổng Hợp', category_id: 7, price: 100000, image: 'https://i.pinimg.com/1200x/51/e9/00/51e90025e4f0f776b454617976400147.jpg' }
    ];