# Falsify

**看起来绿了，还不够。**

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

[English](./README.md) · [线上站点](https://falsify.site/) · [Getting Started](./docs/00-getting-started.zh-CN.md) · [Skills 安装](./docs/17-skills.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Cutline / 风险裁刀](./docs/06-risk-scalpel.md)

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
| **本仓** | [Falsify](https://github.com/shi275773124/Falsify) | **MIT 子集** | 协议、入门 CLI、签收 packs、文档、站点、可选 quant |
| **Agent skill 壳** | [falsify-skill](https://github.com/shi275773124/falsify-skill) | MIT 壳 | 安装入口 — **不含** Pro 生产脚本 |
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

## 文档

- [Getting Started](./docs/00-getting-started.zh-CN.md)
- [Skills 安装（Claude Code / Cursor）](./docs/17-skills.md)
- [ROOTFIX 根治架构](./docs/ROOTFIX-architecture.md)
- [版本轨](./docs/VERSIONING.md)
- [裁决词统一](./docs/verdict-vocabulary.md)
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

## 解决什么问题

AI 让团队更快，也让“看起来很自信的错误”更便宜。

很多坏决策现在会被包装成：

- 漂亮的 AI 摘要
- 看起来成功的日志
- 通过了错误测试的绿色结果
- 另一个模型的同意
- 没有原始证据的安全结论

Falsify 要求结论回到可检查证据：原始产物、代码 diff、命令输出、一手来源、parse status、HTTP status、raw verdict、`finish_reason`，以及可用时的 usage/token counts。

## 三层框架

```text
Falsify = 对抗审 + 框架审 + Cutline
```

| 层 | 白话 | 发现什么 | 产出 |
|---|---|---|---|
| 对抗审 | 专打「看起来没问题」 | false truth、false risk、假绿、第二个模型同意当证据 | 对抗式 findings |
| 框架审（Brooks-Lint） | 专抓「以后会烂掉」 | hidden state、重复权威、脆弱回滚、过度工程 | 结构性审计目标 |
| Cutline / 风险裁刀 | 该改改，该记记，该删删 | 把所有风险都当 P0，或用「简化」删掉真实风险 | Must Fix / Known Debt / Delete |

最终输出（每张回执都带 `claim_scope` 与 `authority_ceiling`；开源回执为 `EPISTEMIC_ONLY`、`capital_authority: NONE`）：

- `PASS`：证据成立，没有当前阻塞项。
- `PASS_WITH_DEBT`：没有当前阻塞项，且每个 Known Debt 都有升级触发条件。
- `BLOCK`：仍有 Must Fix，当前决策缺证据，或审计结果不可解析。

## 快速开始

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]

# 无 API key：本地 fixture demo。
python -m falsify demo

# 无 Falsify API key。真审查走你的 provider key（BYOK）或已登录的 agent CLI。

# 无 API key：本地 tag/blocker lint。
python -m falsify lint examples/comparison-case-study/05-final-excerpt.md

# 真实模型审计。
export DEEPSEEK_API_KEY=sk-...
python -m falsify review report.md --provider deepseek

# 一个模型写，另一个模型审。
python -m falsify run brief.md --drafter claude --reviewer deepseek
```

本地网站：

```bash
python web/serve.py
# 打开 http://127.0.0.1:8000
```

网页中的 reviewer 会调用真实配置的后端；如果没有 key 或 provider 配置，会返回配置错误，不会假装分析。

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

## Falsify 不接受什么作为证据

- “模型说没问题。”
- “另一个 AI 也审过。”
- “日志看起来成功。”
- “输出为空，所以没有问题。”
- “这只是理论风险。”
- “清单里写了要小心。”
- 没有升级触发条件的 Known Debt。
- 绕过证据门槛的 `PASS` 或 `PASS_WITH_DEBT`。

## 适用场景

- AI 生成的 PR 和迁移计划
- 部署、监控、事故复盘结论
- 研究报告和生产决策
- 架构选型和供应商比较
- LLM probe、safety check、prompt-injection audit

## OSS PR gate（自托管）

**快速路径：** [5 分钟安装 GitHub Action](./docs/14-github-action-install.md)

自托管 PR 闸门 — 将 MIT 工作流模板复制到你的仓库：

- 复制 `templates/github-action-pr-review-prototype.yml`
- 粘贴为 `.github/workflows/falsify-pr-review.yml`
- （可选）从 `templates/falsify-policy.yml` 添加 `.falsify/policy.yml`
- 设置可选 secrets 以启用真模型审查：`FALSIFY_API_BASE`、`FALSIFY_API_KEY`、`FALSIFY_MODEL`

无 secrets 时仍运行 lint 并发布评论（咨询模式；真审查显式跳过，不会伪装成 PASS_WITH_DEBT）。

**边界：** 托管 Team 功能（组织 policy UI、留存存储、托管 GitHub App）与本 OSS 模板分离。详见 [Open Core 边界](./docs/12-open-core-boundary.md)。

## 继续关注

Falsify 会继续围绕 AI agent、代码审查和生产风险工作流演进。如果你也在做类似问题，欢迎关注或联系。

- GitHub: https://github.com/shi275773124/Falsify
- X / Twitter: https://x.com/aishikejian
- Email: chrisshi168@icloud.com

## License

MIT. See [LICENSE](./LICENSE).
