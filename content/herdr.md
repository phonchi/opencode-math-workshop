# 用 Herdr 讓 OpenCode 找幫手

> 課後選修 · 先完成工作坊主線，至少做完 Lab 3

Herdr 是一個專門用來跑 coding agent 的終端機 app。它最特別的地方是：**agent 可以自己開另一個 agent 當幫手**，交代工作、等它回報，再把結果整理給你。

OpenCode 內建的 subagent 也能分派子任務，但過程藏在對話裡，你只看得到最後的摘要。Herdr 開出來的幫手是一個真的終端機，你在側欄看得到它正在工作、在等你，還是已經做完，也可以隨時點進去看它讀了什麼、卡在哪裡。

這些事不用自己記指令。Herdr 寫了一份給 agent 看的說明書，官方教學只有一句話：先叫 agent 讀它，再直接說你想要什麼。

兩個 agent 同時工作，大約會用掉兩倍的模型額度。這一章請在課後、自己的網路下做，不要在教室共用網路時做。

:::bg 哪些情況先跳過這一章

- **Intel 晶片的 Mac**：目前沒有安裝檔，只能自己從原始碼編譯。
- **在 WSL 裡跑 OpenCode 的同學**：Herdr 預設不會進到 WSL，設定方式和本章不同。
- **Linux 沒有桌面環境，或顯示卡驅動不支援 Vulkan**：app 開不起來。

:::

## 安裝

### Windows

從開始選單打開 PowerShell，貼上官方的安裝指令。裝好後開始選單會出現 Herdr：

```powershell
irm https://releases.herdr.dev/app/install.ps1 | iex
```

接著把 Herdr 裡的終端機改成 Git Bash。Herdr 在 Windows 預設開 PowerShell，課前安裝的 opencode 和 uv 卻是登記在 Git Bash 裡。打開 Git Bash 執行：

```bash
mkdir -p "$APPDATA/herdr-core"
cat > "$APPDATA/herdr-core/config.toml" <<'EOF'
shell = ['C:\Program Files\Git\bin\bash.exe', '--login', '-i']
EOF
```

這會建立一個只有這一行的設定檔，之後新開的終端機就是 Git Bash。如果你以前自己改過這個檔案，不要執行上面的指令，改用記事本打開它，加上 `shell = …` 那一行。

### macOS（Apple 晶片）

