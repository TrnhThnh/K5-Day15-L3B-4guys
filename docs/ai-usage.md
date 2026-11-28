# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Chạy bản thử | Claude Haiku 5.5 qua OpenRouter | Trích thông tin khiếu nại và diễn đạt phản hồi dựa trên dữ kiện do code tính | Kiểm theo đầu ra và trace; số tiền do code tính | Đức và Thịnh |
| Đào review | AI hỗ trợ lượt gắn nhãn đầu | Gợi ý nhãn sự cố cho review | Chiến soát độc lập 24 dòng; đồng ý 23, sửa 1 | Chiến |
| Khảo sát | Codex | Tạo script Google Form từ câu hỏi nhóm cung cấp, tổng hợp các trường lựa chọn | Số công bố chỉ đếm phiếu có đặt qua app khi tính tỷ lệ gặp sự cố | Chiến và Thịnh |
| Chấm benchmark | Claude, Codex | Claude chấm nháp lượt 1–2; Codex đọc đầu ra lượt 3 và đối chiếu hành động trong trace | Trung đã soát 24 câu lượt 1. Lượt 2–3 chờ người soát | Trung |
| Hồ sơ và slide | Codex | Soạn slide, tính chi phí benchmark từ token ghi nhận và tổng hợp hồ sơ | Thành viên phụ trách duyệt trước khi nộp | Thịnh |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
