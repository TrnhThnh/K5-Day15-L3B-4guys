"""Độ ổn định: chạy mỗi câu thử k lần (mặc định 3), so quyết định giữa các lần.

Không phải một lượt chấm và không thay `python run.py eval`: không ghi run-N.csv, không đụng bộ chạy của khung.
Quyết định của mỗi lần lấy từ bản nháp công cụ ghi vào `tools.OUTBOX`, không đọc chữ trong câu trả lời:
  refund:<số tiền>   có nháp hoàn tiền (draft_refund)
  escalate:<mức>     có phiếu chuyển nhân viên (escalate_to_human)
  ask                không có nháp nào (hỏi lại khách)
Cột `khop_expected` so quyết định với tiền tố của cột `expected` (hoan_tien N · chuyen_nhan_vien · hoi_lai),
phần hành động, số tiền, và mức ưu tiên khi `expected` ghi "ưu tiên cao" (high / urgent) hoặc "mức khẩn" (urgent);
phần lời (xin lỗi, bước tiếp...) vẫn do người chấm theo `pass_criterion`.

  python eval/stability.py                 3 lần mỗi câu, cả bộ
  python eval/stability.py --k 5 --wait 2  5 lần mỗi câu, nghỉ 2 giây giữa hai lần gọi
  python eval/stability.py --only H        chỉ các câu có id bắt đầu bằng H (phần giữ riêng)
  python eval/stability.py --resummarize eval/stability-1.csv   tính lại bản tóm tắt từ file đã chạy, không gọi model

Ra: eval/stability-N.csv (từng lần) + eval/stability-N-summary.md (từng câu: ổn định? khớp expected?).
"""
import csv
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import agent  # noqa: E402
import ai  # noqa: E402
import tools  # noqa: E402

BENCH = os.path.join(ROOT, "eval", "benchmark.csv")


def decision(drafts):
    """Bản nháp của một lần chạy → chuỗi quyết định."""
    refunds = [d for d in drafts if d.get("kind") == "refund"]
    escal = [d for d in drafts if d.get("kind") == "escalation"]
    if refunds:
        return "refund:%d" % sum(int(d.get("amount_vnd") or 0) for d in refunds)
    if escal:
        return "escalate:%s" % (escal[-1].get("priority") or "normal")
    return "ask"


def expected_decision(expected):
    """Cột expected → (loại, số tiền / tập mức ưu tiên chấp nhận được, hoặc None)."""
    m = re.match(r"\s*(hoan_tien|chuyen_nhan_vien|hoi_lai)\s*(\d+)?", expected or "")
    if not m:
        return None, None
    kind = {"hoan_tien": "refund", "chuyen_nhan_vien": "escalate", "hoi_lai": "ask"}[m.group(1)]
    if kind == "refund":
        return kind, int(m.group(2)) if m.group(2) else None
    if kind == "escalate":
        low = expected.lower()
        if "mức khẩn" in low:
            return kind, {"urgent"}
        if "ưu tiên cao" in low:
            return kind, {"high", "urgent"}
    return kind, None


def matches(dec, exp_kind, exp_detail):
    kind, _, rest = dec.partition(":")
    if kind != exp_kind or exp_detail is None:
        return kind == exp_kind
    if exp_kind == "refund":
        return int(rest) == exp_detail
    return rest in exp_detail


def next_path(stem, ext):
    n = 1
    while os.path.exists(os.path.join(ROOT, "eval", "%s-%d%s" % (stem, n, ext))):
        n += 1
    return os.path.join(ROOT, "eval", "%s-%d%s" % (stem, n, ext)), n


