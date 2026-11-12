# -*- coding: utf-8 -*-
# 重庆大学 844 自动控制原理 初试真题 2023–2025.
# 每道题: year, no, score(可无), cats(分类路径列表，第一个为主分类), stem(Markdown+LaTeX),
# answer(最终结果), explanation(文字解析要点)。图片由 crops.json 按 "年-题号" 自动挂载。
# 追加新年份：新增一个同结构的 QUESTIONS 列表文件，并在 build_data.py 的 SOURCES 里登记页码。
Q = []
def q(year, no, cats, stem, answer, explanation, score=None):
    Q.append(dict(year=year, no=no, cats=cats, stem=stem.strip(), answer=answer.strip(),
                  explanation=explanation.strip(), score=score))

# ───────────────────────── 2023 ─────────────────────────
q(2023, 1, ["建模 / 机械系统 / 微分方程与传递函数", "状态空间 / 建立状态空间表达式"], r"""
系统如下图所示（弹簧 $K$、阻尼器 $C$、质量 $m$，输入力 $g(t)$），求：

[[fig:1]]

1、该系统的微分方程；

2、传递函数；

3、状态空间方程表达式。
""", r"""
1. 微分方程：$m\ddot x_0+f\dot x_0+kx_0=g(t)$，即 $\ddot x_0+\dfrac{f}{m}\dot x_0+\dfrac{k}{m}x_0=\dfrac1m g(t)$（$f$ 为阻尼系数，$k$ 为弹簧刚度）。

2. 传递函数：$\Phi(s)=\dfrac{X_0(s)}{G(s)}=\dfrac{\frac1m}{s^2+\frac fm s+\frac km}$。

3. 取 $x_1=x_0,\ x_2=\dot x_0$：$A=\begin{bmatrix}0&1\\-\frac km&-\frac fm\end{bmatrix},\ B=\begin{bmatrix}0\\1\end{bmatrix},\ C=\begin{bmatrix}\frac1m&0\end{bmatrix}$（源答案取 $y=\frac1m x_1$）。
""", r"""
由牛顿第二定律 $g(t)-f\dot x_0-kx_0=m\ddot x_0$，整理得二阶微分方程。

零初始条件下做拉氏变换：$X_0(s)\left(s^2+\dfrac fm s+\dfrac km\right)=\dfrac1m G(s)$。

令 $x_1=x_0$，$x_2=\dot x_1$，则 $\dot x_1=x_2$，$\dot x_2=-\dfrac km x_1-\dfrac fm x_2+g(t)$，写成矩阵形式即可。
""")

q(2023, 2, ["时域分析 / 二阶系统性能指标", "时域分析 / 稳态误差 / 复合控制"], r"""
系统结构图如下，该系统的无阻尼振荡频率为 $2\,\mathrm{rad/s}$，求：

[[fig:1]]

1、$r(t)=1(t)$、$G_c(s)=0$ 时，$e_{ss}=0.4$，求 $k_a$、$\sigma\%$、$t_s\ (5\%)$；

2、当 $e_{ss}=0$ 时，求 $G_c(s)$ 的形式。
""", r"""
1. $k_a=0.4$；闭环 $\Phi(s)=\dfrac{0.833}{s^2+1.233s+1.167}$，$\omega_n=1.08\,\mathrm{rad/s}$，$\zeta=0.571$，$\sigma\%\approx11.2\%$，$t_s=\dfrac{3.5}{\zeta\omega_n}\approx5.676\,\mathrm s\ (5\%)$。

2. $G_c(s)=s+0.4$。
""", r"""
开环 $G(s)=\dfrac{1}{(1.2s+1)(s+k_a)}$，$K_p=\dfrac1{k_a}$，$e_{ss}=\dfrac1{K_p}=k_a=0.4$。

代入得闭环特征多项式 $1.2s^2+1.48s+1.4$，与典型二阶系统比较求 $\zeta,\omega_n$。

第 2 问用梅森公式求误差传递函数：
$$\Phi_e(s)=\frac{s(1.2s+1)+(0.4-G_c(s))(1.2s+1)}{1.2s^2+1.48s+1.4}$$
令分子恒为 0 即得 $G_c(s)=s+0.4$。
""")

q(2023, 3, ["根轨迹 / 常规根轨迹绘制", "时域分析 / 稳态误差 / 静态误差系数", "根轨迹 / 主导极点与降阶"], r"""
$$G(s)=\frac{K(s+4)}{s(s+2)(s+15)}$$

1、绘制其根轨迹；

2、若要求系统稳定，求 $K$ 的开环增益范围；

3、$s_1=-9$ 时，系统是否可视为二阶系统？当 $r(t)=2+3t$ 时，求此时对应的稳态误差？
""", r"""
1. 开环极点 $0,-2,-15$，零点 $-4$；实轴根轨迹 $(-15,-4)\cup(-2,0)$；渐近线 $\sigma_a=-6.5$，$\varphi_a=\pm\dfrac\pi2$；分离点 $s=-1.136$；与虚轴无交点。

2. $K>0$ 时系统均稳定。

3. $s_1=-9$ 时 $K=75.6$，另两极点 $-4\pm4.195j$；$\left|\dfrac{-9}{-4}\right|<5$，**不能**视为二阶系统。$r(t)=2+3t$ 时 $K_v=2.864$，$e_{ss}=\dfrac{3}{K_v}\approx1.05$。
""", r"""
分离点方程 $2s^3+29s^2+136s+120=0$，解得 $s=-1.136$（另两根为复数，舍）。

$D(s)=s^3+17s^2+(30+K)s+4K$，劳斯表首列 $1,\ 17,\ \dfrac{17(30+K)-4K}{17},\ 4K$ 在 $K>0$ 时全正。

根之和：另两根实部 $=\dfrac{-15-2+9}{2}=-4$；模值条件 $K=\dfrac{6\cdot7\cdot9}{5}=75.6$。
""")

