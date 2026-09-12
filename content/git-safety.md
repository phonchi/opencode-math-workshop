# git：讓你敢放手讓 agent 改檔案

> 課後延伸．預計閱讀與練習時間 50 分鐘
> 適用版本：opencode 1.18.30

這章不教 git 的全部，只教**七個指令**。目標很明確：讓你在按下 Enter 讓 agent 改你的檔案時，心裡不會怕。

---

## 1. 你在怕什麼

工作坊上多半會看到這個場景：agent 說「我來幫你改一下 `lab2_pca.py`」，然後停在權限詢問畫面，而你的手指懸在鍵盤上不敢按 `y`。

怕的通常是這幾件事：

- 它把我熬夜寫好的東西蓋掉了怎麼辦
- 它改了五個檔案，我根本不知道它改了什麼
- 它說「已修正」，但程式反而更壞了，我想回到原本的版本卻回不去
- 它改對了一部分、改壞了一部分，我分不出來

這些恐懼都是合理的。而且會導致一個很糟的結果：**你為了安全，乾脆不讓 agent 動手，只讓它給你看程式碼，然後自己複製貼上。** 那就等於把一個能幫你做事的工具，降級成一個比較會講話的搜尋引擎。

git 解決的正是這件事。一句話：

> **git 讓「改壞了」這件事的代價，從「重寫一遍」變成「打一行指令」。**

當還原成本趨近於零，恐懼就消失了，你才敢真的放手用。這才是這章的重點——git 在這門課裡不是「軟體工程規範」，是**心理安全網**。

另外先講一個有關聯的設定。opencode 有個 `--auto` 參數，`--help` 裡它自己標註為「auto-approve permissions that are not explicitly denied (**dangerous!**)」。**學習階段絕對不要用它。** 逐次確認權限，加上這章的 git 工作流，是你目前最好的組合。

---

## 2. 不需要 GitHub 帳號

先破除一個誤會：**git 和 GitHub 是兩回事。**

- **git** 是裝在你電腦上的版本控制程式。完全離線，不需要帳號、不需要網路。
- **GitHub** 是一個放 git 儲存庫的網站。需要帳號、需要網路。

這章從頭到尾**只用本機 git**。你不需要註冊任何東西，你的程式碼不會上傳到任何地方。所有紀錄存在專案資料夾裡一個叫 `.git/` 的隱藏目錄。

先確認你有 git：

```bash
git --version
```

有版本號就可以了。沒有的話，Ubuntu/WSL 用 `sudo apt install git`。

第一次用要設定身分（只設定一次，之後所有專案通用）：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的信箱"
```

這兩個資訊只是寫進本機的 commit 紀錄裡，**不會送到任何伺服器**。

---

## 3. 最小可用的 git：七個指令

### `git init` — 開始追蹤這個資料夾

```bash
cd ~/ai-math-lab
git init
```

只做一次。之後這個資料夾就被 git 追蹤了。

### `git status` — 現在有什麼變動

```bash
git status
```

最常用的指令。看不懂現在是什麼狀況時就打它。

### `git add -A` — 把目前所有變動納入這次存檔

```bash
git add -A
```

`-A` 是 all 的意思，把所有新增、修改、刪除的檔案都納入。

### `git commit -m` — 存檔

```bash
git commit -m "完成 PCA 手刻版本"
```

`-m` 後面是這次存檔的說明，寫給未來的自己看。`git add -A` 和 `git commit` 幾乎總是一起用，可以連起來：

```bash
git add -A && git commit -m "完成 PCA 手刻版本"
```

**把這行背起來。** 這是整章使用頻率最高的指令。

### `git diff` — 看從上次存檔到現在改了什麼

```bash
git diff
```

**這是這章最重要的指令。** 它回答「agent 到底改了我什麼」。下一節專門講怎麼讀它的輸出。

### `git restore` — 丟掉未存檔的修改，回到上次 commit 的樣子

```bash
git restore lab2_pca.py     # 只還原這個檔案
git restore .               # 還原所有檔案
```

**這是你的後悔藥。** 注意：它丟掉的是「還沒 commit 的修改」，這個動作**無法復原**，所以要先用 `git diff` 確認你真的不要那些修改。

### `git log --oneline` — 看存檔歷史

```bash
git log --oneline
```

輸出長這樣：

```
a3f2c81 完成 PCA 手刻版本
7b91e04 加上 k 值選擇的圖
c4d5a22 初始環境
```

前面那串是 commit 的編號（hash）。按 `q` 離開。

---

## 4. 核心工作流：三步驟

這是整章的骨幹。**每次叫 agent 動手之前、之後，各做一件事。**

```
  ┌─────────────────────────────────────────┐
  │  1. 動手前先存檔                          │
  │     git add -A && git commit -m "..."    │
  └─────────────────┬───────────────────────┘
                    ↓
  ┌─────────────────────────────────────────┐
  │  2. 讓 agent 改（在 opencode 裡）          │
  └─────────────────┬───────────────────────┘
                    ↓
  ┌─────────────────────────────────────────┐
  │  3. 檢查                                 │
  │     git diff                             │
  └─────────────────┬───────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   滿意 → 再 commit         不滿意 → git restore .
   git add -A &&            （回到步驟 1 的狀態）
   git commit -m "..."
