# Đào data - cách đếm và kết quả

> Điền ở guide bước 1.2.
> Script đếm ở `evidence/scripts/`, bảng gắn nhãn ở `evidence/reviews-labelled.csv`.
> Repo chỉ chứa số đã tổng hợp và các dòng đã gắn nhãn (không tên người viết) - không chép nguyên file review gốc.

## 1. Cách đếm - viết TRƯỚC khi chạy (27/11/2026, khoảng 17:50)

- **Data dùng:** review công khai tiếng Việt trên Google Play (lang=vi, country=vn), cào bằng `evidence/scripts/scrape_play.py` ngày 26/11/2026, sắp theo mới nhất, mỗi app tối đa 32.000 review.
  Chỉ giữ ngày, số sao, nội dung (script không lưu tên người viết).
  Link nguồn: <https://play.google.com/store/apps/details?id=com.deliverynow> (ShopeeFood), <https://play.google.com/store/apps/details?id=com.grabtaxi.passenger> (Grab), <https://play.google.com/store/apps/details?id=xyz.be.customer> (be), <https://play.google.com/store/apps/details?id=com.gsm.customer> (Xanh SM).
- **Mẫu A - tỉ lệ thiếu món trong các phàn nàn:** 150 review **1-3★** mới nhất của **ShopeeFood** (app chỉ giao đồ ăn, nên không lẫn review gọi xe), có nội dung, tính ngược từ 26/11/2026.
  Lọc 1-3★ là cố ý: mẫu nghiêng về phía phàn nàn, nên % ở đây là "% trong số người đang bực", không phải % mọi người dùng.
  Mẫu số = 150 (mọi review đã đọc, kể cả không liên quan).
- **Mẫu B - chuyện gì xảy ra SAU khi thiếu món:** **mọi** review khớp từ khoá thiếu món (regex trong `evidence/scripts/sample.py`) của cả 4 app, mọi mức sao, từ 27/11/2025 đến 26/11/2026 (12 tháng).
  Đọc từng review: review nào không thật sự kể một đơn đồ ăn bị thiếu món thì gắn "không liên quan" và bỏ khỏi mẫu số.
  Mẫu số = số review B được xác nhận là đơn đồ ăn thiếu món.
- **Nhãn** (một review có thể mang nhiều nhãn; "không liên quan" chỉ dùng khi không nhãn nào khác khớp):
  - `thieu_mon` - thiếu món: khách kể một đơn đồ ăn / đồ uống giao tới thiếu ít nhất một món, phần, ly hoặc topping đã đặt.
  - `sai_mon` - sai món: khách nhận món khác món đã đặt, hoặc nhận nhầm đơn người khác.
  - `bu_voucher` - bù voucher thay vì hoàn giá món: khách kể được bù bằng mã giảm giá / xu / voucher thay vì hoàn tiền đúng giá phần bị thiếu hay sai.
  - `bot_cho_lau` - chờ lâu / bot không giải quyết: khách kể kênh hỗ trợ là bot, trả lời mẫu, không ai phản hồi, hoặc phải chờ lâu (nhiều giờ, nhiều ngày) mà chưa xong.
  - `bi_tu_choi` - bị từ chối: khách kể yêu cầu hoàn tiền / bồi thường bị từ chối, hoặc khiếu nại xong không nhận được gì.
  - `giao_tre` - giao trễ: khách phàn nàn đơn giao muộn so với dự kiến hoặc chờ shipper quá lâu.
  - `khong_lien_quan` - không liên quan: review không nói về bất kỳ nhãn nào ở trên (khen chung, lỗi app, giá, phí, tài xế gọi xe...).
- **Đếm gì:** với mỗi nhãn, x = số review mang nhãn đó, N = mẫu số của mẫu tương ứng, ghi x/N (%).
- **Script:** `evidence/scripts/sample.py` (chọn mẫu A và B, in ra để gắn nhãn) · `evidence/scripts/count_labels.py` (đếm từ `evidence/reviews-labelled.csv`).

## 2. Đọc trước, đếm sau

Đã đọc 30 dòng đầu mẫu A trước khi gắn nhãn.
Mỗi dòng là một review: ngày, số sao (1-5), nội dung; không có mã đơn, không có tên.
Các *kiểu* thấy được:

- giao trễ, phần lớn đổ cho "ghép đơn" (chờ 1 tiếng đến 2 tiếng rưỡi);
- lỗi thanh toán: đã trừ tiền nhưng đơn bị huỷ, không thấy hoàn;
- không cho khách huỷ đơn;
- mua "deal" xong bị tính thêm phí ship;
- lỗi định vị, địa chỉ;
- kênh hỗ trợ là AI / bot trả lời lặp, hoặc không ai giải quyết.

