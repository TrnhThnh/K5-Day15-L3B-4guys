# Reflection — Trịnh Hưng Thịnh

## 1. Vai trò và phần việc

Mình phụ trách ước lượng impact, chi phí và tổng hợp hồ sơ checkpoint của nhóm.
Trong [spec §2](../spec.md), mình tách 6 người có đặt qua app khỏi tổng 12 phiếu để tính tỷ lệ gặp sự cố.
Ở [phần hiệu chuẩn](../eval/hieu-chuan-luot-2.md), mình chấm B03, B06, B09, B17 và B23 đều đạt. Khi đối chiếu, mình và Trung khớp cả 5 câu.

## 2. AI hỗ trợ và phần cần kiểm lại

Codex hỗ trợ đọc trace, cộng token và soạn [bảng chi phí](../cost/cost-estimate.md).
Con số 0,000445 USD ban đầu có đơn vị là **mỗi câu benchmark**. Một phiên khiếu nại có thể cần nhiều lượt hỏi.
Vì vậy, hồ sơ CP4 ghi riêng dự toán theo persona và phần còn thiếu là số đo của 50 phiên thật. Nhóm cũng giữ rõ nguồn của từng giả định.

## 3. Bài học từ B18

Ở lượt 1, khách báo thiếu món sau một tuần nhưng agent vẫn tạo đề nghị hoàn 55.000đ.
Trace cho thấy bước kiểm hạn báo thiếu mốc thời gian để so với quy định 24 giờ. Sau khi truyền mốc đó, lượt 2 chuyển ca này sang nhân viên.
Bài học cho phần công cụ mình phụ trách là phải thử cả đơn quá hạn và kiểm hành động được ghi trong trace. Một câu trả lời có đúng tên món và đúng giá vẫn có thể dẫn tới quyết định sai. [Báo cáo đánh giá](../eval/report.md)
