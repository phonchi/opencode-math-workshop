# 用 AGENTS.md 馴服 agent

> 課後延伸．預計閱讀與練習時間 40 分鐘
> 適用版本：opencode 1.18.30

工作坊上你已經會叫 opencode 幫你寫程式了。但你大概也遇過這些狀況：

- 它用英文回你，你要的是中文
- 它寫 `python lab1.py`，可是你的環境是 uv，跑起來找不到 numpy
- 你叫它「手刻 k-means」，它偷偷 `from sklearn.cluster import KMeans` 交差
- 每開一個新對話，你就要把上面這些規矩再講一次

這章要解決的就是最後一句。`AGENTS.md` 是一個放在專案根目錄的 Markdown 檔，opencode 每次開始工作都會先讀它。把規矩寫一次，之後每個對話都自動生效。

---

## 1. AGENTS.md 是什麼

它就是一個純文字 Markdown 檔，沒有特殊語法、沒有必填欄位。裡面寫的是**你希望 agent 每次都遵守的規則**：用什麼語言、用什麼指令跑程式、圖存哪裡、什麼事不准做。

opencode 會把這個檔案的內容接在系統提示後面送給模型。所以它的效力等同於「你每次對話開頭都手動貼上這段話」，只是你不用真的貼。

重點觀念：**AGENTS.md 是給模型看的，不是給人看的**。它不是 README。README 寫給同學看「這專案怎麼跑」，AGENTS.md 寫給 agent 看「你該怎麼動手」。兩者內容可以重疊，但目的不同。

---

## 2. opencode 什麼時候讀它

opencode 啟動時會依序尋找規則檔：

1. **專案層**：從目前目錄往上層逐層找 `AGENTS.md`（找不到才找 `CLAUDE.md`）
2. **全域**：`~/.config/opencode/AGENTS.md`
3. **Claude Code 相容**：`~/.claude/CLAUDE.md`（除非關閉此相容性）

找到的檔案會**一起合併**使用，不是只取第一個。同一類別中 `AGENTS.md` 優先於 `CLAUDE.md`。

因為是「從目前目錄往上找」，所以有個很實際的後果：

```bash
# 正確：在專案根目錄啟動，AGENTS.md 讀得到
cd ~/ai-math-lab
opencode

# 有風險：在別的地方啟動，讀到的可能不是你的專案規則
cd ~
opencode
```

**養成習慣：一律 `cd` 進專案根目錄再打 `opencode`。** 這是初學者最常見的「規則怎麼沒生效」原因。

---

## 3. AGENTS.md 與 `instructions` 設定的關係

你的 `opencode.json` 目前長這樣：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle",
  "permission": { "bash": "ask", "edit": "ask", "webfetch": "ask" },
  "instructions": ["AGENTS.md"]
}
```

很多人以為是 `instructions` 這行讓 AGENTS.md 生效的。**不是。** 根目錄的 `AGENTS.md` 是自動被找到的，不寫 `instructions` 也會讀。

這點我實際驗證過。建一個乾淨的資料夾，`opencode.json` 裡**完全沒有 `instructions` 這個鍵**：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle"
}
```

旁邊放一份只寫了「執行 Python 一律用 `uv run python <檔案>`」的 `AGENTS.md`，然後問它：

```bash
opencode run "用一句話回答：依照專案規則，執行 Python 檔案應該用哪一個指令？"
```

實測回答：

```
> build · big-pickle

`uv run python <檔案>`
```

**規則生效了，而設定檔裡一個字都沒提到 AGENTS.md。**

`instructions` 真正的用途是**追加其他檔案**。它支援三種寫法：

```json
{
  "instructions": [
    "AGENTS.md",
    "docs/math-conventions.md",
    ".cursor/rules/*.md",
    "https://example.com/team-rules.md"
  ]
}
```

- 相對路徑（相對於設定檔位置）
- glob 萬用字元（`*.md`）
- 遠端 URL（有 5 秒逾時限制）

所有 `instructions` 指到的檔案，會和自動找到的 `AGENTS.md` **合併在一起**。

所以起始專案裡那行 `"instructions": ["AGENTS.md"]` 其實是多餘的，寫明白一點而已，刪掉也不影響。但如果你之後想把規則拆成好幾個檔（例如 `notes-style.md`、`plot-style.md`），就要靠 `instructions` 把它們掛進來。

