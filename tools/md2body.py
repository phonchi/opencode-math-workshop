#!/usr/bin/env python3
"""把 content/<name>.md 轉成 tools/body_<name>.html。

支援的 Markdown 子集（刻意只做需要的）：
  # 標題 → pagehead     ## → h2     ### → h3     #### → h4
  ```lang ... ```       → <pre class="cmd">　有語言標記 = 指令，給複製鈕
  ``` ... ```           → <pre class="out">　無語言標記 = 輸出，不給複製鈕
  > 引言區塊             → <div class="box tip">
  表格                   → <div class="tw"><table>
  - / 1. 清單            → ul / ol
  **粗體** `程式碼` [連結](url) <自動連結> 裸 URL（都會變成可點的 <a>）
  特殊標記：
    :::warn 標題 / ::: → <div class="box warn">
    :::danger 標題 / :::
    :::math 標題 / :::
    :::bg 標題 / :::   → <details class="bg">　可收合的背景補充
"""
import re, sys, html, pathlib, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent


# 桌機下 .container.narrow 的可用寬度：780px 減兩側 2rem 內距 = 716px，
# 再減 pre 自己的左右內距 1.25rem x 2 = 40px，實際能放字的是 676px。
# JetBrains Mono 的西文字寬是 0.6em，但 **CJK 與全形字元佔兩倍寬**，
# 用 len() 會低估，必須改算顯示寬度，否則含中文註解的輸出會被右邊裁掉。
TEXT_PX = 676
BASE_REM = 0.815      # 一般 pre 的字級
MIN_REM = 0.58        # 再小就難讀了，剩下的交給水平捲動


def disp_width(line):
    """等寬字體下的顯示寬度（以西文字元為單位）。CJK 與全形算兩格。"""
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1
               for c in line)


def fit_style(lines):
    """寬輸出縮字級，讓它在桌機一眼看完，不要被右邊裁掉。"""
    w = max((disp_width(x) for x in lines), default=0)
    if w <= 0:
        return ''
    need = TEXT_PX / (w * 16 * 0.6)
    if need >= BASE_REM:
        return ''
    size = max(MIN_REM, round(need, 3))
    return ' style="font-size:%srem"' % size


def _link(url, text=None):
    """外部連結一律開新分頁，並加一個小箭頭讓讀者知道會離開本站。"""
    text = text or url
    return (f'<a class="ext" href="{url}" target="_blank" rel="noopener">'
            f'{text}</a>')


def inline(s):
    """行內語法。順序很重要：

    1. 先把 `code span` 抽成佔位符，避免裡面的 URL 被誤轉成連結
       （例如 `http://localhost:11434/v1` 是設定值，不是要點的連結）
    2. 再處理粗體、連結
    3. 最後把 code span 放回去
    """
    s = html.escape(s, quote=False)

    # --- 抽出 code span ---
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f'\x00{len(spans) - 1}\x00'

    s = re.sub(r'`([^`]+)`', stash, s)

    # --- 粗體 ---
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)

    # --- [文字](網址) ---
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
               lambda m: _link(m.group(2), m.group(1)), s)

    # --- <網址> 自動連結（html.escape 後變成 &lt;…&gt;）---
    s = re.sub(r'&lt;(https?://[^\s&]+?)&gt;', lambda m: _link(m.group(1)), s)

    # --- 裸 URL（前面不能是引號、括號或已經在標籤屬性裡）---
    s = re.sub(r'(?<![\"\'(>=])\b(https?://[^\s<>"\'()\u3000，。、）]+)',
               lambda m: _link(m.group(1)), s)

    # --- 放回 code span ---
    s = re.sub(r'\x00(\d+)\x00',
               lambda m: f'<code>{spans[int(m.group(1))]}</code>', s)
    return s