q(2023, 4, ["频域分析 / Bode 图绘制", "频域分析 / 截止频率与相角裕度"], r"""
已知：
$$G_C(s)=\frac{500(s+2)(s+3)}{s(0.8s+2)(s+10)(s+50)}$$
求：

1、绘制该系统的 Bode 图；

2、求该系统的截止频率 $\omega_C$ 和相角裕度 $\gamma$。
""", r"""
1. 尾一型：$G_C(s)=\dfrac{3\left(\frac s2+1\right)\left(\frac s3+1\right)}{s\left(\frac s{2.5}+1\right)\left(\frac s{10}+1\right)\left(\frac s{50}+1\right)}$，低频斜率 $-20\,\mathrm{dB/dec}$；转折频率 $2,3$（向上），$2.5,10,50$（向下）。

2. $\omega_C=12.5\,\mathrm{rad/s}$，$\gamma\approx103.35^\circ$。
""", r"""
用“拆大放小”分段近似 $|G_C(j\omega_C)|=1$，在 $10<\omega_C<50$ 段有 $\dfrac{3\cdot\frac{\omega_C}{2}\cdot\frac{\omega_C}{3}}{\omega_C\cdot\frac{\omega_C}{2.5}\cdot\frac{\omega_C}{10}}=1$，解得 $\omega_C=12.5$。

$$\gamma=180^\circ+\arctan\frac{\omega_C}{2}+\arctan\frac{\omega_C}{3}-90^\circ-\arctan\frac{\omega_C}{2.5}-\arctan\frac{\omega_C}{10}-\arctan\frac{\omega_C}{50}\approx103.35^\circ$$
""")

q(2023, 5, ["离散系统 / 脉冲传递函数", "离散系统 / 稳定性（朱利判据）", "离散系统 / 差分方程"], r"""
系统结构图如下，求：

[[fig:1]]

1、求该系统的 $\Phi(z)$ 传递函数；

2、求系统稳定时的 $k$ 值范围；

3、求该系统的差分方程；

4、$k=2$ 时，若 $c(0)=0$、$c(1)=0.5$，求 $c(2)$ 及 $c(3)$ 的值。
""", r"""
1. （源答案按 $T=1$）$G(z)=k\dfrac{0.28375z+0.14875}{(z-1)(z-0.135)}$，
$\Phi(z)=\dfrac{0.28375kz+0.14875k}{z^2+(0.28375k-1.135)z+0.135+0.14875k}$。

2. $0<k<5.82$。

3. $c(k)+(0.28375k-1.135)c(k-1)+(0.135+0.14875k)c(k-2)=0.28375k\,r(k-1)+0.14875k\,r(k-2)$。

4. $k=2$：$c(k)-0.5675c(k-1)+0.4325c(k-2)=0.5675r(k-1)+0.2975r(k-2)$，递推得 $c(2)=0.28375+0.5675r(1)$，$c(3)=0.5675c(2)+0.21625+0.5675r(2)+0.2975r(1)$（单位阶跃输入时 $c(2)\approx0.851$）。
""", r"""
$G(z)=k\dfrac{z-1}{z}\mathcal Z\!\left[\dfrac{0.5}{s^2}-\dfrac{0.25}{s}+\dfrac{0.25}{s+2}\right]$，$e^{-2}\approx0.135$。

朱利判据：$|0.135+0.14875k|<1$，$D(1)>0$，$D(-1)>0$，联立得 $0<k<5.82$。

把 $\Phi(z)$ 写成 $z^{-1}$ 的有理式即得差分方程，再代入初值递推。
""")

q(2023, 6, ["非线性系统 / 描述函数法 / 自振分析", "非线性系统 / 非线性环节等效"], r"""
系统结构图如下，求：

[[fig:1]]

[[fig:2]]

1、$N_1$、$N_2$ 等效的非线性环节 $N$；

2、当 $k=10$ 时，是否产生自振，如果产生自振，求出对应的频率和振幅；

3、当该系统不自振时，求 $k$ 的范围。
""", r"""
1. 串联等效为理想继电特性：输入 $>0.5$ 输出 $2$，$|x|<0.5$ 输出 $0$，$<-0.5$ 输出 $-2$（死区 $0.5$、幅值 $2$ 的继电器）。

2. $\omega=1\,\mathrm{rad/s}$ 处 $|G(j1)|=\dfrac k2=5$；由 $N(A)|G(j1)|=1$ 得 $A_1=12.723$，$A_2=0.5$；$A_2$ 为不稳定交点舍去，**产生自振**，频率 $1\,\mathrm{rad/s}$，振幅 $12.723$。

3. $0<k<\dfrac\pi4$ 时系统不自振。
""", r"""
$\angle G(j\omega)=-90^\circ-2\arctan\omega=-180^\circ\Rightarrow\omega=1$。

带死区继电特性 $N(A)=\dfrac{4M}{\pi A}\sqrt{1-\left(\dfrac hA\right)^2}$，$M=2,\ h=0.5$。

不自振 $\Leftrightarrow$ 负倒描述函数曲线与奈氏曲线无交点：$\dfrac k2<\dfrac{\pi h}{2M}=\dfrac\pi8$。
""")

q(2023, 7, ["状态空间 / 状态转移矩阵", "状态空间 / 传递函数矩阵", "状态空间 / 能控性与能观性"], r"""
$$A=\begin{bmatrix}-2&1&0\\0&-2&0\\0&0&-1\end{bmatrix},\quad B=\begin{bmatrix}0\\1\\1\end{bmatrix},\quad C=\begin{bmatrix}0&1&0\end{bmatrix}$$

1、求 $e^{At}$ 状态转移矩阵；

2、求该系统的 $G(s)$ 传递函数；

3、求该系统的能控能观性。
""", r"""
1. $e^{At}=\begin{bmatrix}e^{-2t}&te^{-2t}&0\\0&e^{-2t}&0\\0&0&e^{-t}\end{bmatrix}$。

2. $G(s)=C(sI-A)^{-1}B=\dfrac1{s+2}$。

3. 约旦标准型判据：**完全能控**；**不完全能观**。
""", r"""
$(sI-A)^{-1}=\begin{bmatrix}\frac1{s+2}&\frac1{(s+2)^2}&0\\0&\frac1{s+2}&0\\0&0&\frac1{s+1}\end{bmatrix}$，逐项拉氏反变换。

能控：$B$ 中与每个约旦块最后一行对应的元素（1、1）不为 0。能观：$C$ 中与每个约旦块第一列对应的元素存在 0。
""")

