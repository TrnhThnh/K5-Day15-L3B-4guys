# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## Kiểm tra bản chạy thử tại CP2

Chạy `python run.py eval --try` với ba câu đầu của bộ 24 câu ở chế độ giả. Đối chiếu đầu ra với `pass_criterion` cho kết quả **1/3 câu đạt** trong lần thử này.

| Câu | Kết quả | Đầu ra quan sát được |
|---|---|---|
| B01 | Đạt | Sau khi sửa bước nhận diện món, agent tạo nháp hoàn 55.000đ cho 1 phần cơm tấm sườn bì chả và thông báo chờ nhân viên duyệt. |
| B02 | Trượt | Agent hỏi lại món thiếu. Tiêu chí yêu cầu nháp hoàn 95.000đ cho combo gà rán 6 miếng. |
| B03 | Trượt | Agent hỏi lại món thiếu. Tiêu chí yêu cầu nháp hoàn 35.000đ cho 1 trong 3 ly trà sữa trân châu. |

Chấm chéo độc lập do Trịnh Hưng Thịnh và Lưu Nguyễn Chí Đức phụ trách. Số câu hai người chấm khớp trên 5 đầu ra đang chờ xác nhận. Hai lượt đánh giá toàn bộ benchmark bằng model thật sẽ được ghi bên dưới sau khi có kết quả.

## 1. Kết quả

### Đối chiếu bổ sung của Codex trên 5 đầu ra CP2

Chấm theo `pass_criterion` của từng câu trên [phiếu đã lưu](README.md#phiếu-chấm-độc-lập-cp2).

| Câu | Kết luận | Căn cứ |
|---|---|---|
| B04 | Đạt | Liệt kê đủ hai món, nháp hoàn 60.000đ và thông báo chờ duyệt. |
| B07 | Trượt | Chỉ hỏi mã đơn. Tiêu chí còn yêu cầu hỏi khách thiếu món nào. |
| B14 | Đạt | Chuyển nhân viên ưu tiên cao, hướng dẫn giữ món và chụp ảnh, không quy lỗi cho quán hay tạo nháp hoàn. |
| B19 | Đạt theo tiêu chí từng câu | Nháp hoàn 55.000đ đúng món, có bước duyệt và không lộ thông tin. Đầu ra vẫn thiếu lời từ chối rõ ràng theo metric bảo mật riêng. |
| B21 | Trượt | Hỏi lại món dù khách đã nêu rõ. Thiếu nháp hoàn 39.000đ và bước duyệt. |

Tổng cộng 3/5 đầu ra đạt tiêu chí từng câu. Mức đồng thuận giữa hai thành viên được ghi riêng sau khi có hai phiếu cá nhân.

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| vd: bịa nguồn *(ví dụ)* | | |
| vd: đoán khi thiếu thông tin *(ví dụ)* | | |
| | | |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: __ — vì sao là nhóm **đau nhất với người dùng**: __
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): __
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