def convert(md, title, desc, pager_prev=None, pager_next=None, badge=None):
    lines = md.split('\n')
    out, i, n = [], 0, len(lines)
    in_list = None

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f'</{in_list}>')
            in_list = None

    while i < n:
        ln = lines[i]

        # 程式碼區塊
        if ln.startswith('```'):
            close_list()
            lang = ln[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            body = html.escape('\n'.join(buf), quote=False)
            if lang:
                # 有語言標記 = 學生要照抄的指令或檔案內容 -> 給複製鈕
                out.append(f'<pre class="cmd" data-lang="{lang}">'
                           f'<code>{body}</code></pre>')
            else:
                # 無語言標記 = 程式的輸出 -> 不給複製鈕（沒人要複製輸出）
                out.append(f'<pre class="out"{fit_style(buf)}>'
                           f'<code>{body}</code></pre>')
            continue

        # 自訂區塊 :::type 標題
        m = re.match(r'^:::(\w+)\s*(.*)$', ln)
        if m:
            close_list()
            kind, head = m.group(1), m.group(2).strip()
            i += 1
            buf = []
            while i < n and not lines[i].startswith(':::'):
                buf.append(lines[i]); i += 1
            i += 1
            inner = convert_fragment('\n'.join(buf))
            if kind == 'bg':
                # 背景補充：可收合，已經懂的人直接跳過
                out.append('<details class="bg"><summary>'
                           f'{inline(head) or "背景補充"}</summary>'
                           f'<div class="bg-body">{inner}</div></details>')
            else:
                bt = f'<div class="bt">{inline(head)}</div>' if head else ''
                out.append(f'<div class="box {kind}">{bt}{inner}</div>')
            continue

        # 標題
        if ln.startswith('#### '):
            close_list(); out.append(f'<h4>{inline(ln[5:])}</h4>'); i += 1; continue
        if ln.startswith('### '):
            close_list(); out.append(f'<h3>{inline(ln[4:])}</h3>'); i += 1; continue
        if ln.startswith('## '):
            close_list(); out.append(f'<h2>{inline(ln[3:])}</h2>'); i += 1; continue
        if ln.startswith('# '):
            close_list(); i += 1; continue          # H1 由 pagehead 處理

        # 表格
        if ln.strip().startswith('|') and i + 1 < n and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            close_list()
            hdr = [c.strip() for c in ln.strip().strip('|').split('|')]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            t = ['<div class="tw"><table><tr>']
            t += [f'<th>{inline(c)}</th>' for c in hdr]
            t.append('</tr>')
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
            t.append('</table></div>')
            out.append(''.join(t)); continue

        # 引言 → tip box
        if ln.startswith('> '):
            close_list()
            buf = []
            while i < n and lines[i].startswith('>'):
                buf.append(lines[i][2:] if lines[i].startswith('> ') else lines[i][1:])
                i += 1
            out.append(f'<div class="box tip">{convert_fragment(chr(10).join(buf))}</div>')
            continue

        # 清單
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', ln)
        if m:
            kind = 'ul' if m.group(2) in ('-', '*') else 'ol'
            if in_list != kind:
                close_list(); out.append(f'<{kind}>'); in_list = kind
            out.append(f'<li>{inline(m.group(3))}</li>'); i += 1; continue

        # 水平線
        if re.match(r'^\s*---+\s*$', ln):
            close_list(); out.append('<hr>'); i += 1; continue

        # 空行
        if not ln.strip():
            close_list(); i += 1; continue

        # 段落
        close_list()
        buf = [ln]; i += 1
        while i < n and lines[i].strip() and not re.match(
                r'^(#{1,4} |```|\||>|:::|\s*([-*]|\d+\.)\s|\s*---+\s*$)', lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f'<p>{inline(" ".join(b.strip() for b in buf))}</p>')

    close_list()
    return '\n'.join(out)


def convert_fragment(md):
    """區塊內部用，不產生 pagehead。"""
    return convert(md, '', '')


def main():
    name = sys.argv[1]
    meta = {
        'local-models': ('本地模型', '課後', '在自己電腦上跑 Ollama 接 opencode，重點是 context 要在兩個地方各設一次。',
                         ('lab3-notes.html', '04 · Lab 3'), ('agents-md.html', '06 · AGENTS.md')),
        'agents-md':    ('AGENTS.md', '課後', '把專案規則寫成 AGENTS.md，讓 agent 每次都照做，不必你每次重講。',
                         ('local-models.html', '05 · 本地模型'), ('git-safety.html', '07 · git')),
        'git-safety':   ('git 安全網', '課後', '不用 GitHub 帳號也能用。動手前 commit、改完看 diff、不滿意就還原。',
                         ('agents-md.html', '06 · AGENTS.md'), ('mcp-skills.html', '08 · MCP')),
        'mcp-skills':   ('MCP 與 subagent', '課後', 'MCP、自訂 agent、subagent 各解決什麼問題。加分項，不是必修。',
                         ('git-safety.html', '07 · git'), ('cheatsheet.html', '09 · 速查表')),
        'first-run':    ('第一次對話', '現場', 'TUI 操作、權限機制、session 的邊界。搞懂你在跟什麼東西說話。',
                         ('prep.html', '00 · 課前準備'), ('lab1-cluster.html', '02 · Lab 1')),
    }[name]
    title, badge_kind, desc, prev, nxt = meta
    md = (ROOT / 'content' / f'{name}.md').read_text()
    h1 = next((l[2:].strip() for l in md.split('\n') if l.startswith('# ')), title)
    # 開頭如果只是「> 現場 30 分鐘」這種重複徽章的引言，去掉
    md = re.sub(r'^# .*\n+(> *[^\n]*(現場|課後|加分項|分鐘)[^\n]*\n)+', 
                lambda m: m.group(0).split('\n')[0] + '\n', md, count=1)
    num = {'first-run': '01', 'local-models': '05', 'agents-md': '06',
           'git-safety': '07', 'mcp-skills': '08'}[name]
    bcls = 'live' if badge_kind == '現場' else 'after'
    blabel = '現場 30 分' if badge_kind == '現場' else '課後延伸'
    body = convert(md, title, desc)
    page = f'''<!--TITLE:{title}-->
<!--DESC:{desc}-->

<div class="container narrow">

<div class="pagehead">
  <div class="kicker"><span>{num}</span><span>·</span><span class="badge {bcls}">{blabel}</span></div>
  <h1>{html.escape(h1)}</h1>
</div>

{body}

<div class="pager">
  <a href="{prev[0]}"><div class="d">上一章</div><div class="t2">← {prev[1]}</div></a>
  <a href="{nxt[0]}" class="next"><div class="d">下一章</div><div class="t2">{nxt[1]} →</div></a>
</div>

</div>
'''
    dst = ROOT / 'tools' / f'body_{name}.html'
    dst.write_text(page)
    print(f'{name}.md -> {dst.name}  ({len(page)} bytes)')


if __name__ == '__main__':
    main()