q(2023, 8, ["状态空间 / 稳定性分析", "状态空间 / 状态反馈极点配置"], r"""
$$A=\begin{bmatrix}3&-2\\4&3\end{bmatrix},\quad B=\begin{bmatrix}0\\1\end{bmatrix},\quad C=\begin{bmatrix}1&0\end{bmatrix}$$

1、当 $x_e=0$ 时，求系统的稳定性；

2、系统是否可以通过状态反馈达到完全稳定；

3、若 2 成立的条件下，求该系统的极点要为 $-2\pm3j$ 时的对应状态反馈矩阵。
""", r"""
1. 特征根 $\lambda=3\pm2\sqrt2\,j$，实部为正，**不稳定**。

2. $\operatorname{rank}[B\ AB]=2$，完全能控，可以通过状态反馈镇定。

3. $k=[k_1\ k_2]=[-13\ \ 10]$。
""", r"""
$|\lambda I-A|=(\lambda-3)^2+8=\lambda^2-6\lambda+17$。

期望多项式 $(\lambda+2)^2+9=\lambda^2+4\lambda+13$；实际 $|\lambda I-A+Bk|=\lambda^2+(k_2-6)\lambda-3(k_2-3)-2(k_1-4)$。

比较系数：$k_2-6=4$，$-3k_2+9-2k_1+8=13$，得 $k_2=10,\ k_1=-13$。
""")

# ───────────────────────── 2024 ─────────────────────────
q(2024, 1, ["建模 / 电路网络 / 运放电路传递函数", "频域分析 / 由对数幅频特性确定参数"], r"""
控制系统结构如下图所示。

[[fig:1]]

[[fig:2]]

1. 求 $\dfrac{u_y(s)}{u_r(s)}$；

2. $C_1=10\,\mu\mathrm F$，$C_2=10\,\mu\mathrm F$，求 $R_1$、$R_2$ 的值使得系统满足图 (b) 对数幅频特性曲线。
""", r"""
1. $\dfrac{U_y(s)}{U_r(s)}=\dfrac{(1+sR_2C_2)(1+sR_1C_1)}{sR_1C_2}$（$A_2$ 为 $-1$ 倍反相器）。

2. 由图 (b)：$\dfrac{U_y(s)}{U_r(s)}=\dfrac{10(s+1)\left(\frac s{10}+1\right)}{s}$，得 $R_1=10\,\mathrm{k\Omega}$，$R_2=100\,\mathrm{k\Omega}$。
""", r"""
$\dfrac{U_x(s)}{U_r(s)}=-\dfrac{R_2+\frac1{sC_2}}{R_1\parallel\frac1{sC_1}}=-\dfrac{(1+sR_2C_2)(1+sR_1C_1)}{sR_1C_2}$，$\dfrac{U_y}{U_x}=-\dfrac{R_1}{R_1}=-1$。

低频段以 $-20\,\mathrm{dB/dec}$ 过 $(1,20\,\mathrm{dB})$，转折频率 $1$、$10$（均 $+20\,\mathrm{dB/dec}$），得 $K=10$。

$\dfrac1{R_1C_2}=10\Rightarrow R_1=10\,\mathrm{k\Omega}$；$R_1C_1=\dfrac1{10}$ 对应转折 $10$，$R_2C_2=1\Rightarrow R_2=100\,\mathrm{k\Omega}$。
""")

q(2024, 2, ["时域分析 / 由阶跃响应确定参数", "时域分析 / 二阶系统性能指标", "时域分析 / 稳态误差"], r"""
在开关 $K$ 断开的情况下，系统为二阶系统且单位阶跃输入响应如下图所示。

[[fig:1]]

[[fig:2]]

1. $K$ 断开时，求闭环传递函数；

2. $K$ 断开和闭合后，求系统 $\sigma\%$ 和 $t_s\ (\Delta=2\%)$；

3. 单位阶跃输入时，$K$ 断开和闭合的稳态误差和稳态输出。
""", r"""
1. $\sigma\%=\dfrac{1.7-1.2}{1.2}\approx41.7\%$，$\zeta\approx0.268$，$t_p=2\,\mathrm s\Rightarrow\omega_n\approx1.63$；$\Phi(s)=\dfrac{3.18828}{s^2+0.87368s+2.6569}$。

2. 断开：$\sigma\%\approx41.7\%$，$t_s\approx10.07\,\mathrm s$；闭合：$\Phi(s)=\dfrac{3.19}{s^2+2.465s+2.66}$，$\zeta=0.756$，$\sigma\%\approx2.66\%$，$t_s\approx3.57\,\mathrm s$。

3. 断开、闭合两种情况均有 $c(\infty)\approx1.2$，$e(\infty)=1-1.2=-0.2$。
""", r"""
$K=c(\infty)=1.2$；$\zeta=\sqrt{\dfrac{\ln^2\sigma\%}{\pi^2+\ln^2\sigma\%}}$，$\omega_n=\dfrac{\pi}{t_p\sqrt{1-\zeta^2}}$。

前向通道 $G(s)=\dfrac{\Phi}{1-\Phi}\approx\dfrac{3.19}{s^2+0.87s-0.53}$；闭合 $K$ 后内环反馈 $0.5s$，再求闭环。

劳斯判据确认闭环稳定后用终值定理求 $c(\infty)$。
""")

q(2024, 3, ["根轨迹 / 常规根轨迹绘制", "时域分析 / 稳态误差 / 静态误差系数"], r"""
单位负反馈条件下，开环传递函数
$$G(s)=\frac{K^*}{s(s+5)(s+12)}$$

1. 绘制 $K^*:0\to+\infty$ 变化时的根轨迹，给出必要步骤；

2. 系统稳定时，开环增益 $K$ 的范围；

3. 是否存在 $K^*$，使得静态速度误差系数 $K_v\ge20$。
""", r"""
1. 极点 $0,-5,-12$，实轴根轨迹 $(-\infty,-12)\cup(-5,0)$；渐近线 $\sigma_a=-\dfrac{17}3\approx-5.67$，$\varphi_a=\dfrac\pi3,\pi,\dfrac{5\pi}3$；分离点 $d=\dfrac{-17+\sqrt{109}}3\approx-2.19$；$K^*=1020$ 时与虚轴交于 $\pm j2\sqrt{15}\approx\pm j7.75$。

2. $0<K^*<1020$，即开环增益 $0<K<17$。

3. $K_v=\dfrac{K^*}{60}\ge20\Rightarrow K^*\ge1200>1020$，系统不稳定，**不存在**。
""", r"""
分离点：$3s^2+34s+60=0$。劳斯表 $s^1$ 行 $\dfrac{1020-K^*}{17}$，辅助方程 $17s^2+1020=0$。

开环增益 $K=\dfrac{K^*}{5\times12}=\dfrac{K^*}{60}$。
""")

