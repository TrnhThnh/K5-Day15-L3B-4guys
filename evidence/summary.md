# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau - tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Bản CP2 (27/11): đào review đã có số; khảo sát và phỏng vấn **chờ kết quả**.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ lượt đầu, chờ Chiến soát nhãn | `evidence/data-mining.md` · `evidence/reviews-labelled.csv` · `evidence/scripts/` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☑ 3 khách ngoài nhóm (P1–P3), 2/3 gặp thiếu món trong tháng qua. Câu không có số ghi "không nhớ" / "không trả lời" theo đúng lời người được hỏi, không đoán hộ | `evidence/interviews/script.md` · `evidence/interviews/P1.md` · `P2.md` · `P3.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ chốt 12 phiếu ngày 28/11 (gửi trên Discord chung của khoá), 6 người có đặt qua app; **dưới ngưỡng 20**, chỉ dùng làm tín hiệu sơ bộ. Tư cách ngoài nhóm chưa được xác minh. | Google Sheets của nhóm, câu 1, 3 và 10 |

## 2. Số chính

- **Đào data, mẫu A** (150 review 1-3★ mới nhất ShopeeFood, 20/10 - 26/11/2026): thiếu món **2/150 (1,3%)** · giao trễ 39/150 (26,0%) · chờ lâu / bot không giải quyết 18/150 (12,0%).
- **Đào data, mẫu B** (mọi review khớp từ khoá thiếu món, 4 app, 27/11/2025 - 26/11/2026): 41/50 hit là đơn thiếu món thật; trong 41 đơn đó, chờ lâu / bot **21/41 (51,2%)** · bù voucher thay vì hoàn giá **6/41 (14,6%)** · bị từ chối / không được gì **6/41 (14,6%)** · ít nhất một trong ba **30/41 (73,2%)**.
  Trong 13 review kể rõ kết quả cuối, chỉ 2 được bù đúng phần thiếu.
- Phỏng vấn 3 khách: **2/3 gặp thiếu món trong 1 tháng qua** (P1: thiếu 1 trong 2 bát bún, ShopeeFood, giữa tháng 11; P3: thiếu 1 trong 2 phần cơm, 08/11). P2 không gặp trong tháng qua, kể một lần khoảng 2 năm trước, gọi quán và được hoàn trong khoảng 15 phút. **Cả 3 đều tìm tới quán trước, không ai kể dùng chat hỗ trợ của app**; 2/3 lần gần đây quán không phản hồi. Không ai nhớ hay trả lời kết quả cuối của lần gần đây.
- Khảo sát sơ bộ ngày 27/11 có 12 phiếu. Câu 1 có 6 người chọn 0 lần, 4 người chọn 1–3 lần, 1 người chọn 4–10 lần và 1 người chọn hơn 10 lần. Trong 6 người có đặt, 3 người báo thiếu/sai món ở câu 3. Ở câu 10, 1 trong 3 được hoàn đúng giá, 1 chỉ nhận voucher và 1 không khiếu nại.

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | Khách đặt đồ ăn | Có: thiếu 1 trong 2 bát bún, ShopeeFood, khoảng giữa tháng 11 | 1 (trên ~8 lần đặt) | Không nhớ; gọi nhà hàng không ai nghe máy | Gọi thẳng nhà hàng |
| P2 | Khách đặt đồ ăn | Không trong tháng qua; có lần khoảng 2 năm trước | 0 | Khoảng 15 phút (lần 2 năm trước) | Gọi điện cho quán |
| P3 | Khách đặt đồ ăn | Có: thiếu 1 trong 2 phần cơm, 08/11 | ≥1 (chỉ trả lời câu 3) | Không trả lời; shipper quay lại quán báo, quán không phản hồi | Nhờ shipper báo quán |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Tôi phải chờ đợi để được hỗ trợ, nhưng cuối cùng chỉ nhận được voucher 30k với điều kiện sử dụng, thay vì được hoàn tiền hoặc bù đắp trực tiếp cho phần sản phẩm bị thiếu." - review Grab, 1★, 21/11/2026 (`B-grab-2026-11-21T09:26:00`)
2. "Đối tác giao đơn thiếu món gần 100k, nền tảng đền bù hẳn cái mã giảm giá 15k như bố thí" - review Grab, 1★, 06/07/2026 (`B-grab-2026-07-06T10:00:29`)
3. "giao thiếu, khiếu nại Shopeefood thì nó cho bot nói chuyện, nói tới lui thì đòi gừi theo form báo cáo mà lại bị lỗi ko up ảnh, TỆ" - review ShopeeFood, 1★, 15/01/2026 (`B-shopeefood-2026-01-15T12:38:02`)
4. "Mình gửi yêu cầu trong app lên Green SM khiếu nại. 22 tiếng sau, yêu cầu đó vẫn ở trạng thái "đang mở"? và chưa chuyển qua "xử lý"." - review Xanh SM, 1★, 20/08/2026 (`B-xanhsm-2026-08-20T12:38:54`)
5. "Quán giao món thiếu, shopfood xử lý bằng cách hoàn mã giảm giá, k hoàn tiền, nhưng mã giảm vô nghĩa ship 29k tặng mã 30k. K bao giờ dám đặt lại." - review ShopeeFood, 1★, 07/11/2026 (`A-shopeefood-2026-11-07T16:29:21`)
6. "Mình liên hệ nhưng nhà hàng không nghe máy. Chưa nói chuyện được với ai cả." - P1, khách đặt đồ ăn, phỏng vấn trực tiếp 27/11/2026
7. "Shipper đã quay lại tận quán báo rồi mà bên quán vẫn không phản hồi." - P3, khách đặt đồ ăn, phỏng vấn trực tiếp khoảng 27/11/2026

