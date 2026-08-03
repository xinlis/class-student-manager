#!/bin/zsh
cd "$(dirname "$0")"
mkdir -p "../class-student-manager-data"
open -a "Google Chrome" "http://127.0.0.1:8787/index.html"
python3 local_app_server.py
