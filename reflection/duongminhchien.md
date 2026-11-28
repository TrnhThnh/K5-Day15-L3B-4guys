# Reflection — Dương Minh Chiến

> Soạn cùng coding agent từ git log và file trong repo. Chiến đọc lại và chỉnh câu chữ trước 23:59 Thứ Bảy 28/11.

1. **Vai trò + phần mình làm:**
   Mình là thành viên phụ trách bằng chứng pain (`TEAMS.md`): đào review, khảo sát, phỏng vấn, viết `spec.md` §0–§1.
   - CP1: canvas và giả thuyết D1 (`canvas.md`, `evidence/hypothesis.md`, commit `246b0f7`).
   - CP2: chỉnh `spec.md`, gồm impact §2 có ghi rõ phần _(tự ước tính)_ (commit `5b8893f`), và chấm độc lập 5 đầu ra CP2 với mức đồng thuận 3/5 (`eval/README.md`, commit `6409d1b`).
   - CP3: chạy lượt 1 qua OpenRouter, ra 16/24 (`7f95bf0`). Sửa agent sau lượt 1 (`c39997e`). Chạy lượt 2, ra 24/24 (`a2b34d3`).
   - Soát nhãn review: 24 dòng chọn ngẫu nhiên có seed (`evidence/scripts/sample_review.py` → `evidence/label-review.csv`). Đồng ý 22/24, sửa 1 dòng, còn treo 1 dòng mẫu B chờ đọc toàn văn. Kết quả ghi ở `evidence/data-mining.md` mục 5.
   - Khảo sát: gửi trên kênh Discord chung của toàn khoá, hiện có 12 phiếu.

2. **AI hỗ trợ mình thế nào:**
   - Claude hỗ trợ desk research Track D, soạn nháp canvas, giả thuyết và spec. Nhãn lượt đầu của `evidence/reviews-labelled.csv` cũng do AI gắn trên review thật đã cào.
   - Coding agent hỗ trợ sửa `codebase/agent.py` sau lượt 1 và chấm nháp cột `pass`. Trung là người soát lại điểm.
   - Chỗ phải sửa output của AI: khi soát nhãn, review "đơn hàng xử lý rất lâu nhưng không cho hủy" bị AI gắn `giao_tre`. Mình đổi thành `bot_cho_lau` vì review không nhắc shipper hay giao muộn. Sau khi sửa, mẫu A còn 39/150 review giao trễ (trước là 40/150).
   - Ngược lại, có một dòng mình định bỏ nhãn `thieu_mon` vì đoạn trích không nhắc tới thiếu món. Kiểm lại thì thấy dòng đó chỉ vào mẫu khi toàn văn khớp từ khoá thiếu món, nên mình để treo chờ đọc toàn văn. Người soát cũng có thể sai khi chỉ đọc đoạn trích.

3. **Một câu thử trượt và bài học:**
   Ở lượt 1, câu **B18** (loại `kho`) trượt. Khách báo thiếu món khi đã quá hạn 24 giờ, nhưng agent vẫn tạo bản nháp hoàn 55.000đ (`eval/run-1.csv`).
   Lỗi nằm ở chỗ luật hạn báo chưa được code kiểm trước khi tạo nháp, nên đã sửa ở `c39997e` ("hạn báo 24h") và lượt 2 đạt.
   Bài học: luật về tiền và thời hạn phải để code kiểm, không giao cho model tự nhớ. Bộ câu thử cũng cần có ca sát ngưỡng thì mới bắt được lỗi kiểu này.
