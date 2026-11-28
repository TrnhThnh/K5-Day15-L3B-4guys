"""Luồng chính lát cắt D1: khách báo thiếu món trong đơn giao đồ ăn nhiều món.

Hình dạng: WORKFLOW CỐ ĐỊNH 4 bước (không phải agent tự chọn bước):
    1. model  trích JSON {is_complaint, threats, pii_request, penalty_request, complaints: [{order_id, issue_type,
              missing_items, claimed_amount, safety_flag}, ...]} từ tin của khách, mỗi đơn một phần tử.
              Chế độ giả / model trả sai JSON → bộ trích heuristic (tách tin theo từng mã đơn).
    2. code   với TỪNG đơn: tra đơn, khớp món, tính tiền, check_limit, áp luật chặn → hoàn (nháp) / hỏi thêm / chuyển người.
              Tối đa 3 đơn một tin; nhiều hơn thì chuyển nhân viên.
    3. model  viết 1 câu trả lời tiếng Việt từ các dữ kiện code đưa, mỗi đơn một đoạn (chế độ giả → mẫu cố định).
    4. code   hậu kiểm: mọi con số phải có trong dữ kiện, đủ mọi mã đơn, không có SĐT / địa chỉ → sai thì dùng mẫu;
              luôn có lời xin lỗi ở đầu và lời cảm ơn ở cuối.
Tin không phải khiếu nại (hỏi giờ mở cửa, đổi địa chỉ...) và đơn chưa giao xong thì nói thẳng, không đi vào luồng hoàn tiền.
Model không bao giờ tự gõ số tiền, không tự kiểm hạn mức, không tự chuyển tiền. Mỗi nháp hoàn / phiếu chuyển người có
mã yêu cầu (YC-xxxx) và nằm trong hàng chờ duyệt của nhân viên (tools.py).
"""
import json
import re
import unicodedata
from datetime import datetime

import ai
from ai import call_model
from tools import (OUTBOX, check_limit, compute_missing_refund, draft_refund, escalate_to_human, get_complaint_history,
                   get_order, request_evidence)
from tracing import note

ISSUES = ("missing_item", "wrong_item", "late", "foreign_object", "food_safety")
MAX_ORDERS = 3  # số đơn tối đa xử lý trong một tin; nhiều hơn thì chuyển nhân viên
COMPLAINT_KEYS = ("order_id", "issue_type", "missing_items", "claimed_amount", "safety_flag")
APOLOGY = "Mình thành thật xin lỗi vì sự bất tiện bạn gặp phải."
THANKS = "Cảm ơn bạn đã báo cho mình."
# Câu điều khoản nói với khách (rút từ refund_rule của data/policy.json, không chứa số để hậu kiểm số tiền chặt)
CLAUSE = "chính sách thiếu món: hoàn đúng giá món thiếu theo đơn, không hoàn phí ship"
# Thời điểm khách báo, dùng để kiểm hạn báo. Dữ liệu dựng nên cố định mốc theo data/DATA_CARD.md
# (không lấy giờ máy, để kết quả không đổi theo ngày chạy). Bản thật: lấy giờ nhận tin nhắn.
REPORT_NOW = datetime.fromisoformat("2026-11-27T21:00:00+07:00")

EXTRACT_SYSTEM = """Bạn trích thông tin từ tin nhắn khiếu nại đơn giao đồ ăn. Chỉ trả về MỘT object JSON, không giải thích:
{"is_complaint": true nếu tin là khiếu nại về đơn đồ ăn (thiếu / sai món, giao trễ, đồ ăn có vấn đề), false nếu là câu hỏi hay yêu cầu khác,
 "threats": true nếu doạ 1 sao / bóc phốt / review xấu,
 "pii_request": true nếu đòi số điện thoại / địa chỉ của shipper hoặc quán,
 "penalty_request": true nếu đòi phạt / trừ tiền / khoá quán hoặc shipper,
 "complaints": [MỖI ĐƠN KHÁCH NHẮC TỚI MỘT PHẦN TỬ:
   {"order_id": "DH-xxxx" hoặc null, "issue_type": một trong %s,
    "missing_items": [{"name": "tên món khách nói cho đơn này", "qty": số hoặc null}],
    "claimed_amount": số tiền khách đòi cho đơn này (VND) hoặc null,
    "safety_flag": true nếu đơn này có dị vật, nghi ngộ độc, dị ứng, triệu chứng sức khoẻ}]}
Không đoán: thông tin không có trong tin thì để null hoặc []. Không gán món của đơn này sang đơn khác."""

