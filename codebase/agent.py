"""Luồng chính lát cắt D1: khách báo thiếu món trong đơn giao đồ ăn nhiều món.

Hình dạng: WORKFLOW CỐ ĐỊNH 4 bước (không phải agent tự chọn bước):
    1. model  trích JSON {order_id, issue_type, missing_items, claimed_amount, threats, pii_request,
              penalty_request, safety_flag} từ tin của khách. Chế độ giả / model trả sai JSON → bộ trích heuristic.
    2. code   tra đơn, khớp món, tính tiền, check_limit, áp luật chặn → chọn 1 trong 3: hoàn (nháp) / hỏi thêm / chuyển người.
    3. model  viết 1 câu trả lời tiếng Việt từ các dữ kiện code đưa (chế độ giả → mẫu cố định).
    4. code   hậu kiểm: mọi con số trong câu trả lời phải có trong dữ kiện, không có SĐT / địa chỉ → sai thì dùng mẫu.
Model không bao giờ tự gõ số tiền, không tự kiểm hạn mức, không tự chuyển tiền.
"""
import json
import re
import unicodedata

import ai
from ai import call_model
from tools import (check_limit, compute_missing_refund, draft_refund, escalate_to_human, get_complaint_history,
                   get_order, request_evidence)
from tracing import note

ISSUES = ("missing_item", "wrong_item", "late", "foreign_object", "food_safety")
# Câu điều khoản nói với khách (rút từ refund_rule của data/policy.json, không chứa số để hậu kiểm số tiền chặt)
CLAUSE = "chính sách thiếu món: hoàn đúng giá món thiếu theo đơn, không hoàn phí ship"

EXTRACT_SYSTEM = """Bạn trích thông tin từ tin nhắn khiếu nại đơn giao đồ ăn. Chỉ trả về MỘT object JSON, không giải thích:
{"order_id": "DH-xxxx" hoặc null, "issue_type": một trong %s,
 "missing_items": [{"name": "tên món khách nói", "qty": số hoặc null}],
 "claimed_amount": số tiền khách đòi (VND) hoặc null, "threats": true nếu doạ 1 sao / bóc phốt / review xấu,
 "pii_request": true nếu đòi số điện thoại / địa chỉ của shipper hoặc quán,
 "penalty_request": true nếu đòi phạt / trừ tiền / khoá quán hoặc shipper,
 "safety_flag": true nếu có dị vật, nghi ngộ độc, dị ứng, triệu chứng sức khoẻ}
Không đoán: thông tin không có trong tin thì để null hoặc []."""

REPLY_SYSTEM = """Bạn là nhân viên CSKH app giao đồ ăn. Viết câu trả lời tiếng Việt ngắn (tối đa 4 câu), lịch sự, xưng "mình" gọi "bạn".
Chỉ dùng dữ kiện được đưa. Bắt buộc nêu: quyết định, số tiền (nếu có, chép đúng y nguyên), điều khoản chính sách (nếu có), bước tiếp theo.
Không viết con số nào khác ngoài các số có trong dữ kiện. Không hứa gì ngoài dữ kiện. Không nêu số điện thoại, địa chỉ của ai.
Không đổ lỗi cho quán hay shipper. Chỉ trả về nội dung câu trả lời."""


# ---------- bước 1: trích thông tin ----------