```

實際操作起來是這樣：

```bash
# 1. 動手前先存檔（這是關鍵，不要跳過）
cd ~/ai-math-lab
git add -A && git commit -m "叫 agent 改 PCA 之前的狀態"

# 2. 開 opencode 讓它改
opencode
# ...在裡面對話，讓它修改 lab2_pca.py...
# 改完離開（Ctrl+C 或 /exit）

# 3. 檢查它改了什麼
git diff

# 4a. 覺得不錯 → 存起來
uv run python lab2_pca.py        # 先確認真的能跑
git add -A && git commit -m "PCA 加上 scree plot"

# 4b. 覺得不行 → 全部丟掉
git restore .
```

**注意 `git restore .` 的一個限制**：它只還原「git 已經在追蹤的檔案」。如果 agent **新增**了檔案（例如自己開了一個 `notes/test.md`），`git restore .` **不會把它刪掉**。你會在 `git status` 看到它還躺在那裡（顯示為 untracked），然後以為 restore 失敗了。

要清掉這些新增的檔案，用 `git clean`：

```bash
git clean -n      # 先預演，只列出「會被刪掉」的檔案，不真的刪
git clean -f      # 確認清單沒問題後，真的刪掉
```

**一定要先 `-n` 再 `-f`。** 詳見第 9 節的急救表。

### 為什麼「動手前先 commit」不能跳過

因為 `git diff` 和 `git restore` 都是**相對於上一次 commit** 運作的。

如果你上次 commit 是三天前，中間你自己改了很多東西，那 `git diff` 會把「你自己改的」和「agent 改的」混在一起顯示，你分不出誰是誰。而 `git restore .` 會把你自己三天的心血也一起丟掉。

**先 commit，等於畫一條乾淨的起跑線。** 之後 `git diff` 顯示的每一行，都保證是 agent 幹的。

commit 訊息隨便寫沒關係，`git commit -m "wip"` 也行。**重點是有 commit，不是訊息寫得漂亮。**

---

## 5. 怎麼看懂 `git diff` 的輸出

這是一段真實的 `git diff` 輸出（實際跑出來的，不是示意）：

```diff
diff --git a/kmeans.py b/kmeans.py
index 94c687d..3b8b876 100644
--- a/kmeans.py
+++ b/kmeans.py
@@ -1,10 +1,9 @@
 import numpy as np
 
 
-def kmeans(X, k, n_iter=100):
+def kmeans(X, k, n_iter=300):
     """手刻 k-means。X: (n_samples, n_features)"""
-    rng = np.random.default_rng(0)
-    idx = rng.choice(len(X), k, replace=False)
+    idx = np.random.choice(len(X), k, replace=False)
     centers = X[idx]
     for _ in range(n_iter):
         labels = np.argmin(((X[:, None] - centers) ** 2).sum(-1), axis=1)