def resummarize(path, model, provider, when):
    """Tính lại bản tóm tắt từ một eval/stability-N.csv đã chạy (không gọi model)."""
    with open(BENCH, encoding="utf-8-sig", newline="") as f:
        exp = {r["id"]: (r["type"], r["expected"]) for r in csv.DictReader(f)}
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_id = {}
    for r in rows:
        by_id.setdefault(r["id"], []).append(r["quyet_dinh"])
    summary = []
    for cid, decs in by_id.items():
        typ, expected = exp[cid]
        kind, detail = expected_decision(expected)
        hits = sum(matches(d, kind, detail) for d in decs if d != "error") if kind else None
        summary.append((cid, typ, len(set(decs)) == 1, hits, decs))
    n = int(re.search(r"stability-(\d+)", path).group(1))
    k = max(len(d) for d in by_id.values())
    write_summary(path, n, k, summary, model, provider, when)


def main(args):
    k, wait, only = 3, 0.0, ""
    if args[:1] == ["--resummarize"]:
        old = open(args[1].replace(".csv", "-summary.md"), encoding="utf-8").read()
        m = re.search(r"Model: `([^`]*)` \(([^)]*)\) · chạy lúc (.+)", old)
        return resummarize(args[1], *m.groups())
    i = 0
    while i < len(args):
        if args[i] == "--k":
            k, i = int(args[i + 1]), i + 2
        elif args[i] == "--wait":
            wait, i = float(args[i + 1]), i + 2
        elif args[i] == "--only":
            only, i = args[i + 1], i + 2
        else:
            sys.exit(__doc__)
    if ai.MODEL_PROVIDER == "fake":
        print("Cảnh báo: đang ở chế độ giả (chưa nối model) - kết quả chỉ để thử bộ chạy.")
    with open(BENCH, encoding="utf-8-sig", newline="") as f:
        cases = [r for r in csv.DictReader(f) if r["id"].startswith(only)]

    out_csv, n = next_path("stability", ".csv")
    rows, summary = [], []
    for c in cases:
        exp_kind, exp_amount = expected_decision(c["expected"])
        decs = []
        for run in range(1, k + 1):
            tools.OUTBOX.clear()
            err = ""
            try:
                out = agent.answer(c["input"])["output"]
            except Exception as e:  # một lần lỗi vẫn ghi lại, không dừng cả bộ
                out, err = "", repr(e)
            dec = "error" if err else decision(list(tools.OUTBOX))
            decs.append(dec)
            rows.append({"id": c["id"], "type": c["type"], "lan": run, "quyet_dinh": dec,
                         "khop_expected": int(matches(dec, exp_kind, exp_amount)) if exp_kind and not err else "",
                         "output": out, "error": err})
            print("%s lần %d: %s" % (c["id"], run, dec))
            if wait:
                time.sleep(wait)
        hits = sum(matches(d, exp_kind, exp_amount) for d in decs if d != "error") if exp_kind else None
        summary.append((c["id"], c["type"], len(set(decs)) == 1, hits, decs))

    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    write_summary(out_csv, n, k, summary, ai.MODEL_NAME or "-", ai.MODEL_PROVIDER, time.strftime("%Y-%m-%d %H:%M"))


def write_summary(out_csv, n, k, summary, model, provider, when):
    stable = sum(s[2] for s in summary)
    all_hit = sum(1 for s in summary if s[3] == k)
    lines = ["# Độ ổn định %d - %d câu × %d lần" % (n, len(summary), k), "",
             "- Model: `%s` (%s) · chạy lúc %s" % (model, provider, when),
             "- Cùng quyết định cả %d lần: **%d/%d** câu" % (k, stable, len(summary)),
             "- Quyết định khớp `expected` cả %d lần (hành động + số tiền + mức ưu tiên, chấm bằng code): **%d/%d** câu" % (k, all_hit, len(summary)),
             "- Chi tiết từng lần: `eval/%s`" % os.path.basename(out_csv), "",
             "| id | type | ổn định | khớp expected | các lần |", "|---|---|---|---|---|"]
    for cid, typ, st, hit, decs in summary:
        lines.append("| %s | %s | %s | %s | %s |" % (cid, typ, "có" if st else "**không**",
                                                    "-" if hit is None else "%d/%d" % (hit, k), " · ".join(decs)))
    with open(out_csv.replace(".csv", "-summary.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:5]))


if __name__ == "__main__":
    main(sys.argv[1:])
