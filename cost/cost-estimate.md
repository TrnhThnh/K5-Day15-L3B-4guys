# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào và phép kiểm từ lượt thật

Lượt 2 dùng Claude Haiku 5.5 qua OpenRouter. Cộng 24 dòng trong `eval/run-2.csv` được 28.804 token vào và 15.619 token ra. Theo đơn giá BTC (USD/triệu token), chi phí model của 24 tình huống là 0,010690 USD với Haiku (0,10 vào; 0,50 ra), hoặc 0,047689 USD khi áp giá Gemini 3.5 Flash Lite (0,30 vào; 2,50 ra) trên cùng số token. Bình quân một câu tương ứng 0,000445 và 0,001987 USD. Tỷ lệ đạt lượt 2 đang chấm nháp là 24/24 trên bộ đã dùng để sửa lỗi.

Mô phỏng dùng 50 phiên, seed 42, ba nhóm khách và ba quy mô 550 / 1.100 / 2.200 khách. Các giả định nằm trong `cost/personas.yaml`. Chi phí mỗi phiên nhiều lượt, mỗi task thành công và mỗi tháng chờ phép đo bằng model thật.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-__.csv` · run ID __ · __ phiên · seed __

*(dán bảng từ `cost/simulate-N-summary.md`)*

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): __
- Chi phí / người / tháng (cơ sở, model __): __
- **Kết luận một dòng — đáng làm không:** __

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