q(2024, 4, ["非线性系统 / 描述函数法 / 自振分析"], r"""
非线性系统框图如下图所示，其中 $N(A)=\dfrac{4M}{\pi A}$，$M=1$。

[[fig:1]]

1. 绘制负倒描述函数 $-\dfrac1{N(A)}$ 与 $G(j\omega)$ 的奈奎斯特图像；

2. 判断系统是否会产生自振；

3. 若自振，求 $c(t)$ 的振幅和频率。
""", r"""
1. $-\dfrac1{N(A)}=-\dfrac{\pi A}{4}$，沿负实轴由 $0$ 到 $-\infty$；等效线性部分 $G(s)=\dfrac1{s(s+1)(s+2)}$，与负实轴交于 $\omega_g=\sqrt2$，$G(j\omega_g)=-\dfrac16$。

2. 交点 $A=\dfrac2{3\pi}\approx0.2122$，为**稳定自振**。

3. $c(t)$ 振幅 $A_c\approx0.52$，频率 $\omega=\sqrt2\,\mathrm{rad/s}$。
""", r"""
$\angle G(j\omega)=-90^\circ-\arctan\omega-\arctan\dfrac\omega2=-180^\circ\Rightarrow\omega_g=\sqrt2$。

$x(t)$ 振幅为 $A$；由 $X(s)=-G_1(s)C(s)$，$G_1(s)=\dfrac1{s+2}$，得 $A_c=\dfrac{A}{|G_1(j\sqrt2)|}\approx0.52$。
""")

q(2024, 5, ["校正 / 由校正后特性求校正装置", "频域分析 / 三频段理论", "频域分析 / 截止频率与相角裕度"], r"""
单位负反馈条件下开环传递函数
$$G(s)=\frac{12}{(s+1)(s+3)(s+0.4)}$$
校正后系统的对数幅频特性曲线如下图所示。

[[fig:1]]

1. 写出 $G_c(s)$，并画出 $G_c(s)$ 的对数幅频特性图；

2. 利用三频段理论分析系统校正前与校正后各频段性能；

3. 试求校正前与校正后，系统的相角裕量与截止频率。
""", r"""
1. 校正后 $G(s)G_c(s)=\dfrac{10\sqrt{10}\left(\frac s2+1\right)}{s\left(\frac s{0.4}+1\right)\left(\frac s{10}+1\right)\left(\frac s{20}+1\right)}$，
$G_c(s)=\dfrac{\sqrt{10}\left(\frac s2+1\right)(s+1)\left(\frac s3+1\right)}{s\left(\frac s{10}+1\right)\left(\frac s{20}+1\right)}$。

2. 低频段抬高并增加一个积分（型别 +1），稳态误差减小；中频段以 $-20\,\mathrm{dB/dec}$ 穿越 0 dB，动态性能改善；高频段被抬高，抗高频干扰能力下降。

3. 校正前 $\omega_c\approx2$，$\gamma\approx4.19^\circ$；校正后 $\omega_c=2\sqrt{10}\approx6.32$，$\gamma\approx26.21^\circ$。
""", r"""
校正后低频段以 $-20\,\mathrm{dB/dec}$ 过 $(0.1,50\,\mathrm{dB})$，$20\lg\left|\dfrac K{0.1}\right|=50\Rightarrow K=10\sqrt{10}$。

校正前 $G(s)=\dfrac{10}{(s+1)\left(\frac s3+1\right)\left(\frac s{0.4}+1\right)}$，$G_c=\dfrac{G G_c}{G}$。

校正前 $1<\omega_c<3$：$\dfrac{10}{\frac{\omega_c}{0.4}\omega_c}=1\Rightarrow\omega_c=2$。
""")

q(2024, 6, ["离散系统 / 脉冲传递函数", "离散系统 / 稳定性（朱利判据）", "离散系统 / 稳态误差"], r"""
离散系统控制框图如下图所示，采样时间 $T=1$ 秒，试求：

[[fig:1]]

1. 闭环脉冲传递函数；

2. 判断闭环系统稳定性；

3. 单位阶跃输入作用下，系统的稳态误差。
""", r"""
1. $G(z)=\dfrac{(2z-1)(1-e^{-1})}{z^2-(1+e^{-1})z+e^{-1}}$，
$\dfrac{C(z)}{R(z)}=\dfrac{(2z-1)(1-e^{-1})}{z^2+(1-3e^{-1})z+(2e^{-1}-1)}\approx\dfrac{0.632(2z-1)}{z^2-0.104z-0.264}$。

2. $D(1)=1-e^{-1}>0$，$D(-1)=5e^{-1}-1>0$，$|2e^{-1}-1|<1$，闭环**稳定**（根 $0.568,\ -0.465$）。

3. $e_{ss}(\infty)=0$。
""", r"""
$\mathcal Z\!\left[1+\dfrac1s\right]=\dfrac{2z-1}{z-1}$，$\mathcal Z\!\left[\dfrac{1-e^{-Ts}}{s}\cdot\dfrac1{s+1}\right]=\dfrac{1-e^{-T}}{z-e^{-T}}$，两者相乘。

$e_{ss}=\lim_{z\to1}(z-1)\left[1-\Phi(z)\right]\dfrac{z}{z-1}=1-\dfrac{1-e^{-1}}{1-e^{-1}}=0$。
""")