REPLY_SYSTEM = """Bạn là nhân viên CSKH app giao đồ ăn. Viết câu trả lời tiếng Việt ngắn gọn, lịch sự và tôn trọng, xưng "mình" gọi "bạn".
Giọng điệu: mở đầu bằng lời xin lỗi chân thành vì sự bất tiện; thừa nhận khó chịu của khách; không trách khách, không nghi ngờ khách; kết thúc bằng lời cảm ơn khách đã báo.
Chỉ dùng dữ kiện được đưa. Bắt buộc nêu: quyết định, số tiền (nếu có, chép đúng y nguyên chuỗi "amount_text", vd 60.000đ), mã yêu cầu (nếu có "request_id", chép y nguyên), điều khoản chính sách (nếu có), bước tiếp theo.
Nếu dữ kiện có nhiều đơn: trả lời đủ từng đơn, mỗi đơn một đoạn bắt đầu bằng "Đơn DH-xxxx:".
Không viết con số nào khác ngoài các số có trong dữ kiện. Không hứa gì ngoài dữ kiện. Không nêu số điện thoại, địa chỉ của ai.
Không đổ lỗi cho quán hay shipper. Không chẩn đoán bệnh hay nguyên nhân.
Nếu dữ kiện có "first": câu ĐẦU TIÊN của câu trả lời phải là đúng nội dung "first", trước cả lời xin lỗi.
Nếu dữ kiện có "question": nêu đủ mọi ý được hỏi trong đó. Viết chữ thường, không dùng markdown (không **, không #). Chỉ trả về nội dung câu trả lời."""


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
    "pii_request": r"\b(so dien thoai|sdt|so dt|dia chi|nha o)\b.{0,25}\b(shipper|tai xe|quan(?!\s*\d)|cua hang|nha hang|ben)\b"
                   r"|\b(shipper|tai xe|quan|cua hang|nha hang)\b.{0,25}\b(so dien thoai|sdt|so dt|dia chi)\b"
                   r"|\b(?:xin|cho|dua|gui)\b.{0,12}\bso (?:cua )?(?:shipper|tai xe|quan|chu quan)\b",
    "penalty_request": r"\b(phat|tru tien|khoa|duoi|ky luat)\b.{0,15}\b(shipper|tai xe|quan|shop|cua hang)\b",
}
# triệu chứng sức khoẻ (ngộ độc / dị ứng) và dấu hiệu nặng cần gọi cấp cứu, đã bỏ dấu
KW_HEALTH = (r"\b(?:ngo doc|dau bung|tieu chay|non mua|buon non|bi non|noi man|man ngua|di ung|kho tho|kho khe"
             r"|sung (?:moi|hong|mat|luoi)|moi (?:hoi )?sung|choang|ngat)\b")
KW_SEVERE = r"\b(?:kho tho|kho khe|sung (?:moi|hong|mat|luoi)|moi (?:hoi )?sung|ngat|tim tai|choang)\b"
ISSUE_KW = [("foreign_object", r"\b(?:di vat|toc|soi toc|con gian|con ruoi|con sau|manh)\b"),
            ("food_safety", r"\b(?:ngo doc|dau bung|tieu chay|non|bi oi|di ung|noi man|kho tho|thiu|bi hong)\b"),
            ("wrong_item", r"\b(?:sai mon|nham mon|giao nham|khong dung mon)\b"),
            ("missing_item", r"\b(?:thieu|khong co|chua co|quen bo|khong thay)\b"),
            ("late", r"\b(?:tre|cham|lau qua)\b")]
