#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo 'Đã cài đặt xong. Kiểm tra .env, import database rồi chạy ./run.sh.'
