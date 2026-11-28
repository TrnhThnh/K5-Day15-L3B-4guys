"""Chọn ngẫu nhiên dòng để người soát nhãn (evidence/data-mining.md mục 5).

Chạy từ gốc repo: python evidence/scripts/sample_review.py
- 12 dòng mẫu A + 12 dòng mẫu B, seed cố định 2811 để chạy lại ra cùng danh sách.
- Ghi evidence/label-review.csv: người soát điền cột `nhan_nguoi_soat` (để trống = đồng ý với `nhan_luot_dau`).
- Không ghi đè nếu file đã có, để không mất phần đã soát.
"""
import csv, random, sys, pathlib

sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(__file__).resolve().parents[1]
src = root / "reviews-labelled.csv"
out = root / "label-review.csv"
if out.exists():
    sys.exit(f"{out} đã có, không ghi đè. Xoá tay nếu muốn chọn lại.")

rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
rng = random.Random(2811)
pick = []
for mau in ["A", "B"]:
    pick += rng.sample([r for r in rows if r["mau"] == mau], 12)

with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "mau", "sao", "trich", "nhan_luot_dau", "nhan_nguoi_soat", "ghi_chu_soat"])
    for r in pick:
        w.writerow([r["id"], r["mau"], r["sao"], r["trich"], r["nhan"], "", ""])
print(f"Đã ghi {len(pick)} dòng → {out}")