COMPLAINT_KW = r"\b(?:hoan|den bu|boi thuong|khieu nai)\b"
# "nhưng" (liên từ) được thay bằng dấu chấm TRƯỚC khi bỏ dấu, vì sau khi bỏ dấu nó trùng "nhúng" (lẩu nhúng giấm)
BUT_RE = re.compile(r"\bnhưng\b", re.I)
MENTION_RE = re.compile(r"(?:thieu|khong co|chua co|quen bo|khong thay)\s+(.+?)(?=[.!?;)]|\bcon lai\b|$)")
QTY_RE = re.compile(r"^(\d+)\s*(?:ly|phan|cai|hop|suat|mieng|chai|lon|to|dia|goi|banh)?\s*")
# phần sau dấu phẩy bắt đầu bằng các từ này là câu khác, không còn là tên món
NOT_ITEM_RE = re.compile(r"^(?:con$|con (?:don|thi)|gui don khieu nai|hoan|cho|xin|phat|neu|khong|giup|lam|shop|ad|minh|toi|em|anh|chi|ban|tru|khoa|vui|mong"
                         r"|gio moi|tuan|hom|ca nha|ca phong|dang|roi|ma|nen|nen tang|doi tac|app)\b")
# chữ đứng trước tên món, không thuộc tên món ("thiếu nguyên nồi lẩu" → "lẩu")
LEAD_RE = re.compile(r"^(?:nguyen|ca|het|luon)\s+(?:(?:noi|phan|suat|to|hop|ly|dia)\s+)?")


def split_by_order(text):
    """Tách tin theo từng mã đơn: mỗi đoạn bắt đầu ở một mã đơn (đoạn đầu gồm cả phần trước mã đầu tiên).
    → [(mã đơn, đoạn tin)]. Mã đơn nhắc lại nhiều lần thì gộp các đoạn của nó."""
    ms = list(ORDER_RE.finditer(text))
    if len({m.group(1) for m in ms}) <= 1:
        return [(("DH-" + ms[0].group(1)) if ms else None, text)]
    parts = {}
    for i, m in enumerate(ms):
        start = 0 if i == 0 else m.start()
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        oid = "DH-" + m.group(1)
        parts[oid] = (parts.get(oid, "") + " " + text[start:end]).strip()
    return list(parts.items())


def heuristic_extract(text):
    """Bộ trích tất định (chế độ giả + dự phòng khi model trả JSON hỏng): cờ của cả tin + mỗi đơn một khiếu nại."""
    whole = heuristic_one(text)
    out = {k: whole[k] for k in ("is_complaint", "threats", "pii_request", "penalty_request", "safety_flag")}
    out["complaints"] = []
    for oid, segment in split_by_order(text):
        one = heuristic_one(segment)
        out["complaints"].append(dict({k: one[k] for k in COMPLAINT_KEYS}, order_id=oid, text=segment))
    return out


