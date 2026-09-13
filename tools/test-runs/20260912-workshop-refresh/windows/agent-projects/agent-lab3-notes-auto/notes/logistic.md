# 手刻二元 logistic 迴歸 — digits 3 vs 8

## 資料定義

- 取自 `sklearn.datasets.load_digits()`，只取標籤為 3 與 8 的樣本，共 $n=357$ 筆。
- 像素值除以 16，使特徵落在 $[0,1]$。
- 二元標籤：8 設為 1、3 設為 0，即 $y_i\in\{0,1\}$。
- 在 64 個像素特徵後補一欄 1 作為截距，設計矩陣 $X_b\in\mathbb{R}^{357\times 65}$，參數 $w\in\mathbb{R}^{65}$。
- 線性預測值 $z_i=w^{\top}x_{b,i}$，模型機率 $P(y_i=1\mid x_i)=\sigma(z_i)$，$\sigma$ 為 sigmoid。

## 推導一：負對數概似 $\to$ $L(w)=\frac{1}{n}\sum[\log(1+e^{z})-yz]$

單一樣本 Bernoulli 概似
$$P(y_i\mid x_i)=\sigma(z_i)^{y_i}\bigl(1-\sigma(z_i)\bigr)^{1-y_i},$$
負對數概似（對所有樣本取負號、加總）
$$\mathrm{NLL}=-\sum_{i=1}^{n}\Bigl[y_i\log\sigma(z_i)+(1-y_i)\log\bigl(1-\sigma(z_i)\bigr)\Bigr].$$

用恆等式
$$\log\sigma(z)=-\log(1+e^{-z}),\qquad
\log\bigl(1-\sigma(z)\bigr)=-z-\log(1+e^{-z}),$$
代入可得
$$\mathrm{NLL}=\sum_i\Bigl[\log(1+e^{-z_i})+(1-y_i)z_i\Bigr]
=\sum_i\Bigl[\log(1+e^{-z_i})+z_i-y_iz_i\Bigr].$$

因為 $\log(1+e^{-z})+z=\log e^{z}+\log(1+e^{-z})=\log(e^{z}+1)=\log(1+e^{z})$，最終得平均損失
$$L(w)=\frac{1}{n}\sum_{i=1}^{n}\Bigl[\log\bigl(1+e^{z_i}\bigr)-y_iz_i\Bigr].$$

實作上 `log(1+e^z)` 用穩定 `softplus`：$\mathrm{softplus}(z)=\max(z,0)+\log(1+e^{-|z|})$，避免 $z$ 很大時溢位。

## 推導二：$L(w)\to$ $\nabla L=\frac{1}{n}X_b^{\top}\bigl(\sigma(X_b w)-y\bigr)$

對 $w$ 逐項微分：
$$\frac{d}{dz}\log(1+e^{z})=\frac{e^z}{1+e^z}=\sigma(z),\qquad
\frac{d}{dz}(y z)=y,\qquad
\frac{\partial z_i}{\partial w}=x_{b,i},$$
所以
$$\nabla L(w)=\frac{1}{n}\sum_{i=1}^{n}\bigl(\sigma(z_i)-y_i\bigr)x_{b,i}
=\frac{1}{n}X_b^{\top}\Bigl(\sigma(X_b w)-y\Bigr).$$

## 有限差分梯度檢查

- 中央差分：$\Bigl[\dfrac{\partial L}{\partial w_j}\Bigr]_{\mathrm{fd}}=\dfrac{L(w+he_j)-L(w-he_j)}{2h}$。
- 檢查點 $w_0=\mathrm{RandomState}(0).normal(size=65)\times 0.01$，逐一檢查全部 65 維。
- $h$ 掃過 $10^{-2}$ 到 $10^{-9}$。

實際執行輸出（`uv run python lab3_logistic.py`）：

| $h$ | max $\lvert\nabla_{\mathrm{fd}}-\nabla_{\mathrm{analytic}}\rvert$ | max rel err |
|---|---:|---:|
| $10^{-2}$ | $7.351\times10^{-8}$ | $1.378\times10^{-5}$ |
| $10^{-3}$ | $7.351\times10^{-10}$ | $1.378\times10^{-7}$ |
| $10^{-4}$ | $7.171\times10^{-12}$ | $1.866\times10^{-7}$ |
| $10^{-5}$ | $1.082\times10^{-11}$ | $3.716\times10^{-7}$ |
| $10^{-6}$ | $1.080\times10^{-10}$ | $7.025\times10^{-6}$ |
| $10^{-7}$ | $6.700\times10^{-10}$ | $1.594\times10^{-4}$ |
| $10^{-8}$ | $8.556\times10^{-9}$ | $3.953\times10^{-4}$ |
| $10^{-9}$ | $1.371\times10^{-7}$ | $1.454\times10^{-3}$ |

## 誤差觀察

1. **中段為截斷誤差主導**：中央差分殘差 $O(h^2)$，故 $h$ 每縮小 10 倍、誤差約縮小 100 倍（$7.35\times10^{-8}\to7.35\times10^{-10}\to7.17\times10^{-12}$），與二階中央差分的理論一致。
2. **最佳步長約 $h\approx10^{-4}$**：該處最大絕對誤差 $7.17\times10^{-12}$ 最小。
3. **小 $h$ 為捨入誤差主導**：$h<10^{-4}$ 後，$(L(w+he_j)-L(w-he_j))$ 的相消誤差約為 $\epsilon\cdot |L|/h$，隨 $h$ 變小反而放大，誤差回升至 $10^{-11}\sim10^{-7}$ 量級。
4. 全程最大誤差遠小於解析梯度的量級，驗證 $\nabla L=\frac1n X_b^{\top}(\sigma(X_b w)-y)$ 與 $\displaystyle L(w)=\frac1n\sum[\log(1+e^z)-yz]$ 實作正確。