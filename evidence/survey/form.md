# Khảo sát - đơn đồ ăn thiếu / sai món (lát cắt D1)

> Chép sang Google Form theo đúng thứ tự dưới đây.
> Ngưỡng guide 1.2: **≥20 người ngoài nhóm 4guys**, đúng người dùng (có đặt đồ ăn qua app).
> Ngưỡng giả thuyết (`evidence/hypothesis.md`): **≥1/3** người trả lời gặp đơn thiếu/sai món trong 3 tháng qua, **và** trong số đó **≥1/2** không được hoàn đúng giá phần thiếu.
> Không thu tên, email, SĐT, mã học viên (trừ ô liên hệ cuối form nếu người trả lời tự để lại).
> Khi chốt: ghi kênh đã gửi, giờ mở, giờ chốt vào `evidence/survey/questions.md`; xuất CSV, xoá cột dấu thời gian chi tiết và cột liên hệ, lưu `evidence/survey/results.csv`.

## Tiêu đề và mô tả form

**Tiêu đề:** Lần gần nhất bạn đặt đồ ăn bị thiếu món (3 phút)

**Mô tả:** Nhóm 4guys (AI20K, Track D) đang tìm hiểu chuyện **đã xảy ra** khi đơn đồ ăn giao tới bị thiếu hoặc sai món.
Form ẩn danh, 10 câu, khoảng 3 phút.
Không có câu trả lời đúng sai; không nhớ thì chọn "không nhớ".

## Câu hỏi

| # | Câu hỏi | Kiểu trả lời (Google Form) | Bắt buộc | Dùng để |
|---|---|---|---|---|
| 1 | Trong 3 tháng qua, bạn đặt đồ ăn / đồ uống giao tới qua app (ShopeeFood, GrabFood, be, Xanh SM...) khoảng bao nhiêu lần? | Trắc nghiệm: 0 lần · 1-3 lần · 4-10 lần · Hơn 10 lần | Có | lọc đúng người dùng (0 lần → chuyển tới câu 10) |
| 2 | Bạn đã từng đặt đồ ăn giao tới **bệnh viện** chưa (cho mình hoặc người nhà)? | Trắc nghiệm: Có, trong 3 tháng qua · Có, lâu hơn 3 tháng · Chưa bao giờ | Có | câu sàng lọc cho hướng mở rộng |
| 3 | Trong 3 tháng qua, có đơn nào giao tới bị **thiếu** hoặc **sai** món (thiếu món, thiếu phần, thiếu ly nước, thiếu topping, nhận nhầm món) không? | Trắc nghiệm: Có, thiếu món · Có, sai món · Có, cả hai · Không · Không nhớ | Có | **tử số ngưỡng 1/3** (Không / Không nhớ → chuyển tới câu 10) |
| 4 | Lần gần nhất chuyện đó xảy ra là khi nào, qua app nào? | Lưới trắc nghiệm, hoặc 2 ô: Tuần này · Tuần trước · Trong tháng này · 1-3 tháng trước; app: ShopeeFood · GrabFood · be · Xanh SM · khác | Có | neo vào một lần cụ thể |
| 5 | Lần gần nhất đó, phần bị thiếu / sai trị giá khoảng bao nhiêu? | Trắc nghiệm: Dưới 30k · 30-60k · 60-100k · Trên 100k · Không nhớ | Có | so với giá trị được bù |
| 6 | Lần gần nhất đó, bạn đã làm gì? | Hộp kiểm: Chat với hỗ trợ trong app · Gọi tổng đài · Nhắn / gọi quán · Nhắn / gọi shipper · Đánh giá thấp / viết review · Không làm gì, bỏ qua · Khác | Có | kênh khiếu nại |
| 7 | Lần đó bạn nói chuyện với ai? | Trắc nghiệm: Chỉ bot / trả lời tự động · Bot rồi tới nhân viên · Nhân viên ngay từ đầu · Quán / shipper · Không liên hệ ai | Có | kiểm "toàn bot" |
| 8 | Từ lúc bắt đầu khiếu nại đến khi có kết quả (hoặc bạn bỏ cuộc) mất khoảng bao lâu? | Trắc nghiệm: Không khiếu nại · Dưới 5 phút · 5-15 phút · 15-60 phút · Hơn 1 tiếng · Hơn 1 ngày · Vẫn chưa xong | Có | số phút mất |
| 9 | Kết quả cuối cùng của lần đó là gì? | Trắc nghiệm: Được hoàn **đúng giá** phần thiếu (tiền hoặc ví) · Được giao bù đúng món · Chỉ được **mã giảm giá / voucher / xu** · Được hoàn một phần · **Không được gì** · Đang chờ, chưa xong · **Không khiếu nại** | Có | **tử số ngưỡng 1/2** |
| 10 | Điều gì khó chịu nhất ở lần đó (hoặc lần gần nhất bạn khiếu nại một đơn đồ ăn)? | Đoạn văn | Không | trích dẫn nguyên văn |

Câu 4 đến 9 chỉ hiện với người chọn "Có..." ở câu 3 (Google Form: "Chuyển đến phần dựa trên câu trả lời").
Cuối form thêm một ô **không đánh số, không bắt buộc**: "Nếu sẵn lòng cho nhóm hỏi thêm 10 phút về lần đó, để lại Discord / Zalo." - ô này xoá khỏi `results.csv` trước khi commit.

## Cách đếm (ghi trước khi mở form)

- **n** = số phiếu có câu 1 ≠ "0 lần" (đúng người dùng); phiếu của 4 thành viên nhóm không tính.
- **Ngưỡng 1:** x₁ = số phiếu câu 3 là "Có, thiếu món" / "Có, sai món" / "Có, cả hai"; đạt nếu x₁/n ≥ 1/3.
- **Ngưỡng 2:** trong x₁ phiếu đó, x₂ = số phiếu câu 9 **không phải** "Được hoàn đúng giá" hay "Được giao bù đúng món"; đạt nếu x₂/x₁ ≥ 1/2.
- Ghi thêm: phân bố câu 8 (phút), câu 7 (bao nhiêu người chỉ gặp bot), câu 2 (số người từng đặt tới bệnh viện).
- Dưới khoảng 10 người thì chỉ ghi x/n, không ghi %.

## Tin nhắn gửi lớp (Discord / Zalo)

> Chào cả lớp, nhóm 4guys (Track D) đang làm về chuyện đặt đồ ăn qua app bị **thiếu hoặc sai món**. Bạn nào đã từng đặt ShopeeFood / GrabFood / be / Xanh SM trong 3 tháng qua giúp nhóm mình điền form ẩn danh 10 câu, khoảng 3 phút, hỏi về **lần gần nhất** chuyện đó xảy ra (kể cả chưa bao giờ bị thiếu thì vẫn điền giúp nhé, câu trả lời "không" cũng quý như "có"). Không quảng cáo sản phẩm gì cả. Link: [dán link Google Form]. Cảm ơn mọi người nhiều!
