"""Project skin for canonical Viewer SVG exports; preserve all diagram geometry."""
from pathlib import Path
import re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]; src=ROOT/'tools/diagram-sources'; out=ROOT/'assets/diagrams'
css="""svg { --bg:#f6f2e9; --grid:#e1dbcf; --text:#2a3c78; --text-muted:#555e73; --text-dim:#555e73; --text-faint:#555e73; --panel:#f6f2e9; --panel-border:#d8d1c4; --lane-fill:#f6f2e9; --lane-stroke:#c7c0b5; --arrow:#555e73; --arrow-emphasis:#b8503c; --mask:#f6f2e9; }
svg,svg text { font-family:'Noto Sans TC','Microsoft JhengHei',sans-serif !important; }
"""
for kind in ['frontend','backend','database','cloud','messagebus','external']:
 css+=f'svg {{ --{kind}-fill:#fffdf8; --{kind}-stroke:#2a3c78; }}\n'
css+='svg { --security-fill:#f5e4dc; --security-stroke:#b8503c; }'
css=re.sub(r'(--[\w-]+:[^;{}]+)(;|(?=}))',r'\1 !important\2',css)
css+='svg text[data-node-label]{font-size:18px} svg .t-muted{font-size:14px} svg .c-grid{opacity:0} svg .semantic-sigil{display:none} svg text[data-node-label]{transform:translateY(10px)}'
for name in ['agent-task','git-workflow','agent-delegation']:
 svg=(src/(name+'.canonical.svg')).read_text()
 svg=svg.replace('lang="en"','lang="zh-Hant"').replace('archify-diagram-title',name+'-title').replace('archify-diagram-description',name+'-desc')
 desc={'agent-task':'先說明需求、讀取相關檔案、確認修改範圍，再執行並由學生驗證成果。','git-workflow':'保存起點後請 agent 修改，查看差異並執行，採用就 commit；不採用就 restore 指定的已追蹤檔案。未追蹤檔案仍保留；執行前先確認沒有自己的修改要保留。','agent-delegation':'主 agent 委派唯讀查找與核對工作，子任務回報摘要與證據，由主 agent 核實後整合。'}[name]
 svg=re.sub(r'(<desc\b[^>]*>).*?(</desc>)',lambda m:m[1]+desc+m[2],svg,flags=re.S)
 svg=svg.replace('</svg>','<style>'+css+'</style></svg>')
 ET.fromstring(svg);(out/(name+'.svg')).write_text(svg)
# Diagram Design timeline: ordinal stages, explicitly not an elapsed-time axis.
def text(x,y,s,size=24,weight=500,color='#2a3c78',anchor='middle'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{s}</text>'
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 440" role="img" aria-labelledby="learning-route-title learning-route-desc"><title id="learning-route-title">從第一次對話，到用數學檢查成果</title><desc id="learning-route-desc">依序完成課前準備、初次對話、分群、PCA 與分類筆記，課後可選數學應用或 OpenCode 工作法；間距表示學習順序，不表示時間長短。</desc><defs><style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600&amp;display=swap"); text{font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif}</style>']
for id,c in [('arrow','#555e73'),('arrow-accent','#b8503c'),('arrow-link','#2a3c78')]:s.append(f'<marker id="learning-route-{id}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{c}"/></marker>')
s+=['</defs><rect width="1120" height="440" fill="#f6f2e9"/>',text(48,56,'一段一段完成，成果留在自己的專案',28,600,anchor='start'),text(48,92,'學習順序｜每一步都先操作，再確認',20,color='#555e73',anchor='start'),'<line x1="104" y1="196" x2="1000" y2="196" stroke="#b7b0a5" stroke-width="1"/>']
for i,(x,label,sub) in enumerate([(104,'課前準備','建立環境'),(328,'初次對話','完成小任務'),(552,'分群','比較相似性'),(776,'PCA','理解投影'),(1000,'分類與筆記','說明並驗證')]):
 y=148 if i%2==0 else 252
 s.append(f'<line x1="{x}" y1="196" x2="{x}" y2="{y+12 if i%2==0 else y-32}" stroke="#b7b0a5"/>')
 s.append(f'<circle cx="{x}" cy="196" r="{8 if i==4 else 4}" fill="{"#b8503c" if i==4 else "#2a3c78"}"/>')
 s.extend([text(x,y,label),text(x,y+28,sub,20,color='#555e73')])
s.extend(['<line x1="48" y1="316" x2="1072" y2="316" stroke="#d8d1c4"/>',text(48,368,'課後自由延伸',24,600,anchor='start'),text(352,368,'數學應用',24,600,anchor='start'),text(352,404,'低秩近似・梯度下降・最短路徑',20,color='#555e73',anchor='start'),text(752,368,'OpenCode 工作法',24,600,anchor='start'),text(752,404,'需求・分工・驗證・續作',20,color='#555e73',anchor='start'),'</svg>'])
svg=''.join(s);ET.fromstring(svg)
html='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>工作坊學習路線</title><style>body{margin:0;background:#f6f2e9}svg{display:block;width:100%;height:auto}</style>'+svg+'</html>'
(src/'learning-route.html').write_text(html)
# Official Diagram Design SVG export: extract first SVG, already XML-safe.
(out/'learning-route.svg').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+re.search(r'<svg\b.*?</svg>',html,re.S).group())
(src/'project-tokens.md').write_text('# Workshop diagram skin\n\nUser-approved project tokens: paper #f6f2e9, ink #2a3c78, accent #b8503c; Noto Sans TC / Noto Serif TC. Shared skill files and home profile registry remain unchanged. This local token document is an explicit project override, not a registered Diagram Design profile marker.\n\nArchify checked HTML and canonical exports remain unchanged; build-assets.py adds the project skin to derivative SVGs without modifying geometry. Archify fixed Viewer UI remains English because Traditional Chinese is unsupported; it is not embedded in the teaching site.\n')
