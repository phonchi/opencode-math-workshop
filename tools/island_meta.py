"""3D 課程島（island/index.html）的文案與資料。

頁面標題、說明、徽章與分組一律讀 tools/pages.json，這裡不重複維護；這裡只放島上才有的東西。
build_island.py 會比對：pages.json 的每一頁都要有 STOPS、GUIDE、QUIZ；路線、refs、代表圖 id 要有效；
猜題的 cite 片語要真的出現在教材原文；對比面板的數字要出現在對應的教材頁（數字同源）。

  GROUPS  — pages.json 的分組標題 → 島上的區域鍵
  ISLES   — 區域名稱（列表、標籤、跳轉鈕）
  STOPS   — 每頁的 3D 標籤短名、編號、地標名稱、需要時可查閱的頁
  FIGS    — 三個 Lab 的代表互動圖（教材頁裡 explorer 的標題 id；截圖取 explorer 的預設狀態）
  GUIDE   — 阿卡到每一站說的話，最後一句固定是「我替你做的決定：…」
  TOUR    — 路線與台詞
  QUIZ    — 先猜：每頁一題「答案確定、而且不是該頁動手觀察點」的機制題；answer 是選項索引，正解位置要平衡
  COMPARE — 「做完再對照」的兩種面板，按「我做完這一關了」才展開

防劇透與比喻的約束（改 island-scene.js 時不能違反，check_island_browser.js 會實測）：
  - 島上不先演出學生要親手觀察或判斷的結果：不顯示 Lab 的參考數字、不演 agent 被拒後的反應、
    不演三種步長的結局、門檻桿不停在任何特定門檻
  - 沒有選取時的輪播只用 idle（不露結果）；答完猜題才播完整的 pose，結束時回到靜止姿態
  - Lab 1 的杯子是資料點，永遠不動，只變色；動的只有旗桿（群中心）
  - Lab 3 的門檻桿一定由人手推動
  - AGENTS.md 的告示牌（提示）和 permission 的柵欄是兩個不同的物件
  - 拱橋只表示建議順序，樣式和地標裡的繩索、箭頭不同
  - 猜題不出：agent 被拒後會怎樣、/new 之後還記不記得、「該分幾群」這類沒有唯一答案的題目
"""
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "tools" / "pages.json").read_text(encoding="utf-8"))

GROUPS = {
    "開始之前": "start",
    "現場一起做": "live",
    "課後 · OpenCode 操作": "tools",
    "課後 · 數學應用": "math",
    "課後 · 閱讀與筆記": "notes",
    "隨時查閱": "ref",
}

ISLES = {
    "start": dict(name="啟航港", sub="開始之前", note="總覽與課前準備。出發前先把三樣工具裝好、看到綠燈。"),
    "live": dict(name="現場步道", sub="現場兩小時", note="第一次對話，再走三個 Lab。步道旁的時刻牌是現場的時間表。"),
    "tools": dict(name="工坊島", sub="課後 · OpenCode 操作", note="六間工坊，把 OpenCode 用得更順手；最外面的 Herdr 是選修。"),
    "math": dict(name="數學島", sub="課後 · 數學應用", note="低秩近似、梯度下降與最短路徑，先寫下怎樣算完成，交給 agent 算和畫，再自己判讀。"),
    "notes": dict(name="筆記島", sub="課後 · 閱讀與筆記", note="整理指定的數學來源，每一句都分清楚是原文、AI 解釋還是自己推的。"),
    "ref": dict(name="速查燈船", sub="隨時查閱", note="停在港心，任何時候都點得到。"),
}

STOPS = {
    "index": dict(short="總覽", code="00", landmark="瞭望台"),
    "prep": dict(short="課前準備", code="01", landmark="綠燈檢修棚"),
    "first-run": dict(short="第一次對話", code="02", landmark="權限柵欄", refs=["cheatsheet"]),
    "lab1-cluster": dict(short="Lab 1 分群", code="L1", landmark="手搖飲攤車廣場", refs=["first-run", "cheatsheet"]),
    "lab2-pca": dict(short="Lab 2 PCA", code="L2", landmark="外送投影台", refs=["first-run", "cheatsheet"]),
    "lab3-notes": dict(short="Lab 3 分類", code="L3", landmark="圖書館門檻尺", refs=["first-run", "cheatsheet"]),
    "agent-workflows": dict(short="交代任務", code="C1", landmark="交接驛站"),
    "agents-md": dict(short="AGENTS.md", code="C2", landmark="入口告示牌"),
    "git-safety": dict(short="git", code="C3", landmark="安全網跳台"),
    "mcp-skills": dict(short="MCP 與 skills", code="C4", landmark="工具坊"),
    "local-models": dict(short="本地模型", code="C5", landmark="自家機房"),
    "herdr": dict(short="Herdr", code="C6", landmark="雙塔觀測站"),
    "math-applications": dict(short="數學應用", code="M1", landmark="三題涼亭"),
    "research-notes": dict(short="文獻筆記", code="R1", landmark="核對桌"),
    "cheatsheet": dict(short="速查表", code="Q", landmark="速查燈船"),
}

