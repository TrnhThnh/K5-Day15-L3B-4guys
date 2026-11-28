# Reflection - Lưu Nguyễn Chí Đức

## 1. Vai trò và phần việc

Mình phụ trách luồng agent và phần nối model (`codebase/agent.py`, `codebase/ai.py`), thiết kế ở [spec §4](../spec.md) và phần demo trực tiếp.
Ở CP2, mình dựng spec §0–§7 cùng sơ đồ, khung bản chạy thử ở chế độ giả và bộ câu thử đầu tiên (commit `608f821`).
Sau lượt 2 đạt 24/24 trên chính bộ câu đã dùng để sửa lỗi, mình thêm 6 câu giữ riêng H01–H06, chạy lượt 3 trên 30 câu và viết [`eval/stability.py`](../eval/stability.py) để chạy mỗi câu 3 lần (commit `a076a05`).
Mình cũng thêm nhánh trả lời tin ngoài phạm vi và đơn chưa giao xong (commit `5767131`), [`eval/trace.py`](../eval/trace.py) để mở trace khi giám khảo hỏi, và sơ đồ cho slide trang 3 (commit `c212772`).

## 2. AI hỗ trợ và phần cần kiểm lại

Mình dùng Claude Code để viết phần lớn code và tài liệu, còn mình quyết định thiết kế và kiểm kết quả trên trace.
Bản đầu của `eval/stability.py` chỉ so loại hành động, nên báo 30/30 câu khớp; khi đọc trace mình thấy H04 có lần chuyển người mức `normal` thay vì `high`, nên sửa phép kiểm để so cả mức ưu tiên, số đúng là 29/30.
Bộ câu giữ riêng ban đầu có 8 câu, đưa tổng lên 32, vượt khung 20–30 câu của đề, nên mình cắt còn 6.
Khi chạy thử câu demo, model viết "60000đ" thay vì "60.000đ"; hậu kiểm vẫn qua vì cùng chữ số, nên mình đưa sẵn chuỗi số tiền đã định dạng vào dữ kiện.

## 3. Bài học từ H04

H04 là đơn giao vào bệnh viện cho người vừa mổ, món giao tới trái chế độ "kiêng dầu mỡ".
Agent luôn chuyển nhân viên, nhưng ở 2/6 lần chạy chỉ ở mức `normal`, vì mức ưu tiên phụ thuộc việc model gắn nhãn `wrong_item` ở bước trích ý (`python eval/trace.py run-3 H04`).
Bài học của mình là một quyết định an toàn không nên đi qua nhãn do model gắn: nhóm đã để code quyết số tiền, nhưng vẫn để model quyết gián tiếp mức ưu tiên.
Câu này nằm trong phần giữ riêng nên nhóm ghi nó là lỗi còn lại thay vì sửa ngay trước CP4; cách sửa là để code tự so món với `diet_note`.