到 [Herdr 下載頁](https://herdr.dev/download/) 下載 `Herdr.dmg`，打開後把 Herdr 拖進「應用程式」資料夾。

### Linux

在終端機執行官方安裝指令，裝好後應用程式選單會出現 Herdr：

```bash
curl -fsSL https://releases.herdr.dev/app/install.sh | sh
```

### 使用統計

桌面 app 預設每天送出一次匿名使用統計，內容是用了哪些 agent、開了幾個分頁這類計數，不會送出終端機內容、檔名或提示詞。不想送出的話，點左下角的 Settings，在左邊選 Privacy 關掉。

## 第一次打開

打開 Herdr，畫面上已經有一個終端機。進入工作坊專案，啟動 OpenCode：

```bash
cd ~/Documents/ai-math-lab
opencode
```

之後要開 OpenCode，都是先開終端機再輸入 `opencode`，不要從分頁列的 `+` 選單選。

左邊的側欄有兩區。上面的 Spaces 是工作區，一個專案用一個；下面的 Agents 列出正在跑的 agent，依狀態分組：

| 狀態 | 意思 | 你要做什麼 |
|---|---|---|
| Needs you（紅色） | 在等你回答，通常是權限詢問 | 點過去看清楚再回答 |
| Working | 正在工作 | 不用管它 |
| Done（藍色） | 你沒在看的時候做完了，右下角也會跳通知 | 點過去看結果 |
| Idle | 做完了，或在等你下新的指令 | 不用管它 |

## 練習：請 OpenCode 找一個 reviewer

Lab 3 最後要你自己核對 `notes/logistic.md`：每個數字對不對得上、有沒有哪句話說得比證據更滿。這次先請另一個 OpenCode 審一次，再由你判斷它說得對不對。整個練習請預留約 15 分鐘。

**第 0 步**：先在 `notes/logistic.md` 故意改錯一個數字，例如門檻 0.2 抓到的逾期數，記住你改了哪裡，看等一下 reviewer 抓不抓得到。練習完記得改回來。

**第 1 步**：在 Herdr 裡打開 OpenCode（做法見上一節），貼上：

```text
請先讀 ~/.config/herdr-app/AGENTS.md 和 hc --skill，了解怎麼在 Herdr 裡開另一個 agent。

然後開一個 OpenCode 當 reviewer，請它只讀不改，檢查 notes/logistic.md 的數字和結論，是否對得上 notes/decision.md 和 lab3_logistic.py，有沒有哪句話說得比證據更滿。它做完回報給你，你再整理給我。它要權限時不要替我按，告訴我。
```

**第 2 步**：接下來幾分鐘，它會讀說明、開幫手。過程中 OpenCode 會停下來問你很多次能不能執行某個指令，多半是 `hc` 開頭的。`hc` 是 Herdr 用來開終端機、傳話給別的 agent 的工具，你不用記它，只要看懂它想做什麼，再選 `Allow once`。如果它要傳給 reviewer 的只是 y、Enter 這類按鍵，那是想替你回答 reviewer 的問題，選 Reject，自己過去看。

**第 3 步**：reviewer 開起來後，會出現在側欄的 Agents。它要回報時，同樣會停下來問你，側欄會出現紅色的 Needs you。點過去看清楚它要做的事，再決定要不要同意，然後點側欄回到原本的 OpenCode。

**第 4 步**：reviewer 的回報會直接出現在原本那個 OpenCode 的對話裡，開頭標著 `<hc from="…">`。原本的 OpenCode 收到後會整理重點給你。

**第 5 步**：自己核對。請原本的 OpenCode 重跑 `lab3_logistic.py`，拿印出來的門檻表逐項對照 reviewer 說的問題。reviewer 常常只能說「兩個地方對不上」，哪一個才對要你決定。也看看它有沒有抓到你在第 0 步改錯的數字。

**第 6 步**：想補問，直接跟原本的 OpenCode 說，例如：

```text
請 reviewer 再看一下 notes/logistic.md 的「不能證明什麼」那段：每一句真的都是在說不能證明嗎？有沒有提到新一批只有 13 個逾期？
```

**第 7 步**：看完結果，跟它說「收工，把 reviewer 關掉」。

## 兩個 agent 不共用記憶

reviewer 只知道傳給它的那段話，不知道你們之前聊過什麼。要交代的事如果很長，請 agent 先寫成檔案，再叫 reviewer 去讀，就像[讓 agent 把工作做完整](agent-workflows.html)裡的 `notes/progress.md`。

## 再試試其他說法

學會上面的流程後，可以換別的說法：

- 「開一個 reviewer，先不要給任務。等我在它的窗格用 `/models` 換成別的模型，再把任務傳過去。」不同模型看問題的角度不一樣，常會抓到不同的問題。可用的免費模型見[課前準備的備案](prep.html#backup-keys)。
- 「幫我做一個版面，把我的 agent 排成三欄：Needs you、Working、Done。」這是官方教學的例子，agent 會照說明書改 Herdr 的介面，做好後用 `Ctrl+Shift+L`（macOS 是 `Cmd+Shift+L`）切換版面。

reviewer 的窗格也可以直接點進去，自己打字跟它對話。

## 關掉視窗、關掉分頁、重新開機

| 你做的事 | 裡面的程式 |
|---|---|
| 關掉 Herdr 視窗，或 Herdr 自動更新 | 繼續在背景跑，重新打開就接回 |
| 關掉某個窗格或分頁 | 那裡面的程式跟著結束 |
| 關掉原本那個 OpenCode | 它開的 reviewer 也跟著結束 |
| 電腦重新開機 | 程式都停了。窗格會回來，但只剩一個新的終端機。先 `cd` 到專案資料夾，再啟動 `opencode`，用 `/sessions` 找回對話 |

關掉視窗不等於停止。OpenCode 還在做事時關掉視窗，它會繼續執行，也繼續使用模型額度。

## 常見問題

| 狀況 | 怎麼處理 |
|---|---|
| 側欄沒有出現 reviewer | 它可能改用了內建的 subagent。跟它說「請用 Herdr 的 hc 開，不要用內建 subagent」 |
| reviewer 開不起來，說找不到 opencode | 跟它說「先開一個終端機，再在裡面執行 opencode」 |
| 側欄顯示 Needs you，畫面上卻沒有詢問 | 同一個資料夾的 OpenCode 對話會互相影響。看畫面上方哪個對話分頁標著 `!`，切過去回答 |
| 補問傳不過去，說 reviewer 在等權限 | 先把所有 Needs you 處理完，再請它重送 |
| Windows 打 `opencode` 找不到指令（`command not found`，或「無法辨識」的紅字） | 出現紅字表示還在用 PowerShell。檢查 `config.toml` 有沒有寫好，再開一個新的分頁試 |
| Windows 新開的窗格不在專案資料夾，space 名稱也一直是 `~` | 用 Git Bash 時 Herdr 追不到你 `cd` 去哪裡，這是已知問題。每個新窗格先 `cd ~/Documents/ai-math-lab` |
| 貼不上文字 | Windows 用 `Ctrl+V` 或 `Ctrl+Shift+V`，Linux 用 `Ctrl+Shift+V` 或 `Shift+Insert`，macOS 用 `Cmd+V` |

## 參考資料

- [Herdr 官方網站](https://herdr.dev/)
- [Herdr 官方教學](https://herdr.dev/guide/)：「Ask your agent」，列出更多可以直接對 agent 說的話
- [Herdr 寫給 agent 的說明書（GitHub）](https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md)
- [herdr-core 說明（GitHub）](https://github.com/herdrdev/herdr-core)：`hc` 指令與 `config.toml`
- [Herdr 隱私說明](https://herdr.dev/privacy/)
- 延伸觀看：[摸摸說門道：Herdr 好用嗎？](https://www.youtube.com/watch?v=C2zXbxPzqu4)，介紹桌面版、hc 的四個常見情境與 Mods
- 延伸觀看：[AI懶人報 EP459：Herdr，AI agent 時代的 tmux](https://www.youtube.com/watch?v=OVl3fFSHxqY)，第四段示範讓 agent 自己派工、互相 review；片中用的是終端機版（TUI），按鍵與桌面 app 不同