q(2024, 7, ["状态空间 / 状态转移矩阵", "状态空间 / 能控性与能观性", "状态空间 / 李雅普诺夫稳定性"], r"""
状态空间表达式为
$$\begin{cases}\dot x=\begin{bmatrix}0&1\\-2&-3\end{bmatrix}x+\begin{bmatrix}0\\1\end{bmatrix}u\\[4pt] y=\begin{bmatrix}1&a\end{bmatrix}x\end{cases}$$

1. 试求状态转移矩阵 $\phi(t)$，以及传递函数 $G(s)$；

2. $a$ 为何值时，系统完全可测；

3. 试用李雅普诺夫第二法判断系统稳定性。
""", r"""
1. $\Phi(t)=\begin{bmatrix}2e^{-t}-e^{-2t}&e^{-t}-e^{-2t}\\-2e^{-t}+2e^{-2t}&-e^{-t}+2e^{-2t}\end{bmatrix}$，$G(s)=\dfrac{as+1}{s^2+3s+2}$。

2. $Q_o=\begin{bmatrix}1&a\\-2a&1-3a\end{bmatrix}$，$|Q_o|=2a^2-3a+1\ne0$，即 $a\ne1$ 且 $a\ne\dfrac12$ 时完全能观（源答案此处未写出结论，按判别阵补全）。

3. 解 $A^TP+PA=-I$ 得 $P=\begin{bmatrix}\frac54&\frac14\\\frac14&\frac14\end{bmatrix}$ 正定，系统在原点**大范围渐近稳定**。
""", r"""
$(sI-A)^{-1}=\dfrac{1}{s^2+3s+2}\begin{bmatrix}s+3&1\\-2&s\end{bmatrix}$，部分分式后逐项反变换。

$P_1=\dfrac54>0$，$|P|=\dfrac{5}{16}-\dfrac1{16}=\dfrac14>0$；$V(x)=\dfrac54x_1^2+\dfrac12x_1x_2+\dfrac14x_2^2$，$\dot V=-x_1^2-x_2^2$ 负定，且 $\|x\|\to\infty$ 时 $V\to\infty$。
""")

q(2024, 8, ["状态空间 / 建立状态空间表达式", "状态空间 / 状态反馈极点配置"], r"""
控制系统框图如下图所示。

[[fig:1]]

1. 求状态空间表达式；

2. 是否存在状态反馈 $K$ 使极点配置在 $-1\pm j\sqrt2,\ -5$。
""", r"""
1. $\dot x=\begin{bmatrix}0&1&0\\0&-2&1\\-1&0&-1\end{bmatrix}x+\begin{bmatrix}0\\0\\1\end{bmatrix}r$，$y=\begin{bmatrix}1&0&0\end{bmatrix}x$。

2. $\operatorname{rank}Q_c=3$，完全能控，**存在**：$K=\begin{bmatrix}14&3&4\end{bmatrix}$。
""", r"""
由框图：$\dot x_3=-x_1-x_3+r$，$\dot x_2=x_3-2x_2$，$\dot x_1=x_2$，$y=x_1$。

$Q_c=[B\ AB\ A^2B]=\begin{bmatrix}0&0&1\\0&1&-3\\1&-1&1\end{bmatrix}$。

$|\lambda I-A+BK|=\lambda^3+(3+k_3)\lambda^2+(2+k_2+2k_3)\lambda+(1+k_1)$，期望 $(\lambda+5)(\lambda^2+2\lambda+3)=\lambda^3+7\lambda^2+13\lambda+15$。
""")

# ───────────────────────── 2025 ─────────────────────────
q(2025, 1, ["建模 / 电路网络 / 运放电路传递函数", "状态空间 / 建立状态空间表达式"], r"""
已知某运算放大电路如图 1 所示（17 分）

[[fig:1]]

1. 求运算放大器电路的传递函数；

2. 求以电流 $i_L$ 和电容电压 $u_c$ 为状态变量的状态空间表达式。
""", r"""
1. $\dfrac{U_o(s)}{U_i(s)}=\dfrac{-RLCs^2+Ls+R}{RLCs^2+(L+R^2C)s+R}$。

2. 取 $x_1=u_C$，$x_2=-i_L$：$\dot x=\begin{bmatrix}-\frac1{RC}&0\\-\frac1L&-\frac RL\end{bmatrix}x+\begin{bmatrix}\frac1{RC}\\\frac1L\end{bmatrix}u_i$，$u_o=\begin{bmatrix}2&R\end{bmatrix}x-u_i$。
""", r"""
虚短虚断 $U_A=U_B=U_C$。B 端：$\dfrac{U_i-U_C}{R}=C\dfrac{du_C}{dt}$；A 端：$\dfrac{U_i-U_C}{R}=i_L+\dfrac{U_C-U_o}{R}$；电感：$u_C=u_o+L\dfrac{di_L}{dt}$。

拉氏变换后消去 $U_C$、$I_L$ 得传递函数；时域方程整理即得状态方程。
""", score=17)

q(2025, 2, ["时域分析 / 信号流图与梅森公式", "时域分析 / 二阶系统性能指标", "时域分析 / 稳态误差"], r"""
如图所示控制系统。

[[fig:1]]

（1）求 $\dfrac{E(s)}{R(s)}$，$\dfrac{C(s)}{R(s)}$；

（2）$\omega_n=2$，在单位阶跃信号作用下 $e_{ss}=0.5$，求 $k$ 和 $T_d$；

（3）在第二问的条件下求 $t_s$ 和 $\sigma\%$。
""", r"""
1. $\dfrac{C(s)}{R(s)}=\dfrac{KT_d}{s^2+(2+KT_d+T_d)s+T_d+KT_d}$，$\dfrac{E(s)}{R(s)}=\dfrac{s^2+(T_d+2)s+T_d}{s^2+(2+KT_d+T_d)s+T_d+KT_d}$。

2. $e_{ss}=\dfrac1{1+K}=0.5\Rightarrow K=1$；$2T_d=\omega_n^2=4\Rightarrow T_d=2$（$\zeta=1.5$，过阻尼）。

3. $D(s)=s^2+6s+4$，极点 $-3\pm\sqrt5$；$s_1=-3+\sqrt5$ 为主导极点，$t_s=3T=\dfrac{3(3+\sqrt5)}4\approx3.93\,\mathrm s$，$\sigma\%=0$。
""", r"""
三条回路 $L_1=-K\dfrac{T_d}{s}$，$L_2=-\dfrac{T_d}{s}$，$L_3=-\dfrac1{s+1}$ 两两接触，$\Delta=1+K\dfrac{T_d}s+\dfrac{T_d}s+\dfrac1{s+1}$。

$\left|\dfrac{s_1}{s_2}\right|=\dfrac{3-\sqrt5}{3+\sqrt5}<0.2$，可按一阶系统近似，$T=\dfrac1{3-\sqrt5}$。
""")

