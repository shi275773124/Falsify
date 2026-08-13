# Falsify

[English](README.md) | 中文

**看起来绿了，还不够。**

官方站点：[https://falsify.site/](https://falsify.site/)

先审，再信；先证据，再放行。

两个痛点。三层白话。

| 痛点 | Falsify 怎么做 |
|------|----------------|
| **AI 幻觉与假绿** — 日志绿了、另一个模型也同意，仍可能不安全 | **对抗审** — 专打「看起来没问题」 |
| **长期腐烂 / 过度工程** — 隐状态、脆弱回滚、流程表演 | **框架审 + Cutline** — 专抓「以后会烂掉」；该改改、该记记、该删删 |

```text
对抗审   →  专打「看起来没问题」
框架审   →  专抓「以后会烂掉」
Cutline  →  该改改 / 该记记 / 该删删
回执     →  PASS / PASS_WITH_DEBT / BLOCK
```

> 只做审查签收，不自动部署、不下单。

**证据驱动的决策闸门** — Falsify 是高风险声明的决策闸门：对抗审 + 框架审 + Cutline，然后给出签署回执。不是聊天机器人的第二意见。


[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[线上站点](https://falsify.site/) · [快速开始](./docs/00-getting-started.zh-CN.md) · [Skills 安装](./docs/17-skills.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)

## 快速开始

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
pip install -e ".[dev]"
python -m falsify demo
```

1. 在 [Claude Code 或 Cursor 安装 skill](./docs/17-skills.md) — 从 [`skills/`](./skills/) 复制文件夹（BYOK；无需 Falsify API key）。
2. 安装 [GitHub Action](./docs/14-github-action-install.zh-CN.md) — [一屏分享包](./docs/github-action-share-pack.md) · [假绿卡片](./examples/real-cases/SHARE-CARDS.md)。
3. 可选打开[首页格式演示](https://falsify.site/#try) — 仅看回执形态，不是完整门禁能力。
4. 在一个高风险产物上跑 Falsify，再决定是否放行。

## Skills（4 个工作流）

v0 skills pack 把证据纪律封装为可重复签收工作流 — 不是提示词。每个 skill 含输入契约、原始产物要求、裁决 schema、BLOCK / PASS_WITH_DEBT 样例、陷阱与最小动作。

Packs 定义**打什么**。强制执行仍是 **CLI / CI / Pro 闸门**（[skills/README.md](./skills/README.md)）。

| 工作流 | 路径 | 用途 |
|---|---|---|
| Deployment Claim Review | [`skills/falsify-deployment-claim/`](./skills/falsify-deployment-claim/) | 拦截「日志绿了」的虚假自信。 |
| AI PR Review | [`skills/falsify-ai-pr-review/`](./skills/falsify-ai-pr-review/) | 用原始证据审查 agent 或人工 PR 声明。 |
| Research Report Audit | [`skills/falsify-research-report/`](./skills/falsify-research-report/) | 抓过期数据、cherry-pick 与结论越界。 |
| Agent Safety Check | [`skills/falsify-agent-safety-check/`](./skills/falsify-agent-safety-check/) | 信任前验证 agent 完成声明。 |

**安装：** [Skills 指南（Claude Code / Cursor / BYOK）](./docs/17-skills.md) · [GitHub 浏览 `skills/`](https://github.com/shi275773124/Falsify/tree/main/skills)

## Open core 与「声称做过 Falsify」

| 表面 | 仓库/位置 | 开源？ | 角色 |
|------|-----------|--------|------|
| **本仓** | [shi275773124/Falsify](https://github.com/shi275773124/Falsify) | **MIT 子集** | 协议、入门 CLI、签收 packs、文档、站点、可选 quant |
| **Agent skill 壳** | [shi275773124/falsify-skill](https://github.com/shi275773124/falsify-skill) | MIT 壳 | 安装入口 — **不含** Pro 生产脚本 |
| **Pro 运行时** | 私有（操作机 skill 树） | **闭源** | 生产/量化强制闸门、事故抗体、live 接线 |
| **对外版本** | `falsify/__init__.py` → `VERSION` | 公开 | 仅表示 OSS 产品版，不是 Pro skill 版 |

> **Open core（不是全部开源）：** 协议、入门 CLI、模板与 JSON schema 为 [MIT](./LICENSE)。**生产强制、真金 fixture 库、私有运行时 skill 默认闭源（Pro）。** 详见 [Open Core 边界](./docs/12-open-core-boundary.md)、[Pro vs OSS](./docs/18-pro-vs-oss.md)、[ROOTFIX](./docs/ROOTFIX-architecture.md)。

**声称做过 Falsify** = 跑过权威出口并保留命令与产物——不只是安装 skill。真金强制在 **Pro**，不在本 MIT 树。见 [skills/README.md](./skills/README.md)。

## 交付状态（今天能拿到什么）

LLM 负责攻击声明并签署边界内裁决；**authority adapter** 负责核对物理事实；**统一 kernel** 决定该裁决能否授权动作。每个交付物都标明状态——这里没有任何东西会把一次审查悄悄变成生产或付款闸门。

| 交付物 | 状态 | 内容 |
|---|---|---|
| **Falsify Review** | **AVAILABLE · 开源** | 对抗式 LLM 审查，签发边界内的认知层裁决：CLI、本地 demo、JSON 裁决格式、GitHub Action 模板、文档、示例、入门 skills。 |
| **Falsify Authority Gate** | **需要 ADAPTER** | 对真实权威路径执行可执行的证据检查；只有这样 `PASS` 才能承载动作。目前没有公开的 adapter——没有它，所有裁决只停留在认知层。 |
| **Audit Sprint** | **AVAILABLE · 服务** | 针对一个高风险产物：声明清单、kill-shots、证据包，以及签署的裁决回执（[交付物模板](./templates/audit-sprint.md)）。 |
| **Production / Quant Pro** | **DESIGN PARTNER · 私有** | 按具体权威路径集成（部署、数据、执行）。小规模试点，不自助开放。 |
| **Team / Enterprise** | **TARGET · 未交付** | Dashboard、SSO、RBAC、留存、托管集成。路线图目标，不是已交付功能。 |

License/商业边界：本仓含 MIT `LICENSE`。商业化工作流封装、托管集成、支持、私有部署路径，以及受控的 Falsify 品牌/认证标识，仍属商业边界事项。

## 解决什么问题

AI 让团队更快，也让“看起来很自信的错误”更便宜。

很多坏决策现在会被包装成：漂亮的摘要、绿色日志、测了错误东西却通过的测试、第二个模型的同意，以及证据很弱却很自信的报告。

Falsify 要求结论回到可检查证据：代码、diff、命令输出、一手来源、parse status、HTTP status、raw verdict、`finish_reason`，以及可用时的 usage/token counts。

## 三层框架

```text
Falsify = 对抗审 + 框架审 + Cutline
```

| 层 | 白话 | 发现什么 | 产出 |
|---|---|---|---|
| 对抗审 | 专打「看起来没问题」 | false truth、false risk、静默失败、过期数据、假验收、第二个模型同意当证据 | 对抗式 findings |
| 框架审（Brooks-Lint） | 专抓「以后会烂掉」 | hidden state、隐式权威、重复控制路径、脆弱回滚、过度工程 | 结构性审计目标 |
| Cutline / 风险裁刀 | 该改改，该记记，该删删 | 把所有风险都当 P0，或用「简化」删掉真实风险 | Must Fix / Known Debt / Delete |

最终输出（每张回执都带 `claim_scope` 与 `authority_ceiling`；开源回执为 `EPISTEMIC_ONLY`、`capital_authority: NONE`）：

- `PASS`：证据成立，没有当前阻塞项。
- `PASS_WITH_DEBT`：没有当前阻塞项，且每个 Known Debt 都有升级触发条件。
- `BLOCK`：仍有 Must Fix，当前决策缺证据，或审计结果不可解析。

## Quant Gate — 回测审计

Falsify 的量化层抓回测藏起来的东西：过拟合、前视偏差、成本乐观。

```bash
pip install -e ".[quant]"  # 在仓库根目录：numpy, scipy, pandas
python -m falsify.quant_gate --script strategy.py --contract contract.yaml --results-dir results/
```

**Gates 0–5：** 合约校验 → PIT/幸存者偏差 → 静态代码扫描（gate4 前视） → 数值复算（PSR/DSR） → 稳健性（PBO/walk-forward/regime/多目标 Calmar/逐笔 edge-vs-cost） → live 对账。

### PBO=0.99 的故事

一个策略家族算出 PBO=0.9991 — 「几乎确定过拟合，拒绝。」但 0.9991 高得可疑。排查发现 PBO 函数在算 Sharpe 前先减了均值，把所有 Sharpe 归零，「样本内最优」变成纯噪声。PBO 量的是噪声均值回归，不是过拟合。修完后：**PBO=0.09**。策略其实稳健。

**教训：** PBO ≈ 1.0 首先是*实现*的红灯，不只是策略的红灯。永远用合成数据复核。

### gate4 抓什么（前视偏差）

| 模式 | 严重度 | 例子 |
|---|---|---|
| `shift(-N)` | CRITICAL | `df["close"].shift(-5)` — 把未来拉进现在 |
| `rolling(VAR).std()` 没有 `shift(1)` | WARN | 波动率包含当前 bar 的收益 |
| `rolling(20).std()` 没有 `shift(1)` | WARN | 同上，窗口是字面量 |
| 手写 for 循环里用 `iloc[i+N]` | WARN | gate4 无法静态验证 — 需要人工审 |

### 可信度资产

- **85 个绿灯 fixture** — 每个统计函数的已知答案测试（PBO、DSR、PSR、walk-forward、regime、成本真实性、执行真实性）。夜间跑。
- **6 个红灯毒药** — 故意注入公式的 bug（PSR 峰度、PBO 排名、DSR 公式、gate4 的 shift/rolling/for-loop）。毒药如果过了，检查就是死的 — 立刻告警。

```bash
# 跑可信度套件
python -m pytest tests/quant/ -v
```

### Hermes gate6 分叉

Hermes 上的 Falsify 部署额外跑 `gate6_harness_boundary.deployment_parity`（研究/live 合约哈希 + Jaccard 选股相似度 + 宇宙/权重/归一化一致性；默认 `min_selected_jaccard=0.8`）。这个闸门**不在** OSS 仓：它依赖 live 执行上下文和 OSS 不交付的 production-guard 概念。OSS 用户若需要研究/live 一致性检查，应另设计适合 OSS 的可复现闸门，不要移植 hermes gate6。

## 快速开始（完整）

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]

# 量化回测审计（PBO/DSR/gate4）：
python -m pip install -e .[quant]  # 增加 numpy, scipy, pandas

# 无 API key：确定性本地 fixture demo。
python -m falsify demo

# 无 Falsify API key。真审查走你的 provider key（BYOK）或已登录的 agent CLI。

# 无 API key：本地标签/阻断器 lint。
python -m falsify lint examples/comparison-case-study/05-final-excerpt.md

# 通过 OpenAI 兼容 provider 做真实模型审查。
export DEEPSEEK_API_KEY=sk-...
python -m falsify review report.md --provider deepseek

# 完整回路：一个模型写，另一个模型审。
python -m falsify run brief.md --drafter claude --reviewer deepseek
```

也可以把审查路由到你已经登录的本地 agent CLI：

```bash
python -m falsify review report.md --provider claude
python -m falsify review report.md --provider codex
FALSIFY_AGENT_CMD="myagent --headless" python -m falsify review report.md -p myagent
```

启动本地产品站和粘贴即审：

```bash
python web/serve.py
# 打开 http://127.0.0.1:8000
```

首页演示面板会调用已配置的后端。它不是假的 live 分析；没有 provider key/配置时会返回配置错误。

## 示例

普通审查：

> 部署成功了，因为日志跑完了。

Falsify：

```text
[AGENT-B audit] logs are treated as state verification
Failure mode: logs prove something ran; they do not prove the intended system state changed
Cutline: Must Fix
Evidence needed: raw artifact or command output that proves the claim
Minimal action: verify the actual state with a read-after-write check, deployment query, or invariant test
VERDICT: BLOCK
```

另一个例子：

> 第二个 AI 审过 prompt-injection 风险，没发现问题。

Falsify 要求原始输出、parse status、HTTP status、`finish_reason`、可用时的 usage/token counts，以及已知模式或复现证据。同意本身不是证明。

## 适用场景

- AI 生成的 PR 和迁移计划
- 部署或事故声明
- 研究结论和市场报告
- 架构或供应商选型
- LLM probe、监控和 safety check
- 任何「自信摘要可能藏弱证据」的工作流

## Falsify 不接受什么作为证据

- “模型说没问题。”
- “另一个 AI 也审过。”
- “日志看起来成功。”
- “输出为空，所以没有问题。”
- “这只是理论风险。”
- “清单里写了要小心。”
- 没有升级触发条件的 Known Debt。
- 绕过证据门槛的 `PASS` 或 `PASS_WITH_DEBT`。

## 文档

- [Getting Started](./docs/00-getting-started.zh-CN.md)
- [Skills 安装（Claude Code / Cursor）](./docs/17-skills.md)
- [ROOTFIX 根治架构](./docs/ROOTFIX-architecture.md) — 版本 / 双仓 / 声称漂移的结构性治疗
- [版本轨](./docs/VERSIONING.md) — 一个对外产品版本
- [裁决词统一](./docs/verdict-vocabulary.md) — Core + 扩展
- [Brooks-Lint](./docs/09-brooks-lint.md)
- [Adversarial Review](./docs/05-adversarial-review.md)
- [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)
- [Examples](./docs/08-examples.md)
- [Audit-channel risks](./docs/07-audit-channel-risks.md)
- [Team delivery & business model blueprint](./docs/10-team-delivery-and-business-model.md)
- [BYOK + Policy (Team MVP)](./docs/11-byok-and-policy.md)
- [Install GitHub Action (5 min)](./docs/14-github-action-install.md)
- [CI and release gate](./docs/15-ci-and-release-gate.md)
- [Open Core boundary](./docs/12-open-core-boundary.md)
- [Team edition spec (reserved)](./docs/13-team-edition-spec.md)
- [Pro vs OSS](./docs/18-pro-vs-oss.md)

## OSS PR gate（自托管）

**快速路径：** [5 分钟安装 GitHub Action](./docs/14-github-action-install.md)

自托管 PR 闸门 — 将 MIT 工作流模板复制到你的仓库：

- 复制 `templates/github-action-pr-review-prototype.yml`
- 粘贴为 `.github/workflows/falsify-pr-review.yml`
- （可选）从 `templates/falsify-policy.yml` 添加 `.falsify/policy.yml`
- 设置可选 secrets 以启用真模型审查：
  - `FALSIFY_API_BASE`
  - `FALSIFY_API_KEY`
  - `FALSIFY_MODEL`

无 secrets 时仍运行 lint 并发布评论（咨询模式；真审查显式跳过，不会伪装成 PASS_WITH_DEBT）。
工作流在 JSON 模式下默认严格执行债务卫生：
`FALSIFY_STRICT_KNOWN_DEBT_TRIGGER=1`（没有触发条件的 Known Debt 变成 BLOCK）。

**边界：** 托管 Team 功能（组织 policy UI、留存存储、托管 GitHub App）与本 OSS 模板分离。详见 [Open Core 边界](./docs/12-open-core-boundary.md)。

## 自吃狗粮 — `falsify-review.yml`

本仓对自己跑 Falsify。每个 PR 触发 [`.github/workflows/falsify-review.yml`](./.github/workflows/falsify-review.yml)，调用 `falsify gate` 子命令：

```bash
python -m falsify gate \
  --base "origin/${{ github.base_ref }}" \
  --tier "${FALSIFY_TIER:-auto}" \
  --glob 'demo-vault/research/**/*.md' \
  --json falsify-out.json
```

工作流随后发一条幂等 PR 评论（`<!-- falsify-pr-review -->` 标记 — 再推只更新同一条，不刷屏），并在 `BLOCK` / `KILL` 时让 CI 失败。输出 JSON 作为 `falsify-gate-out` artifact 上传，供审计。

`falsify gate` 是**诚实的 L2 stub**：它在 PR diff 里对变更的决策文档聚合 `falsify lint`。干净输入绝不假报 `BLOCK`，脏输入绝不假报 `PASS`。stub 范围写在 JSON 输出里（`schema_version: falsify.gate.v0.1`，`stub: true`）。v1.1 会把 `--tier quant` 接到 `quant_falsify_gate`（gate0–gate6），见 [risk-contract schema](https://github.com/shi275773124/Falsify/blob/main/docs/06-risk-scalpel.md)。要对单份草稿做模型对抗审，用 `falsify review <file> --json`。

给某个 PR 调闸门：
- `FALSIFY_TIER` 仓库变量：`auto`（默认） / `normal` / `production` / `quant`
- 工作流 `env` 里的 `FALSIFY_GLOBS`：要 lint 哪些变更的 `.md` 路径

## 继续关注

Falsify 会继续围绕 AI agent、代码审查和生产风险工作流演进。如果你也在做类似问题，欢迎关注或联系。

- 官方站点：https://falsify.site/
- GitHub: https://github.com/shi275773124/Falsify
- X / Twitter: https://x.com/aishikejian
- Email: chrisshi168@icloud.com

## 许可证

MIT. See [LICENSE](./LICENSE).
