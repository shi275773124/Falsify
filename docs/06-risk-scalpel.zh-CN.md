# 06. 风险裁刀（第 3 层）

[English](./06-risk-scalpel.md) · [返回 README](../README.zh-CN.md)

**这是第 3 层。**[第 1 层 · 互审](./03-collaboration.zh-CN.md)抓事实错。[第 2 层 · 对抗审议](./05-adversarial-review.zh-CN.md)抓结论错。**风险裁刀抓的是好审计之后的失败：把每个 finding 都升成 P0，或者打着“极简”的名义删掉真实风险。**

Falsify 负责找出哪里会错。风险裁刀负责决定现在必须改什么。

---

## 问题

一次强对抗审可能产出十个有效 finding。之后常见两种坏结果：

1. **补丁膨胀** —— 每个 finding 都变成紧急项，v1 永远 ship 不出去。
2. **假极简** —— 团队说“砍 scope”，实际把真实风险也悄悄删了。

风险裁刀是 review findings 和 implementation work 之间的裁决层。

它不删除风险事实。它只判断这个风险是否阻断当前交付。

---

## 一句话规则

```text
对抗审产出 failure modes。
风险裁刀切 scope，不切风险事实。
```

每个 finding 先改写成：

```text
Finding:
Failure mode if unfixed:
Current phase/objective:
```

然后只能进入一个桶。

---

## 三个桶

| Class | 不修会导致什么 | 必须输出 | 禁止 |
|---|---|---|---|
| **Must Fix** | 假真相、假风险、silent failure、未授权 action、不可复算、或当前阶段无法验收 | 最小修复 + 验收证据 | “以后优化” |
| **Known Debt** | 真实风险，但不阻断当前阶段 | debt note + 升级触发条件 | 模糊 TODO |
| **Delete** | 没有当前具体 failure mode，只是完整性、通用抽象、更好看、dashboard 欲望、平台化 | 删除理由 | 改名塞回 backlog |

---

## Must-Fix 闸门

如果不修会让当前交付里的这些东西变假或不安全，就是 **Must Fix**：

1. **Truth** —— 报告可能发布假的数字、事实或结论。
2. **Risk** —— 系统可能低估 exposure、权限、blast radius 或安全状态。
3. **Silence** —— 缺失、过期、坏掉的数据看起来像成功。
4. **Action boundary** —— 文案或代码可能暗示或触发未授权 action。
5. **Reproducibility** —— 之后无法复原数字、来源、单位、符号或决策路径。
6. **Verification** —— 当前阶段不修就无法测试或审查。

这些都不满足，就不自动紧急。

---

## Known Debt 必须有触发条件

Known Debt 不是垃圾桶。它必须说明什么时候升级成紧急项。

```text
Known Debt: <issue>
Why not blocking now: <current phase does not depend on it>
Upgrade trigger: becomes Must Fix when <specific event/scale/use-case happens>
```

例子：

- **完整机器可读 schema** → 现在是 debt；当报告被 CI、dashboard 或其他程序消费时升级 Must Fix。
- **高级归因** → 现在是 debt；当归因被用于停止、调仓、批准或扩张某个决策时升级 Must Fix。
- **通用 adapter/framework** → 现在是 debt；当两个真实实现需要同一个标准接口时升级 Must Fix。

没有升级触发条件，就不是合格 debt。要么 Must Fix，要么 Delete。

---


## GLOSSOPETRAE / 审计通道 findings

像处理其他 finding 一样裁剪这些问题——不要让新词变成补丁膨胀。

**Must Fix**：当前决策依赖以下情况时：

- 用 AI summary 代替 raw artifact / 可读 diff / fixture / 命令输出；
- 语义 verdict 诱导在没有证据的情况下改变决策；
- LLM probe 没有 raw verdict、parse status、HTTP status、finish reason 或 usage 却被打分；
- 没有 reproducer/probe 就声称“没有 hidden channel”。

**Known Debt**：

- Layer-2 / semantic-channel 风险真实存在，但当前阶段只是 read-only，不授权 action；
- 没跑 reproducer，但报告也没有声称 channel 不存在；
- known-pattern library 不完整，升级触发条件可以写成：“当本报告开始 gate CI、生产、资金、账号权力或公开发布时，升级为 Must Fix”。

**Delete**：

- 只是理论 channel，没有当前具体失败模式；
- 给未证明会 strip/preserve 相关 carrier 的模型/路径加 sanitizer；
- 没有证据就说“same vendor”或“different vendor”天然安全/不安全。

---
## 输出模板

```markdown
## Verdict
PASS / PASS_WITH_DEBT / BLOCK

## Cut-line table
| Finding | Failure mode if unfixed | Class | Minimal action | Upgrade trigger |
|---|---|---|---|---|

## Must Fix now
- ...

## Known Debt
- ... — Upgrade when ...

## Delete
- ... — reason

## One-line rule
...
```

---

## 微型例子

对抗审发现：

```text
The proposed system has no full JSON schema.
```

风险裁刀先改写：

```text
Finding: no full JSON schema.
Failure mode if unfixed: downstream tools may misread fields once reports are machine-consumed.
Current phase/objective: human-reviewed v0 report.
```

裁决：

```text
Known Debt: full JSON schema.
Why not blocking now: v0 is human-read only.
Upgrade trigger: Must Fix when the report is consumed by CI, dashboards, aggregation, or another program.
```

同一个 finding，到了后面阶段：

```text
Current phase/objective: CI blocks deploys based on this report.
Class: Must Fix.
Minimal action: define field names, units, signs, missing-data policy, and schema validation.
```

---

## 反模式

- **Reviewer 接管 roadmap** —— 对抗审 finding 是攻击面，不是自动需求。
- **“极简”删除风险事实** —— 只能裁实现 scope，不能删“哪里会错”的记录。
- **没有触发条件的债** —— 这只是隐藏 backlog。
- **项目管理化** —— 风险裁刀是一张表和一个 verdict，不是 planning system。
- **Action 泄漏** —— 证据层不能悄悄变成行动建议层。

---

## 它在 Falsify 里的位置

```text
第 1 层 · 互审       → 错事实 / 错数字
第 2 层 · 对抗审议   → 对的事实，错的结论
第 3 层 · 风险裁刀   → 审计之后：Must Fix / Known Debt / Delete
```

在第 2 层之后用它；也可以在代码腐烂审查、事故复盘、或任何严肃 audit 产出太多 findings 时使用。