設定檔本身也是多層合併的，由低到高：

```
remote (.well-known/opencode)
  → 全域 ~/.config/opencode/opencode.json
  → OPENCODE_CONFIG 環境變數指定的檔
  → 專案根目錄 opencode.json          ← 教材一律用這層
```

後面的會覆蓋前面同名的鍵。**這門課的所有設定都寫在專案根目錄的 `opencode.json`**，這樣你的設定跟著專案走，換台電腦、交作業都不會掉。

（附帶一提：opencode 會在全域設定目錄自動產生 `opencode.jsonc`，裡面只有一行 `$schema`，以及一個依賴 `@opencode-ai/plugin` 的 `package.json`。那是它自己要用的，不用去動。`.jsonc` 格式允許寫註解。）

---

## 4. 全域 vs 專案層的 AGENTS.md

| | 全域 `~/.config/opencode/AGENTS.md` | 專案 `<專案>/AGENTS.md` |
|---|---|---|
| 適合放 | 你個人的偏好 | 這個專案的技術規則 |
| 例子 | 「一律用繁體中文回答」「解釋時先講結論」 | 「用 `uv run python`」「圖存 `figs/`」 |
| 會不會跟著作業一起交 | 不會 | 會（建議進版控） |
| 換專案還在嗎 | 在 | 不在 |

判斷原則很簡單：**換一個專案還成立的，放全域；只對這個專案成立的，放專案層。**

「用繁體中文」兩邊都可以。放全域你每個專案都不用再寫；放專案層則保證同學拿到你的專案也會得到中文回應。這門課建議**放專案層**，因為要交作業。

---

## 5. `/init` 指令會做什麼

在 opencode 的對話介面裡輸入：

```
/init
```

它會掃描專案的重要檔案（`pyproject.toml`、目錄結構、既有設定等），可能問你幾個問題，然後產生或更新 `AGENTS.md`，內容涵蓋建置指令、架構、慣例。

**什麼時候用**：從零開始一個新專案，你懶得自己想要寫什麼，用 `/init` 生一份草稿再手動改。

**警告**：官方文件寫的是「產生或更新」`AGENTS.md`，中文教學站則說如果檔案已存在，它會「改善而非覆寫」。不管是哪一種，它都會動到你那個檔案。你的起始專案已經有一份精心寫好的 `AGENTS.md`，跑 `/init` 之後內容一定會變。

（未實測：我沒有實際拿課程專案去跑 `/init`，因為風險不對稱：寫壞了要重來，跑對了也只是省幾分鐘。）

如果你真的想試：

```bash
cd ~/ai-math-lab
git add -A && git commit -m "跑 /init 之前的存檔"   # 先存檔
# 然後在 opencode 裡打 /init
# 不滿意就：
git restore AGENTS.md
```

這正是下一章要講的 git 工作流。**先 commit 再讓 agent 動手**，永遠不會錯。

---

## 6. 實用寫法：六件值得寫進去的事

以下每一條都對應一個真實會出錯的狀況。

### 6.1 語言

```markdown
## 語言
一律使用台灣繁體中文回答。程式碼、變數名稱、函式名稱、套件名稱保留英文。
```

要寫「保留英文」的部分，否則有些模型會很熱心地把 `n_clusters` 翻成 `叢集數`，程式就壞了。

### 6.2 執行環境（最重要的一條）

```markdown
## 執行環境
本專案用 uv 管理環境。執行 Python 一律用：

    uv run python <檔案>

不要用 `python`、`python3`、`pip install`。要加套件用 `uv add <套件>`。
```

為什麼這條最重要：你的套件（numpy、sklearn）裝在專案的 `.venv/` 裡。直接打 `python lab1.py` 用的是系統的 Python，**看不到那些套件**，會噴 `ModuleNotFoundError`。而 agent 的訓練資料裡絕大多數是 `python xxx.py`，不特別交代它就會照慣例寫。

同理，`pip install` 會裝到錯的地方或直接失敗；uv 的做法是 `uv add`，它會同時更新 `pyproject.toml`，環境才可重現。

### 6.3 可重現性

```markdown
## 可重現性
任何用到隨機性的地方，一律設定 `random_state=0`（或 `np.random.seed(0)`）。
包括但不限於：train_test_split、KMeans、PCA 的 randomized solver、資料洗牌。
```

