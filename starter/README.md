# AI-Math 工作坊　起始專案

## 這是什麼

這是工作坊三個實作用的起始專案。裡面已經幫你準備好：

| 檔案 | 作用 |
|---|---|
| `pyproject.toml` | Python 套件清單（numpy / matplotlib / scikit-learn / networkx） |
| `opencode.json` | opencode 的專案設定（指定模型與權限） |
| `AGENTS.md` | 給 agent 的專案規則（語言、執行方式、驗證要求） |
| `notes/` | 放你的數學筆記 |
| `figs/` | 放程式產生的圖 |

## 怎麼開始

```bash
uv sync          # 建立 Python 環境（第一次要幾分鐘，請在家先做完）
opencode         # 啟動 agent
```

## 檢查環境有沒有好

```bash
uv run python -c "import numpy, sklearn, matplotlib, networkx; print('環境 OK')"
```
