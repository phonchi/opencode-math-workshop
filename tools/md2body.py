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
import re, sys, html, pathlib, json

ROOT = pathlib.Path(__file__).resolve().parent.parent


def table_cells(line):
    """表格分隔線不包含 code span 或跳脫的直線字元。"""
    text = line.strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|') and not text.endswith('\\|'):
        text = text[:-1]
    cells, current, ticks = [], [], 0
    i = 0
    while i < len(text):
        if text[i:i + 2] == '\\|':
            current.append('|'); i += 2; continue
        if text[i] == '`':
            end = i
            while end < len(text) and text[end] == '`':
                end += 1
            count = end - i
            ticks = 0 if ticks == count else (count if not ticks else ticks)
            current.append(text[i:end]); i = end; continue
        if text[i] == '|' and not ticks:
            cells.append(''.join(current).strip()); current = []
        else:
            current.append(text[i])
        i += 1
    cells.append(''.join(current).strip())
    return cells


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
    s = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',
               lambda m: (_link(m.group(2), m.group(1))
                          if m.group(2).startswith(('https://', 'http://'))
                          else f'<a href="{html.escape(html.unescape(m.group(2)), quote=True)}">{m.group(1)}</a>'), s)

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

        # 建置期可信資產標記，不當作一般段落跳脫。
        if re.fullmatch(r'\s*<!--(?:DIAGRAM|INCLUDE):[^\n]+-->\s*', ln):
            close_list(); out.append(ln.strip()); i += 1; continue

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
                out.append('<pre class="out">'
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
            hdr = table_cells(ln)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                row = table_cells(lines[i])
                if len(row) != len(hdr):
                    raise ValueError(f'表格第 {i + 1} 行有 {len(row)} 欄，標題有 {len(hdr)} 欄')
                rows.append(row)
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
                r'^(#{1,4} |```|\||>|:::|<!--(?:DIAGRAM|INCLUDE):|\s*([-*]|\d+\.)\s|\s*---+\s*$)', lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f'<p>{inline(" ".join(b.strip() for b in buf))}</p>')

    close_list()
    return '\n'.join(out)


def convert_fragment(md):
    """區塊內部用，不產生 pagehead。"""
    return convert(md, '', '')


def render_page(name, md, meta):
    """純函式：由 Markdown 與共用頁面資訊產生 body，不寫檔。"""
    title, desc = meta['title'], meta['description']
    badge_kind = meta.get('badge', '課後延伸')
    h1 = next((l[2:].strip() for l in md.split('\n') if l.startswith('# ')), title)
    # 開頭如果只是「> 現場 30 分鐘」這種重複徽章的引言，去掉
    md = re.sub(r'^# .*\n+(> *[^\n]*(現場|課後|加分項|分鐘)[^\n]*\n)+', 
                lambda m: m.group(0).split('\n')[0] + '\n', md, count=1)
    bcls = 'live' if badge_kind == '現場' else 'after'
    body = convert(md, title, desc)
    page = f'''<!--TITLE:{title}-->
<!--DESC:{desc}-->

<div class="container narrow">

<div class="pagehead">
  <div class="kicker"><span class="badge {bcls}">{html.escape(badge_kind)}</span></div>
  <h1>{html.escape(h1)}</h1>
</div>

{body}

</div>
'''
    return page


def main():
    name = sys.argv[1]
    meta = json.loads((ROOT / 'tools/pages.json').read_text())['pages'][name]
    md = (ROOT / 'content' / f'{name}.md').read_text()
    page = render_page(name, md, meta)
    dst = ROOT / 'tools' / f'body_{name}.html'
    dst.write_text(page)
    print(f'{name}.md -> {dst.name}  ({len(page)} bytes)')


if __name__ == '__main__':
    main()