# 三個 Lab 的代表互動圖：fig 是教材頁裡 explorer 的標題 id（深連結落點），shot 是截圖的元素。
# 三個 explorer 都用示範資料、預設停在第 1 步。只截圖表本身：explorer 下方的「玩完回答」會寫出它自己的答案。
FIGS = {
    "lab1-cluster": dict(fig="kmeans-title", shot="#kmeans-plot",
                         caption="先玩一次 k-means：一步一步看「指派」和「更新」。"),
    "lab2-pca": dict(fig="projection-title", shot="#projection-figure",
                     caption="只准記一個數字，要記哪個？轉動方向，看投影留下多少差異。"),
    "lab3-notes": dict(fig="threshold-title", shot=".th-queue-wrap",
                       caption="60 筆示範借閱依風險排隊，移動門檻看要寄幾封提醒。"),
}

GUIDE = {
    "index": "這裡看得到整座島。三個 Lab 的資料都是為這堂課造的，AI 沒見過。我替你做的決定：先帶你看全景，沒問你是不是已經上過課。",
    "prep": "三盞燈都轉綠再出發：git、opencode、uv。最重要的是測試三，要親眼看到 agent 真的建立檔案。我替你做的決定：備案 key 排在測試之後，額度用完時才用得上，但還是要先申請好。",
    "first-run": "agent 要動手之前，會先停在柵欄前問你。這一站要你親手拒絕一次，看它接下來怎麼做。我替你做的決定：不先告訴你它會怎麼反應。",
    "lab1-cluster": "杯子是一天的營業紀錄，旗桿是群中心。分幾群，要看你拿去做什麼。我替你做的決定：先帶你玩 k-means，等一下才讓你問 AI。",
    "lab2-pca": "金色的點是每張訂單投影到軸上的位置；軸轉到點散得最開時，就是第一個主成分。留幾個才夠？要先講清楚「夠做什麼」。我替你做的決定：用二維示意，真正的資料有 11 欄。",
    "lab3-notes": "門檻桿要你自己推。模型只會算分數，要寄幾封提醒，看館員的人力，也看你的判斷。我替你做的決定：沒有替你選門檻。",
    "agent-workflows": "交代任務的五格：目標、輸入、限制、輸出、完成判準。做到一半，就把進度寫進 notes/progress.md。我替你做的決定：先讓你自己寫需求，再拿去問它。",
    "agents-md": "告示牌寫的是規則，柵欄才擋得住人。AGENTS.md 是告示牌，真的不能出事的，要用 permission 擋。我替你做的決定：把「不准 commit」也算進要寫的規則。",
    "git-safety": "動手前先 commit，等於畫一條起跑線。改壞了，git diff 看得到差在哪，也還原得回來。我替你做的決定：commit 留給你自己做，push 這門課用不到。",
    "mcp-skills": "MCP 多給它一隻手，自訂 agent 換一個專家，subagent 找人分頭辦事。我替你做的決定：只建議接一個 Context7，不接也能完成作業。",
    "local-models": "模型檔放得進槽裡，不代表跑起來記憶體夠，對話越長越吃空間。我替你做的決定：本地模型排在課後，現場用網路模型就好。",
    "herdr": "兩座塔各住一個 OpenCode，靠繩子傳話，不共用記憶。我替你做的決定：把它排成選修，沒裝也不影響其他章。",
    "math-applications": "三座涼亭：低秩近似、梯度下降、最短路徑。先寫下你怎麼判斷完成，再交給 agent。我替你做的決定：三題的順序是我排的，可以挑一題先做。",
    "research-notes": "每一項論斷都蓋一個章：原文、AI 解釋、我推導。「我推導」那格只能你自己填。我替你做的決定：先帶你看標記規則，沒先問你要讀哪一份來源。",
    "cheatsheet": "現場卡住，先來這艘船翻一翻；找不到操作，就按 ctrl+p。我替你做的決定：把速查表停在港心，不管走到哪都點得到。",
}

_LIVE = ["first-run", "lab1-cluster", "lab2-pca", "lab3-notes"]
_TOOLS = ["agent-workflows", "agents-md", "git-safety", "mcp-skills", "local-models", "herdr"]

