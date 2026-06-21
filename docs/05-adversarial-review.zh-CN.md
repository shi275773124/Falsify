# 05. 对抗审议（第 2 层）

[English](./05-adversarial-review.md) · [返回 README](../README.zh-CN.md)

**这是第 2 层。**[第 1 层 · 互审](./03-collaboration.zh-CN.md)抓*数字错*，这一层抓*结论错*。它不取代第 1 层——是在它之上更深一层，给高风险决策用。

第 1 层互审（docs 03）拦的是**把错数字写漂亮**。它拦不住更难的一类：**事实对、结论错**——用错的工具量了对的数据，或者把局部事实当成完整结论，或者"fail-close 写个 ABORT 文件就算完成"。

这个变体在 v1 之上加四样东西。它更重,用在高风险决策上——策略/方案的生死判定、生产变更、任何"一个自信的错**结论**(不只是错数字)代价很大"的场景。

---

## 1. Verdict ladder — 决策是离散的，不是模糊打分

一次审议不输出"差不多还行",只输出三选一:

- **PROCEED** — 通过,进下一步
- **HOLD-N** — 第 N 轮拒绝,列出必须修的项,循环
- **ARCHIVE** — 架构性死亡,参数怎么调都救不活

`HOLD-N` 带编号,因为审议是**多轮**的:

```
Round 1: HOLD   (2 个 kill 项 + 5 个 fix 项)
  → 作者 commit 一个修复版
Round 2: HOLD-2 (fix-1 自杀 / fix-3 表面糊弄 / fix-5 与 fix-1 互锁)
  → 作者再 commit 一个修复版
Round 3: PROCEED
```

规则:轮与轮之间不要追加辩论,而是 commit 修复版,让 reviewer **独立重新判定**。"我已经认错了"不能软化下一轮的 verdict。修复只有扛过一次全新攻击才算数。

## 2. 四道前置闸门（G1–G4）

v1 的三条规则都在问"这个事实对不对?"。这四道闸问"建立在事实上的**断言**到底有没有意义?"。任何对外断言前过一遍。

| 闸 | 防什么 | 一句话 |
|---|---|---|
| G1 实体消歧 | 把"X 的一部分变了"说成"X 死了" | 我说的 X 到底是哪个 X？ |
| G2 量纲对齐 | "−0.5%/8h"看着没事(其实约 −547%/yr) | 换成人类尺度还合理吗？ |
| G3 先验冲突=刹车 | 用户怀疑你时,你还堆证据辩护 | 用户不同意 → 减速重查,别 double down |
| G4 尺子-对象匹配 | 用稠密数据的检验去测稀疏信号 | 工具假设和数据结构匹配吗？ |

填空模板:[`templates/precondition-checklist.md`](../templates/precondition-checklist.md)。
G4 的完整案例:[`examples/wrong-tool-right-data.md`](../examples/wrong-tool-right-data.md)。

## 3. 跨模型 reviewer（不用两台机器也能独立）

不需要两台主机。**两个不同模型族 + 上下文隔离**就够独立了。reviewer 可以是对一个不同模型的一次性调用,走任意 OpenAI 兼容端点。reviewer 的 system prompt 必须写:*找漏洞,不客套,不复述对方*。

做法 + 可直接复制的调用:[`examples/cross-model-rpc.md`](../examples/cross-model-rpc.md)。

## 4. verdict-as-file + 步骤守卫

对多步 pipeline,让每一步产出**一个独立文件**,并把"步骤 verdict"当成 `文件 + 三个检查`:**存在**、**≥ 大小下限**、**不以 ABORT/ERROR 开头**。一个步骤如果"fail-close"——写个 `ABORT` 然后 exit 0——在调度器看来是成功的,下游步骤就会在缺失输入上继续跑、还自洽,直到几小时后人来问才发现。

用 [`templates/step-verify.sh`](../templates/step-verify.sh) 守每一步:fail loud(非零退出 + 告警),绝不 fail silent。

---


## 5. GLOSSOPETRAE 检查 — 审计审计通道本身

前沿模型的程序化外语 / covert channel 研究给 Falsify 的提醒是：另一个模型说“我审过了”还不够。AI 可能在一层人类和 monitor 都不可靠审计的文本/代码结构里工作。

不要新增第四层。把这些检查并入对抗审：

- **人类可审计性。** verdict 是否落到 raw artifact、可读 diff、命令、fixture、源链接等人能检查的证据？如果只依赖 AI summary，HOLD。
- **语义 verdict 诱导。** 普通语言是否在没有满足 gate 的情况下推动 reviewer 判 `PROCEED` / `Known Debt`？例如“not blocking / 证据已足够 / 另一个模型同意 / 只是理论风险 / blocker 改名 debt”。
- **Prompt-only audit theater。** 只写一句“注意 prompt injection”不是防线。优先使用已知 pattern 检查、fixture 或 reproducer。pattern library 只覆盖已知模式，不能证明 unknown channel 不存在。
- **Monitor-failure laundering。** 空响应、不可解析、截断、content-filtered、confident-"no issue" 默认都不是 clean。LLM/API probe 作为证据时，保留 raw verdict、parse status、HTTP status、`finish_reason`、token usage（如果 provider 暴露）。

Cutline 纪律：如果当前 claim 依赖缺失的证据，这是 Must Fix。如果只是 read-only 且没有声称 channel 不存在，记 Known Debt，并写升级触发条件。

---
## 什么时候用哪个

| 场景 | 用 |
|---|---|
| 事实准确性、费率表、文档审计 | v1 普通互审(docs 03) |
| 方案/策略的生死判定、生产变更 | 本变体(verdict ladder + G1–G4) |
| 多步自动化 pipeline | 再加 verdict-as-file + `step-verify.sh` |

## 待解问题

剩下的口子:**AI 反向操纵 reviewer**——用一个*表面*修复(把东西改个名而不是真修)让 reviewer 觉得"已解决"。reviewer 是不是也该把自己的断言过一遍 G1–G4?未解。

## 下一步

- [故障排查](./04-troubleshooting.zh-CN.md)
