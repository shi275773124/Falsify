# 真实案例：Sharpe 4.06 的策略在 5 轮双 AI 对抗审查后死亡

> 这是 Falsify 在量化策略上的**真实审计日志**，不是预先植入的 demo。
> 所有交易场所 / 账号 / 路径标识已脱敏；数字和时间线未做编辑。
>
> 领域：量化交易 / regime-switching 动量策略
> 时长：约 2.5 小时 wall-clock，5 轮，3 个 commit
> 结果：一份 `PAPER_CANDIDATE / SR ≈ 4.06 / PBO 0.000` 的策略，在
> 任何 live 之前被重新分类为 **NOT_VIABLE**

## TL;DR

单 AI 跑出一份 "正式 7 门审计通过" 的报告：

```
Sharpe 4.06–4.31（4 个 universe）
PBO 0.000
DSR p < 1e-7
6/7 关通过（第 7 关 intentionally False，因为是历史回测，
          live 执行无法离线证明）
```

单 AI 工作流到这里下一步就是 shadow / tiny-live。

Falsify 强制第二个 AI 反向审。5 轮后：

- 1 个作者自己漏掉的 lookahead bias
- 1 个审计员自己的归因错误（自己 catch）
- 1 个审计员对 live mechanic 的错误假设（自己拉生产 journal 后 catch）
- 1 个审计员反测脚本的实现 bug（自己 catch）
- 1 个 **fictional horizon mechanic 缺陷** —— 真正的 killer ——
  只在两个 AI 用 *不同 mechanic* 跑同一份 panel、且审计员的数字崩了
  之后才被逼出来

Sharpe 4.06 不是 alpha。是把成本摊销到了一个**策略本身从不真正持有**
的虚构持仓期。

## Round 1 — 作者的 lookahead bias

7 门审计脚本里 regime quantile 阈值是这样算的：

```python
ql = m.quantile(.33)   # 整条样本常数
qh = m.quantile(.67)
vh = v.quantile(.67)
```

day-100 在判 "今天是不是 risk_off" 时用的是 day 100→1836 的 33 分位
数。每个 regime label 都"先知"。

审计员提交修复版：rolling 252 天 quantile + `shift(1)`。

## Round 2 — 审计员自我打脸

审计员的第一个断言："lookahead 是 SR≈4 的主因。"

实际跑修复版后，4 个 universe：

```
universe A:  SR 4.06 → 3.66
universe B:  SR 4.08 → 3.96
universe C:  SR 4.31 → 4.20
universe D:  SR 3.06 → 2.67
```

SR 只掉 0.1–0.4。Lookahead 是真 bug，但 **不是主因**。审计员撤回断言。

如果不实跑这一步，错误的诊断就会被推给用户。**这是对抗审查的第一次自我
打脸**：强制审计员产出数字证据而不是论断。

## Round 3 — 审计员对 live mechanic 假设错

审计员下一个断言："live 执行器是 daily K=3 rebal，所以现实成本应该是
~5 bps/day。"

审计员去拉生产 journal：

```
journal events: 2 条（首次开仓 + 补 cap，同一 basket）
当前 plan:      verdict=MATCH, actions=[], 无 rotation
ledger:         6 天 1 次 basket flip
```

live 执行器是 **hold-until-flip**，不是 daily rebal。审计员的 mechanic
B 假设是错的。撤回。

## Round 4 — 审计员反测脚本的实现 bug

审计员重写 mechanic B 用 hold-until-flip：

```
universe A mechanic B: SR -0.28, MDD -87.5%,
                       1403 flips / 1836 days,
                       median hold = 1.0 day
```

median hold = 1.0 天，flip rate 76%。审计员根本没实现 hold-until-flip
—— daily ranking 噪声让 bottom-3 天天换，等于伪装成 daily rebal。

审计员加 `min_hold=7` 重跑。

## Round 5 — 虚构的持仓期

加了 `min_hold=7` 之后，mechanic B 仍然：

```
universe A: SR -0.22, MDD -83.7%, median hold 仍是 1.0 day
```

审计员跑了一个 regime distribution probe：

```
risk_off run-length（4 个 universe）:
  universe A:  median 1.0d, mean 1.51d, max 5d, 87% runs ≤ 2 days
  universe B:  median 1.0d, mean 1.64d, max 4d, 83% runs ≤ 2 days
  universe C:  median 1.0d, mean 1.73d, max 4d, 80% runs ≤ 2 days
  universe D:  median 1.0d, mean 1.57d, max 4d, 86% runs ≤ 2 days
```

