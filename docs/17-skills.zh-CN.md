# 17. Falsify Skills（安装）

[返回 README](../README.zh-CN.md) · [快速开始](./00-getting-started.zh-CN.md) · [BYOK + Policy](./11-byok-and-policy.md)

Falsify skills 是**可重复的签收工作流**，不是提示词片段。每个 pack 包含输入契约、原始产物要求、裁决 schema（`falsify.review.v1`）、样例 BLOCK / PASS_WITH_DEBT 输出、常见陷阱与最小动作。

线上站点：[falsify.zjdeng.xyz](https://falsify.zjdeng.xyz/)

## 五个工作流 pack（v0）

| Skill | 目录 | 一句话用途 |
|---|---|---|
| **Deployment Claim Review** | [`skills/falsify-deployment-claim/`](../skills/falsify-deployment-claim/) | 在生产签收前拦截「日志绿了」的虚假自信。 |
| **Live Production Gate** | [`skills/falsify-live-production-gate/`](../skills/falsify-live-production-gate/) | 真钱/定时 executor 的 Production Falsify：derived freshness、事故 replay fixture、input provenance manifest。 |
| **AI PR Review** | [`skills/falsify-ai-pr-review/`](../skills/falsify-ai-pr-review/) | 用原始 diff、测试与运行时证据审查 agent 或人工 PR 声明。 |
| **Research Report Audit** | [`skills/falsify-research-report/`](../skills/falsify-research-report/) | 抓研究报告中的过期数据、 cherry-pick 与结论越界。 |
| **Agent Safety Check** | [`skills/falsify-agent-safety-check/`](../skills/falsify-agent-safety-check/) | 信任前验证 agent 完成声明 — 看原始产物与副作用，不看摘要。 |

匿名化 live 事故模式（derived freshness / stale panel）：[`examples/real-cases/02-derived-freshness-stale-panel.md`](../examples/real-cases/02-derived-freshness-stale-panel.md)。

GitHub 浏览全部 pack：[`skills/`](https://github.com/shi275773124/Falsify/tree/main/skills)

## 在 Claude Code 中安装

1. 克隆或下载本仓库（或从 GitHub 复制单个 skill 文件夹）。
2. 将 skill 目录复制到工作区或用户 skills 路径，例如：
   - **项目级：** `.claude/skills/falsify-deployment-claim/`（文件夹内需有 `SKILL.md`）
   - **用户级：** `~/.claude/skills/falsify-deployment-claim/`
3. 按 host 要求重启 Claude Code 或重新加载 skills。
4. 当声明需要签收时调用工作流 — 按 `templates/input.md` 粘贴声明与所需原始产物。

无需 Falsify API key。实时模型审查走**自带 provider key（BYOK）**或已登录的 agent CLI。见 [BYOK + Policy](./11-byok-and-policy.md)。

## 在 Cursor 中安装

1. 从 [`skills/`](https://github.com/shi275773124/Falsify/tree/main/skills) 复制 skill 文件夹到：
   - **项目级：** `.cursor/skills/<skill-name>/`（含 `SKILL.md`）
   - **用户级：** `~/.cursor/skills-cursor/<skill-name>/`
2. 当任务匹配工作流（部署声明、PR 审查、研究审计、agent 完成检查）时，agent 会加载 `SKILL.md`。
3. 自带模型 key — 本地或 BYOK 使用不需要托管 Falsify API key。

## 每个 pack 包含什么

```text
skills/falsify-<name>/
  SKILL.md              # 工作流契约
  README.md             # 快速开始
  templates/input.md    # 声明 + 产物粘贴模板
  templates/verdict.schema.json
  examples/             # 样例 BLOCK 输入与裁决 JSON
```

## CLI 与 GitHub Action（其他入口）

Skills 是**编辑器优先**入口。你也可以：

- 运行 CLI：`python falsify.py review report.md --provider deepseek`（[快速开始](./00-getting-started.zh-CN.md)）
- 安装 PR 闸门：[GitHub Action（5 分钟）](./14-github-action-install.zh-CN.md)

## 升级路径

Starter skills 属于 MIT 开放核心。当一个产物控制资金、生产或客户承诺时，考虑 **Audit Sprint** 或 **Design Partner** pilot — 见 [Team delivery blueprint](./10-team-delivery-and-business-model.md)。

另见：[Pro vs OSS — 三层边界](./18-pro-vs-oss.zh-CN.md)。
