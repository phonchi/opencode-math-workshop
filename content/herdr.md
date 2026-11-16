# 用 Herdr 顧著 OpenCode

> 課後選修 · 先完成工作坊主線，再決定要不要裝

Herdr 是一個專門用來跑 coding agent 的終端機 app。OpenCode 照原本的方式執行，Herdr 只多做兩件事：

- 側欄標出 OpenCode 正在工作、在等你回答，還是已經做完。
- 關掉視窗後，裡面的程式繼續在背景跑，重新打開就接回原本的畫面。

現場只開一個 OpenCode 時，用原本的終端機就夠了。等你開始一邊讓 OpenCode 做事、一邊在旁邊跑程式或看檔案，Herdr 會比較方便。它不會增加模型額度，也不會改變 OpenCode 回答的品質。

這一章用 Herdr 的桌面 app。三個平台的畫面和操作都一樣，只有 Windows 安裝時多一步設定；快捷鍵在 macOS 用 `Cmd`，Windows 和 Linux 用 `Ctrl`。

:::bg 哪些情況先跳過這一章

- **Intel 晶片的 Mac**：目前沒有安裝檔，只能自己從原始碼編譯。
- **在 WSL 裡跑 OpenCode 的同學**：Herdr 預設不會進到 WSL，設定方式和本章不同。
- **Linux 沒有桌面環境，或顯示卡驅動不支援 Vulkan**：app 開不起來。

:::

## 安裝

### Windows

打開 Git Bash，貼上這一行。它會呼叫 PowerShell 執行官方安裝程式，裝好後開始選單會出現 Herdr：

```bash
powershell -c "irm https://releases.herdr.dev/app/install.ps1 | iex"
```

接著把 Herdr 裡的終端機改成 Git Bash。Herdr 在 Windows 預設開 PowerShell，課前安裝的 opencode 和 uv 卻是登記在 Git Bash 裡。在同一個 Git Bash 視窗執行：

```bash
mkdir -p "$APPDATA/herdr-core"
cat > "$APPDATA/herdr-core/config.toml" <<'EOF'
shell = ['C:\Program Files\Git\bin\bash.exe', '--login', '-i']
EOF
```

這會建立一個只有這一行的設定檔，重複執行也沒關係。不用重開 Herdr，之後新開的終端機就是 Git Bash；設定前已經開著的終端機不會變。

### macOS（Apple 晶片）