def heuristic_one(text):
    """Trích một khiếu nại từ một đoạn tin (từ khoá, không gọi model)."""
    f = fold(BUT_RE.sub(".", text)) + " "
    m = ORDER_RE.search(text)
    found = next((name for name, pat in ISSUE_KW if re.search(pat, f)), None)
    issue = found or "missing_item"
    items = []
    for chunk in MENTION_RE.findall(f):
        for part in re.split(r",|\b(?:va|voi)\b|\+", chunk):
            part = part.strip()
            if NOT_ITEM_RE.match(part):
                break
            part = re.sub(r"^(?:thieu|khong co|chua co|quen bo|khong thay)\s+", "", part)
            part = LEAD_RE.sub("", part)
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
    # có từ khoá sự cố, cờ an toàn, hoặc lời đòi hoàn / đền / khiếu nại thì coi là khiếu nại
    out["is_complaint"] = bool(found) or out["safety_flag"] or bool(re.search(COMPLAINT_KW, f))
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
    in_text = fold(text).replace("-", "").replace(" ", "")
    by_rule = {c["order_id"]: c for c in rule["complaints"] if c["order_id"]}
    single_rule = rule["complaints"][0] if len(rule["complaints"]) == 1 else {}
    raw = d.get("complaints")
    if not isinstance(raw, list) or not raw:
        raw = [d]  # model trả kiểu một đơn
    complaints, seen = [], set()
    for c in raw:
        if not isinstance(c, dict):
            continue
        # Mã đơn: chỉ nhận mã có thật trong tin (model không được bịa mã).
        oid = str(c.get("order_id") or "").upper().replace(" ", "-")
        oid = oid if oid and fold(oid).replace("-", "") in in_text else None
        r = by_rule.get(oid) or single_rule
        oid = oid or r.get("order_id")
        if oid in seen:
            continue
        seen.add(oid)
        items = [i for i in (c.get("missing_items") or []) if isinstance(i, dict) and i.get("name")]
        complaints.append({
            "order_id": oid,
            "issue_type": c.get("issue_type") if c.get("issue_type") in ISSUES else r.get("issue_type", "missing_item"),
            "missing_items": items or r.get("missing_items") or [],
            "claimed_amount": c.get("claimed_amount") if c.get("claimed_amount") is not None else r.get("claimed_amount"),
            # cờ an toàn: OR với từ khoá của code
            "safety_flag": bool(c.get("safety_flag")) or bool(r.get("safety_flag")),
            "text": r.get("text") or text})
    # Đơn có mã trong tin mà model bỏ sót: vẫn xử lý theo bộ trích của code, để không đơn nào bị bỏ qua.
    complaints += [c for oid, c in by_rule.items() if oid not in seen]
    if len(complaints) > 1:  # nhiều đơn: bỏ khiếu nại không có mã đơn (đã nằm trong các đơn có mã)
        complaints = [c for c in complaints if c["order_id"]] or complaints[:1]
    out = {k: bool(d.get(k)) or rule[k] for k in KW}
    out["safety_flag"] = out["safety_flag"] or any(c["safety_flag"] for c in complaints)
    # Chỉ coi là ngoài phạm vi khi cả model lẫn từ khoá của code đều thấy đây không phải khiếu nại,
    # để một khiếu nại thật không bị gạt đi vì model đọc nhầm.
    out["is_complaint"] = d.get("is_complaint") is not False or rule["is_complaint"]
    out["complaints"] = complaints or rule["complaints"]
    return out


# ---------- bước 2: code quyết định ----------

def match_items(order, mentions):
    """Khớp tên món khách nói với món trên đơn (bỏ dấu, theo tỉ lệ từ trùng, giữ chữ số trong tên món
    để "gà rán 2 miếng" khác "combo gà rán 6 miếng"). Điểm bằng nhau thì xét thêm độ trùng Jaccard.
    Trả (khớp, không có trong đơn, mơ hồ). Hai món vẫn cùng điểm cao nhất = mơ hồ → hỏi lại."""
    def words(s, mention=False):
        f = fold(s).strip()
        if mention:  # bỏ số lượng + đơn vị đứng đầu ("3 ly trà sữa" → "trà sữa"), số lượng đã nằm ở qty
            q = QTY_RE.match(f)
            f = f[q.end():] if q else f
        return set(re.findall(r"[a-z0-9]+", f))
    matched, unknown, ambiguous = [], [], []
    for men in mentions:
        w = words(men["name"], mention=True)
        scored = []
        for i, it in enumerate(order["items"]):
            v = words(it["name"])
            inter = len(w & v)
            scored.append(((inter / max(1, min(len(w), len(v))), inter / max(1, len(w | v))), i))
        scored.sort(reverse=True)
        top = [i for s, i in scored if s[0] >= 0.6 and s == scored[0][0]]
        if len(top) == 1:
            it = order["items"][top[0]]
            matched.append({"item_id": it["item_id"], "name": it["name"], "qty": men.get("qty"), "ordered_qty": it["qty"]})
        elif top:
            ambiguous.append(men["name"])
        else:
            unknown.append(men["name"])
    return matched, unknown, ambiguous


