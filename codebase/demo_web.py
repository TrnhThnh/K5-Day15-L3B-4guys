"""Giao diện demo cục bộ. Chạy python codebase/demo_web.py."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

import tracing
from agent import answer
from ai import MODEL_PROVIDER, MODEL_NAME, API_KEY

TRACE_LOCK = Lock()
PAGE = Path(__file__).with_name("demo.html")


class DemoHandler(BaseHTTPRequestHandler):
    def respond(self, status, data, content_type="application/json"):
        body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            return self.respond(200, PAGE.read_bytes(), "text/html")
        if self.path == "/mode":
            name = "Mô phỏng" if MODEL_PROVIDER == "fake" else MODEL_NAME
            return self.respond(200, {"name": name, "ready": MODEL_PROVIDER == "fake" or bool(API_KEY)})
        self.send_error(404)

    def do_POST(self):
        if self.path != "/answer":
            return self.send_error(404)
        if self.headers.get_content_type() != "application/json":
            return self.send_error(415)
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 24000:
                raise ValueError()
            payload = json.loads(self.rfile.read(size))
            message = payload["message"].strip()
            if not message or len(message) > 4000:
                raise ValueError()
        except (ValueError, KeyError, TypeError, AttributeError):
            return self.respond(400, {"error": "Nhập mô tả từ 1 đến 4.000 ký tự."})
        try:
            with TRACE_LOCK:
                tracing.begin("web-demo")
                try:
                    result = answer(message)
                finally:
                    summary, _ = tracing.end()
        except Exception:
            return self.respond(502, {"error": "Chưa xử lý được yêu cầu. Kiểm tra kết nối và cấu hình model rồi thử lại."})
        self.respond(200, {"output": result["output"], "summary": {k: summary[k] for k in
                           ("models", "tokens_in", "tokens_out", "tool_calls", "model_calls")}})


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8765), DemoHandler) as server:
        print("Demo: http://127.0.0.1:8765", flush=True)
        server.serve_forever()