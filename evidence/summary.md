# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau - tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Bản CP2 (27/11): đào review đã có số; khảo sát và phỏng vấn **chờ kết quả**.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ lượt đầu, chờ Chiến soát nhãn | `evidence/data-mining.md` · `evidence/reviews-labelled.csv` · `evidence/scripts/` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ chờ kết quả | `evidence/interviews/script.md` · `P1.md`… |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ chờ kết quả | `evidence/survey/form.md` |

## 2. Số chính

- **Đào data, mẫu A** (150 review 1-3★ mới nhất ShopeeFood, 20/10 - 26/11/2026): thiếu món **2/150 (1,3%)** · giao trễ 40/150 (26,7%) · chờ lâu / bot không giải quyết 17/150 (11,3%).
- **Đào data, mẫu B** (mọi review khớp từ khoá thiếu món, 4 app, 27/11/2025 - 26/11/2026): 41/50 hit là đơn thiếu món thật; trong 41 đơn đó, chờ lâu / bot **21/41 (51,2%)** · bù voucher thay vì hoàn giá **6/41 (14,6%)** · bị từ chối / không được gì **6/41 (14,6%)** · ít nhất một trong ba **30/41 (73,2%)**.
  Trong 13 review kể rõ kết quả cuối, chỉ 2 được bù đúng phần thiếu.
- Phỏng vấn: *chờ kết quả* - __/3 người gặp *(n nhỏ không ghi %)* · số lần / tháng: P1 __, P2 __, P3 __ · mỗi lần mất __–__ phút
- Khảo sát: *chờ kết quả* - n = __ · gặp thiếu/sai món 3 tháng qua __/__ (__%) · trong đó không được hoàn đúng giá __/__ (__%)

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | *chờ kết quả* | | | | |
| P2 | *chờ kết quả* | | | | |
| P3 | *chờ kết quả* | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Tôi phải chờ đợi để được hỗ trợ, nhưng cuối cùng chỉ nhận được voucher 30k với điều kiện sử dụng, thay vì được hoàn tiền hoặc bù đắp trực tiếp cho phần sản phẩm bị thiếu." - review Grab, 1★, 21/11/2026 (`B-grab-2026-11-21T09:26:00`)
2. "Đối tác giao đơn thiếu món gần 100k, nền tảng đền bù hẳn cái mã giảm giá 15k như bố thí" - review Grab, 1★, 06/07/2026 (`B-grab-2026-07-06T10:00:29`)
3. "giao thiếu, khiếu nại Shopeefood thì nó cho bot nói chuyện, nói tới lui thì đòi gừi theo form báo cáo mà lại bị lỗi ko up ảnh, TỆ" - review ShopeeFood, 1★, 15/01/2026 (`B-shopeefood-2026-01-15T12:38:02`)
4. "Mình gửi yêu cầu trong app lên Green SM khiếu nại. 22 tiếng sau, yêu cầu đó vẫn ở trạng thái "đang mở"? và chưa chuyển qua "xử lý"." - review Xanh SM, 1★, 20/08/2026 (`B-xanhsm-2026-08-20T12:38:54`)
5. "Quán giao món thiếu, shopfood xử lý bằng cách hoàn mã giảm giá, k hoàn tiền, nhưng mã giảm vô nghĩa ship 29k tặng mã 30k. K bao giờ dám đặt lại." - review ShopeeFood, 1★, 07/11/2026 (`A-shopeefood-2026-11-07T16:29:21`)
6. *(phỏng vấn - chờ kết quả)*
7. *(khảo sát câu 10 - chờ kết quả)*

## 4. Các nguồn có khớp nhau không

Data nói: thiếu món **hiếm** trong review (2/150 phàn nàn ShopeeFood), nhưng khi đã xảy ra thì phần lớn người viết review kể bị bot / chờ lâu / chỉ được voucher / không được gì (30/41).
Người dùng nói: *chờ kết quả khảo sát và phỏng vấn.*
Khớp / lệch ở đâu, vì sao: *chờ kết quả* - điểm cần kiểm nhất là tần suất (review không đo được) và kết quả lần gần nhất của người **không** viết review.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: *chờ kết quả khảo sát* - ngưỡng giả thuyết đo bằng khảo sát, không bằng review.
Tín hiệu từ review: vế "kênh khiếu nại là bot / chờ lâu, thường chỉ được voucher" được ủng hộ; vế "thiếu món xảy ra đủ thường" **chưa** được ủng hộ - cách giải thích khác (a) và (b) trong giả thuyết vẫn mở, vì giao trễ là phàn nàn lớn hơn nhiều (40/150 so với 2/150).
Điều vẫn chưa biết: bao nhiêu % người trong lớp gặp thiếu món trong 3 tháng; mỗi lần mất bao nhiêu phút; người không viết review có được hoàn đúng giá không.

## Lịch hẹn (dùng cho CP2 - chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| *chờ nhóm điền* | | |