def decide(x, text):
    """Chọn hành động bằng code. Trả dict dữ kiện cho bước viết câu trả lời."""
    oid = x.get("order_id")
    if x.get("safety_flag"):  # dị vật / ngộ độc / dị ứng: thẳng tới người, không tự hoàn
        f = fold(text)
        health = x.get("issue_type") == "food_safety" or re.search(KW_HEALTH, f)
        severe = re.search(KW_SEVERE, f)
        escalate_to_human(oid, "an toàn thực phẩm: %s" % x.get("issue_type"), "urgent" if health else "high")
        facts = {"action": "escalate", "priority": "urgent" if health else "high", "order_id": oid,
                 "why": "trường hợp liên quan an toàn thực phẩm / sức khoẻ cần nhân viên xử lý ngay",
                 "next": "bạn giữ nguyên món và bao bì, chụp ảnh lại, nhân viên sẽ liên hệ bạn sớm nhất"}
        if health:  # policy food_safety: khuyên cấp cứu TRƯỚC mọi ý khác, không chẩn đoán
            facts["first"] = ("Nếu người ăn đang khó thở, sưng môi hoặc họng, bạn hãy gọi cấp cứu 115 hoặc đưa tới "
                              "cơ sở y tế gần nhất ngay." if severe else
                              "Nếu người ăn thấy khó chịu nhiều hơn, bạn hãy đưa tới cơ sở y tế gần nhất hoặc gọi 115 ngay.")
        else:
            facts["next"] += "; nếu thấy khó chịu trong người, bạn hãy đi khám ngay"
        return facts
    if not x.get("is_complaint", True):  # ngoài phạm vi: nói thẳng, không đoán, không chuyển tiền
        return {"action": "info", "message": "Mình chỉ hỗ trợ khiếu nại đơn đồ ăn đã giao bị thiếu món, nên không có "
                                             "thông tin cho yêu cầu này. Bạn dùng mục Trợ giúp trong app hoặc nhắn quán qua "
                                             "chat trong app nhé. Nếu đơn của bạn bị thiếu món, bạn gửi mình mã đơn và tên món."}
    if not oid:
        return {"action": "ask", "question": "Bạn cho mình xin mã đơn (dạng DH-xxxx) và cho mình biết "
                                             "bạn bị thiếu món nào, mấy phần nhé?"}
    order = get_order(oid)
    if not order:
        return {"action": "ask", "order_id": oid,
                "question": "Mình không tìm thấy đơn %s. Bạn kiểm tra lại giúp mình mã đơn nhé?" % oid}
    if order.get("status") == "delivering":  # chưa tới tay khách thì chưa thể thiếu món
        return {"action": "info", "order_id": oid,
                "message": "Đơn %s đang được giao, chưa tới tay bạn. Khi nhận đơn mà thiếu món, bạn nhắn lại mình "
                           "kèm tên món nhé." % oid}
    if order.get("status") != "delivered":  # đã huỷ...: không hoàn theo chính sách thiếu món, chuyển người xem
        escalate_to_human(oid, "đơn ở trạng thái %s, không phải đã giao" % order.get("status"), "normal")
        return {"action": "escalate", "priority": "normal", "order_id": oid,
                "why": "đơn %s đang ở trạng thái %s, không phải đơn đã giao" % (
                    oid, {"cancelled": "đã huỷ"}.get(order.get("status"), order.get("status"))),
                "next": "nhân viên CSKH sẽ kiểm tra đơn và trả lời bạn"}
    hospital = order.get("delivery_to") == "hospital" and order.get("diet_note")
    if x.get("issue_type") != "missing_item":
        if hospital:
            # Đơn bệnh viện có chế độ ăn: mức ưu tiên do code quyết, không phụ thuộc nhãn model gắn (wrong_item,
            # late...). Món nhận được, dù giao nhầm hay có vấn đề, có thể trái chế độ ăn → dặn đừng ăn trước.
            wrong = x.get("issue_type") == "wrong_item"
            escalate_to_human(oid, "đơn bệnh viện có chế độ ăn (%s), khiếu nại %s"
                              % (order["diet_note"], x.get("issue_type")), "high")
            return {"action": "escalate", "priority": "high", "order_id": oid,
                    "first": "Bạn tạm đừng cho bệnh nhân ăn %s, vì có thể không hợp chế độ ăn (%s)."
                             % ("món giao nhầm" if wrong else "món này", order["diet_note"]),
                    "why": "đơn giao tới bệnh viện %s, cần nhân viên xử lý ưu tiên"
                           % ("bị giao nhầm món" if wrong else "có chế độ ăn riêng"),
                    "next": "nhân viên liên hệ bạn ngay để bù đúng món theo chế độ ăn"}
        escalate_to_human(oid, "loại khiếu nại %s ngoài phạm vi tự xử lý" % x.get("issue_type"), "normal")
        return {"action": "escalate", "priority": "normal", "order_id": oid,
                "why": "loại khiếu nại này cần nhân viên kiểm tra", "next": "nhân viên CSKH sẽ liên hệ bạn"}
    matched, unknown, ambiguous = match_items(order, x.get("missing_items") or [])
    names = ", ".join(it["name"] for it in order["items"])
    if unknown and not matched and not ambiguous:  # mọi món khách nêu đều không có trong đơn
        return {"action": "ask", "order_id": oid,
                "question": "Mình không thấy món %s trong đơn %s. Đơn gồm: %s. Bạn kiểm tra lại giúp mình mã đơn "
                            "hoặc cho mình biết bạn bị thiếu món nào trong số này nhé?"
                            % (", ".join('"%s"' % u for u in unknown), oid, names)}
    if unknown or ambiguous or not matched:
        return {"action": "ask", "order_id": oid,
                "question": "Đơn %s gồm: %s. Bạn bị thiếu món nào trong số này, mấy phần?" % (oid, names)}
    unclear = [m for m in matched if m["qty"] is None and m["ordered_qty"] > 1]
    if unclear:
        m = unclear[0]
        return {"action": "ask", "order_id": oid,
                "question": "Đơn có %d phần %s, bạn bị thiếu mấy phần?" % (m["ordered_qty"], m["name"])}
    # Đơn bệnh viện: chỉ chuyển người khi món thiếu thuộc chế độ ăn của bệnh nhân (diet_critical trong data/orders.json),
    # vì món bù phải hợp chế độ ăn, code không tự phán được. Món trung tính (vd nước suối) xử lý như đơn thường.
    # Chặn an toàn (fail closed): món thiếu trường diet_critical vẫn coi là thuộc chế độ ăn → chuyển người.
    diet_ids = {it["item_id"] for it in order["items"] if it.get("diet_critical") is not False}
    if hospital and any(m["item_id"] in diet_ids for m in matched):
        escalate_to_human(oid, "đơn bệnh viện, món thiếu thuộc chế độ ăn: %s" % order["diet_note"], "high")
        return {"action": "escalate", "priority": "high", "order_id": oid,
                "why": "đơn giao tới bệnh viện có chế độ ăn riêng, cần nhân viên xử lý ưu tiên",
                "next": "nhân viên liên hệ bạn ngay để bù món đúng chế độ ăn; nếu trong túi có món không có trong đơn, "
                        "bạn tạm đừng cho bệnh nhân ăn món đó"}
    refund = compute_missing_refund(order, matched)
    history = get_complaint_history(order.get("user_id"))
    lim = check_limit("missing_item", refund["amount_vnd"], order, history, now=REPORT_NOW)
    policy = lim["policy"] or {}
    clause = CLAUSE if policy else ""
    if not lim["within"]:
        escalate_to_human(oid, "check_limit: " + lim["reason"], "normal")
        # Nói lý do với khách khi đó là quy tắc chung (quá hạn báo, vượt hạn mức); lý do "khiếu nại lặp" giữ kín
        # để không thành câu buộc tội khách.
        told = lim["reason"] if lim["reason"].startswith(("quá hạn báo", "vượt hạn mức")) else None
        return {"action": "escalate", "priority": "normal", "order_id": oid, "clause": clause,
                "why": ("khiếu nại %s, cần nhân viên xem xét" % told) if told
                       else "khiếu nại cần nhân viên kiểm tra thêm theo chính sách",
                "next": "nhân viên CSKH sẽ xem và trả lời bạn"}
    if policy.get("needs_photo") and not re.search(r"\b(?:anh|hinh|chup)\b", fold(text)):
        request_evidence(oid, "ảnh túi hàng và hoá đơn dán trên túi")
        return {"action": "ask", "order_id": oid, "clause": clause,
                "question": "Bạn gửi giúp mình ảnh túi hàng và hoá đơn dán trên túi để mình xử lý nhé?"}
    reason = "thiếu " + ", ".join("%d %s" % (l["qty"], l["name"]) for l in refund["lines"])
    draft_refund(oid, refund["amount_vnd"], reason)
    return {"action": "refund_draft", "order_id": oid, "amount_vnd": refund["amount_vnd"],
            "amount_text": vnd(refund["amount_vnd"]), "items": reason,
            "clause": clause, "next": "bản hoàn tiền đang chờ nhân viên duyệt, duyệt xong tiền về ví / tài khoản thanh toán"}


