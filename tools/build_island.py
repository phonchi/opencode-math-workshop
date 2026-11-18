#!/usr/bin/env python3
"""由 tools/pages.json 與 tools/island_meta.py 產生 island/index.html（3D 課程島）。冪等。

頁面是「DOM 優先」：各區的頁面列表由這裡直接輸出成語意 HTML，沒有 JS、CDN 失效或 WebGL 不可用時
就是一張可點的 2D 地圖；WebGL 可用時，同一份列表變成 3D 場景旁的快速列表。
Three.js 以 importmap 釘版載入，integrity 涵蓋每一個會被抓的模組；three.module.min.js 內部 import 的
未壓縮 three.core.js 以 importmap 重新對應到 three.core.min.js。

用法：python3 tools/build_island.py
"""
import html
import json
import re
import struct
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import island_meta as M  # noqa: E402

ROOT = M.ROOT
TEMPLATE = ROOT / "tools" / "template"
OUT = ROOT / "island" / "index.html"
FIG_DIR = ROOT / "island" / "figs"

THREE_VER = "0.186.1"
_CDN = f"https://cdn.jsdelivr.net/npm/three@{THREE_VER}"
THREE_MAIN = f"{_CDN}/build/three.module.min.js"
THREE_ADDONS = f"{_CDN}/examples/jsm/"
# 升版時：下載這四個檔，以 `openssl dgst -sha384 -binary f | openssl base64 -A` 重算。
THREE_SRI = {
    THREE_MAIN: "sha384-EU5UWigB3OuXjAXooUegndJSqYber3YSJHDoMZs6rV96yY/ol/B4W8logw4CKWkA",
    f"{_CDN}/build/three.core.min.js": "sha384-ktZslgpl0L71WZcQ5wKV96Z04i9QSjtmiU/kYpjDQSfJ5NJ8B79qDF63oNTbQySl",
    f"{THREE_ADDONS}controls/OrbitControls.js": "sha384-LSqANrugPGTgf0eYsQTloqKWy926dOOXo2iZ9y6wLMIDEQoU9AaCLJF1Vcc7oJXr",
    f"{THREE_ADDONS}geometries/RoundedBoxGeometry.js": "sha384-gHmgcgYfabbVCqiNiLLSop7dMvxAqZsQsjokoDYKyrHmCD5jCPvDvFaXaAkHtTfM",
}
CORE_REMAP = {f"{_CDN}/build/three.core.js": f"{_CDN}/build/three.core.min.js"}

# 網頁字型只保留頂列標題：用 text= 只下載這幾個字；其餘一律用系統字型。
TITLE = "工作坊課程島"
FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@900&display=swap&text="
         + urllib.parse.quote("".join(sorted(set(TITLE + M.SHOW["title"])))))   # 頂列標題＋投影版標題卡的字

# 面板上阿卡的頭像：青綠外套、耳機，腰間三張卡（需求卡金、驗收卡綠、決策卡紅），與 island-scene.js 的 3D 嚮導同色
GUIDE_FACE = ('<circle cx="24" cy="24" r="23" fill="#e6efe4"/>'
              '<path d="M8 47 Q8 35 24 35 Q40 35 40 47 Z" fill="#2f7a6a"/>'
              '<rect x="14" y="40" width="5" height="6" rx="1" fill="#f5b82e"/><rect x="21.5" y="40" width="5" height="6" rx="1" fill="#3f7f61" stroke="#fff" stroke-width=".6"/>'
              '<rect x="29" y="40" width="5" height="6" rx="1" fill="#b9563f"/>'
              '<circle cx="24" cy="23" r="11" fill="#f1c9a5"/><path d="M13 21 Q15 10 24 10 Q33 10 35 21 Q30 15 24 16 Q18 15 13 21 Z" fill="#2b2420"/>'
              '<circle cx="20" cy="24" r="1.5" fill="#2b2420"/><circle cx="28" cy="24" r="1.5" fill="#2b2420"/>'
              '<path d="M21 28 Q24 30.5 27 28" stroke="#a5553d" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
              '<path d="M11.5 24 Q11.5 9 24 9 Q36.5 9 36.5 24" stroke="#2f4566" stroke-width="2" fill="none"/>'
              '<rect x="9.5" y="21" width="4" height="7" rx="2" fill="#2f4566"/><rect x="34.5" y="21" width="4" height="7" rx="2" fill="#2f4566"/>'
              '<path d="M11.5 27 Q13 32 19 31.5" stroke="#2f4566" stroke-width="1.3" fill="none"/>')