q(2025, 3, ["根轨迹 / 参数根轨迹与圆", "根轨迹 / 常规根轨迹绘制"], r"""
单位负反馈控制系统的闭环特征方程（18 分）
$$D(s)=K(s+4)+s(s+2)=0$$

1. 试绘制 $K$ 从 $0\to\infty$ 变化的根轨迹图（要有简略的步骤）；

2. 确定系统稳定时的 $K$ 的取值范围；

3. 已知闭环极点 $s=-4.1$，求 $K$ 值。
""", r"""
1. 等效开环 $G_{eq}(s)=\dfrac{K(s+4)}{s(s+2)}$；实轴根轨迹 $(-\infty,-4]\cup[-2,0]$；分离/会合点 $-4\pm2\sqrt2$；复平面部分是以 $(-4,0)$ 为圆心、$2\sqrt2$ 为半径的圆；与虚轴无交点（$K>0$）。

2. $K>0$ 时系统稳定。

3. $K=86.1$。
""", r"""
分离点：$M'(s)N(s)-M(s)N'(s)=0\Rightarrow s^2+8s+8=0\Rightarrow s=-4\pm2\sqrt2$。

设 $s=\alpha\pm\beta j$，由韦达定理 $2\alpha=-(K+2)$，$\alpha^2+\beta^2=4K$，消去 $K$ 得 $(\alpha+4)^2+\beta^2=8$。

代入 $s=-4.1$：$D(-4.1)=-0.1K+(-4.1)(-2.1)=-0.1K+8.61=0\Rightarrow K=86.1$。
""", score=18)

q(2025, 4, ["校正 / 串联超前校正", "频域分析 / Bode 图绘制", "频域分析 / 截止频率与相角裕度"], r"""
单位负反馈开环传递函数（20 分）
$$G(s)H(s)=\frac{K}{s(s+2)(s+100)}$$

1. 静态速度误差系数 $K_v=18$，绘制对数频率特性曲线并计算开环截止频率 $\omega_c$、相角裕量 $\gamma$；

2. 在满足以上控制精度的条件下要求相角裕量 $\gamma=45^\circ$，求串联校正网络 $G_c(s)$。

（参考数据：$\arctan3\approx71.57^\circ$，$\arctan0.06\approx0^\circ$，$\sin37^\circ\approx0.6$）
""", r"""
1. $K_v=\dfrac K{200}=18\Rightarrow K=3600$；$\omega_c=6\,\mathrm{rad/s}$，$\gamma\approx15^\circ$。

2. 超前校正：$\varphi_m=45^\circ-15^\circ+7^\circ=37^\circ$，$a=\dfrac{1+\sin\varphi_m}{1-\sin\varphi_m}=4$，$\omega_c'=6\sqrt2\,\mathrm{rad/s}$，$T=\dfrac1{\omega_c'\sqrt a}=0.06$；
$G_c(s)=\dfrac{0.24s+1}{0.06s+1}$，校验 $\gamma\approx45^\circ$。
""", r"""
$\omega_c\in(2,100)$：$\dfrac{18}{\omega_c\cdot\frac{\omega_c}{2}}=1\Rightarrow\omega_c=6$；$\gamma=180^\circ-90^\circ-\arctan3-\arctan0.06\approx15^\circ$。

新截止频率满足 $-20\lg|G(j\omega_c')|=10\lg a$，即 $\left(\dfrac{\omega_c'}{6}\right)^2=4$。
""", score=20)

q(2025, 5, ["离散系统 / 脉冲传递函数", "离散系统 / 稳定性（朱利判据）", "离散系统 / 稳态误差"], r"""
离散控制系统如图所示，其中采样周期 $T=0.1\,\mathrm s$（20 分）

1. 求系统的闭环脉冲传递函数；

2. 分析闭环系统的稳定性；

3. 当 $r(t)=1(t)$ 时计算系统的稳态误差。

其中 $e^{-T}=e^{-0.1}=0.905$，$\dfrac1s\leftrightarrow1(t)\leftrightarrow\dfrac{z}{z-1}$，$\dfrac1{s+a}\leftrightarrow e^{-at}\leftrightarrow\dfrac{z}{z-e^{-aT}}$，$\dfrac1{s^2}\leftrightarrow\dfrac{zT}{(z-1)^2}$。

[[fig:1]]
""", r"""
1. $G(z)=\dfrac{K\left[(e^{-0.1}-0.9)z+(1-1.1e^{-0.1})\right]}{(z-1)(z-e^{-0.1})}$，$\Phi(z)=\dfrac{G(z)}{1+G(z)}$，特征方程 $D(z)=z^2+(0.005K-1.905)z+0.0045K+0.905=0$。

2. 朱利判据：$D(1)=0.0095K>0$，$D(-1)=3.81-0.0005K>0$，$|0.0045K+0.905|<1$，综合得 $0<K<21.11$ 时稳定。

3. I 型系统，单位阶跃稳态误差 $e_{ss}=0$（在稳定范围内）。
""", r"""
$G(z)=K\dfrac{z-1}{z}\mathcal Z\!\left[\dfrac1{s^2}-\dfrac1s+\dfrac1{s+1}\right]$，留数法得部分分式系数 $A=1,\ B=-1,\ C=1$。
""", score=20)

q(2025, 6, ["非线性系统 / 描述函数法 / 自振分析"], r"""
如图所示非线性控制系统，非线性系统描述函数 $N(A)=\dfrac{A+3}{A+1}$，其中 $A>0$（20 分）

[[fig:1]]

1. 求该系统稳定、不稳定、自振运动时，参数 $K$ 的取值范围；

2. 发生自振运动时，绘制 $G(j\omega)$ 与 $-1/N(A)$ 图像，画在一张图中；

3. 计算发生自振时系统输出信号的振幅和频率。
""", r"""
1. $-\dfrac1{N(A)}=-\dfrac{A+1}{A+3}$ 由 $-\dfrac13$（$A\to0$）到 $-1$（$A\to\infty$）；$G(j\omega_x)=-\dfrac K6$，$\omega_x=\sqrt2$。
$0<K<2$ 稳定；$2<K<6$ 产生稳定自振；$K>6$ 不稳定。（源答案此处误印为 “$\pi<K<6$”，按推导应为 $2<K<6$。）

2. 见原图解析中的 $G(j\omega)$ 与 $-1/N(A)$ 曲线。

3. 振幅 $A=\dfrac{3K-6}{6-K}$，频率 $\omega=\sqrt2\,\mathrm{rad/s}$。
""", r"""
线性部分 $G(j\omega)=\dfrac{0.5K}{j\omega(1+j\omega)(1+j0.5\omega)}$，$\varphi(\omega_x)=-180^\circ\Rightarrow\omega_x=\dfrac1{\sqrt{T_1T_2}}=\sqrt2$，$G(j\omega_x)=-\dfrac{K'T_1T_2}{T_1+T_2}=-\dfrac K6$。

令 $N(A)=-\dfrac1{G(j\omega_x)}$：$\dfrac{A+3}{A+1}=\dfrac6K\Rightarrow A=\dfrac{3K-6}{6-K}$。
""", score=20)

