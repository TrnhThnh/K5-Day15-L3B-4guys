"""Đếm nhãn từ evidence/reviews-labelled.csv (cách đếm ở evidence/data-mining.md mục 1).

Chạy từ gốc repo: python evidence/scripts/count_labels.py
- Mẫu A: N = mọi dòng mẫu A (kể cả không liên quan).
- Mẫu B: N = dòng mẫu B có nhãn thieu_mon (đã đọc và xác nhận là đơn đồ ăn thiếu món).
"""
import csv, sys, pathlib
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
LABELS = ["thieu_mon", "sai_mon", "bu_voucher", "bot_cho_lau", "bi_tu_choi", "giao_tre", "khong_lien_quan"]
path = pathlib.Path(__file__).resolve().parents[1] / "reviews-labelled.csv"
rows = list(csv.DictReader(path.open(encoding="utf-8")))


def report(name, sub):
    n = len(sub)
    c = Counter(l for r in sub for l in r["nhan"].split())
    print(f"\n{name}: N = {n}")
    for l in LABELS:
        print(f"  {l:16} {c[l]:3}/{n} ({100 * c[l] / n:.1f}%)")
    return c


a = [r for r in rows if r["mau"] == "A"]
b_all = [r for r in rows if r["mau"] == "B"]
b = [r for r in b_all if "thieu_mon" in r["nhan"].split()]
report("Mẫu A - 150 review 1-3★ mới nhất ShopeeFood", a)
print(f"\nMẫu B - keyword hit 4 app, 12 tháng: {len(b_all)} hit, {len(b)} xác nhận thiếu món")
for app in ["shopeefood", "grab", "be", "xanhsm"]:
    print(f"  {app:10} {sum(r['app'] == app for r in b)}/{sum(r['app'] == app for r in b_all)}")
c = report("Mẫu B - đã xác nhận thiếu món", b)
bad = sum(1 for r in b if {"bu_voucher", "bot_cho_lau", "bi_tu_choi"} & set(r["nhan"].split()))
print(f"\n  có ít nhất một trong bu_voucher / bot_cho_lau / bi_tu_choi: {bad}/{len(b)} ({100 * bad / len(b):.1f}%)")
told = sum(1 for r in b if {"bu_voucher", "bi_tu_choi"} & set(r["nhan"].split()) or r["ghi_chu"].startswith(("lần 2 được trả", "quán tự")))
print(f"  kể rõ kết quả cuối (voucher / không được gì / được bù): {told}/{len(b)}")
