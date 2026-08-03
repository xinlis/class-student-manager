#!/usr/bin/env python3
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "class-student-manager-data"
DATA_FILE = DATA_DIR / "classroom-data.json"
HOST = "127.0.0.1"
PORT = int(os.environ.get("CLASS_MANAGER_PORT", "8787"))


def default_state():
    return {
        "students": [],
        "records": {},
        "subjectTests": {},
        "events": [],
        "quickNotes": [],
        "knowledgeDates": {},
        "homeworkNames": ["讲义", "宝典"],
        "className": "VIP2 班",
    }


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(default_state(), ensure_ascii=False, indent=2), encoding="utf-8")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/api/state":
            self.send_json_state()
            return
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/state":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data.get("students"), list) or not isinstance(data.get("records"), dict):
                raise ValueError("数据格式不正确")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            tmp_file = DATA_FILE.with_suffix(".json.tmp")
            tmp_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp_file.replace(DATA_FILE)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as exc:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))

    def send_json_state(self):
        ensure_data_file()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(DATA_FILE.read_bytes())


if __name__ == "__main__":
    ensure_data_file()
    print(f"学生档案本机版已启动：http://{HOST}:{PORT}/index.html")
    print(f"数据文件：{DATA_FILE}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
