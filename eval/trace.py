"""In trace của một câu thử cho dễ đọc (dùng khi giám khảo hỏi "câu này vì sao trượt?").

  python eval/trace.py run-3 H04        từng bước của câu H04 trong traces/run-3.jsonl
  python eval/trace.py run-3            danh sách câu trong lượt, kèm quyết định cuối

Mỗi bước một dòng: model (token vào / ra), công cụ (input → output rút gọn), ghi chú của code, câu trả lời cuối.
Chỉ đọc file trace, không gọi model, không sửa gì.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def short(s, n=160):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 1] + "…"


def main(args):
    if not args:
        sys.exit(__doc__)
    run = args[0].removesuffix(".jsonl")
    path = os.path.join(ROOT, "traces", run + ".jsonl")
    with open(path, encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]
    if len(args) == 1:
        for e in events:
            if e.get("kind") == "note" and e.get("text", "").startswith("quyết định:"):
                print("%-4s %s" % (e["case"], e["text"]))
        return
    case = args[1]
    steps = [e for e in events if e.get("case") == case]
    if not steps:
        sys.exit("Không có câu %s trong %s." % (case, path))
    print("%s · câu %s · %d bước" % (steps[0].get("run_id"), case, len(steps)))
    for i, e in enumerate(steps, 1):
        kind = e.get("kind")
        if kind == "model":
            print("%2d. model  %s · token vào %s / ra %s · %ss" % (
                i, e.get("model"), e.get("tokens_in"), e.get("tokens_out"), e.get("latency_s")))
            print("            → %s" % short(e.get("output", ""), 200))
        elif kind == "tool":
            print("%2d. công cụ %s%s" % (i, e.get("name"), short(e.get("input", ""), 110)))
            print("            → %s" % short(e.get("output", "")))
        elif kind == "note":
            print("%2d. code   %s" % (i, e.get("text")))
        elif kind == "final":
            print("%2d. trả lời %s" % (i, e.get("output")))
        else:
            print("%2d. %s %s" % (i, kind, short(json.dumps(e, ensure_ascii=False))))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
