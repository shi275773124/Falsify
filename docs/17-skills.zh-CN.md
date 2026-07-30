# 使用 Falsify 工作流包

[快速开始](./00-getting-started.zh-CN.md) · [本地使用与 BYOK](./11-byok-and-policy.zh-CN.md)

工作流包是一组本地、可重复执行的审查说明，不是托管服务，也不能自行构成证据。每个包会告诉 agent 应请求哪些证据、如何质疑一项声明，以及如何整理裁决。请将最终证据和裁决产物与工作一同保留。

## 可用工作流包

| 工作流包 | 适用场景 |
|---|---|
| [Brooks-Lint（L0 框架审）](../skills/falsify-brooks-lint/) | 对抗攻击前的结构腐烂 / 可审计性审查；产品 L0 层。见 [Brooks-Lint](./09-brooks-lint.md)。 |
| [Deployment Claim Review](../skills/falsify-deployment-claim/) | 部署似乎成功，但你需要目标状态的证据。 |
| [AI PR Review](../skills/falsify-ai-pr-review/) | 人或 agent 声称一个 PR 已完成。 |
| [Research Report Audit](../skills/falsify-research-report/) | 备忘录可能依赖过期、选择性引用或缺少支持的证据。 |
| [Agent Safety Check](../skills/falsify-agent-safety-check/) | agent 声称已完成一项重要任务。 |
| [Live Production Gate](../skills/falsify-live-production-gate/) | 线上/cron 恢复或类生产声明（模式导出）。 |

**说明：** 安装 Brooks-Lint 包不等于 Claiming Falsify。承载声明的权威出口仍是 `python -m falsify review`（默认含 L0）或 `python -m falsify brooks`。`falsify lint` 只是 markdown 标签/阻断器静态检查——不是 Brooks-Lint。

## 在 Claude Code 中安装

1. 将 [`skills/`](../skills/) 中的一个文件夹复制到项目或用户的 skills 目录，例如 `.claude/skills/falsify-deployment-claim/`。
2. 确认该文件夹包含 `SKILL.md`。
3. 如果宿主要求，请重新加载或重启。
4. 使用工作流包的输入模板，并提供声明及其要求的原始产物。

## 在 Cursor 中安装

1. 将 [`skills/`](../skills/) 中的一个文件夹复制到 `.cursor/skills/<skill-name>/` 或 Cursor 用户 skills 目录。
2. 确认该文件夹包含 `SKILL.md`。
3. 当任务匹配时让宿主加载该工作流包，并提供所要求的证据。

安装工作流包不需要 Falsify API key。需要模型支持的实时审查仍会使用你的 provider key 或已在本机认证的 agent CLI。

## 工作流包不会做什么

工作流包不会自动检查你的云账户、运行生产闸门，也不会把 agent 的回答变成证据。它用于组织审查；请用 CLI 或你自己的验证命令生成并保留产物。

## 下一步

- [运行本地审查](./00-getting-started.zh-CN.md)
- [CLI 与产物参考](./20-cli-and-artifacts.zh-CN.md)
- [添加 GitHub PR 闸门](./14-github-action-install.zh-CN.md)