```

一行一行拆解：

| 符號 | 意思 |
|---|---|
| `diff --git a/kmeans.py b/kmeans.py` | 接下來講的是 `kmeans.py` 這個檔案 |
| `index 94c687d..3b8b876` | 內部編號，**看不懂沒關係，直接跳過** |
| `--- a/kmeans.py` | `a/` 代表**舊版**（你上次 commit 的） |
| `+++ b/kmeans.py` | `b/` 代表**新版**（agent 改完的） |
| `@@ -1,10 +1,9 @@` | 位置標記：舊版從第 1 行起算 10 行，新版從第 1 行起算 9 行 |
| 開頭是 `-` 的行 | **被刪掉的**（舊版有，新版沒有） |
| 開頭是 `+` 的行 | **新增的**（新版才有） |
| 開頭是空白的行 | 沒改，只是顯示出來讓你知道上下文 |

記憶法：**`-` 是拿掉，`+` 是加上。修改一行 = 先 `-` 舊的再 `+` 新的，所以會看到成對出現。**

`@@` 那行叫 hunk header。初學階段你只要知道「它標示這段變動在檔案的哪個位置」就夠了，數字不用細讀。一次 diff 可能有好幾個 `@@` 區塊，代表檔案的好幾處分別被改動。

### 讀出這個 diff 的問題

現在來實際判讀。這個 diff 有兩處變動：

**變動一**：`n_iter=100` → `n_iter=300`。迭代次數變多，合理，沒問題。

**變動二**：看仔細——

```diff
-    rng = np.random.default_rng(0)
-    idx = rng.choice(len(X), k, replace=False)
+    idx = np.random.choice(len(X), k, replace=False)
```

原本用的是 `np.random.default_rng(0)`，**帶了亂數種子 `0`**，所以每次執行的初始中心點都一樣，結果可重現。

改完之後變成 `np.random.choice(...)`，**種子不見了**。程式看起來更簡潔、跑起來完全正常、結果也對——但**每次跑出來的分群結果都不一樣了**。

這正是我們在 `AGENTS.md` 裡用 `random_state=0` 想守住的可重現性，被一個看似無害的「簡化」偷偷破壞了。

**這就是 `git diff` 的價值。** 如果你只是看 agent 說「我把程式碼簡化了一點，並增加迭代次數」，你會覺得很好、按下接受。只有逐行看 diff，才會發現種子被拿掉了。

> **養成習慣：diff 裡每一個 `-` 開頭的行都要問一句「這行為什麼該被刪掉？」** 新增的程式碼通常看得出好壞，**被偷偷刪掉的東西才是真正的陷阱**。

### 幾個好用的變化

```bash
git diff --stat           # 只看每個檔案改了幾行，先抓全貌
git diff lab2_pca.py      # 只看某一個檔案
git diff --word-diff      # 以「詞」為單位標示，改一兩個字時比較好讀
```

檔案改很多時，先 `git diff --stat` 看規模：

```
 kmeans.py   | 5 ++---
 lab2_pca.py | 32 ++++++++++++++++++++++++++++++++
 2 files changed, 34 insertions(+), 3 deletions(-)
```

如果你只叫它改一個檔案，結果這裡列出五個，那就是警訊，值得仔細看。

---

## 6. `.gitignore`：哪些東西不要進版控

有些檔案不該被 git 追蹤。在專案根目錄建立一個叫 `.gitignore` 的檔案：

```bash
cd ~/ai-math-lab
cat > .gitignore <<'EOF'
# Python 虛擬環境（幾百 MB，可以用 uv sync 重建）
.venv/

# Python 快取
__pycache__/
*.pyc

# 作業系統雜物
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/
EOF

