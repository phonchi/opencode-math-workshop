#!/usr/bin/env bash
# 從 Markdown / body 來源建置靜態教材；也可指定頁面 slug。
# 完整建置（不帶參數）最後會重建 3D 課程島 island/index.html；單頁建置不重建島。
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/build_site.py "$@"
if [ "$#" -eq 0 ]; then
  python3 tools/build_island.py
fi