Bộ nhãn giữ như mục 1 (đặt trước khi đọc).
Ba kiểu "lỗi thanh toán", "không cho huỷ", "deal / phí ship" không thuộc lát cắt D1 nên rơi vào `khong_lien_quan`.

## 3. Kết quả

Chạy `python evidence/scripts/count_labels.py` ra đúng các số dưới đây.

### Mẫu A - 150 review 1-3★ mới nhất của ShopeeFood (20/10/2026 - 26/11/2026)

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| thiếu món | 2/150 | 1,3% | khớp desk research trước đó (2-3/150) |
| sai món | 1/150 | 0,7% | |
| bù voucher thay vì hoàn giá món | 1/150 | 0,7% | chính là 1 trong 2 review thiếu món |
| chờ lâu / bot không giải quyết | 18/150 | 12,0% | mọi loại sự cố, không riêng thiếu món |
| bị từ chối / không được hoàn | 5/150 | 3,3% | chủ yếu đơn bị huỷ đã trừ tiền |
| giao trễ | 39/150 | 26,0% | phàn nàn lớn nhất |
| không liên quan | 91/150 | 60,7% | lỗi thanh toán, không cho huỷ, deal, định vị, chửi chung |

### Mẫu B - mọi review khớp từ khoá thiếu món, 4 app, 27/11/2025 - 26/11/2026

50 review khớp từ khoá; đọc từng review, **41/50** là đơn đồ ăn thiếu món thật (ShopeeFood 11/14 · Grab 18/19 · be 7/9 · Xanh SM 5/8).
9 review bị loại: "không có món" nghĩa là hết món / không có quán (5), giao bưu kiện hoặc tài liệu (2), đơn đi chợ (1), khớp nhầm "thiếu đồng bộ" (1).

| Đếm gì (trong số đơn thiếu món) | x / N | % | Ghi chú |
|---|---|---|---|
| chờ lâu / bot không giải quyết | 21/41 | 51,2% | từ 30 phút không ai trả lời đến "sắp 1 năm" |
| bù voucher thay vì hoàn giá món | 6/41 | 14,6% | mã 15-30k, có điều kiện; 1 ca đơn thiếu gần 100k được mã 15k |
| bị từ chối / không được gì | 6/41 | 14,6% | |
| sai món (kèm thiếu) | 4/41 | 9,8% | |
| giao trễ (kèm thiếu) | 3/41 | 7,3% | |
| **ít nhất một trong: bot/chờ lâu, voucher, bị từ chối** | **30/41** | **73,2%** | phần còn lại chỉ kể "bị thiếu", không nói đã khiếu nại ra sao |
| kể rõ kết quả cuối | 13/41 | | trong 13 review này: 6 voucher, 6 không được gì, 1 quán tự bù món (Xanh SM); review 1 Grab được trả tiền phần thiếu ở lần khiếu nại thứ 2 nhưng đã nằm trong 6 voucher (lần 1 được mời mã giảm giá) |

Đọc: trong số review **đã kể kết quả**, chỉ 2/13 được bù đúng phần thiếu (1 bằng tiền sau lần khiếu nại thứ hai, 1 do quán tự bù) - n nhỏ, đọc như dấu hiệu, không như tỉ lệ.

## 4. ≥5 ví dụ cụ thể (mã dòng trong `evidence/reviews-labelled.csv`, không tên người viết)

1. `B-grab-2026-11-21T09:26:00` · 1★ · "Đơn hàng của tôi bị thiếu 2 miếng gà trong combo. [...] Tôi phải chờ đợi để được hỗ trợ, nhưng cuối cùng chỉ nhận được voucher 30k với điều kiện sử dụng, thay vì được hoàn tiền hoặc bù đắp trực tiếp cho phần sản phẩm bị thiếu." - thiếu món, chờ lâu, bù voucher
2. `B-grab-2026-07-06T10:00:29` · 1★ · "Đối tác giao đơn thiếu món gần 100k, nền tảng đền bù hẳn cái mã giảm giá 15k như bố thí" - thiếu món, bù voucher
3. `A-shopeefood-2026-11-07T16:29:21` · 1★ · "Quán giao món thiếu, shopfood xử lý bằng cách hoàn mã giảm giá, k hoàn tiền, nhưng mã giảm vô nghĩa ship 29k tặng mã 30k. K bao giờ dám đặt lại." - thiếu món, bù voucher
4. `B-shopeefood-2026-01-15T12:38:02` · 1★ · "giao thiếu, khiếu nại Shopeefood thì nó cho bot nói chuyện, nói tới lui thì đòi gừi theo form báo cáo mà lại bị lỗi ko up ảnh, TỆ" - thiếu món, bot
5. `B-xanhsm-2026-08-20T12:38:54` · 1★ · "Mình gửi yêu cầu trong app lên Green SM khiếu nại. 22 tiếng sau, yêu cầu đó vẫn ở trạng thái "đang mở"? và chưa chuyển qua "xử lý"." - thiếu món, chờ lâu
6. `B-be-2026-06-10T17:46:08` · 1★ · "Còn be này gửi 7749 quả mail phản hồi kêu bên nhà hàng sẽ liên hệ, báo lại 7749 lần đều nhận được mail y như cũ là đợi liên hệ. [...] Giờ sắp 1 năm rồi, chắc chắn không có vụ hoàn tiền giao thiếu món đó được xử lí." - thiếu món, trả lời mẫu, chờ lâu
7. `B-grab-2026-04-09T12:30:02` · 1★ · "Xài AI hỗ trợ mất thời gian, thiếu món mà không cho chọn món thiếu :) dẹp mấy con AI ngu đi dùm" - thiếu món, bot
8. `B-xanhsm-2026-10-21T19:53:00` · 1★ · "Quán biết quán liên hệ bù đồ bị thiếu cho mình rồi, mình sửa đánh giá lại k được." - ví dụ **ngược** giả thuyết: được bù món, do quán tự làm