git add -A && git commit -m "加上 .gitignore"
```

### 逐項說明

**`.venv/` — 一定要排除。** 這是 uv 建立的虛擬環境，幾百 MB、上萬個檔案，而且可以用 `uv sync` 從 `pyproject.toml` 和 `uv.lock` 完整重建。把它放進 git 只會讓儲存庫爆掉。

> 小提醒：uv 其實會在 `.venv/` 裡自動放一個內容為 `*` 的 `.gitignore`，所以就算你沒寫，git 也不會追蹤它。自己在根目錄再寫一次是好習慣，因為你一眼就看得到這個決定。

**`__pycache__/`、`*.pyc` — 一定要排除。** Python 自動產生的編譯快取，沒有保存價值。

**`uv.lock` — 要進版控。** 它記錄了每個套件的精確版本，是可重現性的保證。不要把它加進 `.gitignore`。

### `figs/` 要不要進版控：這題沒有標準答案

這是真正需要你自己判斷的取捨。

**支持「進版控」的理由：**

- 圖是你作業或報告的一部分，交出去時要有
- 可以看到圖隨著程式修改怎麼變化——`git log` 翻回去就能對照「那時候的圖長什麼樣」
- 助教或組員不用重跑你的程式就能看到結果
- 你的圖多半是幾十 KB 的 png，數量也有限，完全不會造成負擔

**支持「不進版控」的理由：**

- 圖是**衍生產物**，理論上跑一次程式就能重新生成
- 每次重跑即使結果完全一樣，png 的二進位內容也可能有細微差異（時間戳記等），造成 `git status` 一直有雜訊
- 圖檔的 diff 看不懂——git 只會說「binary files differ」

**這門課的建議：`figs/` 進版控。**

理由是課程情境：你的圖數量少、體積小，而且「看得到圖的演變過程」對學習的價值遠大於那點雜訊。更重要的是——**你要交作業**，圖在版控裡最保險。

如果你之後做的專案會產生上百張高解析度的圖，那時再改成排除，並在 README 寫清楚怎麼重新生成。

（如果你選擇不進版控，就在 `.gitignore` 加 `figs/*.png`，但保留 `figs/.gitkeep`，這樣目錄結構還在。）

---

## 7. 把數學筆記放進 git 的好處

`notes/` 底下的 `.md` 筆記**一定要進版控**，而且好處比程式碼更明顯。

### 好處 1：看得到 agent 改了你筆記的哪一個字

純文字檔的 diff 精準到字元層級。假設你請 agent 潤飾筆記：

```bash
git add -A && git commit -m "PCA 筆記初稿"
opencode run "幫我潤飾 notes/pca.md 的說明，讓推導更清楚"
git diff notes/pca.md
```

你會看到類似這樣：

```diff
-我們要找一個方向 $w$，讓投影後的變異數最大。
+我們要找一個單位向量 $w$（即 $\|w\|=1$），使投影 $Xw$ 的變異數最大。
```

一眼就知道它加了「單位向量」的限制條件。**這是真的改好了**，你學到了一個原本漏掉的條件。

但也可能看到：

```diff
-特徵值 $\lambda_i$ 代表第 $i$ 個主成分解釋的變異量。
+特徵值 $\lambda_i$ 代表第 $i$ 個主成分的重要性。
```

「重要性」比「解釋的變異量」模糊，**這是改差了**，`git restore notes/pca.md` 退回去。

### 好處 2：你自己的理解歷程被保留下來

`git log --oneline notes/pca.md` 可以看到這份筆記的所有版本。期末複習時翻回三週前的版本，你會看到當時的自己哪裡想錯了——**那個「想錯又改對」的過程，比最終正確的版本更有學習價值**。

### 好處 3：安心讓 agent 大改

知道隨時能還原，你才敢下「幫我重寫這一節，用更直觀的方式解釋特徵值分解」這種大動作的指令。不敢放手，就只能請它做無關痛癢的小修改。

---

## 8. 明確警告：不要叫 agent 幫你 `git push`

**這是這章唯一一條完全沒有彈性的規則。**

### 為什麼

1. **`push` 會把東西送到網路上，而且收不回來。** 本機的東西改壞了，`git restore` 就好。推上去的東西別人可能已經看到、已經拉下來了。
2. **你可能不小心推上不該公開的東西** —— 沒寫進 `.gitignore` 的金鑰、個人資料、還沒交的作業答案。
3. **這門課根本不需要。** 本機 repo 就能得到這章所有的好處。
4. **推錯地方的修復難度遠超出本課範圍**，`git revert`、`git reset --hard`、force push 都是會讓初學者更慌的工具。

### 連帶的：`git commit` 也交給你自己做

你的 `AGENTS.md` 裡已經有這條：

```markdown
- 不要 `git commit`、`git push`，除非我明講。
```

為什麼連 commit 都不給：**commit 是「我檢查過了，這個版本我認可」的意思。** 如果 agent 改完自己 commit 了，`git diff` 就沒東西可看了（變動已經被存進歷史），你就失去了檢查的機會。

**分工要清楚：agent 負責改，你負責檢查和存檔。**

### 用 permission 真正擋住它

AGENTS.md 是請求，不是強制。要真的擋住，用 `opencode.json` 的 `permission`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/big-pickle",
  "permission": {
    "bash": {
      "*": "ask",
      "git status": "allow",
      "git diff *": "allow",
      "git log *": "allow",
      "git push": "deny",
      "git push *": "deny",
      "rm -rf *": "deny"
    },
    "edit": "ask",
    "webfetch": "ask"
  },
  "instructions": ["AGENTS.md"]
}
```

其中 **`"git push *": "deny"` 這條是我實際驗證過的**：存檔後執行 `opencode agent list`，可以在解析後的權限規則裡看到 `{"permission": "bash", "pattern": "git push *", "action": "deny"}`。同一份設定裡的 `git status` / `git diff *` 樣式也一併正確解析。`rm -rf *` 那條我沒有單獨測試，它只是同樣語法的套用。

四個要點：

1. **`deny` 代表直接拒絕**，連問都不問。`ask` 是每次問你，`allow` 是直接放行。
2. **最後一條符合的規則勝出**，所以萬用的 `"*": "ask"` 要寫在最前面，特例寫在後面。順序寫反了就沒效果。
3. 把 `git status`、`git diff`、`git log` 設成 `allow`，是因為它們是唯讀的、不會改任何東西，讓 agent 自由查詢反而方便（它可以自己檢查改了什麼）。
4. **`"git push"` 和 `"git push *"` 兩條都要寫。** 前者擋不帶參數的 `git push`（最常見的形式），後者擋 `git push origin main` 這種帶參數的。我沒有實測單寫帶 `*` 的能不能同時擋住不帶參數的情況，所以兩條都寫。

改完設定用這個指令確認生效：

```bash
opencode debug config
```

---

## 9. 出事時的急救表

| 狀況 | 指令 |
|---|---|
| agent 改壞了，還沒 commit | `git restore .` |
| 只想還原其中一個檔案 | `git restore lab2_pca.py` |
| 想看 agent 到底改了什麼 | `git diff` |
| 改很多檔，想先看規模 | `git diff --stat` |
| 不確定現在是什麼狀態 | `git status` |
| 想看歷史版本 | `git log --oneline` |
| 想看某個舊版本的檔案內容 | `git show a3f2c81:lab2_pca.py` |
| agent 新增了一堆你不要的檔案（還沒 add） | `git clean -n` 先看，確認後 `git clean -f` |

**兩個保命原則：**

1. **`git restore` 之前一定先 `git diff`。** 還原無法復原，先確認你真的不要那些修改。
2. **`git clean -f` 之前一定先 `git clean -n`。** `-n` 是預演，只列出會被刪的檔案、不真的刪。

---

## 10. 本章重點

1. git 的價值是**心理安全網**：還原成本趨近於零，你才敢放手讓 agent 做事。
2. **不需要 GitHub 帳號**，純本機 repo 就能得到全部好處。
3. 七個指令：`init` / `status` / `add -A` / `commit -m` / `diff` / `restore` / `log --oneline`。
4. 核心工作流：**動手前 commit → 讓 agent 改 → `git diff` 檢查 → 滿意再 commit，不滿意 `git restore`**。
5. 讀 diff：`-` 是刪掉、`+` 是新增、`@@` 是位置。**特別注意被刪掉的行**。
6. `.gitignore` 放 `.venv/`、`__pycache__/`；`uv.lock` 要進版控；`figs/` 這門課建議進版控。
7. 筆記進版控，看得到 agent 改了哪個字，也保留你自己的理解歷程。
8. **絕對不要叫 agent `git push`**，並用 `permission` 的 `"git push *": "deny"` 真正擋住。
9. 學習階段不要用 `opencode --auto`。

---

## 練習

1. 在你的專案跑 `git init`，建立 `.gitignore`，做出第一個 commit。
2. 跑 `git log --oneline` 確認 commit 存在。
3. 做一次完整工作流：commit → 叫 agent 改 `reference/` 裡任一支程式 → `git diff` 逐行讀 → 判斷好壞 → commit 或 restore。
4. 故意做一次 `git restore .`，親手體驗「改壞了也沒關係」的感覺。**這一步不要跳過**，恐懼是靠實際經驗消除的，不是靠讀文章。
5. 把第 8 節的 `permission` 設定寫進 `opencode.json`，用 `opencode debug config` 確認生效，然後叫 agent 執行 `git push`，看它是不是真的被擋下來。

---

## 資料來源

- https://opencode.ai/docs/permissions/ — `permission` 的鍵、`allow`/`ask`/`deny`、樣式比對「最後一條符合的勝出」
- https://opencode.ai/docs/config/ — 設定檔位置與合併順序
- https://opencode.ai/docs/rules/ — AGENTS.md 與 git 相關規則的寫法
- https://learnopencode.com/2-daily/06-git-basics.html — git 基礎指令與「保留最後一次人工確認」的原則（中文教學站，簡體）
- https://learnopencode.com/5-advanced/05-permissions.html — bash 樣式規則範例、「最後匹配的規則生效」（中文教學站，簡體）

本機實測（opencode 1.18.30，Linux/WSL2）：

- 第 5 節的 `git diff` 輸出為實際執行 git 產生，非示意
- `opencode agent list` 確認 `"git push *": "deny"` 規則正確解析
- `opencode --help` 中 `--auto` 的原文警語 "(dangerous!)"
- `starter/.venv/.gitignore` 內容確為 `*`
