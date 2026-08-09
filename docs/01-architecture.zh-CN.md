# 01. 架构

[English](./01-architecture.md) · [返回 README](../README.zh-CN.md)

## 产品定义（唯一真源）

**Falsify 是证据驱动的决策门。**

它尝试**推翻** AI 或人类提出的高风险声明，并基于以下要素输出**范围受限**的裁决（`PASS` / `PASS_WITH_DEBT` / `BLOCK`）：

- 明确的 **authority path**（哪个系统/状态是最终权威），
- **原始工件**（不能只靠总结），
- 明确的 **策略版本**。

多模型 / 多 Agent 审查只是**可选攻击器**，不是信任根。

> 模型可以提出指控，但不能单独制造事实。硬 `BLOCK` 应优先由确定性策略、缺证或可验证的状态冲突触发。

**当前公开 MVP 切口：** 在 GitHub 上拦截**变更周围的声明**（PR 叙事、部署计划、决策文档）——并不声称今天已能自动验完一切云端部署。

## 问题

AI 系统会用流畅文案宣称“完成”：

- CI 绿、日志齐、“另一个 AI 也看过了”
- 但目标状态从未改变
- 或证据面在指标门之前就已被污染

Code review / lint 问的是：*diff 看起来对不对？*  
Falsify 问的是：*沿权威路径，这个声明是否可辩护？*

## 门禁模式（公开核心）

一条可检查的回路：

1. **Frame（界定）** — 声明、负责人、权威路径、claim ceiling  
2. **L0 Brooks-Lint（框架审）** — 在对抗攻击之前先扫结构腐烂 / 可审计性表面（营销别名「框架审计」；协议名是 Brooks-Lint）  
3. **Attack（反查）** — 先找成本最低的反证（确定性检查优先）  
4. **Recompute / re-read（复算/回读）** — 打到真实状态、计算、命令或原始来源  
5. **Cutline（分级）** — Must Fix / Known Debt / Delete（含 L0 结构性 Must Fix）  
6. **Receipt（回执）** — 保留裁决、证据路径、策略/工具版本、freshness，以及证明 L0 已跑（或明确 SCOPE_REFUSED / 带硬顶 cap 的 skip）的 **`brooks_lint` 块**

`PASS` 不是永久有效。环境、工件、策略、freshness 或权威路径任一变化，回执应失效。承载声明的 `review` / `run` 若无 L0 证明，不得给出 `PASS` / `PASS_WITH_DEBT`。

**不是同一工具：** `falsify lint` 是 **markdown 标签/阻断器的静态检查**（L2 gate 路径），**不是** Brooks-Lint。见 [Brooks-Lint](./09-brooks-lint.md)。

## 多 Agent 审查是什么（不是什么）

本仓库历史上还记录过一种**双 Agent 协作写稿**模式（A 起草、B 审计，共享 Obsidian vault + git）。它仍可作为研究写作的**协作适配器**。

但它**不是**产品信任根：

| 角色 | 是否可信任 |
|------|------------|
| 确定性探针 + 策略 | 是 — 主路径 |
| 原始工件哈希 / 权威回读 | 是 — 主路径 |
| 第二个模型 / Agent | 仅可选攻击器 |
| “两模型很少共享同一错误” | **不主张** — 无测量口号已删除 |

若两个 Agent 共享同一错误假设，只要没打到权威路径，门禁仍应失败。

## 可选拓扑：共享 vault 协作

```
            ┌──────────────────────────────────┐
            │   GitHub 私有 repo                │
            │   = 单一事实源                    │
            └──────────────────────────────────┘
              ▲          ▲           ▲
       git push│   git push│   Obsidian Git
              │          │           │
       ┌──────┴──┐  ┌────┴────┐  ┌───┴────────┐
       │ Agent A │  │ Agent B │  │ 本机人类    │
       │ (起草)  │  │ (反查)  │  │ 阅读       │
       └─────────┘  └─────────┘  └─────────────┘
```

研究写作可以多人共写一份真相。**门禁**仍必须落到权威路径 + 工件 + 策略，而不是 Agent 共识。

## 门禁针对的失败形态

- **日志 ≠ 状态** — “部署成功”但目标未变  
- **派生新鲜度** — 今天的信号时间戳盖在过期输入上  
- **镜像漂移** — 文档/运行时不一致  
- **指标剧场** — 证据面已被塑造后再跑检验  
- **意见堆叠** — 把第二个 AI 的同意当成证据  

## 相关文档

- [Getting Started](./00-getting-started.zh-CN.md)
- [Brooks-Lint（L0 框架审）](./09-brooks-lint.md)
- [GitHub Action 安装](./14-github-action-install.md)
- [Adversarial Review](./05-adversarial-review.md)（L1 攻击层）
- [Cutline / 风险裁刀](./06-risk-scalpel.md)
- [工作流包](./17-skills.zh-CN.md)
- [Open Core 边界](./12-open-core-boundary.md)
