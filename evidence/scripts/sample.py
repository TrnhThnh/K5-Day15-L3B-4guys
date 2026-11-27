"""Chọn mẫu A và B cho evidence/data-mining.md, in ra TSV để gắn nhãn.

Chạy: python evidence/scripts/sample.py <thư mục chứa shopeefood.json, grab.json, be.json, xanhsm.json> > sample.tsv
Mỗi file JSON do scrape_play.py tạo: {"meta": ..., "rows": [{"at", "score", "content"}]} (không có tên người viết).
Mã dòng = <mẫu>-<app>-<thời điểm review>, đủ để tìm lại review trong file gốc.
"""
import json, re, sys, pathlib

sys.stdout.reconfigure(encoding="utf-8")
d = pathlib.Path(sys.argv[1])
END = "2026-11-27"          # review đến hết 26/11/2026 (ngày cào)
B_START = "2025-11-27"      # mẫu B: 12 tháng
A_APP, A_N, A_MAX_STARS = "shopeefood", 150, 3

MISS = re.compile(
    r"thiếu món|thieu mon|thiếu đồ|thiếu 1 món|thiếu một món|giao thiếu|đơn (hàng )?(bị )?thiếu|bị thiếu"
    r"|thiếu phần|thiếu topping|thiếu ly|thiếu hộp|thiếu nước|thiếu cơm|không có món|ko có món|mất món",
    re.I,
)


def load(app):
    rows = json.loads((d / f"{app}.json").read_text(encoding="utf-8"))["rows"]
    rows = [r for r in rows if r.get("content") and r["at"] < END]
    return sorted(rows, key=lambda r: r["at"], reverse=True)


def emit(sample, app, r):
    text = " ".join(r["content"].split())
    print(f"{sample}-{app}-{r['at']}\t{app}\t{r['at'][:10]}\t{r['score']}\t{text}")


print("id\tapp\tdate\tstars\tcontent")
a = [r for r in load(A_APP) if r["score"] <= A_MAX_STARS][:A_N]
for r in a:
    emit("A", A_APP, r)
for app in ["shopeefood", "grab", "be", "xanhsm"]:
    for r in load(app):
        if r["at"] >= B_START and MISS.search(r["content"]):
            emit("B", app, r)
