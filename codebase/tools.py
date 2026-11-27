"""Công cụ của lát cắt D1 (khách báo thiếu món trong đơn giao đồ ăn nhiều món).

Mỗi công cụ là một hàm Python có @tool; docstring ghi: tên · input · output · có tác động ra ngoài không.
Ba nhóm:
    chỉ đọc        get_order, get_policy, get_complaint_history   (đọc data/*.json, nạp lười lần đầu dùng)
    code kiểm      check_limit, compute_missing_refund            (con số do code tính, không do model)
    tác động ngoài draft_refund, escalate_to_human, request_evidence  (CHỈ tạo bản nháp chờ nhân viên duyệt)
Bản nháp được giữ trong OUTBOX (bộ nhớ). Bản thật sẽ đẩy vào hàng chờ của nhân viên CSKH.
"""
import json
import os
from datetime import datetime, timedelta

from tracing import tool, TOOLS  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("D1_DATA_DIR") or os.path.join(ROOT, "data")  # D1_DATA_DIR: chỉ để thử với fixture riêng
_cache = {}
OUTBOX = []  # bản nháp hoàn tiền / chuyển người / xin bằng chứng, chờ nhân viên duyệt


def _load(name, default):
    """Đọc data/<name> một lần rồi giữ trong bộ nhớ. Thiếu file thì trả default."""
    if name not in _cache:
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as f:
                _cache[name] = json.load(f)
        else:
            _cache[name] = default
    return _cache[name]


# ---------- chỉ đọc ----------

@tool
def get_order(order_id: str):
    """get_order · input: mã đơn (vd "DH-1001") · output: dict đơn (món, giá, giờ giao, delivery_to, diet_note,
    status) hoặc None nếu không có · không tác động ra ngoài."""
    key = (order_id or "").strip().upper()
    return next((o for o in _load("orders.json", []) if o.get("order_id", "").upper() == key), None)


@tool
def get_policy(issue_type: str):
    """get_policy · input: loại khiếu nại (missing_item, wrong_item, late, foreign_object, food_safety) ·
    output: dict điều khoản (hạn mức, số lần / 30 ngày, cần ảnh, nguồn) hoặc None · không tác động ra ngoài."""
    return next((p for p in _load("policy.json", []) if p.get("issue_type") == issue_type), None)


@tool
def get_complaint_history(user_id: str) -> list:
    """get_complaint_history · input: mã khách (vd "KH-01") · output: danh sách khiếu nại cũ
    {date, order_id, issue_type, outcome, amount_vnd} · không tác động ra ngoài."""
    return list(_load("complaint_history.json", {}).get(user_id or "", []))


# ---------- code kiểm (model không được tự làm) ----------

def _when(s):
    return datetime.fromisoformat(s) if s else None


@tool
def compute_missing_refund(order: dict, missing: list) -> dict:
    """compute_missing_refund · input: đơn + danh sách {item_id, qty} khách báo thiếu ·
    output: {amount_vnd, lines:[{item_id, name, qty, unit_price_vnd, subtotal_vnd}]}, số tiền cộng từ giá
    trên đơn (không hoàn phí ship), qty không vượt số lượng đã đặt · không tác động ra ngoài."""
    by_id = {it["item_id"]: it for it in order.get("items", [])}
    lines = []
    for m in missing:
        it = by_id.get(m["item_id"])
        if not it:
            continue
        qty = max(1, min(int(m.get("qty") or it["qty"]), int(it["qty"])))
        lines.append({"item_id": it["item_id"], "name": it["name"], "qty": qty,
                      "unit_price_vnd": it["unit_price_vnd"], "subtotal_vnd": qty * it["unit_price_vnd"]})
    return {"amount_vnd": sum(l["subtotal_vnd"] for l in lines), "lines": lines}


