# 產線感測讀數運作模式分析 (Line Modes Analysis)

本文件針對 `data/line_modes.csv` 中的產線感測讀數進行分群與運作模式分析。

## 資料概述

`data/line_modes.csv` 包含 723 筆記錄與 8 個欄位：
1. `temp_c`：溫度 (°C)
2. `vibration_mm_s`：震動 (mm/s)
3. `pressure_kpa`：壓力 (kPa)
4. `flow_lpm`：流量 (L/min)
5. `current_a`：電流 (A)
6. `speed_rpm`：轉速 (RPM)
7. `firmware_ver`：韌體版本（常數 3.0）
8. `sample_period_s`：取樣週期（常數 0.5）

前 6 個數值特徵用於進行無監督分群（K-Means 與 GMM）。

## 分群與模式辨識結果

透過標準化處理（StandardScaler）與 K-Means 分群演算法，評估不同的群數 $k$：

- 當 $k = 4$ 時，資料可明確劃分為 4 種主要的運作模式：
  - **模式 1** (136 筆, 18.8%)：低溫、中高震動、低壓力、中等轉速。
  - **模式 2** (285 筆, 39.4%)：高溫、高震動、中高壓力、中等轉速。
  - **模式 3** (65 筆, 9.0%)：中高溫、高壓力、高速。
  - **模式 4** (237 筆, 32.8%)：低溫、低震動、高速。

- 當進一步細分為 $k = 6$ 時，可捕捉更細緻的負載狀態與速度區段。

數學模型評估指標（如手肘法 Inertia、輪廓係數 Silhouette Score、BIC/AIC）顯示 $k = 4$ 至 $k = 6$ 均具有良好的聚類效果。

相關視覺化圖表已儲存至 `figs/line_modes_evaluation.png`。
