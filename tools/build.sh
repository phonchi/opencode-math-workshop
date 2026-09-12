#!/usr/bin/env bash
# 把 tools/body_<page>.html 組成根目錄的 <page>.html
# 用法：tools/build.sh            # 全部
#       tools/build.sh lab2-pca   # 單頁
set -euo pipefail
cd "$(dirname "$0")/.."
OCVER="1.18.30"
TESTDATE="2026-09-12"

build_one() {
  local page="$1" body="tools/body_$1.html"
  [ -f "$body" ] || { echo "跳過 $page（沒有 $body）"; return; }
  local title desc
  title=$(sed -n '1s/^<!--TITLE:\(.*\)-->$/\1/p' "$body")
  desc=$(sed -n '2s/^<!--DESC:\(.*\)-->$/\1/p' "$body")
  [ -n "$title" ] || { echo "錯誤：$body 第 1 行缺少 <!--TITLE:...-->"; exit 1; }
  [ -n "$desc" ]  || { echo "錯誤：$body 第 2 行缺少 <!--DESC:...-->"; exit 1; }
  { sed -e "s|__TITLE__|$title|g" -e "s|__DESC__|$desc|g" tools/_head.fragment
    tail -n +3 "$body"
    sed -e "s|__OCVER__|$OCVER|g" -e "s|__TESTDATE__|$TESTDATE|g" tools/_tail.fragment
  } > "$page.html"
  echo "已產生 $page.html ($(wc -c < "$page.html") bytes)"
}

if [ $# -gt 0 ]; then
  for p in "$@"; do build_one "$p"; done
else
  for b in tools/body_*.html; do
    p=$(basename "$b" .html); p=${p#body_}
    build_one "$p"
  done
fi