@tool
def check_limit(issue_type: str, amount_vnd: int, order: dict, history: list, now=None) -> dict:
    """check_limit · input: loại khiếu nại, số tiền đề xuất, đơn, lịch sử khiếu nại của khách,
    (tuỳ chọn) thời điểm khách báo · output: {"within": bool, "reason": str, "policy": dict|None} ·
    không tác động ra ngoài. Đây là chốt chặn hạn mức: chạy bằng code, không phải model."""
    policy = get_policy(issue_type)
    if not policy:
        return {"within": False, "reason": "không có điều khoản cho loại khiếu nại %s" % issue_type, "policy": None}
    if order.get("status") != "delivered":
        return {"within": False, "reason": "đơn ở trạng thái %s, không phải đã giao" % order.get("status"), "policy": policy}
    cap = int(policy.get("max_refund_vnd_per_order") or 0)
    if amount_vnd <= 0:
        return {"within": False, "reason": "số tiền hoàn bằng 0", "policy": policy}
    if amount_vnd > cap:
        return {"within": False, "reason": "vượt hạn mức %sđ / đơn" % "{:,}".format(cap).replace(",", "."),
                "policy": policy}
    if amount_vnd > int(order.get("total_vnd") or 0):
        return {"within": False, "reason": "lớn hơn tổng tiền đơn", "policy": policy}
    delivered = _when(order.get("delivered_at"))
    window = policy.get("report_window_hours")
    if now and delivered and window and now - delivered > timedelta(hours=window):
        return {"within": False, "reason": "quá hạn báo %s giờ sau khi giao" % window, "policy": policy}
    max_claims = policy.get("max_claims_per_user_30d")
    if delivered and max_claims is not None:
        since = delivered - timedelta(days=30)
        day = lambda h: datetime.fromisoformat((h.get("date") or h.get("created_at"))[:10]).date()  # noqa: E731
        recent = [h for h in history if h.get("order_id") != order.get("order_id")
                  and since.date() <= day(h) <= delivered.date()]
        if len(recent) >= int(max_claims):
            return {"within": False, "reason": "khách đã khiếu nại %d lần trong 30 ngày (tối đa %s)"
                    % (len(recent), max_claims), "policy": policy}
    return {"within": True, "reason": "trong hạn mức %d đ / đơn" % cap, "policy": policy}


# ---------- tác động ra ngoài: chỉ tạo bản nháp ----------

def _draft(kind, **fields):
    d = dict(kind=kind, status="chờ duyệt", **fields)
    OUTBOX.append(d)
    return d


@tool
def draft_refund(order_id: str, amount_vnd: int, reason: str) -> dict:
    """draft_refund · input: mã đơn, số tiền (lấy từ compute_missing_refund), lý do · output: bản nháp
    hoàn tiền status "chờ duyệt" · CÓ tác động ra ngoài, nên chỉ tạo bản nháp; nhân viên duyệt mới chuyển tiền.
    Không trừ tiền quán / shipper."""
    return _draft("refund", order_id=order_id, amount_vnd=int(amount_vnd), reason=reason)


@tool
def escalate_to_human(order_id, reason: str, priority: str = "normal") -> dict:
    """escalate_to_human · input: mã đơn (có thể None), lý do, mức ưu tiên "normal" | "high" | "urgent"
    (urgent: sức khoẻ, ngộ độc, dị ứng) · output: phiếu
    chuyển nhân viên status "chờ duyệt" · CÓ tác động ra ngoài (vào hàng chờ CSKH), đảo được."""
    return _draft("escalation", order_id=order_id, reason=reason, priority=priority)


@tool
def request_evidence(order_id: str, what: str) -> dict:
    """request_evidence · input: mã đơn, bằng chứng cần (vd "ảnh túi hàng và hoá đơn") · output: bản nháp
    yêu cầu bằng chứng status "chờ duyệt" · CÓ tác động ra ngoài (tin gửi khách), chỉ tạo bản nháp."""
    return _draft("evidence_request", order_id=order_id, what=what)
