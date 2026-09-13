#!/usr/bin/env bash
# 從 Markdown / body 來源建置靜態教材；也可指定頁面 slug。
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 tools/build_site.py "$@"
