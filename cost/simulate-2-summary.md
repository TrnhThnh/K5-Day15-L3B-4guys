# Tóm tắt mô phỏng simulate-2@20261128-143936

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| it_gap | 24 | 1 | 1321 | 604 | 2.0 | 5.2 |
| thinh_thoang | 19 | 2 | 2614 | 1081 | 4.0 | 9.1 |
| hay_gap | 7 | 3 | 3871 | 1764 | 6.0 | 14.3 |

Tỉ lệ đạt dùng để tính: 28/30 (93%) — lượt run-3@20261128-021028

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-3.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (550 người) | Chi phí / tháng — cơ sở (1.100 người) | Chi phí / tháng — cao (2.200 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| anthropic/claude-haiku-5.5 (vào 0.1 · ra 0.5 $/1M) | $0.00069 | $0.00074 | $0.00045 | $0.4559 | $0.9117 | $1.82 | $0.00083 |
| google/gemini-3.5-flash-lite (vào 0.3 · ra 2.5 $/1M) | $0.0030 | $0.0032 | $0.0019 | $1.99 | $3.99 | $7.98 | $0.0036 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.7) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: anthropic/claude-haiku-5.5. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