這是數學課的硬需求。沒固定亂數種子，你今天跑出來的圖和明天跑出來的不一樣，寫報告時你會不知道要相信哪一張。助教重跑你的程式也對不上你的數字。

### 6.4 不准偷呼叫現成函式充數

```markdown
## 不要偷懶呼叫現成函式
如果我要求「手刻」「自己實作」某個方法，就不可以直接呼叫 sklearn 的對應
實作來充數。sklearn 只能當作**對照組**：手刻的結果算完後，可以再跑一次
sklearn 的版本，印出兩者的數值差異來驗證。
```

這是這門課最容易被 agent 陽奉陰違的一條。你說「幫我實作 PCA」，它回一個包了 `sklearn.decomposition.PCA` 的三行函式。程式會跑、結果會對，但你什麼都沒學到，作業分數是零。

寫成「sklearn 只能當對照組」比單純寫「不准用 sklearn」更好，因為前者給了 agent 一個**合法的替代做法**。純禁止的規則容易被繞過，給出路的規則比較會被遵守。

### 6.5 圖存哪裡

```markdown
## 圖檔
所有圖存到 `figs/`，用 `matplotlib.pyplot.savefig()`，不要用 `plt.show()`
（這是無視窗環境，`show()` 不會有任何效果）。
檔名用英文小寫加底線，例如 `figs/pca_scree_plot.png`。
```

`plt.show()` 在終端機環境裡是靜默無效的：不會報錯，就是什麼都沒發生，然後你以為程式壞了。明確要求 `savefig()` 到固定目錄，你才找得到圖。

### 6.6 不准 commit

```markdown
## 不要做的事
- 不要執行 `git commit`、`git push`，除非我明講。
- 不要改 `pyproject.toml` 以外的設定檔。
- 不要刪除 `figs/` 或 `notes/` 裡既有的檔案。
```

為什麼不准 agent commit：**commit 是你檢查過之後的動作**。如果 agent 改完自己就 commit 了，你就失去了「用 `git diff` 看它改了什麼」的機會，而那正是下一章的核心工作流。讓 agent 只負責改，你負責檢查和存檔。

`git push` 更是絕對不行，那會把東西推到網路上，收不回來。

---

## 7. 完整範例（可直接複製）

這是你的起始專案裡那份，可以直接用，也可以照自己的需要改：

```markdown
# AI-Math 工作坊　專案規則

## 語言
一律使用台灣繁體中文回答。程式碼、變數名稱、函式名稱、套件名稱保留英文。

## 執行環境
本專案用 uv 管理環境。執行 Python **一律**用：

    uv run python <檔案>

不要用 `python`、`python3`、`pip install`。要加套件用 `uv add <套件>`。

## 數學程式的規矩
1. **可重現**：任何用到隨機性的地方，一律設定 `random_state=0`（或 `np.random.seed(0)`）。
2. **先說數學，再寫程式**：動手前先用兩三句話說明你要用的公式或演算法步驟。
3. **自己驗證**：寫完數值方法後，必須附一段驗證程式碼，並實際執行、印出比對結果。
   不可以只說「應該正確」。
4. **不要偷懶呼叫現成函式**：如果我要求「手刻」某個方法，就不可以直接呼叫
   `sklearn` 的對應實作來充數。`sklearn` 只能當作**對照組**。

## 圖檔
所有圖存到 `figs/`，用 `matplotlib.pyplot.savefig()`，不要用 `plt.show()`
（這是無視窗環境，`show()` 不會有任何效果）。

## 筆記
數學筆記寫在 `notes/` 底下的 `.md` 檔，數學式用 `$...$`（行內）與 `$$...$$`（獨立行）。

## 不要做的事
- 不要 `git commit`、`git push`，除非我明講。
- 不要改 `pyproject.toml` 以外的設定檔。
- 不要刪除 `figs/` 或 `notes/` 裡既有的檔案。
```

注意第 3 條「自己驗證」的寫法：它不只說「要驗證」，還說「**必須實際執行、印出比對結果**，不可以只說『應該正確』」。這個補充很關鍵。不加的話，agent 常常寫一段驗證程式碼然後直接宣稱通過，根本沒跑。

---

## 8. 反例：哪些寫法沒用或有反效果

### 反例 1：寫得像許願，沒有可判斷的標準

```markdown
請寫出高品質、優雅、專業的程式碼。
```

