# 產線感測讀數運作模式分析報告 (`line_modes.csv`)

## 1. 資料概況
`data/line_modes.csv` 包含 723 筆產線感測器讀數紀錄，主要特徵包含：
- `temp_c`：溫度 (°C)
- `vibration_mm_s`：震動 (mm/s)
- `pressure_kpa`：壓力 (kPa)
- `flow_lpm`：流量 (LPM)
- `current_a`：電流 (A)
- `speed_rpm`：轉速 (RPM)
- `firmware_ver`：韌體版本 (固定為 3.0)
- `sample_period_s`：取樣週期 (固定為 0.5 秒)

## 2. 分群與模式判定方法
使用標準化 (StandardScaler) 後的數值特徵，透過非監督式機器學習演算法（如 K-Means 分群與 Gaussian Mixture Model, GMM）進行模式識別，並以 Silhouette Score、Calinski-Harabasz Index 及 BIC/AIC 評估最佳分群數 $k$。

評估指標表現：
- $k = 2$：Silhouette = $0.4212$
- $k = 3$：Silhouette = $0.4570$
- $k = 4$：Silhouette = $0.5356$
- $k = 5$：Silhouette = $0.5651$
- $k = 6$：Silhouette = $0.6060$

## 3. 運作模式解析
依據業務邏輯與分群特徵中心點分析，產線主要可劃分為 **4 種核心運作模式**（若進一步細分製程狀態，亦可擴展至 **5 ~ 6 種子模式**）：

$$
\text{Total Modes} = 4 \text{ (主要大模式)} \text{ 或 } 5 \sim 6 \text{ (細緻運作狀態)}
$$

### 4 大核心運作模式特徵：
1. **模式 0（低速運轉模式）**：
   - 特徵：溫度偏低 ($\approx 55.7^\circ\text{C}$)、轉速較低 ($\approx 1216 \text{ RPM}$)、壓力與電流較低。
2. **模式 1（中速重載模式）**：
   - 特徵：溫度高 ($\approx 78.8^\circ\text{C}$)、轉速中等 ($\approx 1436 \text{ RPM}$)、流量較高。
3. **模式 2（高速高壓模式）**：
   - 特徵：高溫 ($\approx 70.8^\circ\text{C}$)、高轉速 ($\approx 1795 \text{ RPM}$)、極高壓力 ($\approx 496 \text{ kPa}$) 與高電流 ($\approx 15.3 \text{ A}$)。
4. **模式 3（高速低溫模式）**：
   - 特徵：低溫 ($\approx 56.1^\circ\text{C}$)、極高轉速 ($\approx 1855 \text{ RPM}$)、震動較小。

## 4. 視覺化圖表
- 肘部法則與群集評估圖已儲存至 `figs/line_modes_bic_aic.png`
- 4 模式與 5 模式散佈圖已儲存至 `figs/line_modes_k4.png` 與 `figs/line_modes_k5.png`
