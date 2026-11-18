#!/usr/bin/env python3
"""3D 課程島 island/index.html 的靜態檢查。無外部相依。

產物同步、pages.json 的頁面齊全、相對連結與代表圖 id、外部資源釘版＋SRI、學生可見文字的用語、
總覽與側欄的入口。猜題出處與對比數字同源由 build_island.check_meta() 檢查（這裡會呼叫 build）。
--net 時重新下載 Three.js 模組，比對 sha384 與 importmap 的 integrity。

用法：python3 tools/check_island.py [--net]
"""
import base64
import hashlib
import json
import re
import struct
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_island as I  # noqa: E402

ROOT = I.ROOT
F = ROOT / "island" / "index.html"
fails = []


def fail(msg):
    fails.append(msg)


# 第一次出現必須寫全名：縮寫 → 第一次出現時前面要有的英文全名
ACRONYMS = {}
# 學生頁不放製作歷程與工作紀錄；台灣用語
FORBIDDEN = ["本次更新", "已同步", "量測", "重現命令", "視頻", "軟件", "硬件", "數據", "信息", "默認", "質量", "用戶", "文檔", "代碼"]


class Text(HTMLParser):
    """只留學生看得到的文字：略過 style、module script 與 head"""
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "head") or (tag == "script" and dict(attrs).get("type") != "application/json"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "head", "script") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def main():
    net = "--net" in sys.argv
    if not F.exists():
        raise SystemExit("尚未產生，先跑 python3 tools/build_island.py")
    src = F.read_text(encoding="utf-8")
    try:
        built = I.build()
    except SystemExit as e:
        raise SystemExit(str(e))
    if built != src:
        fail("產物與產生器不一致（手改了，或改了 island_meta／template 後沒重跑 build_island.py）")

    m = re.search(r'<script type="application/json" id="island-data">\n(.*?)\n</script>', src, re.S)
    assert m, "找不到 island-data"
    data = json.loads(m.group(1).replace("<\\/", "</"))
    stems = [p["stem"] for p in data["pages"]]
    order = [s for g in I.M.CONFIG["groups"] for s in g["pages"]]
    if stems != order:
        fail(f"單元與 pages.json 不一致：{stems} ≠ {order}")
    links = re.findall(r'class="isl-link" href="([^"]+)"', src)
    if [f"../{s}.html" for s in stems] != links:
        fail("列表入口與 PAGES 不一致")
    for href in set(re.findall(r'href="(\.\./[^"#]+)', src)):
        if not (ROOT / "island" / href).resolve().exists():
            fail(f"連結指向不存在的 {href}")
    # 代表圖：檔案、深連結 id，且 island/figs 只放 FIGS 列出的章節
    figs = {f.stem for f in (ROOT / "island" / "figs").glob("*")}
    if figs != set(I.M.FIGS):
        fail(f"island/figs 與 FIGS 不一致：多 {sorted(figs - set(I.M.FIGS))}、缺 {sorted(set(I.M.FIGS) - figs)}")
    for p in data["pages"]:
        fg = p.get("fig")
        if fg:
            page, fid = fg["href"].split("#")
            if f'id="{fid}"' not in (ROOT / "island" / page).read_text(encoding="utf-8"):
                fail(f"{p['stem']} 的深連結 #{fid} 不存在")
    # 外部資源只能是 Three.js（釘版）與 Google Fonts
    for u in set(re.findall(r'https?://[^\s"\'<>)]+', src)):
        if not (u.startswith(I._CDN) or u.startswith("https://fonts.g") or u.startswith("http://www.w3.org") or u.startswith(I.M.SITE_URL)):
            fail(f"未允許的外部資源 {u}")
    m = re.search(r'<script type="importmap">\n(.*?)\n</script>', src, re.S)
    assert m, "找不到 importmap"
    imap = json.loads(m.group(1))
    if imap["integrity"] != I.THREE_SRI:
        fail("importmap 的 integrity 與 build_island.THREE_SRI 不一致")
    for spec in ("three",):
        if imap["imports"][spec] not in imap["integrity"]:
            fail(f"importmap 的 {spec} 缺 integrity")
    for frm, to in I.CORE_REMAP.items():
        if imap["imports"].get(frm) != to or to not in imap["integrity"]:
            fail(f"{frm} 沒有對應到有 integrity 的 {to}")
    if net:
        for url, want in I.THREE_SRI.items():
            try:
                body = urllib.request.urlopen(url, timeout=30).read()
            except Exception as e:  # noqa: BLE001
                fail(f"無法下載以驗證 SRI：{url}：{e}")
                continue
            got = "sha384-" + base64.b64encode(hashlib.sha384(body).digest()).decode()
            if got != want:
                fail(f"SRI 不符：{url}（CDN 實際為 {got}）")
    # 學生可見文字
    tp = Text()
    tp.feed(src)
    text = "\n".join(tp.out)
    for w in FORBIDDEN:
        if w in text:
            fail(f"用語：學生可見文字出現「{w}」")
    for ab, full in ACRONYMS.items():
        i = re.search(rf"\b{ab}\b", text)
        if i and full not in text[max(0, i.start() - 60):i.end()]:
            fail(f"縮寫 {ab} 第一次出現時沒有拼出全名（{full}）")
    # 對比面板的參考數字不能出現在 3D 標籤或列表裡（只在「做完再對照」打開後由 JS 畫出）
    tv = Text()
    tv.feed(re.sub(r'<script type="application/json".*?</script>', "", src, flags=re.S))
    shown = "\n".join(tv.out)
    for c in I.M.COMPARE["purpose"]:
        for n in c["nums"]:
            if "." in n and n in shown:
                fail(f"參考數字 {n} 出現在學生一進來就看得到的文字裡")
    # 會場投影版：QR code 要能解碼回工作坊總覽首頁（有 OpenCV 才解碼；沒有就只檢查檔案）
    qr = ROOT / "island" / "qr.png"
    if not qr.exists() or qr.read_bytes()[:4] != b"\x89PNG":
        fail("缺投影版的 island/qr.png")
    else:
        try:
            import cv2  # noqa: PLC0415
            got = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(qr)))[0]
            if got != I.M.SHOW["qr_url"]:
                fail(f"qr.png 解碼是「{got}」，不是 {I.M.SHOW['qr_url']}（跑 uv run --with segno python tools/make_island_qr.py）")
        except ImportError:
            print("· 沒有 OpenCV，略過 QR 解碼")
    for cls in ('class="show-title"', 'class="show-card"', 'src="qr.png"'):
        if cls not in src:
            fail(f"投影版少了 {cls}")
    # 連結預覽：island/og.png 1200×630、300 KB 以內；每一頁都有 og 標籤且指向它
    og = ROOT / "island" / "og.png"
    if not og.exists():
        fail("缺 island/og.png：跑 node tools/make_island_og.js")
    else:
        w, h = struct.unpack(">II", og.read_bytes()[16:24])
        if (w, h) != (1200, 630) or og.stat().st_size > 300 * 1024:
            fail(f"og.png 應為 1200×630、300 KB 以內，現在 {w}×{h}、{og.stat().st_size // 1024} KB")
    for page in ["island/index"] + [f"{p}" for p in ["index"] + order]:
        html_ = (ROOT / f"{page}.html").read_text(encoding="utf-8")
        if f'<meta property="og:image" content="{I.M.SITE_URL}island/og.png">' not in html_:
            fail(f"{page}.html 沒有指向 island/og.png 的 og:image")
    # 總覽 hero 與每頁側欄的入口
    for page in ["index"] + order:
        html = (ROOT / f"{page}.html").read_text(encoding="utf-8")
        if 'href="island/index.html"' not in html:
            fail(f"{page}.html 沒有課程島入口")
    if fails:
        print("\n".join("✗ " + f for f in fails))
        sys.exit(1)
    print(f"check_island：通過（{len(stems)} 頁、{len(figs)} 張代表圖、SRI {'已對 CDN 比對' if net else '未連網比對'}）")


if __name__ == "__main__":
    main()