沒用。「高品質」對模型來說沒有可操作的意義，它本來就在盡力產生它認為好的程式碼。這行字佔了 context 卻改變不了任何行為。

**改成**：說出可以檢查的具體要求。

```markdown
每個函式都要有 docstring，說明輸入的 shape 與輸出的 shape。
例如：`X: (n_samples, n_features) -> (n_samples, n_components)`
```

### 反例 2：寫成「教學」而不是「規則」

```markdown
PCA 是一種降維方法，它透過計算共變異數矩陣的特徵向量⋯⋯
```

沒用而且浪費空間。模型知道什麼是 PCA。AGENTS.md 要寫的是**你的專案的特殊約定**，不是通識教材。

### 反例 3：太長

塞三千字進去，效果通常比三百字差。規則一多，每條被遵守的機率就下降，而且長規則會擠壓真正重要的內容。

**原則：只寫「不講就會做錯」的事。** 講了跟沒講一樣的（例如「請寫正確的程式」），刪掉。

### 反例 4：自相矛盾

```markdown
不要使用任何第三方套件。
...
用 sklearn 做交叉驗證。
```

矛盾的規則會讓模型行為變得不可預測，它可能隨機挑一條遵守。寫完整份檔案後從頭讀一次，確認沒有打架的條文。

### 反例 5：以為 AGENTS.md 能強制執行

這是最重要的一個認知：AGENTS.md 是提示，**不是權限控制**。

「不要 `git push`」寫在 AGENTS.md 裡，是請求 agent 不要做；模型絕大多數時候會聽，但不保證。真正的強制要靠 `opencode.json` 的 `permission` 設定：

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git push": "deny",
      "git push *": "deny"
    }
  }
}
```

這是實測可用的：把上面這段放進 `opencode.json` 後，用 `opencode agent list` 檢視解析後的權限規則，可以看到 `{"permission": "bash", "pattern": "git push *", "action": "deny"}` 確實生效。規則以樣式比對，**最後一條符合的規則勝出**，所以 `"*": "ask"` 要寫在前面，特例寫後面。

注意上面**同時寫了 `"git push"` 和 `"git push *"` 兩條**。前者擋不帶參數的 `git push`，後者擋 `git push origin main` 這類帶參數的。我沒有實測單寫 `"git push *"` 能不能擋住不帶參數的 `git push`，所以兩條都寫，比較保險。

`permission` 的可用值是 `"allow"`、`"ask"`、`"deny"`。除了 `bash`、`edit`、`webfetch`，還有 `read`、`glob`、`grep`、`task`、`skill`、`websearch`、`external_directory` 等。

**心法：想拜託的事寫 AGENTS.md，不能出事的事寫 permission。**

---

## 9. 怎麼驗證 AGENTS.md 真的生效了

不要憑感覺。有三個層次的檢查。

### 層次 1：確認 opencode 讀到了你的設定

```bash
cd ~/ai-math-lab
opencode debug config
```

實測輸出（在起始專案裡執行）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle",
  "permission": {
    "bash": "ask",
    "edit": "ask",
    "webfetch": "ask"
  },
  "instructions": [
    "AGENTS.md"
  ],
  "agent": {},
  "mode": {},
  "plugin": [],
  "command": {},
  "username": "phonchi"
}
```

這證明 opencode 找到了你的專案 `opencode.json`，模型是 `opencode/big-pickle`，權限是 `ask`。

**注意這個指令的限制**：它顯示的是**合併後的設定**，不會把 AGENTS.md 的內文印出來。所以它能證明「設定讀到了」，不能證明「規則被遵守了」。要驗證後者，往下看。

### 層次 2：直接問它（實測有效）

最快的行為測試，在專案根目錄執行：

```bash
cd ~/ai-math-lab
opencode run "用一句話回答：依照專案規則，執行 Python 檔案應該用哪一個指令？"
```

實測輸出：

```
> build · big-pickle

`uv run python <檔案>`。
```

兩件事同時被驗證了：它**用繁體中文回答**（語言規則生效），而且**答出了 `uv run python`**（執行環境規則生效）。

### 這個測試的陷阱（我實際踩到了）

我原本想做一個對照實驗：把 `AGENTS.md` 改名成 `AGENTS.md.bak`，預期 agent 就答不出 `uv run python` 了。**結果完全不是這樣。** 實測輸出：

```
→ Read AGENTS.md.bak
→ Read opencode.json

`uv run python <檔案>`。
```

