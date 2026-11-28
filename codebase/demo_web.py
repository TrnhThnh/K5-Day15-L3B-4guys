"""Giao diện demo cục bộ. Chạy python codebase/demo_web.py rồi mở http://127.0.0.1:8765.

Ba tab: Khiếu nại (khách nhắn, xem phản hồi + đơn liên quan + mã yêu cầu) · Đơn hàng (dữ liệu dựng data/orders.json)
· Chờ duyệt (nhân viên duyệt / từ chối nháp hoàn tiền và phiếu chuyển người trong outbox/approval-queue.jsonl).
"""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

import tools
import tracing
from agent import ORDER_RE, answer
from ai import MODEL_PROVIDER, MODEL_NAME, API_KEY

TRACE_LOCK = Lock()
PAGE = Path(__file__).with_name("demo.html")


def all_orders():
    """Đơn dựng đọc thẳng từ data/orders.json (không qua @tool, để không ghi vào trace của khách)."""
    return tools._load("orders.json", [])


def orders_in(message):
    ids = {"DH-" + m.group(1) for m in ORDER_RE.finditer(message)}
    return [o for o in all_orders() if o["order_id"] in ids]


class DemoHandler(BaseHTTPRequestHandler):
    def respond(self, status, data, content_type="application/json"):
        body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        if self.headers.get_content_type() != "application/json":
            raise ValueError()
        size = int(self.headers.get("Content-Length", 0))
        if not 0 < size <= 24000:
            raise ValueError()
        return json.loads(self.rfile.read(size))

    def do_GET(self):
        if self.path == "/":
            return self.respond(200, PAGE.read_bytes(), "text/html")
        if self.path == "/mode":
            name = "Mô phỏng" if MODEL_PROVIDER == "fake" else MODEL_NAME
            return self.respond(200, {"name": name, "ready": MODEL_PROVIDER == "fake" or bool(API_KEY)})
        if self.path == "/orders":
            return self.respond(200, {"orders": all_orders()})
        if self.path == "/queue":
            return self.respond(200, {"requests": tools.list_requests()})
        self.send_error(404)

    def do_POST(self):
        if self.path == "/queue":
            return self.review()
        if self.path != "/answer":
            return self.send_error(404)
        try:
            message = self.read_json()["message"].strip()
            if not message or len(message) > 4000:
                raise ValueError()
        except (ValueError, KeyError, TypeError, AttributeError):
            return self.respond(400, {"error": "Nhập mô tả từ 1 đến 4.000 ký tự."})
        try:
            with TRACE_LOCK:
                before = len(tools.OUTBOX)
                tracing.begin("web-demo")
                try:
                    result = answer(message)
                finally:
                    summary, _ = tracing.end()
                created = tools.OUTBOX[before:]
        except Exception:
            return self.respond(502, {"error": "Chưa xử lý được yêu cầu. Kiểm tra kết nối và cấu hình model rồi thử lại."})
        self.respond(200, {"output": result["output"],
                           "summary": {k: summary[k] for k in
                                       ("models", "tokens_in", "tokens_out", "tool_calls", "model_calls")},
                           "orders": orders_in(message),
                           "requests": [r for r in created if r["kind"] in ("refund", "escalation")]})

    def review(self):
        """Nhân viên duyệt / từ chối một yêu cầu đang chờ: {"request_id": "YC-0001", "approve": true}."""
        try:
            data = self.read_json()
            rid = str(data["request_id"])
            if not re.fullmatch(r"YC-\d{4,}", rid):
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            return self.respond(400, {"error": "Thiếu mã yêu cầu hợp lệ."})
        done = tools.review_request(rid, bool(data.get("approve")))
        if not done:
            return self.respond(409, {"error": "Yêu cầu %s không còn ở trạng thái chờ duyệt." % rid})
        self.respond(200, {"request": done})


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8765), DemoHandler) as server:
        print("Demo: http://127.0.0.1:8765", flush=True)
        server.serve_forever()
