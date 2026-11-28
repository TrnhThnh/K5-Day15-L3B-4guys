# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau - tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Bản CP2 (27/11): đào review đã có số; khảo sát và phỏng vấn **chờ kết quả**.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ lượt đầu, chờ Chiến soát nhãn | `evidence/data-mining.md` · `evidence/reviews-labelled.csv` · `evidence/scripts/` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ mới có thông tin tóm tắt của P2; chưa đạt ngưỡng | `evidence/interviews/script.md` · `evidence/interviews/P2.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | 12 phiếu tại lần đọc ngày 27/11; 6 người có đặt qua app. Tư cách ngoài nhóm chưa được xác minh. | Google Sheets của nhóm, câu 1, 3 và 10 |

## 2. Số chính

- **Đào data, mẫu A** (150 review 1-3★ mới nhất ShopeeFood, 20/10 - 26/11/2026): thiếu món **2/150 (1,3%)** · giao trễ 39/150 (26,0%) · chờ lâu / bot không giải quyết 18/150 (12,0%).
- **Đào data, mẫu B** (mọi review khớp từ khoá thiếu món, 4 app, 27/11/2025 - 26/11/2026): 41/50 hit là đơn thiếu món thật; trong 41 đơn đó, chờ lâu / bot **21/41 (51,2%)** · bù voucher thay vì hoàn giá **6/41 (14,6%)** · bị từ chối / không được gì **6/41 (14,6%)** · ít nhất một trong ba **30/41 (73,2%)**.
  Trong 13 review kể rõ kết quả cuối, chỉ 2 được bù đúng phần thiếu.
- Phỏng vấn hiện có 1 câu trả lời được ghi tóm tắt: P2 không gặp sự cố trong tháng qua, kể một lần cách đây khoảng 2 năm, gọi quán và được hoàn trong khoảng 15 phút. Chưa đủ 3 cuộc phỏng vấn; metadata và câu hỏi nguyên văn cần bổ sung từ người phỏng vấn.
- Khảo sát sơ bộ ngày 27/11 có 12 phiếu. Câu 1 có 6 người chọn 0 lần, 4 người chọn 1–3 lần, 1 người chọn 4–10 lần và 1 người chọn hơn 10 lần. Trong 6 người có đặt, 3 người báo thiếu/sai món ở câu 3. Ở câu 10, 1 trong 3 được hoàn đúng giá, 1 chỉ nhận voucher và 1 không khiếu nại.

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | *chờ kết quả* | | | | |
| P2 | Khách đặt đồ ăn | Không trong tháng qua; có lần khoảng 2 năm trước | 0 | Khoảng 15 phút (lần 2 năm trước) | Gọi điện cho quán |
| P3 | *chờ kết quả* | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Tôi phải chờ đợi để được hỗ trợ, nhưng cuối cùng chỉ nhận được voucher 30k với điều kiện sử dụng, thay vì được hoàn tiền hoặc bù đắp trực tiếp cho phần sản phẩm bị thiếu." - review Grab, 1★, 21/11/2026 (`B-grab-2026-11-21T09:26:00`)
2. "Đối tác giao đơn thiếu món gần 100k, nền tảng đền bù hẳn cái mã giảm giá 15k như bố thí" - review Grab, 1★, 06/07/2026 (`B-grab-2026-07-06T10:00:29`)
3. "giao thiếu, khiếu nại Shopeefood thì nó cho bot nói chuyện, nói tới lui thì đòi gừi theo form báo cáo mà lại bị lỗi ko up ảnh, TỆ" - review ShopeeFood, 1★, 15/01/2026 (`B-shopeefood-2026-01-15T12:38:02`)
4. "Mình gửi yêu cầu trong app lên Green SM khiếu nại. 22 tiếng sau, yêu cầu đó vẫn ở trạng thái "đang mở"? và chưa chuyển qua "xử lý"." - review Xanh SM, 1★, 20/08/2026 (`B-xanhsm-2026-08-20T12:38:54`)
5. "Quán giao món thiếu, shopfood xử lý bằng cách hoàn mã giảm giá, k hoàn tiền, nhưng mã giảm vô nghĩa ship 29k tặng mã 30k. K bao giờ dám đặt lại." - review ShopeeFood, 1★, 07/11/2026 (`A-shopeefood-2026-11-07T16:29:21`)
6. *(P2, câu trả lời tóm tắt do thành viên cung cấp; chưa có bản ghi nguyên văn đầy đủ)*

## 4. Các nguồn có khớp nhau không

Data nói: thiếu món **hiếm** trong review (2/150 phàn nàn ShopeeFood), nhưng khi đã xảy ra thì phần lớn người viết review kể bị bot / chờ lâu / chỉ được voucher / không được gì (30/41).
Khảo sát cũng ghi nhận một trường hợp chỉ nhận voucher. Một người bỏ qua khi gặp sự cố, nên việc chỉ đọc review có thể bỏ sót trải nghiệm này. P2 kể một lần cách đây khoảng hai năm được quán hoàn tiền sau 15 phút, và không gặp sự cố trong tháng qua. Đây là lời kể lịch sử, không xác nhận pain hiện tại. Cần phỏng vấn thêm ít nhất hai khách.

## 5. Kết luận

Hai tỷ lệ sơ bộ để kiểm giả thuyết ở `evidence/hypothesis.md` là 3/6 gặp sự cố và 2/3 không được hoàn đúng giá hay giao bù. Cỡ mẫu người có đặt còn dưới ngưỡng 20 người ngoài nhóm, nên nhóm chưa chốt giả thuyết từ khảo sát.
Tín hiệu từ review: vế "kênh khiếu nại là bot / chờ lâu, thường chỉ được voucher" được ủng hộ; vế "thiếu món xảy ra đủ thường" **chưa** được ủng hộ - cách giải thích khác (a) và (b) trong giả thuyết vẫn mở, vì giao trễ là phàn nàn lớn hơn nhiều (39/150 so với 2/150).
Điều vẫn chưa biết: bao nhiêu % người trong lớp gặp thiếu món trong 3 tháng; mỗi lần mất bao nhiêu phút; người không viết review có được hoàn đúng giá không.

## Lịch hẹn (dùng cho CP2 - chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| *chờ nhóm điền* | | |