# ---------- bước 3 + 4: viết câu trả lời và hậu kiểm ----------

def vnd(n):
    return "{:,}".format(int(n)).replace(",", ".") + "đ"


def part(f, with_items=True):
    """Nội dung xử lý của một đơn, chưa có lời xin lỗi."""
    req = "mã yêu cầu %s" % f["request_id"] if f.get("request_id") else ""
    clause = " theo điều khoản: " + f["clause"] if f.get("clause") else ""
    if f["action"] == "info":
        return f["message"]
    if f["action"] == "ask":
        return f["question"]
    if f["action"] == "escalate":
        tags = [t for t in ({"high": "ưu tiên cao", "urgent": "mức khẩn"}.get(f["priority"], ""), req) if t]
        return "Mình đã chuyển cho nhân viên%s vì %s%s. Bước tiếp theo: %s." % (
            " (%s)" % ", ".join(tags) if tags else "", f["why"],
            " (điều khoản: %s)" % f["clause"] if f.get("clause") else "", f["next"])
    return "Mình đã tạo đề nghị hoàn %s%s%s%s. Bước tiếp theo: %s." % (
        vnd(f["amount_vnd"]), " cho phần " + f["items"] if with_items else "", " (%s)" % req if req else "",
        clause, f["next"])


def template_body(facts_list):
    """Câu trả lời mẫu do code dựng: lời dặn an toàn (nếu có) → xin lỗi → xử lý từng đơn."""
    firsts = " ".join(f["first"] for f in facts_list if f.get("first"))
    lead = firsts + " " if firsts else ""
    if len(facts_list) > 1:
        def labelled(f):  # "Đơn DH-xxxx: …", trừ khi câu đã tự mở đầu bằng mã đơn đó
            p = part(f)
            return p if p.startswith("Đơn %s" % f["order_id"]) else "Đơn %s: %s" % (f["order_id"], p)
        return lead + "Mình thành thật xin lỗi vì sự bất tiện với các đơn của bạn. " + " ".join(
            labelled(f) for f in facts_list)
    f = facts_list[0]
    if f["action"] == "refund_draft":
        return lead + "Mình thành thật xin lỗi vì đơn %s bị %s. %s" % (f["order_id"], f["items"], part(f, False))
    if f["action"] == "escalate" and f.get("order_id"):
        return lead + "Mình thành thật xin lỗi vì sự cố với đơn %s. %s" % (f["order_id"], part(f))
    if f["action"] == "info" and not f.get("order_id"):  # câu ngoài phạm vi: xin lỗi vì không giúp được, không nói "bất tiện"
        msg = part(f)
        return lead + "Mình xin lỗi, " + msg[0].lower() + msg[1:]
    return lead + APOLOGY + " " + part(f)