def fold(s):
    """Chữ thường, bỏ dấu tiếng Việt, để so khớp tên món."""
    s = unicodedata.normalize("NFD", (s or "").lower().replace("đ", "d"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


ORDER_RE = re.compile(r"\bDH[-\s]?(\d{3,})\b", re.I)
KW = {  # từ khoá đã bỏ dấu
    "safety_flag": r"\b(?:di vat|toc|soi toc|con gian|con ruoi|con sau|con trung|manh (thuy tinh|nhua|kim loai)|ngo doc"
                   r"|dau bung|tieu chay|non mua|bi oi|di ung|noi man|kho tho|ngua)\b",
    "threats": r"\b(?:1 sao|mot sao|boc phot|review xau|danh gia (thap|xau)|len mang|bao chi)\b",
    "pii_request": r"\b(so dien thoai|sdt|so dt|dia chi|nha o)\b.{0,25}\b(shipper|tai xe|quan|cua hang|nha hang|ben)\b"
                   r"|\b(shipper|tai xe|quan|cua hang|nha hang)\b.{0,25}\b(so dien thoai|sdt|so dt|dia chi)\b",
    "penalty_request": r"\b(phat|tru tien|khoa|duoi|ky luat)\b.{0,15}\b(shipper|tai xe|quan|shop|cua hang)\b",
}
ISSUE_KW = [("foreign_object", r"\b(?:di vat|toc|soi toc|con gian|con ruoi|con sau|manh)\b"),
            ("food_safety", r"\b(?:ngo doc|dau bung|tieu chay|non|bi oi|di ung|noi man|kho tho|thiu|bi hong)\b"),
            ("wrong_item", r"\b(?:sai mon|nham mon|giao nham|khong dung mon)\b"),
            ("missing_item", r"\b(?:thieu|khong co|chua co|quen bo|khong thay)\b"),
            ("late", r"\b(?:tre|cham|lau qua)\b")]
MENTION_RE = re.compile(r"(?:thieu|khong co|chua co|quen bo|khong thay)\s+(.+?)(?=[.!?;]|\bnhung\b|\bcon lai\b|$)")
QTY_RE = re.compile(r"^(\d+)\s*(?:ly|phan|cai|hop|suat|mieng|chai|lon|to|dia|goi|banh)?\s*")
# phần sau dấu phẩy bắt đầu bằng các từ này là câu khác, không còn là tên món
NOT_ITEM_RE = re.compile(r"^(?:gui don khieu nai|hoan|cho|xin|phat|neu|khong|giup|lam|shop|ad|minh|toi|em|anh|chi|ban|tru|khoa|vui|mong)\b")


def heuristic_extract(text):
    """Bộ trích tất định (chế độ giả + dự phòng khi model trả JSON hỏng)."""
    f = fold(text) + " "
    m = ORDER_RE.search(text)
    issue = next((name for name, pat in ISSUE_KW if re.search(pat, f)), "missing_item")
    items = []
    for chunk in MENTION_RE.findall(f):
        for part in re.split(r",|\b(?:va|voi)\b|\+", chunk):
            part = part.strip()
            if NOT_ITEM_RE.match(part):
                break
            part = re.sub(r"^(?:thieu|khong co|chua co|quen bo|khong thay)\s+", "", part)
            q = QTY_RE.match(part)
            name = part[q.end():].strip() if q else part
            if name and name != "mon":
                items.append({"name": name, "qty": int(q.group(1)) if q and q.group(1) else None})
    money = re.search(r"(\d[\d.,]*)\s*(k|nghin|ngan|d|vnd|dong)\b", f)
    claimed = None
    if money:
        claimed = int(re.sub(r"\D", "", money.group(1))) * (1000 if money.group(2) in ("k", "nghin", "ngan") else 1)
    out = {"order_id": "DH-" + m.group(1) if m else None, "issue_type": issue, "missing_items": items,
           "claimed_amount": claimed}
    out.update({k: bool(re.search(p, f)) for k, p in KW.items()})
    return out


def parse_json(s):
    """Lấy object JSON đầu tiên trong chữ model trả (chịu được ```json ... ``` và chữ thừa)."""
    start, end = (s or "").find("{"), (s or "").rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        d = json.loads(s[start:end + 1])
    except ValueError:
        return None
    return d if isinstance(d, dict) else None


def extract(text):
    rule = heuristic_extract(text)
    if ai.MODEL_PROVIDER == "fake":
        return rule
    d = parse_json(call_model(EXTRACT_SYSTEM % (ISSUES,), text)["text"])
    if not d:
        note("model trả JSON hỏng → dùng bộ trích heuristic")
        return rule
    # Mã đơn: chỉ nhận mã có thật trong tin (model không được bịa mã). Cờ an toàn: OR với từ khoá của code.
    oid = str(d.get("order_id") or "").upper().replace(" ", "-")
    d["order_id"] = oid if oid and fold(oid).replace("-", "") in fold(text).replace("-", "").replace(" ", "") else rule["order_id"]
    if d.get("issue_type") not in ISSUES:
        d["issue_type"] = rule["issue_type"]
    d["missing_items"] = [i for i in (d.get("missing_items") or []) if isinstance(i, dict) and i.get("name")] \
        or rule["missing_items"]
    for k in KW:
        d[k] = bool(d.get(k)) or rule[k]
    return d


# ---------- bước 2: code quyết định ----------

def match_items(order, mentions):
    """Khớp tên món khách nói với món trên đơn (bỏ dấu, theo tỉ lệ từ trùng).
    Trả (khớp, không khớp). Hai món cùng điểm cao nhất = mơ hồ → coi như không khớp để hỏi lại."""
    def words(s):
        return set(re.findall(r"[a-z]+", fold(s)))
    matched, unknown = [], []
    for men in mentions:
        w = words(men["name"])
        scored = sorted(((len(w & words(it["name"])) / max(1, min(len(w), len(words(it["name"])))), i)
                         for i, it in enumerate(order["items"])), reverse=True)
        top = [i for s, i in scored if s >= 0.6 and s == scored[0][0]]
        if len(top) == 1:
            it = order["items"][top[0]]
            matched.append({"item_id": it["item_id"], "name": it["name"], "qty": men.get("qty"), "ordered_qty": it["qty"]})
        else:
            unknown.append(men["name"])
    return matched, unknown


def decide(x, text):
    """Chọn hành động bằng code. Trả dict dữ kiện cho bước viết câu trả lời."""
    oid = x.get("order_id")
    if x.get("safety_flag"):  # dị vật / ngộ độc / dị ứng: thẳng tới người, không tự hoàn
        escalate_to_human(oid, "an toàn thực phẩm: %s" % x.get("issue_type"), "high")
        return {"action": "escalate", "priority": "high", "order_id": oid,
                "why": "trường hợp liên quan an toàn thực phẩm / sức khoẻ cần nhân viên xử lý ngay",
                "next": "bạn giữ nguyên món và bao bì, chụp ảnh lại, nhân viên sẽ liên hệ bạn sớm nhất; "
                        "nếu thấy khó chịu trong người, bạn hãy đi khám ngay"}
    if not oid:
        return {"action": "ask", "question": "Bạn cho mình xin mã đơn (dạng DH-xxxx) bị thiếu món nhé?"}
    order = get_order(oid)
    if not order:
        return {"action": "ask", "order_id": oid,
                "question": "Mình không tìm thấy đơn %s. Bạn kiểm tra lại giúp mình mã đơn nhé?" % oid}
    hospital = order.get("delivery_to") == "hospital" and order.get("diet_note")
    if x.get("issue_type") != "missing_item":
        prio = "high" if hospital and x.get("issue_type") == "wrong_item" else "normal"
        escalate_to_human(oid, "loại khiếu nại %s ngoài phạm vi tự xử lý" % x.get("issue_type"), prio)
        return {"action": "escalate", "priority": prio, "order_id": oid,
                "why": "loại khiếu nại này cần nhân viên kiểm tra", "next": "nhân viên CSKH sẽ liên hệ bạn"}
    matched, unknown = match_items(order, x.get("missing_items") or [])
    names = ", ".join(it["name"] for it in order["items"])
    if unknown or not matched:
        return {"action": "ask", "order_id": oid,
                "question": "Đơn %s gồm: %s. Bạn bị thiếu món nào trong số này?" % (oid, names)}
    unclear = [m for m in matched if m["qty"] is None and m["ordered_qty"] > 1]
    if unclear:
        m = unclear[0]
        return {"action": "ask", "order_id": oid,
                "question": "Đơn có %d phần %s, bạn bị thiếu mấy phần?" % (m["ordered_qty"], m["name"])}
    if hospital:  # đơn tới bệnh viện có ghi chú ăn kiêng: món bù phải hợp chế độ ăn, code không tự phán được
        escalate_to_human(oid, "đơn bệnh viện, ghi chú ăn kiêng: %s" % order["diet_note"], "high")
        return {"action": "escalate", "priority": "high", "order_id": oid,
                "why": "đơn giao tới bệnh viện có chế độ ăn riêng, cần nhân viên xử lý ưu tiên",
                "next": "nhân viên liên hệ bạn ngay để bù món đúng chế độ ăn"}
    refund = compute_missing_refund(order, matched)
    history = get_complaint_history(order.get("user_id"))
    lim = check_limit("missing_item", refund["amount_vnd"], order, history)
    policy = lim["policy"] or {}
    clause = CLAUSE if policy else ""
    if not lim["within"]:
        escalate_to_human(oid, "check_limit: " + lim["reason"], "normal")
        return {"action": "escalate", "priority": "normal", "order_id": oid, "clause": clause,
                "why": "khiếu nại cần nhân viên kiểm tra thêm theo chính sách",
                "next": "nhân viên CSKH sẽ xem và trả lời bạn"}
    if policy.get("needs_photo") and not re.search(r"\b(?:anh|hinh|chup)\b", fold(text)):
        request_evidence(oid, "ảnh túi hàng và hoá đơn dán trên túi")
        return {"action": "ask", "order_id": oid, "clause": clause,
                "question": "Bạn gửi giúp mình ảnh túi hàng và hoá đơn dán trên túi để mình xử lý nhé?"}
    reason = "thiếu " + ", ".join("%d %s" % (l["qty"], l["name"]) for l in refund["lines"])
    draft_refund(oid, refund["amount_vnd"], reason)
    return {"action": "refund_draft", "order_id": oid, "amount_vnd": refund["amount_vnd"], "items": reason,
            "clause": clause, "next": "bản hoàn tiền đang chờ nhân viên duyệt, duyệt xong tiền về ví / tài khoản thanh toán"}


# ---------- bước 3 + 4: viết câu trả lời và hậu kiểm ----------

def vnd(n):
    return "{:,}".format(int(n)).replace(",", ".") + "đ"


def template(f, x):
    if f["action"] == "ask":
        body = "Xin lỗi bạn vì sự bất tiện. " + f["question"]
    elif f["action"] == "escalate":
        body = "Xin lỗi bạn vì sự cố%s. Mình đã chuyển cho nhân viên%s vì %s%s. Bước tiếp theo: %s." % (
            " với đơn " + f["order_id"] if f.get("order_id") else "",
            " (ưu tiên cao)" if f["priority"] == "high" else "", f["why"],
            " (điều khoản: %s)" % f["clause"] if f.get("clause") else "", f["next"])
    else:
        body = "Xin lỗi bạn vì đơn %s bị %s. Mình đã tạo đề nghị hoàn %s%s. Bước tiếp theo: %s." % (
            f["order_id"], f["items"], vnd(f["amount_vnd"]),
            " theo điều khoản: " + f["clause"] if f.get("clause") else "", f["next"])
    extra = []
    if x.get("threats") or (x.get("claimed_amount") and f.get("amount_vnd") and x["claimed_amount"] > f["amount_vnd"]):
        extra.append("Mức xử lý theo chính sách và giá món trên đơn, như nhau với mọi khách.")
    if x.get("pii_request"):
        extra.append("Mình không thể cung cấp số điện thoại hay địa chỉ của shipper / quán.")
    if x.get("penalty_request"):
        extra.append("Quán và shipper chỉ bị xử lý khi đã xác minh có lỗi.")
    return " ".join([body] + extra)


NUM_RE = re.compile(r"\d[\d.,]*\d|\d")
PHONE_RE = re.compile(r"(?:\+?84|0)(?:[\s.-]?\d){8,10}")
ADDR_RE = re.compile(r"\b\d+[a-z]?(?:/\d+)*\s+(?:đường|phố|ngõ|hẻm|ngách|kiệt)\b|\b(?:phường|quận|huyện)\s+\S", re.I)


def numbers(s):
    return {re.sub(r"\D", "", n) for n in NUM_RE.findall(s)}


def post_check(reply, fallback):
    """Câu trả lời của model chỉ được dùng số có trong mẫu (do code dựng) và không có SĐT / địa chỉ."""
    if not reply.strip():
        return "rỗng"
    extra = numbers(reply) - numbers(fallback)
    if extra:
        return "số lạ: %s" % sorted(extra)
    if PHONE_RE.search(reply) or ADDR_RE.search(reply):
        return "có SĐT / địa chỉ"
    return None


def answer(text: str) -> dict:
    x = extract(text)
    facts = decide(x, text)
    note("quyết định: %s" % facts["action"])
    fallback = template(facts, x)
    if ai.MODEL_PROVIDER == "fake":
        return {"output": fallback}
    reply = call_model(REPLY_SYSTEM, "Dữ kiện (do hệ thống tính, chép đúng số):\n%s\n\nCâu trả lời mẫu tham khảo:\n%s"
                       % (json.dumps(facts, ensure_ascii=False), fallback))["text"].strip()
    problem = post_check(reply, fallback)
    if problem:
        note("hậu kiểm trượt (%s) → dùng câu mẫu" % problem)
        return {"output": fallback}
    return {"output": reply}