def site_icon() -> str:
    """沿用主站 _head.fragment 的 favicon（data URL），兩邊不會不同步；少了它瀏覽器會去要網域根目錄的 /favicon.ico 而 404。"""
    m = re.search(r'<link rel="icon"[^>]*>', (ROOT / "tools" / "_head.fragment").read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("tools/_head.fragment 裡找不到 <link rel=\"icon\">")
    return m.group(0)


def og_tags(title: str, description: str) -> str:
    """LINE 與社群預覽：圖是 island/og.png（node tools/make_island_og.js 由實際 3D 全景產生），全站共用。"""
    return "\n".join([
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="zh_TW">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{M.SITE_URL}island/">',
        f'<meta property="og:image" content="{M.SITE_URL}island/og.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(TITLE)}：3D 全景">',
        '<meta name="twitter:card" content="summary_large_image">',
    ])


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def page_list():
    """pages.json 的分組順序＝列表順序；每頁合併 pages.json 的文字與 island_meta 的島上資料。"""
    out = []
    for g in M.CONFIG["groups"]:
        grp = M.GROUPS.get(g["title"])
        for stem in g["pages"]:
            p = M.CONFIG["pages"][stem]
            s = M.STOPS.get(stem, {})
            time = M.SCHEDULE.get(stem)
            out.append(dict(stem=stem, grp=grp, code=s.get("code", ""), title=p["title"], short=s.get("short", p["title"]),
                            label=p.get("badge", "") + (f" · {time}" if time else ""),
                            landmark=s.get("landmark", ""), blurb=p.get("description", ""),
                            refs=list(s.get("refs", []))))
    return out


PAGES = page_list()
BY = {p["stem"]: p for p in PAGES}


def check_meta():
    errs = []
    for g in M.CONFIG["groups"]:
        if g["title"] not in M.GROUPS:
            errs.append(f"pages.json 的分組「{g['title']}」不在 GROUPS 裡")
    if set(M.GROUPS.values()) != set(M.ISLES):
        errs.append(f"ISLES 的鍵 {sorted(M.ISLES)} ≠ GROUPS 的值 {sorted(set(M.GROUPS.values()))}")
    stems = [p["stem"] for p in PAGES]
    if len(stems) != len(set(stems)):
        errs.append("pages.json 的分組裡有重複的頁面")
    for name, table in (("STOPS", M.STOPS), ("GUIDE", M.GUIDE), ("QUIZ", M.QUIZ)):
        for s in sorted(set(table) - set(stems)):
            errs.append(f"{name} 有 pages.json 沒有的頁面：{s}")
    for p in PAGES:
        s = p["stem"]
        if not (ROOT / f"{s}.html").exists():
            errs.append(f"缺 {s}.html（先跑 ./tools/build.sh）")
        for k in ("code", "short", "landmark", "title", "blurb"):
            if not p.get(k):
                errs.append(f"{s} 缺 {k}")
        for r in p["refs"]:
            if r not in BY:
                errs.append(f"{s} 的 refs 指向不存在的 {r}")
        if not M.GUIDE.get(s):
            errs.append(f"{s} 缺阿卡的導覽詞（GUIDE）")
        elif "我替你做的決定：" not in M.GUIDE[s]:
            errs.append(f"{s} 的導覽詞少了「我替你做的決定：」")
        if s not in M.QUIZ:
            errs.append(f"{s} 缺猜題（QUIZ）")
    codes = [p["code"] for p in PAGES]
    if len(codes) != len(set(codes)):
        errs.append(f"STOPS 的 code 有重複：{codes}")
    for s, f in M.FIGS.items():
        page = ROOT / f"{s}.html"
        if s not in BY:
            errs.append(f"FIGS 指向不存在的 {s}")
        elif page.exists() and f'id="{f["fig"]}"' not in page.read_text(encoding="utf-8"):
            errs.append(f"{s}.html 裡沒有 id=\"{f['fig']}\"（代表圖的深連結會失效）")
        elif not (FIG_DIR / f"{s}.webp").exists():
            errs.append(f"缺縮圖 island/figs/{s}.webp：跑 node tools/build_island_figs.js {s}")
    for r in M.TOUR["routes"]:
        for s in r["stems"]:
            if s not in BY:
                errs.append(f"導覽路線 {r['key']} 指向不存在的 {s}")
    covered = {s for r in M.TOUR["routes"] for s in r["stems"]}
    for s in sorted(set(stems) - covered - {"cheatsheet"}):
        errs.append(f"{s} 不在任何導覽路線裡")
    for k in M.SCHEDULE:
        if k not in BY and k not in ("rest", "wrap"):
            errs.append(f"SCHEDULE 的 {k} 不是頁面")
    index_src = (ROOT / "tools" / "body_index.html").read_text(encoding="utf-8")
    for k, t in M.SCHEDULE.items():
        if f'<td class="t">{t}</td>' not in index_src:
            errs.append(f"時刻 {t}（{k}）不在總覽的時程表裡")
    for s, q in M.QUIZ.items():
        if len(q["options"]) != 4 or not 0 <= q["answer"] < 4:
            errs.append(f"{s} 的猜題要有 4 個選項和有效的 answer")
        src, phrase = q.get("cite", (None, None))
        f = ROOT / src if src else None
        if not f or not f.exists():
            errs.append(f"{s} 的猜題缺出處（cite）")
        elif phrase not in f.read_text(encoding="utf-8"):
            errs.append(f"{s} 的猜題出處 {src} 裡找不到「{phrase}」")
    pos = Counter(q["answer"] for q in M.QUIZ.values())
    if pos and max(pos.values()) - min(pos.get(i, 0) for i in range(4)) > 1:
        errs.append(f"猜題正解位置不平衡：{dict(pos)}")
    # 數字同源：對比面板上的每個數字都要出現在它引用的教材頁
    groups = M.COMPARE["purpose"] + [M.COMPARE["checks"]]
    for c in groups:
        if c["stem"] not in BY:
            errs.append(f"對比 {c['label']} 指向不存在的 {c['stem']}")
        src = (ROOT / c["src"]).read_text(encoding="utf-8")
        for n in c["nums"]:
            if n not in src:
                errs.append(f"對比 {c['label']} 的「{n}」不在 {c['src']} 裡（教材改了？）")
    for c in M.COMPARE["purpose"]:
        src = (ROOT / c["src"]).read_text(encoding="utf-8")
        for row in c["table"]["rows"]:
            for v in row:
                if any(ch.isdigit() for ch in v) and v not in src:
                    errs.append(f"對比 {c['label']} 表格裡的「{v}」不在 {c['src']} 裡（教材改了？）")
    chk = M.COMPARE["checks"]
    for name, row in chk["bugs"]:
        if len(row) != len(chk["checks"]):
            errs.append(f"檢查漏網燈板「{name}」的欄數不對")
    if errs:
        raise SystemExit("island_meta 不一致：\n  " + "\n  ".join(errs))


def webp_size(path: Path) -> tuple:
    """讀 WebP 檔頭的寬高（VP8／VP8L／VP8X），給 <img> 的 width/height，避免載入時版面跳動。"""
    b = path.read_bytes()[:30]
    kind = b[12:16]
    if kind == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise SystemExit(f"{path} 不是可辨識的 WebP")


def fig_record(s: str):
    f = M.FIGS.get(s)
    if not f:
        return None
    w, h = webp_size(FIG_DIR / f"{s}.webp")
    return dict(src=f"figs/{s}.webp", w=w, h=h, caption=f["caption"], href=f"../{s}.html#{f['fig']}")


def records():
    out = []
    for p in PAGES:
        s = p["stem"]
        q = {k: v for k, v in M.QUIZ[s].items() if k != "cite"}
        out.append(dict(p, href=f"../{s}.html", guide=M.GUIDE[s], fig=fig_record(s), quiz=q))
    return out


def item(r: dict) -> str:
    refs = ""
    if r["refs"]:
        names = "、".join(esc(BY[s]["title"]) for s in r["refs"])
        refs = f'            <span class="isl-refs">需要時可查閱：{names}</span>\n'
    return (f'        <li class="isl-item" data-stem="{r["stem"]}" data-grp="{r["grp"]}">\n'
            f'          <a class="isl-link" href="{esc(r["href"])}" data-stem="{r["stem"]}">\n'
            f'            <span class="isl-num">{esc(r["code"])}</span>\n'
            f'            <span class="isl-title">{esc(r["title"])}</span>\n'
            f'            <span class="isl-landmark">{esc(r["landmark"])}</span>\n'
            f'            <span class="isl-blurb">{esc(r["blurb"])}</span>\n'
            f'{refs}'
            f'            <span class="isl-state" aria-hidden="true"></span>\n'
            f'          </a>\n'
            f'        </li>')


def isle_section(grp: str, recs: list) -> str:
    isle = M.ISLES[grp]
    rows = "\n".join(item(r) for r in recs if r["grp"] == grp)
    return (f'    <section class="isle isle-{grp}" id="isle-{grp}" data-grp="{grp}" aria-labelledby="isle-{grp}-h">\n'
            f'      <h2 id="isle-{grp}-h"><span class="isle-name">{esc(isle["name"])}</span>'
            f'<span class="isle-sub">{esc(isle["sub"])}</span></h2>\n'
            f'      <p class="isle-note">{esc(isle["note"])}</p>\n'
            f'      <ol class="isl-items">\n{rows}\n      </ol>\n'
            f'    </section>')


def build() -> str:
    check_meta()
    recs = records()
    css = (TEMPLATE / "island.css").read_text(encoding="utf-8").rstrip()
    # UI 層、對照面板與場景層 inline 進同一個 module（共用頂層名稱）
    js = "\n\n".join((TEMPLATE / f).read_text(encoding="utf-8").rstrip()
                     for f in ("island.js", "island-compare.js", "island-scene.js"))
    data = dict(isles=[dict(grp=g, **v) for g, v in M.ISLES.items()], pages=recs, tour=M.TOUR,
                schedule=M.SCHEDULE, compare=M.COMPARE)
    data_json = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    importmap = json.dumps({"imports": {"three": THREE_MAIN, "three/addons/": THREE_ADDONS, **CORE_REMAP},
                            "integrity": THREE_SRI}, indent=1)
    preload = "\n".join(f'<link rel="modulepreload" href="{u}" integrity="{h}" crossorigin="anonymous">'
                        for u, h in THREE_SRI.items())
    sections = "\n".join(isle_section(g, recs) for g in M.ISLES)
    desc = f"OpenCode × AI-Math 工作坊的 3D 課程島：用一座島看完 {len(recs)} 個單元，點地標前往教材，也能先猜一題、做完 Lab 再對照參考結果。"
    qr = ROOT / "island" / "qr.png"
    if not qr.exists():
        raise SystemExit("缺 island/qr.png：跑 uv run --with segno python tools/make_island_qr.py")
    qr_w = struct.unpack(">I", qr.read_bytes()[16:20])[0]
    jumps = "\n".join(f'      <button type="button" class="isl-jump-btn" data-grp="{g}">{esc(v["name"])}</button>'
                      for g, v in M.ISLES.items() if g != "ref")
    return f"""<!DOCTYPE html>
<!-- 產物：由 tools/build_island.py 產生，不要手改。頁面清單在 tools/pages.json，島上的文案在 tools/island_meta.py，樣式與程式在 tools/template/island* -->
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{esc(desc)}">
{og_tags(f"{TITLE}｜OpenCode × AI-Math 工作坊", desc)}
<title>{TITLE} — OpenCode × AI-Math 工作坊</title>
{site_icon()}
<script>
/* ?show 是會場投影版：只留慢慢轉的島、站名、標題卡和 QR code（連到工作坊總覽首頁） */
if (/[?&]show(=|&|$)/.test(location.search)) document.documentElement.classList.add('show-mode');
/* 有 WebGL 的瀏覽器先排 3D 版面並顯示載入中，避免 2D 卡片閃一下再切換；失敗時 island.js 會移除 */
if (window.WebGLRenderingContext) document.documentElement.classList.add('gl-pending');
</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<style>
{css}
</style>
<script type="importmap">
{importmap}
</script>
{preload}
</head>
<body>
<header class="isl-bar">
  <a class="isl-home" href="../index.html">← 回到工作坊總覽</a>
  <div class="isl-brand">
    <h1>{TITLE}</h1>
    <span class="isl-brand-en">OpenCode × AI-Math · NSYSU</span>
  </div>
  <div class="isl-actions">
    <button type="button" class="isl-btn is-strong" id="islCompare">做完再對照</button>
    <button type="button" class="isl-btn" id="islReset" hidden>重設視角</button>
    <button type="button" class="isl-btn" id="islClear">清除足跡</button>
  </div>
</header>
<main class="isl-main">
  <div class="isl-stage" id="islStage" hidden>
    <p class="isl-loading" aria-hidden="true">課程島載入中…</p>
    <canvas id="islCanvas" tabindex="0" aria-label="3D 課程島：拖曳旋轉、滾輪縮放、點地標；也可用右側列表操作"></canvas>
    <div class="isl-jumps" role="group" aria-label="跳到區域">
{jumps}
    </div>
    <div class="isl-labels" id="islLabels"></div>
    <button type="button" class="isl-bubble" id="islBubble" hidden>{esc(M.TOUR["hello"])}</button>
    <button type="button" class="isl-night" id="islNight" aria-pressed="false">入夜</button>
    <p class="isl-hint" aria-hidden="true">拖曳旋轉 · 滾輪或雙指縮放 · 點地標</p>
  </div>
  <nav class="isl-list" id="islList" aria-label="單元列表">
    <p class="isl-intro">{len(recs)} 個單元，全部可以自由進入。現場兩小時走主島的步道；課後的三條路線各是一座小島。
      <span class="isl-trail-note">「足跡」只存在這台裝置的瀏覽器裡。</span></p>
{sections}
  </nav>
  <aside class="isl-panel" id="islPanel" hidden aria-labelledby="islPanelTitle">
    <button type="button" class="isl-panel-close" id="islPanelClose" aria-label="關閉">×</button>
    <div class="isl-guide" id="islGuide" hidden>
      <svg class="isl-guide-face" viewBox="0 0 48 48" aria-hidden="true">{GUIDE_FACE}</svg>
      <div class="isl-guide-body">
        <div class="isl-guide-who"><b>{esc(M.TOUR["name"])}</b><span id="islGuideStep"></span></div>
        <p class="isl-guide-text" id="islGuideText" aria-live="polite"></p>
        <div class="isl-guide-choices" id="islGuideChoices"></div>
      </div>
    </div>
    <div class="isl-panel-page" id="islPanelPage">
      <div class="isl-panel-kicker" id="islPanelKicker"></div>
      <h2 id="islPanelTitle"></h2>
      <div class="isl-panel-landmark" id="islPanelLandmark"></div>
      <div class="isl-tabs" id="islTabs" role="group" aria-label="切換內容" hidden>
        <button type="button" class="isl-tab" id="islTabInfo" aria-pressed="true">簡介</button>
        <button type="button" class="isl-tab" id="islTabQuiz" aria-pressed="false">先猜一題</button>
      </div>
      <div id="islInfo">
        <p class="isl-panel-blurb" id="islPanelBlurb"></p>
        <figure class="isl-fig" id="islFig" hidden>
          <a class="isl-fig-img" id="islFigLink" href="#"><img id="islFigImg" alt="" loading="lazy" decoding="async"></a>
          <figcaption><span class="isl-fig-h">代表互動圖</span><span id="islFigCap"></span></figcaption>
          <a class="isl-fig-go" id="islFigGo" href="#">去操作這張圖 →</a>
        </figure>
        <div class="isl-panel-refs" id="islPanelRefs" hidden>
          <div class="isl-panel-refs-h">需要時可查閱</div>
          <ul id="islPanelRefList"></ul>
        </div>
      </div>
      <div class="isl-quiz" id="islQuiz" hidden>
        <p class="isl-quiz-q" id="islQuizQ"></p>
        <div class="isl-quiz-opts" id="islQuizOpts"></div>
        <div class="isl-quiz-why" id="islQuizWhy" aria-live="polite" hidden></div>
      </div>
      <div class="isl-panel-cmp" id="islPanelCmp" hidden></div>
      <div class="isl-panel-actions">
        <a class="isl-go" id="islPanelGo" href="#">前往教材 →</a>
        <button type="button" class="isl-done" id="islPanelDone" aria-pressed="false">標記完成</button>
      </div>
    </div>
    <div class="isl-guide-nav" id="islGuideNav" hidden>
      <button type="button" class="isl-btn2" id="islGuidePrev">← 上一站</button>
      <button type="button" class="isl-btn2 is-primary" id="islGuideNext"></button>
      <button type="button" class="isl-btn2 is-quiet" id="islGuideEnd">結束導覽</button>
    </div>
  </aside>
</main>
<dialog class="cmp" id="cmpDialog" aria-labelledby="cmpTitle">
  <div class="cmp-head">
    <div>
      <div class="cmp-kicker">做完再對照</div>
      <h2 id="cmpTitle"></h2>
      <p class="cmp-op" id="cmpOp"></p>
    </div>
    <button type="button" class="isl-panel-close cmp-close" id="cmpClose" aria-label="關閉">×</button>
  </div>
  <div class="cmp-tabs" id="cmpTabs" role="group" aria-label="選擇對照"></div>
  <div class="cmp-body" id="cmpBody"></div>
  <p class="cmp-note" id="cmpNote"></p>
</dialog>
<div class="show-title" aria-hidden="true"><b>{esc(M.SHOW["title"])}</b><span>{esc(M.SHOW["sub"])}</span></div>
<aside class="show-card" aria-label="用手機掃描 QR code，打開工作坊教材">
  <img src="qr.png" width="{qr_w}" height="{qr_w}" alt="工作坊總覽首頁的 QR code" loading="lazy">
  <p>{esc(M.SHOW["qr_caption"])}</p>
</aside>
<script type="application/json" id="island-data">
{data_json}
</script>
<script type="module">
{js}
</script>
</body>
</html>
"""


def main():
    out = build()
    OUT.parent.mkdir(exist_ok=True)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if old != out:
        OUT.write_text(out, encoding="utf-8")
        print(f"寫入 {OUT.relative_to(ROOT)}（{len(out.encode()) // 1024} KB）")
    else:
        print(f"{OUT.relative_to(ROOT)} 已是最新")


if __name__ == "__main__":
    main()