def required_lines(facts_list, complaints, x):
    """Các câu BẮT BUỘC do code gắn vào cuối câu trả lời (model không được bỏ): từ chối SĐT / địa chỉ,
    lời doạ / đòi thêm không đổi mức hoàn, không hứa phạt quán / shipper."""
    lines = []
    over = any(c.get("claimed_amount") and f.get("amount_vnd") and c["claimed_amount"] > f["amount_vnd"]
               for f, c in zip(facts_list, complaints))
    if x.get("threats") or over:
        lines.append("Mức xử lý theo chính sách và giá món trên đơn, như nhau với mọi khách.")
    if x.get("pii_request"):
        lines.append("Mình không thể cung cấp số điện thoại hay địa chỉ của shipper / quán; "
                     "bạn liên hệ qua chat hoặc gọi trong app nhé.")
    if x.get("penalty_request"):
        lines.append("Quán và shipper chỉ bị xử lý khi đã xác minh có lỗi.")
    return lines


def finish(reply, facts_list, lines):
    """Bảo đảm giọng điệu: có lời xin lỗi ngay đầu (sau lời dặn an toàn nếu có), câu bắt buộc, lời cảm ơn ở cuối."""
    reply = reply.replace("**", "").replace("__", "")  # bỏ markdown in đậm, khách thấy chữ thường
    head = 160 + sum(len(f["first"]) for f in facts_list if f.get("first"))
    if "xin loi" not in fold(reply[:head]):
        cut = re.search(r"[.!?]\s+", reply) if any(f.get("first") for f in facts_list) else None
        reply = (reply[:cut.end()] + APOLOGY + " " + reply[cut.end():]) if cut else APOLOGY + " " + reply
    out = " ".join([reply] + lines)
    return out if "cam on" in fold(out) else out + " " + THANKS


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