## 4. Các nguồn có khớp nhau không

Data nói: thiếu món **hiếm** trong review (2/150 phàn nàn ShopeeFood), nhưng khi đã xảy ra thì phần lớn người viết review kể bị bot / chờ lâu / chỉ được voucher / không được gì (30/41).
Khảo sát cũng ghi nhận một trường hợp chỉ nhận voucher. Một người bỏ qua khi gặp sự cố, nên việc chỉ đọc review có thể bỏ sót trải nghiệm này. Phỏng vấn **khớp một phần**: P1 và P3 gặp thiếu món trong tháng qua và đều không được giải quyết ngay, nên vế "khiếu nại khó thành" được ủng hộ. Nhưng chỗ vướng họ kể là **quán không phản hồi**, không phải bot của app như trong review. Cả 3 người (kể cả P2, chuyện 2 năm trước) đều tìm tới quán trước. Review không cho thấy điều này vì người viết review là người đã khiếu nại qua app. Phỏng vấn không xác nhận được vế "chỉ được voucher", vì không ai nhớ hoặc trả lời kết quả cuối.

## 5. Kết luận

Hai tỷ lệ sơ bộ để kiểm giả thuyết ở `evidence/hypothesis.md` là 3/6 gặp sự cố và 2/3 không được hoàn đúng giá hay giao bù. Cỡ mẫu người có đặt còn dưới ngưỡng 20 người ngoài nhóm, nên nhóm chưa chốt giả thuyết từ khảo sát.
Tín hiệu từ review: vế "kênh khiếu nại là bot / chờ lâu, thường chỉ được voucher" được ủng hộ; vế "thiếu món xảy ra đủ thường" **chưa** được ủng hộ - cách giải thích khác (a) và (b) trong giả thuyết vẫn mở, vì giao trễ là phàn nàn lớn hơn nhiều (39/150 so với 2/150).
Tín hiệu từ phỏng vấn: 2/3 khách gặp thiếu món trong tháng qua; lần gần nhất của cả hai không được quán phản hồi. **Giả thuyết phải đổi một phần:** chỗ đau không chỉ ở bot / voucher của app mà còn ở bước đầu, khi khách hoặc shipper liên hệ quán không được. Lát cắt hiện tại (AI xử lý khiếu nại trong app) vẫn hợp, vì đó là kênh còn lại khi quán không phản hồi; slide trang 1 nên nói rõ điều này.
Điều vẫn chưa biết: bao nhiêu % người trong lớp gặp thiếu món trong 3 tháng; mỗi lần mất bao nhiêu phút (P1 không nhớ, P3 không trả lời); cuối cùng khách có được hoàn đúng giá không.

## Lịch hẹn (dùng cho CP2 - chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| *chờ nhóm điền* | | |
