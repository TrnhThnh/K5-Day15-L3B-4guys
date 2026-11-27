"""Cào review Google Play (tiếng Việt, VN) của 4 app, sắp theo mới nhất.

Chạy: pip install google-play-scraper ; python evidence/scripts/scrape_play.py 32000 <thư mục ra>
Lần chạy dùng cho evidence/data-mining.md: 26/11/2026, N = 32000 mỗi app.
Chạy lại hôm khác sẽ ra review mới hơn, nên mẫu A (150 review mới nhất) sẽ dịch; mẫu B lọc theo ngày nên gần như giữ nguyên.
Chỉ lưu ngày, số sao, nội dung - KHÔNG lưu tên người viết. Không commit thư mục ra (file thô).
"""
import json, os, re, sys, ssl
sys.stdout.reconfigure(encoding="utf-8")
_ca = r"C:\Users\User\.ssl\win-ca-bundle.pem"  # CA của proxy trường, chỉ dùng nếu máy có file này
if os.path.exists(_ca):
    os.environ.setdefault("SSL_CERT_FILE", _ca)
from google_play_scraper import reviews, Sort, app

APPS = {
    "shopeefood": "com.deliverynow",
    "grab": "com.grabtaxi.passenger",
    "be": "xyz.be.customer",
    "xanhsm": "com.gsm.customer",
}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
out_dir = sys.argv[2]
for name, pkg in APPS.items():
    try:
        info = app(pkg, lang="vi", country="vn")
        meta = {"title": info.get("title"), "score": info.get("score"), "ratings": info.get("ratings"), "reviews": info.get("reviews")}
    except Exception as e:
        meta = {"error": str(e)}
    allr = []
    token = None
    try:
        while len(allr) < N:
            batch, token = reviews(pkg, lang="vi", country="vn", sort=Sort.NEWEST, count=min(4000, N - len(allr)), continuation_token=token)
            if not batch:
                break
            allr.extend(batch)
            if token is None:
                break
    except Exception as e:
        meta["review_error"] = str(e)
    rows = [{"at": r["at"].isoformat() if r.get("at") else None, "score": r.get("score"), "content": r.get("content")} for r in allr]
    with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "rows": rows}, f, ensure_ascii=False)
    print(name, meta, len(rows), rows[-1]["at"] if rows else None, flush=True)