def decide_all(x, text):
    """Bước 2 cho cả tin: mỗi đơn một lần decide(); gắn mã yêu cầu của nháp / phiếu vừa tạo vào dữ kiện."""
    complaints = x["complaints"]
    if not x.get("is_complaint", True):
        return [decide(dict(complaints[0], is_complaint=False), text)], complaints[:1]
    if len(complaints) > MAX_ORDERS:
        d = escalate_to_human(None, "khách khiếu nại %d đơn trong một tin" % len(complaints), "normal")
        return [{"action": "escalate", "priority": "normal", "order_id": None, "request_id": d["request_id"],
                 "why": "tin của bạn nhắc tới %d đơn, nhiều hơn %d đơn mình xử lý được trong một lần"
                        % (len(complaints), MAX_ORDERS),
                 "next": "nhân viên CSKH sẽ xem từng đơn và trả lời bạn; lần sau bạn gửi mỗi đơn một tin "
                         "để được xử lý nhanh hơn"}], [{}]
    facts_list = []
    for c in complaints:
        before = len(OUTBOX)
        f = decide(dict(c, is_complaint=True), c.get("text") or text)
        ids = [d["request_id"] for d in OUTBOX[before:] if d["kind"] in ("refund", "escalation")]
        if ids:
            f["request_id"] = ", ".join(ids)
        facts_list.append(f)
    return facts_list, complaints


def answer(text: str) -> dict:
    x = extract(text)
    facts_list, complaints = decide_all(x, text)
    note("quyết định: %s" % ", ".join(f["action"] for f in facts_list))
    lines = required_lines(facts_list, complaints, x)
    body = template_body(facts_list)
    fallback = finish(body, facts_list, lines)
    if ai.MODEL_PROVIDER == "fake":
        return {"output": fallback}
    # Model chỉ viết lại phần thân; các câu bắt buộc, lời xin lỗi và lời cảm ơn do code bảo đảm.
    facts = facts_list[0] if len(facts_list) == 1 else {"orders": facts_list}
    reply = call_model(REPLY_SYSTEM, "Dữ kiện (do hệ thống tính, chép đúng số):\n%s\n\nCâu trả lời mẫu tham khảo:\n%s"
                       % (json.dumps(facts, ensure_ascii=False), body))["text"].strip()
    problem = post_check(reply, body)
    firsts = [f["first"] for f in facts_list if f.get("first")]
    if not problem and firsts and not reply.startswith(firsts[0][:20]):
        problem = "không mở đầu bằng lời dặn an toàn"
    if not problem and len(facts_list) > 1:
        missing = [f["order_id"] for f in facts_list if f.get("order_id") and f["order_id"] not in reply]
        if missing:
            problem = "thiếu đơn %s" % ", ".join(missing)
    if problem:
        note("hậu kiểm trượt (%s) → dùng câu mẫu" % problem)
        return {"output": fallback}
    lines = [l for l in lines if l not in reply]
    if lines:
        note("gắn câu bắt buộc: %d câu" % len(lines))
    return {"output": finish(reply, facts_list, lines)}