q(2025, 7, ["状态空间 / 传递函数矩阵", "状态空间 / 能控性与能观性", "状态空间 / 能控/能观标准型"], r"""
已知系统状态空间表达式（18 分）
$$\dot x=\begin{bmatrix}1&2&3\\0&1&1\\0&1&1\end{bmatrix}x+\begin{bmatrix}0\\0\\1\end{bmatrix}u,\quad y=\begin{bmatrix}1&0&0\end{bmatrix}x$$

1. 求传递函数；

2. 判断能控能观；

3. 求可控标准型，可观标准型。
""", r"""
1. $G(s)=\dfrac{3s-1}{s(s-1)(s-2)}=\dfrac{3s-1}{s^3-3s^2+2s}$。

2. $Q_c=\begin{bmatrix}0&3&8\\0&1&2\\1&1&2\end{bmatrix}$，$\det Q_c=-2$，**完全能控**；$Q_o=\begin{bmatrix}1&0&0\\1&2&3\\1&7&8\end{bmatrix}$，$\det Q_o=-5$，**完全能观**。

3. 能控标准型：$\dot x=\begin{bmatrix}0&1&0\\0&0&1\\0&-2&3\end{bmatrix}x+\begin{bmatrix}0\\0\\1\end{bmatrix}u$，$y=\begin{bmatrix}-1&3&0\end{bmatrix}x$；
能观标准型：$\dot x=\begin{bmatrix}0&0&0\\1&0&-2\\0&1&3\end{bmatrix}x+\begin{bmatrix}-1\\3\\0\end{bmatrix}u$，$y=\begin{bmatrix}0&0&1\end{bmatrix}x$。
""", r"""
$|sI-A|=(s-1)\left[(s-1)^2-1\right]=s(s-1)(s-2)$；只需 $(sI-A)^*$ 第 1 行第 3 列元素 $3s-1$。

由传递函数系数 $a_0=0,\ a_1=2,\ a_2=-3$，$b_0=-1,\ b_1=3,\ b_2=0$ 直接写出两种标准型。
""", score=18)

q(2025, 8, ["状态空间 / 状态反馈极点配置"], r"""
已知系统的状态方程为（17 分）
$$\dot x=\begin{bmatrix}0&1&0\\0&0&1\\-1&-2&-3\end{bmatrix}x+\begin{bmatrix}0\\0\\1\end{bmatrix}u$$

1. 说明上述系统是否可以用状态反馈任意配置闭环极点；

2. 设计状态反馈矩阵 $K$ 使极点位于 $-3$，$-1+j$，$-1-j$。
""", r"""
1. 系统为能控标准型，一定完全能控，**可以**任意配置闭环极点。

2. $K=\begin{bmatrix}5&6&2\end{bmatrix}$（$u=-Kx+v$）。
""", r"""
$f(s)=\det(sI-A+bK)=s^3+(3+k_3)s^2+(2+k_2)s+1+k_1$。

期望 $f^*(s)=(s+3)(s+1+j)(s+1-j)=s^3+5s^2+8s+6$，比较系数得 $k_3=2,\ k_2=6,\ k_1=5$。
""", score=17)


