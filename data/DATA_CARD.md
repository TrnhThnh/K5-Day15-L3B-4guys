# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

Ba tệp JSON trong `data/` dùng dữ liệu nhóm viết tay, nhãn `synthetic`. Seed ngẫu nhiên không áp dụng. Bản v1 được lưu trực tiếp trong Git để tái hiện cùng dữ liệu.
Không có số điện thoại, địa chỉ hay tên người thật nào.
Mốc giờ dùng khi chạy bộ câu thử: `2026-11-27T21:00:00+07:00` (code nên cố định mốc này khi tính hạn báo 24 giờ, để kết quả không đổi theo ngày chạy).

## Dataset 1 · Đơn hàng (`data/orders.json`)

| Mục | Nội dung |
| --- | --- |
| Dùng để làm gì | nguồn cho công cụ `get_order` (món, số lượng, đơn giá, phí ship, giờ giao, nơi giao, `diet_note`) · số tiền hoàn luôn lấy từ đây · bộ câu thử |
| Từ đâu | nhóm tự viết · 10 quán dựng tên "Quán Mẫu …" |
| Xử lý những bước gì | viết tay danh sách món và đơn; `total_vnd` = Σ `qty × unit_price_vnd` + `ship_fee_vnd`, tính và kiểm bằng script (không tính tay); `promised_at` = `ordered_at` + 35 phút |
| Số dòng / số đoạn | 35 đơn (DH-1001 … DH-1035), 28 khách (KH-01 … KH-28): 19 giao nhà, 12 văn phòng, 4 bệnh viện có `diet_note`; 33 `delivered`, 1 `cancelled`, 1 `delivering` |
| Phiên bản / ngày lấy | v1, 27/11/2026 · đơn trong tháng 11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | menu nhỏ (41 món), giá kiểu quán bình dân TP.HCM *(tự ước tính)*; không có ảnh, không có phương thức thanh toán; DH-1001 … DH-1024 khớp từng câu B01 … B24 trong `eval/benchmark.csv`, còn DH-1025 … DH-1035 làm lịch sử khiếu nại và đa dạng |

## Dataset 2 · Chính sách (`data/policy.json`)

| Mục | Nội dung |
| --- | --- |
| Dùng để làm gì | nguồn cho `get_policy(issue_type)` và `check_limit` (hạn mức chặn bằng code) |
| Từ đâu | **chính sách dựng**, tham khảo trang trợ giúp công khai <https://help.shopee.vn/portal/4/article/79191>, kiểm 27/11/2026; trang đó hiện là hướng dẫn liên hệ CSKH, không ghi mức hoàn, nên các con số là *(tự ước tính)* theo kiểu chính sách app giao đồ ăn; không phải chính sách thật của hãng nào |
| Xử lý những bước gì | 5 loại sự cố: `missing_item`, `wrong_item`, `late`, `foreign_object`, `food_safety`; mỗi loại có điều kiện, cách hoàn, hạn mức/đơn, số khiếu nại tối đa/30 ngày, hạn báo, có cần ảnh, khi nào chuyển người |
| Số dòng / số đoạn | 5 |
| Phiên bản / ngày lấy | v1, 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | `missing_item`: hoàn đúng giá món thiếu, tối đa 200.000đ/đơn, ≥3 khiếu nại/30 ngày thì chuyển người, báo trong 24 giờ, không cần ảnh; `late` theo tình huống track (trễ quá 30 phút mới có voucher); dị vật, ngộ độc, dị ứng luôn chuyển người (hạn mức AI = 0) |

## Dataset 3 · Lịch sử khiếu nại (`data/complaint_history.json`)

| Mục | Nội dung |
| --- | --- |
| Dùng để làm gì | nguồn cho `get_complaint_history(user_id)` · phát hiện khách khiếu nại lặp |
| Từ đâu | nhóm tự viết, khớp với đơn DH-1025 … DH-1035 |
| Xử lý những bước gì | dạng `{user_id: [khiếu nại]}`, mỗi khiếu nại có `complaint_id`, `order_id`, `issue_type`, `created_at`, `claimed_item`, `refund_vnd`, `outcome`; khách không có khoá = chưa khiếu nại lần nào |
| Số dòng / số đoạn | 9 khiếu nại của 4 khách: KH-07 có 4 lần/30 ngày, KH-12 có 3 lần (cả hai đã chạm ngưỡng), KH-11 có 1, KH-24 có 1 |
| Phiên bản / ngày lấy | v1, 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | lịch sử chỉ là một tín hiệu; không dùng làm căn cứ duy nhất để từ chối (track D, bẫy), nên ca lặp được chuyển người chứ không tự từ chối |

## Dataset 4 · Review công khai Google Play (đầu vào cho bộ câu thử)

| Mục | Nội dung |
| --- | --- |
| Dùng để làm gì | lấy lời thật của người dùng cho 10/24 câu trong `eval/benchmark.csv` (`source` = `data_that`) |
| Từ đâu | review công khai trên Google Play của ShopeeFood, Grab, be, Xanh SM, cào tháng 11/2026, review mới nhất ngày 26/11/2026 (file cào để ngoài repo này) |
| Xử lý những bước gì | lọc review từ 2025 có cụm thiếu món / giao thiếu / dị vật / số tài xế; bỏ tên người viết, bỏ tên quán thật; chỉnh nhẹ: chèn mã đơn dựng và tên món để khớp `orders.json`, có câu bỏ tên app; giữ nguyên phần lời còn lại |
| Số dòng / số đoạn | 10 review được dùng |
| Phiên bản / ngày lấy | review mới nhất 26/11/2026 · dùng review từ 2025 |
| Nhãn | thật (lời người dùng), đã chỉnh nhẹ như trên |
| Giới hạn | review 1★ lệch về phía bực bội, không đại diện mọi người dùng; không biết đơn thật của họ |