## 5. Giới hạn của data

- Review nghiêng hẳn về phía người đang bực: mẫu A chỉ lấy 1-3★, mẫu B gần như toàn 1★ (47/50 hit).
  % ở đây là "% trong số người viết review phàn nàn", **không** phải % người dùng gặp thiếu món.
- Thiếu món hiếm trong review: 2/150 (1,3%) phàn nàn mới nhất của ShopeeFood, và chỉ 50 hit / khoảng 31.000 review 12 tháng của 4 app.
  Người được bù ổn thì ít khi lên viết review, nên mẫu B thổi phồng tỉ lệ xử lý tệ.
- Chỉ 13/41 review kể kết quả cuối, nên tỉ lệ "voucher thay vì hoàn giá" chưa đo được chắc chắn - cần khảo sát.
- Từ khoá có thể sót cách viết khác ("thiếu 1 phần", không dấu); Grab và be lẫn review gọi xe nên chỉ dùng ở mẫu B.
- Chỉ Google Play, không có App Store; review không có mã đơn nên không kiểm được thật giả.
- Data cho biết người ta **kể gì**, không cho biết **bao nhiêu người trong lớp** gặp, mỗi lần mất bao nhiêu phút.
  → Kiểm lại bằng khảo sát `evidence/survey/form.md` (ngưỡng ≥1/3 gặp thiếu/sai món, trong đó ≥1/2 không được hoàn đúng giá) và phỏng vấn `evidence/interviews/script.md` (số phút, kết quả lần gần nhất).

> **Lượt gắn nhãn này là lượt đầu, làm với trợ giúp của AI** (đọc và gắn nhãn từng review trong file thô), trên review thật đã cào, không bịa dòng nào.
> **Dương Minh Chiến (phụ trách bằng chứng) cần soát lại**: đọc ngẫu nhiên ít nhất 20 dòng trong `evidence/reviews-labelled.csv`, sửa nhãn nếu không đồng ý, rồi chạy lại `count_labels.py`.
> **Phiếu soát:** `python evidence/scripts/sample_review.py` (seed 2811) → `evidence/label-review.csv`, 12 dòng A + 12 dòng B. Người soát điền `nhan_nguoi_soat` khi không đồng ý (để trống = đồng ý).
> **Kết quả soát (Dương Minh Chiến, 28/11):** đồng ý 23/24 · sửa 1/24.
> - Sửa: A `2026-10-22T11:09:38` `giao_tre` → `bot_cho_lau` ("xử lý rất lâu nhưng không cho huỷ", không nói shipper hay giao muộn). Đã sửa trong `reviews-labelled.csv` và chạy lại `count_labels.py`: mẫu A giao trễ 40 → 39/150, bot / chờ lâu 17 → 18/150. Mẫu B không đổi.
> - Đã kiểm: B `xanhsm-2026-08-20T12:38:54`. Người soát định bỏ `thieu_mon` vì đoạn trích không nói thiếu món. Đọc toàn văn trên Google Play (28/11) thấy câu "Mình đặt food. Quán giao thiếu món…", nên giữ `thieu_mon bot_cho_lau`. Mẫu B giữ 30/41. Bài học: soát nhãn phải đọc toàn văn, không chỉ đoạn trích.
> Ca ranh giới đã biết: A `2026-10-27T19:36:31`, `2026-11-07T11:55:27`, `2026-11-01T19:20:43` (gắn "bot / không giải quyết" dù không nói rõ kênh); B `2026-07-04T14:35:18` (đơn đi chợ, đã loại).