到 [Herdr 下載頁](https://herdr.dev/download/) 下載 `Herdr.dmg`，打開後把 Herdr 拖進「應用程式」資料夾。

### Linux

在終端機執行官方安裝指令，裝好後應用程式選單會出現 Herdr：

```bash
curl -fsSL https://releases.herdr.dev/app/install.sh | sh
```

### 使用統計

桌面 app 預設每天送出一次匿名使用統計，內容是用了哪些 agent、開了幾個分頁這類計數，不會送出終端機內容、檔名或提示詞。不想送出的話，打開 Herdr 後點左下角的 Settings（或按 `Ctrl+,`，macOS 是 `Cmd+,`），在左邊選 Privacy 關掉。

## 認識畫面

Herdr 的畫面分三層：

| 名稱 | 是什麼 | 本章的用法 |
|---|---|---|
| space | 一個專案的工作區，列在左側欄 | 工作坊專案 `ai-math-lab` 用一個 space |
| tab（分頁） | space 裡的一件工作 | 先只用一個分頁 |
| pane（窗格） | 分頁切出來的一塊，每塊都是一個終端機 | 左邊跑 OpenCode，右邊跑一般指令 |

本章會用到的按鍵：

| 動作 | Windows、Linux | macOS |
|---|---|---|
| 往右切出新窗格 | `Ctrl+Shift+O` | `Cmd+D` |
| 打開設定 | `Ctrl+,` | `Cmd+,` |
| 指令面板 | `Ctrl+Shift+P` | `Cmd+Shift+P` |

按鍵記不住時就打開指令面板，輸入關鍵字找動作，旁邊也會列出快捷鍵。

## 練習：左邊 OpenCode，右邊跑指令

這個練習只請 OpenCode 做一件很小的事，用掉的額度很少。

**第 1 步**：打開 Herdr，畫面上已經有一個終端機。進入工作坊專案，啟動 OpenCode：

```bash
cd ~/Documents/ai-math-lab
opencode
```

以後要開 OpenCode，都像這樣先開一般的終端機，再自己輸入 `opencode`。

**第 2 步**：按 `Ctrl+Shift+O`（macOS 是 `Cmd+D`）往右切開。右邊會出現一個新的終端機，它不一定在專案資料夾，先進去：

```bash
cd ~/Documents/ai-math-lab
```

**第 3 步**：點一下左邊的窗格回到 OpenCode，送出：

```text
請在 notes/ 新增 herdr-test.md，內容只寫一行：Herdr 練習。
```

**第 4 步**：OpenCode 要寫檔時會停下來問你。先不要回答，看左側欄下方的 Agents：這個 agent 出現在紅色的 Needs you 底下，窗格右上角也會標出 Needs you。回到 OpenCode，選 `Allow once` 按 Enter，它會接著做完。你一直看著這個窗格的話，做完後顯示 Idle；如果你那時切到別的 space，會顯示 Done，右下角也會跳出完成通知。

**第 5 步**：點右邊的窗格，確認檔案真的寫出來了：

```bash
cat notes/herdr-test.md
```

**第 6 步**：關掉 Herdr 的視窗（macOS 可以直接按 `Cmd+Q` 結束），再從開始選單或應用程式重新打開。左右兩個窗格都還在，OpenCode 的對話也還在。

側欄的狀態是 OpenCode 自己回報的。版本太舊的 OpenCode 不會回報，側欄就看不到狀態，但照樣可以使用。顯示做完也不代表結果正確，還是要像第 5 步一樣自己檢查。

## 關掉視窗、關掉分頁、重新開機

| 你做的事 | 裡面的程式 |
|---|---|
| 關掉 Herdr 視窗，或 Herdr 自動更新 | 繼續在背景跑，重新打開就接回 |
| 關掉某個窗格或分頁 | 那裡面的程式跟著結束 |
| 電腦重新開機 | 程式都停了。窗格會回來，但只剩一個新的終端機。先 `cd` 到專案資料夾，再啟動 `opencode`，用 `/sessions` 找回對話 |

關掉視窗不等於停止。OpenCode 還在做事時關掉視窗，它會繼續執行，也繼續使用模型額度。真的要停，回到那個窗格讓 OpenCode 停下，或關掉那個窗格。

## 常見問題

| 狀況 | 怎麼處理 |
|---|---|
| Windows 打 `opencode` 找不到指令（`command not found`，或「無法辨識」的紅字） | 出現紅字表示還在用 PowerShell。檢查 `config.toml` 有沒有寫好，再開一個新的分頁試 |
| Windows 新開的窗格不在專案資料夾，space 名稱也一直是 `~` | 用 Git Bash 時 Herdr 追不到你 `cd` 去哪裡，這是已知問題。每個新窗格先 `cd ~/Documents/ai-math-lab` |
| 側欄看不到狀態 | 更新 OpenCode；看不到狀態也能正常使用 |
| 貼不上文字 | Windows 用 `Ctrl+V` 或 `Ctrl+Shift+V`，Linux 用 `Ctrl+Shift+V` 或 `Shift+Insert`，macOS 用 `Cmd+V` |

## 想再多玩一點

Herdr 還能讓一個 agent 開另一個 agent 幫忙審查，也能用 Mods 改介面。多開 agent 會更快用完免費額度；Mods 可以執行任意程式，安裝前要先看過內容。有興趣再看官方說明。

## 參考資料

- [Herdr 官方網站](https://herdr.dev/)
- [Herdr 桌面 app 說明（GitHub）](https://github.com/herdrdev/herdr-app)
- [herdr-core 設定說明（GitHub）](https://github.com/herdrdev/herdr-core)：預設 shell 與 `config.toml`
- [Herdr 隱私說明](https://herdr.dev/privacy/)
- 延伸觀看：[摸摸說門道：Herdr 好用嗎？](https://www.youtube.com/watch?v=C2zXbxPzqu4)，介紹桌面版、hc 指令與 Mods
- 延伸觀看：[AI懶人報 EP459：Herdr，AI agent 時代的 tmux](https://www.youtube.com/watch?v=OVl3fFSHxqY)，以終端機版（TUI）示範，按鍵與桌面 app 不同