# 勘误（独立核对）。errataLevel: 'severe' / 'conflict' / 'ok'；省略则为普通勘误。
ERRATA = {
(2023, 1): (None, r"""微分方程与 $\Phi(s)$ 正确。源答案状态矩阵 $A_{12}$ 写成了 $0$，且 $B$、$C$ 与 $1/m$ 的安置不一致；正确为 $A=\begin{bmatrix}0&1\\-k/m&-f/m\end{bmatrix}$，$B=\begin{bmatrix}0\\1/m\end{bmatrix}$，$C=\begin{bmatrix}1&0\end{bmatrix}$。第 3 问不能照抄。网站文本已把 $A_{12}$ 改为 $1$，但仍把 $1/m$ 放在 $C$ 而非 $B$。"""),
(2023, 2): ('severe', r"""题干亦有矛盾：无阻尼振荡频率 $\omega_n=2$、图中 $1.2s+1$ 与 $e_{ss}=0.4$ 三者不能同时成立（若 $\omega_n=2$ 则 $k_a=3.8$，此时 $e_{ss}\neq 0.4$ 且 $\zeta>1$）。源答案未使用 $\omega_n=2$。

另，系统为 0 型，$e_{ss}=k_a/(1+k_a)$，源答案写成 $e_{ss}=1/K_p=k_a=0.4$，因而 $k_a$、$\zeta$、$\sigma\%$、$t_s$ 及 $G_c=s+0.4$ 均不可照抄。按 $e_{ss}=0.4$ 与结构图（忽略矛盾的 $\omega_n=2$）：$k_a=2/3$，$\omega_n=\sqrt{25/18}\approx 1.179$，$\zeta\approx 0.636$，$\sigma\%\approx 7.49\%$，$t_s(5\%)\approx 4.667\,\mathrm{s}$，全补偿 $G_c(s)=s+2/3$。"""),
(2023, 3): (None, r"""根轨迹、稳定性、$s=-9$ 时 $K=75.6$ 与另两极点均对。求 $e_{ss}$ 时用错开环传函，源答案 $K_v=2.864$、$e_{ss}=1.05$ 不能照抄。正确为 $K_v=10.08=252/25$，$e_{ss}=3/K_v=25/84\approx 0.298$。"""),
(2023, 4): ('ok', r"""已核对：正确。拆大放小得 $\omega_C=12.5$、$\gamma\approx 103.35^\circ$ 与考场算法一致；精确值为 $\omega_C\approx 8.20\,\mathrm{rad/s}$，$\gamma\approx 114.49^\circ$。"""),
(2023, 5): (None, r"""题图采样周期为 $\tau$ 且未给数值，源答案默认 $T=1$。该假定下 $\Phi(z)$ 与 $0<k<5.82$ 正确，但 $G(z)$ 分子曾写为 $0.26375$（应为 $0.28375$），特征式出现 $-11.135$ 笔误。$c(2)$ 漏了 $0.2975\,r(0)$，$c(3)$ 把 $-0.21625$ 写成了 $+0.21625$。第 4 问不能直接照抄。网站文本已注明按 $T=1$。"""),
(2023, 6): ('ok', r"""已核对：正确。等效为死区 $h=0.5$、幅值 $M=2$ 的继电器；$k=10$ 时 $\omega=1$、$A\approx 12.723$；不自振范围为 $0<k<\pi/4$。"""),
(2023, 7): ('ok', r"""已核对：正确。$e^{At}$、$G(s)=1/(s+2)$、完全能控、不完全能观均对。"""),
(2023, 8): (None, r"""特征根、能控性、$k=[-13\ \ 10]$ 全部正确。开环特征方程被写成 $-\lambda^2-6\lambda+17=0$（少了正的 $\lambda^2$），随后的根是按正确方程 $\lambda^2-6\lambda+17=0$ 解的。"""),
(2024, 1): (None, r"""总传递函数表达式与 $R_1$、$R_2$ 正确；合并两级时左侧误写成 $U_x/U_r$，右式其实是 $U_y/U_r$。"""),
(2024, 2): (None, r"""超调、$\zeta$、$\omega_n$、闭环与稳态值正确（存在常规四舍五入）。第 3 问叙述中有一处把 $2.465s$ 写成了 $2.645s$，劳斯表仍用 $2.465$，属笔误。"""),
(2024, 3): ('ok', r"""已核对：正确。稳定范围 $0<K^*<1020$（开环增益 $0<K<17$）；不存在同时满足 $K_v\ge 20$ 的稳定 $K^*$。"""),
(2024, 4): ('ok', r"""已核对：正确。稳定自振振幅 $A=2/(3\pi)\approx 0.2122$，输出振幅 $A_c\approx 0.52$，频率 $\omega=\sqrt{2}$。"""),
(2024, 5): (None, r"""校正前后 $\omega_c$、$\gamma$ 的数值（渐近 $\omega_c=2$、$\gamma\approx 4.185^\circ$；校正后 $\omega_c=2\sqrt{10}$、$\gamma\approx 26.21^\circ$）按正确公式在渐近截止频率处计算，可以照抄。相位公式书写有误（符号写反），属笔误而非算错。补充精确值（对照用，不是对折线法的否定）：校正前 $\omega_c\approx 1.709$、$\gamma\approx 13.84^\circ$；校正后 $\omega_c\approx 5.620$、$\gamma\approx 29.45^\circ$。"""),
(2024, 6): ('ok', r"""已核对：正确。$G(z)$、闭环、朱利稳定与单位阶跃 $e_{ss}=0$ 均对。"""),
(2024, 7): (None, r"""$\Phi(t)$、$G(s)$ 与李雅普诺夫结论正确。源答案列出能观判别阵后未解出 $a\neq 1$ 且 $a\neq 1/2$；网站文本已按判别阵补全。随后把 $P$ 的元素写成 $a,b,c,d$，与输出参数 $a$ 混用。"""),
(2024, 8): ('ok', r"""已核对：正确。"""),
(2025, 1): (None, r"""传递函数与状态方程矩阵正确。源答案把 $x_2=i_L$ 写成了 $x_2=-i_L$，与所写矩阵及题面不符；改成 $x_2=i_L$ 即可。中间 $du_i$、$1+RC$ 等笔误未传入终式。"""),
(2025, 2): ('severe', r"""梅森公式把 $K/s$ 当成 $K$，漏掉一个积分，把三阶系统写成二阶，所得 $C/R$、$E/R$ 及 $K=1$、$T_d=2$、$t_s\approx 3.93$ 均不可照抄。正确为 $\dfrac{U}{R}=\dfrac{KT_d}{s^2+T_d s+KT_d}$，$\dfrac{E}{R}=\dfrac{s(s+T_d)}{s^2+T_d s+KT_d}$，$\dfrac{C}{R}=\dfrac{KT_d}{(s+2)(s^2+T_d s+KT_d)}$。按正确结构，输出误差稳态恒为 $1/2$，与 $K$、$T_d$ 无关，题给 $e_{ss}=0.5$ 不能用来定 $K$；$\omega_n=2$ 对三阶系统也没有唯一含义。"""),
(2025, 3): ('ok', r"""已核对：正确。等效开环、根轨迹（圆）、稳定性及 $s=-4.1$ 时 $K=86.1$ 均对。"""),
(2025, 4): (None, r"""$G_c(s)=\dfrac{0.24s+1}{0.06s+1}$ 与 $\gamma\approx 45^\circ$ 的校验正确，可以照抄。中间式写成 $(\omega_c^{\prime 2}/6^2)=4\Rightarrow\omega_c'=6\sqrt{2}$，前半与后半矛盾（应为 $(\omega_c'/6)^2=2$）。校正前渐近 $\omega_c=6$、$\gamma\approx 15^\circ$；精确值为 $\omega_c\approx 5.830$、$\gamma\approx 15.60^\circ$。"""),
(2025, 5): (None, r"""开环 $G(z)$、朱利范围 $0<K<21.11$ 与 $e_{ss}=0$ 正确。闭环 $\Phi(z)$ 分子中 $z$ 与后一项之间漏写加号，特征多项式仍按正确 $G(z)$ 展开。"""),
(2025, 6): (None, r"""源答案第 1 问把稳定自振范围误印为 $\pi<K<6$，应为 $2<K<6$（网站文本已注明）。另有一条与本题无关的幅频式 $A(\omega)=15/\cdots$，后文未使用。第 3 问振幅 $A=(3K-6)/(6-K)$、频率 $\omega=\sqrt{2}$ 正确。"""),
(2025, 7): (None, r"""$G(s)$、能控能观与两种标准型均正确。源答案把 $sI-A$ 的 $(2,3)$ 元写成了 $+1$，应为 $-1$；行列式和伴随矩阵用的是正确的 $-1$，终式未受影响。"""),
(2025, 8): ('ok', r"""已核对：正确。$K=\begin{bmatrix}5&6&2\end{bmatrix}$，闭环极点为 $-3$、$-1\pm j$。"""),
}
for d in Q:
    item = ERRATA.get((d['year'], d['no']))
    if not item:
        continue
    lv, notes = item
    d['notes'] = notes.strip()
    if lv:
        d['errataLevel'] = lv