策略设计是 `regime → switched_kill`：regime 翻转时仓位**必须立即退出**。
`min_hold=7` 完全没用，因为 regime 自己在 1–2 天内就 force-exit，
80%+ 时间都是这样。

这暴露了 **原始 mechanic A 的真正致命缺陷** —— 它用 nominal
`horizon=14` 的 overlapping-portfolio convention：

```
mechanic A 的成本摊销假设:
  cost = 9 bps / 14 days  ≈  0.64 bps/day

regime-chop 下的真实有效持仓期:
  cost = 9 bps / 1.5 days ≈  6 bps/day

成本被低估了约 9.4 倍
```

**SR 4.06 不是 alpha**。是把真实交易成本除以一个策略自身设计**从未真正
持有过**的持仓期，得到的会计幻象。

live 执行器 "6 天 1 次 flip" 的快照只是抽样到了一段稳定 risk_off 窗口。
历史上 80%+ 的时间是 1–2 天 chop，那时 live 系统会被像 mechanic B
一样砸。

## 最终 verdict

```
REJECT_DAILY_LIVE_EQUIVALENT
SWITCHED_KILL_MECHANIC_NOT_VIABLE
SR_IS_COST_OVER_AMORTIZATION_ARTIFACT
NO_LIVE / NO_CAP_INCREASE / NO_AUTO_PROMOTION
```

允许的后续方向：

1. 把 regime 分类器换成更平滑的设计（更长 rolling、加 hysteresis），
   从零重新审计。
2. 接受这个 alpha 在 daily live-equivalent 形态下不存在。
3. **不**允许用 local patch 把当前版本推进生产。

## 可发现性矩阵 —— 为什么必须双 AI

| # | Bug | 类型 | 单 AI 能 catch 吗 |
|---|---|---|---|
| 1 | Full-sample quantile lookahead | 作者盲点 | 很少 —— 作者很难自审到这种 |
| 2 | "lookahead 是主因" | 审计员超预 | 仅在强制实跑时 catch |
| 3 | live mechanic 假设错 | 跨系统盲点 | 仅在审生产 artifact 时 catch |
| 4 | min_hold 没实现 | 审计员实现 bug | 偶尔 —— 需要 sanity 字段 |
| 5 | **fictional horizon × regime chop** | **mechanic 假设穿透** | **几乎不能** |

Bug 5 是 killer。它只在以下条件凑齐时才会浮出来：

- 作者和审计员跑 *不同 mechanic* 在 *同一份 panel* 上
- 审计员的 mechanic 数字崩了
- 这逼出 regime distribution probe
- probe 揭示作者假设的 `horizon=14` 在 80% 历史里是虚构的

当作者和审计员共用一个 mechanic 假设时，PBO=0 / DSR p<1e-7 两个指标
看起来都过 —— 但它们只测假设**内部**的稳定性，不能测假设本身是否合理。
**强制审计员用不同 mechanic 是唯一能把这个问题问出来的方式**。

## 这个案例验证的 6 条 audit 纪律

任何 backtest 在升级 paper-candidate / shadow / tiny-live 前必须：

1. **lookahead 卫生**：所有 quantile / rank / threshold 必须
   rolling-only + `shift(1)`。
2. **mechanic 实证对照**：backtest 的 horizon / hold / rebalance 必须
   能从 live 执行器的真实 journal 反推匹配。
3. **regime run-length 必查**：如果策略依赖 regime 分类，必须知道每个
   regime label 的实际持续时长分布。
4. **成本摊销必须 explicit**：报告 cost-per-hold **和** cost-per-day，
   而不是只报 cost-per-hold。
5. **PBO 解释必须保守**：PBO=0 意思是 "在这个 mechanic 和这个 grid 内
   邻域稳定"，**不是** "无过拟合" 或 "live-safe"。
6. **双 AI 必须用不同 mechanic**：当两个审计员共享一个假设时，audit
   只测内部一致性，不测假设是否合理。

## 复现

这是真实运行，不是策划好的 demo。完整脱敏时间线、两份回测脚本
（mechanic A vs mechanic B）、regime-inspector 都保留在原始审计的
artifact 目录里。上面所有数字都是原文。

> 一句话：单 AI 高高兴兴出了一份 "Sharpe 4 paper-candidate"。
> 强制第二个 AI 用不同 mechanic 重审，2.5 小时内就用 5 个独立发现把
> 它判死。Killer 不是数学 bug —— 是任何单审计员都不会去质疑的
> mechanic 假设本身。
