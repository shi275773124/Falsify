# 18. Pro vs OSS

[返回 README](../README.zh-CN.md) · [Open Core 边界](./12-open-core-boundary.zh-CN.md) · [Skills](./17-skills.zh-CN.md)

一页纸：GitHub 上 MIT 开源什么、闭源 Pro skill/runtime 留什么、Team 作为 workspace 产品卖什么。供 README、页脚或 onboarding 链接 — 不是 pitch deck。

## 三层

| 层 | 是什么 | 来源 / 交付 | 付费点 |
|---|---|---|---|
| **OSS (MIT)** | 协议、CLI、五个 workflow pack、模板、示例 | [GitHub](https://github.com/shi275773124/Falsify) — 自托管、BYOK | 无（自备模型 key） |
| **Pro（闭源）** | 伞形 Falsify skill + Production  enforcement + fixture 库更新 | 私有 canonical（`~/.cursor/skills/falsify`、vault Hermes runtime）— 无完整公开副本 | skill/runtime 更新、事故抗体库、Production cutline 执行 |
| **Team（付费产品）** | 组织治理、留存、集成、rollout | 托管或合同 workspace — 见 [Team 版 spec](./13-team-edition-spec.md) | 席位 / workspace 费（BYOK 混合，见 [商业模式](./10-team-delivery-and-business-model.md)） |

**命名：** Pro ≠ Team。Pro = 伞形 skill 栈 + Production 闸门纪律。Team = 付费 workspace（组织级 policy、产物历史、集成）— 见 [docs/13](./13-team-edition-spec.md)。

## OSS 清单（GitHub，MIT）

与 [Open Core 边界](./12-open-core-boundary.zh-CN.md) 一致：

- **协议** — `PASS / PASS_WITH_DEBT / BLOCK`、Cutline、 `falsify.review.v1` JSON schema
- **CLI** — `falsify lint`、`falsify review --json`、`falsify demo`
- **GitHub / CI** — workflow 模板、BYOK、JSON + Markdown 产物
- **Policy** — `.falsify/policy.yml` 基础字段
- **报告** — 仅本地/CI 产物
- **集成** — 示例与 webhook 模式（非生产级连接器）
- **五个 workflow pack（v0）** — deployment-claim、live-production-gate、ai-pr-review、research-report、agent-safety-check（[skills 索引](./17-skills.zh-CN.md)）
- **模板 + 示例** — 含 anonymized 事故模式 [`examples/real-cases/02-derived-freshness-stale-panel.md`](../examples/real-cases/02-derived-freshness-stale-panel.md)

## Pro 清单（闭源）

不以完整副本发布在 GitHub。Canonical 在私有伞形 skill 与 vault Hermes runtime；仅 **子集** 导出到 OSS（见下）。

Pro 提供 OSS 模板描述但无法单独 fully enforce 的能力：

| 能力 | Pro 拥有 |
|---|---|
| **Daily vs Production 硬边界** | Daily 健康检查 ≠ Production 签收；真钱 claim 需 dual-model 或 delegated audit — 非同一 agent 自签 |
| **事故 → fixture → gate** | 真实事故失败形态 → 永久 red sample；后续 closure 须经 **production runner** 入口 RED→GREEN |
| **Negative fixtures** | 最小覆盖集（derived freshness false-green、缺失覆盖、fail-close 标记、signer/账户不匹配、合成 non-NOOP 分支）作为活库维护 |
| **Input provenance manifest** | 独立 manifest 闸门：源名、新鲜度边界、min/max 时间戳、覆盖、缺失/ stale 列表 |
| **Replacement semantics** | 数据源/字段/窗口/指标替换需 old-vs-new diff 或显式策略变更登记 |
| **Hermes 集成** | Skill manifest + runtime hooks，使定时/live executor 与人类 audit 同一 Production 规则 |
| **Delegated / self-Falsify 纪律** | 同一 agent 对高风险 claim 自签最多 `PASS_WITH_DEBT`，除非有第二 authority 路径记录 |

OSS 导出 pack 中可见的 rule ID（如 `FALSIFY_INCIDENT_REPLAY_V1`）命名闸门；Pro 拥有 **执行深度**、fixture 语料与更新节奏。

## 导出策略（单向 sync）

```text
canonical（私有伞形 + vault runtime）
        │
        │  单向导出 — 仅经审查的子集
        ▼
OSS  skills/falsify-live-production-gate/
```

- **Canonical** = 私有伞形 skill + vault `hermes-skills-runtime` falsify skill
- **导出目标** = [`skills/falsify-live-production-gate/`](../skills/falsify-live-production-gate/) 仅此 pack
- **方向** = 仅 Pro → OSS；OSS PR 不是 Production enforcement 的 source of truth

**导出 denylist** — 永不进入 OSS GitHub：

| 禁止 | 原因 |
|---|---|
| 完整伞形 `SKILL.md` 工作流图 | Pro 跨 Daily + Production + 领域 pack 编排 |
| 完整 negative-fixture 语料 + PM/vault fixture 路径 | 事故抗体库是付费更新面 |
| Hermes runtime manifest、调度 hooks、executor 接线 | Live loop 集成 |
| 仅 Production 的 cutline 表与 dual-model audit 契约 | 执行更新，非协议 |
| 客户/vault 特定事故文档、主机路径、账户边界 | 隐私 + 未 anonymize 的运营真相 |
| Delegated-audit runtime enforcement（谁可签 Production PASS） | 信任模型，非 schema |

OSS 可保留 **anonymized 模式文档** 与 **rule ID 名称**；denylist 项即 rule 名出现在导出 skill 文本中也不进入公开仓。

## 护城河（实话）

Pro **不**声称：

- 跨 vendor 独家锁定 — Falsify 领地是 **可辩护签收的决策闸门**，不是占有 broker/CI/模型商（白皮书 §9）

Pro **确实**卖：

- **领地** — Production Falsify 与 Daily ops 的硬边界（白皮书 §10）
- **事故抗体库** — 每次真实事故 → 须经 production 路径 replay 的永久 fixture（白皮书 §13：incident → fixture → gate）
- **执行更新** — 新失败类出现时的 cutline 收紧与 fixture 覆盖，从 canonical sync 到 OSS 导出子集

护城河 = 更新 + 库 + live loop 纪律 — 不是单纯藏已在公开 markdown 里写全的文件。

## Team 路径（与 Pro 分开）

Pro 面向在本地或 vault 跑 Production Falsify 的操作者。

Team 是 **工程组织的 workspace 产品**：

- **现在：** 单个高风险 artifact 的 Audit Sprint，或 4–8 周 Design Partner（[商业模式](./10-team-delivery-and-business-model.md)）
- **Team MVP 顺序（严格）：** PR comment + check → 稳定 JSON/MD 产物 → `policy.yml` enforcement → 产物历史 → 单一集成 → 仪表盘最后（[Team spec](./13-team-edition-spec.md)）

Team 不替代 Pro；它增加 OSS 仓不托管的组织 rollout、留存与集成。

## Known debt

| 项 | 状态 |
|---|---|
| Open-core 商业模式转化 | **未验证** — OSS 今日可交付；dbt/Vault 类比不是 Team 会转化的证据（[docs/12 Known Debt](./12-open-core-boundary.zh-CN.md#known-debt--开源核心商业模式)） |
| OSS `falsify-live-production-gate` 范围 | **计划 P1** — 二 bot 审：公开 pack 可能收窄为 Daily/部分 Production 模式文档；完整四闸门 enforcement 留 Pro，待 export 策略重切 |
| 物理拆仓（`falsify` + `falsify-team`） | 延后至设计伙伴稳定 + 版本化 API 边界（[docs/12](./12-open-core-boundary.zh-CN.md#何时再考虑物理拆仓)） |

## 相关链接

- [12. Open Core 边界](./12-open-core-boundary.zh-CN.md)
- [17. Skills](./17-skills.zh-CN.md)
- [10. Team 交付与商业模式](./10-team-delivery-and-business-model.md)
- [13. Team 版 spec](./13-team-edition-spec.md)
- [真实案例：derived freshness stale panel](../examples/real-cases/02-derived-freshness-stale-panel.md)