看到沒有？它**自己用讀檔工具去把 `AGENTS.md.bak` 翻出來讀了**，然後照樣答對。

這件事有兩個重要的意涵：

1. **「問它規則」這個測試會有偽陽性。** 它答對，不代表規則是透過 AGENTS.md 機制自動載入的；也可能是它自己去翻檔案翻到的。agent 比你想的還會找東西。
2. 所以**要搭配層次 1 的 `opencode debug config` 一起看**。`debug config` 是靜態的設定解析結果，不會被 agent 的臨場發揮干擾。

真的想做乾淨的對照實驗，應該要把檔案**移到專案目錄外面**（例如 `mv AGENTS.md /tmp/`），不能只是改個副檔名放在原地。（我沒有再測這一步，所以不保證有效，agent 對某些外部路徑仍有讀取權限。）

### 層次 3：實際任務測試

最終還是要看真實行為。給它一個小任務：

```bash
opencode run "在 notes/ 寫一個 test.md，裡面用 LaTeX 寫出 PCA 的目標函式"
```

然後檢查：檔案是不是寫在 `notes/`？數學式是不是用 `$$...$$`？說明是不是繁體中文？

有任何一項不符，就回頭把 AGENTS.md 那條規則寫得更具體。通常是規則太含糊，不是模型不聽話。

### 常見「規則沒生效」的原因

| 症狀 | 最可能的原因 | 怎麼修 |
|---|---|---|
| 完全不理會規則 | 不在專案根目錄啟動 opencode | `cd` 到根目錄再開 |
| 偶爾遵守偶爾不遵守 | 規則太含糊，或整份檔案太長 | 改具體、砍掉不重要的條文 |
| 改了 AGENTS.md 沒反應 | 可能是舊對話的脈絡還在 | 開新對話再試（中文教學站說規則是熱載入、改完立即生效，我未實測） |
| 某條永遠沒用 | 跟另一條規則矛盾 | 從頭讀一次，找出打架的條文 |

---

## 10. 本章重點

1. `AGENTS.md` 放專案根目錄，**自動被讀取**，不需要靠 `instructions` 宣告。
2. `instructions` 是用來**追加**其他檔案的（支援相對路徑、glob、遠端 URL）。
3. 設定多層合併，這門課**一律用專案根目錄的 `opencode.json`**。
4. 最該寫的規則：語言、`uv run python`、`random_state=0`、不准用 sklearn 充數、圖存 `figs/`、不准 commit。
5. 規則要**具體可檢查**；許願式、教學式、過長、矛盾的寫法都沒用。
6. AGENTS.md 是提示不是強制。**不能出事的事情要用 `permission` 擋。**
7. 驗證三層次：`opencode debug config` 看設定、`opencode run` 問它規則、真實任務看行為。

---

## 練習

1. 在你的專案跑 `opencode debug config`，確認 `model` 是 `opencode/big-pickle`。
2. 跑一次層次 2 的行為測試，確認它答出 `uv run python`。
3. 在 AGENTS.md 加一條你自己的規則（例如「所有 `.py` 檔開頭要有一行註解說明這支程式在做什麼」），開新對話，叫它寫一支小程式，檢查有沒有遵守。
4. 想一想：你加的那條規則，應該放 AGENTS.md 還是 `permission`？為什麼？

---

## 資料來源

- https://opencode.ai/docs/rules/ — AGENTS.md 的尋找順序、`instructions` 設定、`/init` 指令
- https://opencode.ai/docs/config/ — 設定檔位置與多層合併順序、JSONC 支援、變數替換
- https://opencode.ai/docs/permissions/ — `permission` 的鍵、值與樣式比對規則
- https://learnopencode.com/3-workflow/03-init.html — `/init` 對既有 AGENTS.md 是「改善而非覆寫」（中文教學站，簡體）
- https://learnopencode.com/2-daily/04-global-rules.html — 全域規則路徑、規則熱載入的說法（中文教學站，簡體）

本機實測（opencode 1.18.30，Linux/WSL2）：

- `opencode debug config` 於起始專案的實際輸出
- `opencode run` 的行為測試，含「無 `instructions` 鍵仍讀取 AGENTS.md」與「改名後 agent 自行讀檔」兩組對照
- `opencode agent list` 解析後的 `permission` 規則（`git push *` → `deny`）