TOUR: dict[str, Any] = dict(
    name="阿卡",
    hello="嗨，我是阿卡，要我帶你走一趟嗎？",
    short="阿卡帶路",
    ask="想走哪一條路線？",
    resume="上次走到第 {n} 站「{title}」，要接著走嗎？",
    bye="走完了。我替你做的決定：路線的順序是我排的，你不一定要照著走。想去哪裡，直接點那個地方。",
    routes=[
        dict(key="first", label="第一次來", note="總覽、課前準備，再走現場四站", stems=["index", "prep"] + _LIVE),
        dict(key="live", label="照現場走", note="第一次對話和三個 Lab", stems=_LIVE),
        dict(key="tools", label="課後 OpenCode", note="工坊島六間，Herdr 是選修", stems=_TOOLS),
        dict(key="math", label="課後數學與筆記", note="數學島和筆記島", stems=["math-applications", "research-notes"]),
    ],
)

# 現場時刻牌：出自 tools/body_index.html 的時程表
SCHEDULE = {"first-run": "00:05", "lab1-cluster": "00:18", "rest": "00:43", "lab2-pca": "00:48",
            "lab3-notes": "01:18", "wrap": "01:43"}

# 先猜：答完才播放該站的完整動畫。cite＝(教材檔, 原文片語)，build 會確認片語真的在檔案裡。
QUIZ = {
    "index": dict(
        q="工作坊的每一關，最後一步都要做什麼？",
        options=["寫一句帶條件的結論", "把 AI 的答案直接貼進報告", "換一個模型再問一次", "把程式全部重寫"], answer=0,
        why="每一關都走同樣的節奏：先問、自己判斷、揭曉現場資訊、自己改問題、實際驗證，最後寫一句帶條件的結論。",
        cite=("tools/body_index.html", "最後寫一句帶條件的結論")),
    "prep": dict(
        q="課前的綠燈自測有三個測試，哪一個是「最重要的一關」？",
        options=["測試一：Python 環境能執行", "測試二：agent 會回話", "開啟狀態列", "測試三：agent 真的會動手，產生檔案"], answer=3,
        why="只會回話還不夠。測試三要看到 agent 真的產生 hello.py 並印出結果，整場工作坊都要它動手改檔、跑程式。",
        cite=("tools/body_prep.html", "測試三：agent 真的會動手（最重要的一關）")),
    "first-run": dict(
        q="在 OpenCode 的輸入框開頭打 !，會發生什麼事？",
        options=["跳出斜線指令清單", "補上檔名", "進入 Shell 模式，直接跑 shell 指令", "把這句話交給 subagent"], answer=2,
        why="! 進入 Shell 模式，按 Esc 退出；/ 是斜線指令，@ 用來補檔名或叫 subagent。",
        cite=("content/first-run.md", "進入 Shell 模式")),
    "lab1-cluster": dict(
        q="k-means 的「更新」這一步，移動的是什麼？",
        options=["每一個資料點", "每一群的中心", "群的數量 k", "資料的欄位"], answer=1,
        why="指派：每個點歸到離它最近的中心。更新：每個中心移到自己那群所有點的平均位置。資料點自己不會動。",
        cite=("tools/body_lab1-cluster.html", "每個中心移到自己那群所有點的平均位置")),
    "lab2-pca": dict(
        q="算共變異數矩陣、找主成分之前，PCA 要先對每一欄做什麼？",
        options=["四捨五入成整數", "刪掉讀數小的欄", "由小到大排序", "減掉這一欄的平均（中心化）"], answer=3,
        why="主成分是繞著資料的中心找變化最大的方向，所以要先把每一欄減掉自己的平均。",
        cite=("tools/body_lab2-pca.html", "為什麼要先中心化")),
    "lab3-notes": dict(
        q="logistic 迴歸替每一筆借閱算出來的，是什麼？",
        options=["0 或 1 兩種值", "會逾期幾天", "0 到 1 之間的分數（逾期的機率）", "借閱次數的排名"], answer=2,
        why="模型先算一個 0 到 1 的分數，再看分數有沒有超過門檻，決定要不要寄提醒。門檻是另外選的。",
        cite=("tools/body_lab3-notes.html", "0 到 1 的分數")),
    "agent-workflows": dict(
        q="交代一份任務時，「完成判準」要回答哪一個問題？",
        options=["我要看到什麼才算完成？", "我想知道什麼？", "資料或程式在哪裡？", "要交給哪個模型？"], answer=0,
        why="五格是目標、輸入、限制、輸出、完成判準。完成判準例如：檔案確實存在、程式跑完、解釋對得上結果。",
        cite=("content/agent-workflows.md", "我要看到什麼才算完成")),
    "agents-md": dict(
        q="在 AGENTS.md 寫「不准刪除 data/」，agent 就一定做不到嗎？",
        options=["對，寫進去就會被擋下", "不一定。AGENTS.md 是提示，真的要擋得用 permission", "對，但只限 Windows", "要重開機才會生效"], answer=1,
        why="AGENTS.md 會接在系統提示後面送給模型，效力像每次開頭貼一段話。它是提示，不是權限控制。",
        cite=("content/agents-md.md", "不是權限控制")),
    "git-safety": dict(
        q="請 agent 改檔之前，為什麼要先 commit？",
        options=["commit 會讓 agent 跑得比較快", "commit 會自動備份到雲端", "留一條乾淨的起跑線，之後看得到它改了什麼，也還原得回來", "不 commit 就不能開 OpenCode"], answer=2,
        why="先 commit，等於畫一條乾淨的起跑線。之後用 git diff 檢查這一輪的修改，不要的再還原。",
        cite=("content/git-safety.md", "畫一條乾淨的起跑線")),
    "mcp-skills": dict(
        q="照這一章的比喻，MCP 是什麼？",
        options=["換一個專家來", "找人分頭辦事", "把模型換成更大的", "多給 agent 一隻手（新的工具）"], answer=3,
        why="MCP 是多給它一隻手，自訂 agent 是換一個專家來，subagent 是找人分頭辦事。",
        cite=("content/mcp-skills.md", "多給它一隻手")),
    "local-models": dict(
        q="模型檔 6.6 GB，顯示卡有 12 GB。可以斷定跑起來記憶體一定夠嗎？",
        options=["可以，12 比 6.6 大", "不行。對話和工具也要記憶體，載入後要再確認", "可以，只要改用 CPU", "不行，本地模型至少要 24 GB"], answer=1,
        why="模型檔案放得下，不代表執行時的記憶體一定夠。對話變長、工具變多都會增加負擔，載入後用 ollama ps 確認。",
        cite=("content/local-models.md", "不代表執行時的記憶體一定夠")),
    "herdr": dict(
        q="用 Herdr 開第二個 OpenCode 當 reviewer，它知道你和第一個 OpenCode 聊過什麼嗎？",
        options=["不知道，只知道傳給它的那段話", "知道，兩個共用記憶", "只知道最後一句", "登入同一個帳號就知道"], answer=0,
        why="reviewer 只知道傳給它的那段話。要交代的事很長，就請 agent 先寫成檔案，再叫 reviewer 去讀。",
        cite=("content/herdr.md", "reviewer 只知道傳給它的那段話")),
    "math-applications": dict(
        q="梯度下降的每一步，往哪個方向走？",
        options=["導數指的方向", "隨機挑一個方向", "永遠往右", "導數的反方向"], answer=3,
        why="導數告訴你函數往哪邊上升，所以每次沿反方向走一小步：x 減掉步長乘以導數。",
        cite=("content/math-applications.md", "每次沿反方向走一小步")),
    "research-notes": dict(
        q="筆記裡有一句是 AI 解釋給你的，你自己還沒推過。這一句要標什麼？",
        options=["[原文]", "[AI 解釋]", "[我推導]", "不用標"], answer=1,
        why="[我推導] 只留給你自己完成的內容；原文沒提的假設或推導，也不能歸到 [原文]。",
        cite=("content/research-notes.md", "[我推導] 只留給")),
    "cheatsheet": dict(
        q="現場卡住，又想不起某個操作在哪裡，在 OpenCode 裡可以按什麼？",
        options=["ctrl+p 開指令面板", "ctrl+z 復原", "F5 重新整理", "Esc 結束程式"], answer=0,
        why="速查表開頭就寫了：找不到對應操作時，按 ctrl+p 開啟指令面板。",
        cite=("tools/body_cheatsheet.html", "按 ctrl+p 開啟指令面板")),
}

# 「做完再對照」：兩種面板。每一組都要先按「我做完這一關了」才展開。
# nums 列出面板上出現的每一個數字字串；build 會確認它們出現在 src 指的教材頁（數字同源）。
COMPARE: dict[str, Any] = dict(
    note="參考結果：參考程式跑出來的一種結果，換模型或換做法，數字可能不同。",
    purpose=[
        dict(key="lab1", stem="lab1-cluster", label="Lab 1 · 分群", src="tools/body_lab1-cluster.html",
             ask="手搖飲的營業紀錄，該分幾群？",
             default=dict(h="沒講用途時", text="三個指標沒有選同一個 k：silhouette 和 DB 選 9，CH 選 10。只說「分 9 群」並沒有算錯，只是還不知道你要拿去做什麼。"),
             table=dict(head=["做法", "k", "silhouette", "對店別的 ARI"],
                        rows=[["標準化", "9", "0.794", "0.881"], ["標準化", "10", "0.725", "0.990"]]),
             uses=[
                 dict(label="任務 A：店型手冊", hi=0, text="9 群可以。9 群把同一個捷運站兩個出口的兩家店併成一群，它們的營業樣貌幾乎一樣，寫成同一型很合理。"),
                 dict(label="任務 B：客訴回查", hi=1, text="要選 10 群，而且要說明還有少數紀錄可能分錯；真的要回查到店，最好補回店別紀錄。"),
             ],
             nums=["9", "10", "0.794", "0.725", "0.881", "0.990"]),
        dict(key="lab2", stem="lab2-pca", label="Lab 2 · PCA", src="tools/body_lab2-pca.html",
             ask="外送訂單 11 欄，要留幾個主成分？",
             default=dict(h="沒講用途時", text="參考程式照累積變異 90% 這類門檻，會留 5 個（92.9%）就說「夠了」。這回答的是「整體變化留了多少」。你那次 AI 說幾個，先對一下。"),
             table=dict(head=["保留", "累積變異", "辨識客訴的 AUC"],
                        rows=[["前 3 個主成分", "69.0%", "0.588"], ["前 4 個主成分", "83.9%", "1.000"], ["前 5 個主成分", "92.9%", "1.000"]]),
             uses=[
                 dict(label="任務 A：訂單概況週報", hi=2, text="照 90% 留 5 個很合理，它回答的正是「整體變化留了多少」。"),
                 dict(label="任務 B：客訴預警", hi=1, text="4 個就夠，3 個不夠。變異比例量的是「變化多大」，不是「對你多重要」，客訴的訊號要用客訴標籤檢查。"),
             ],
             nums=["69.0%", "83.9%", "92.9%", "0.588", "1.000", "90%"]),
        dict(key="lab3", stem="lab3-notes", label="Lab 3 · 門檻", src="tools/body_lab3-notes.html",
             ask="下一批借閱，門檻要設多少？",
             default=dict(h="沒講代價時", text="參考程式的準確率是用門檻 0.5 算的：分數過半就寄。你那次 AI 用了哪個門檻，要回工具紀錄查。這個數字沒有考慮館員一次能寄幾封，也沒考慮漏掉一個逾期有多嚴重。"),
             table=dict(head=["門檻", "提醒數", "抓到", "漏掉"],
                        rows=[["0.5", "17", "7", "6"], ["0.3", "27", "10", "3"], ["0.2", "37", "11", "2"],
                              ["0.1", "49", "11", "2"], ["0.05", "69", "13", "0"]]),
             cap_col=1,
             uses=[
                 dict(label="每 300 筆最多 40 封", cap=40, text="超過 40 封的門檻先劃掉，剩下的由你依「漏掉一個有多嚴重」拍板。這裡不替你選。"),
                 dict(label="改成最多 20 封", cap=20, text="這是 Lab 3 的「自己試」：上限變了，能選的門檻就變了，你的決定會跟著變嗎？"),
             ],
             nums=["0.5", "0.3", "0.2", "0.1", "0.05", "17", "27", "37", "49", "69", "40", "20"]),
    ],
    checks=dict(
        stem="lab2-pca", label="Lab 2 · 檢查漏網", src="tools/body_lab2-pca.html",
        ask="五項檢查都開著時，每一種故意放的錯誤都抓得到嗎？先關掉你覺得多餘的檢查，再看哪些錯誤溜過去。",
        checks=["比例", "|cos|", "重建", "正交", "特徵值"],
        # 每列：錯誤名稱、五項檢查各自 FAIL(1)／PASS(0)。出自 lab2_pca_bugs.py 的參考輸出
        bugs=[
            ["比例分母只用前 4 個", [1, 0, 0, 0, 0]],
            ["變異數分母用 n", [0, 0, 0, 0, 1]],
            ["忘記中心化", [1, 1, 1, 0, 1]],
            ["主成分取錯方向", [0, 1, 1, 0, 0]],
        ],
        nums=["比例分母只用前 4 個", "變異數分母用 n", "忘記中心化", "主成分取錯方向"],
        after="一整列都沒有 FAIL，就是那個錯誤溜過去了。「驗證通過」只表示在這組檢查下沒發現差異。"),
)
