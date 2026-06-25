# 14. 安装 Falsify GitHub Action（5 分钟）

[返回 README](../README.zh-CN.md) · [BYOK + Policy](./11-byok-and-policy.md)

本指南在 **目标仓库**（你要保护的仓库）安装 PR 闸门，不一定是 Falsify 仓库本身。

## 你将得到

安装后，每次改动决策文档的 PR 会产出：

- 带 `PASS / PASS_WITH_DEBT / BLOCK` 的 PR 评论
- `falsify-report.json`（机器可读）
- `falsify-report.md`（人类可读）
- 裁决为 `BLOCK` 时失败的 GitHub Check

## 前置条件

- 已启用 Actions 的 GitHub 仓库
- 决策文档为 markdown（例如 `reports/`、`research/`、迁移计划）
- （可选）OpenAI 兼容 API key，用于真模型审查（BYOK）

## 步骤 1 — 添加 workflow（2 分钟）

1. 在目标仓库创建：

```text
.github/workflows/falsify-pr-review.yml
```

2. 从此处复制内容：

```text
https://github.com/shi275773124/Falsify/blob/main/templates/github-action-pr-review-prototype.yml
```

3. 编辑 job `env` 块顶部的 `TARGET_GLOBS`：

```yaml
env:
  TARGET_GLOBS: "reports/**/*.md research/**/*.md"
```

尽量收紧。不要扫描整个仓库。

4. Commit 并 push 到 `main`。

## 步骤 2 — 开测试 PR（1 分钟）

改动一个落在 target globs 下的 markdown，例如：

```text
reports/deployment-claim.md
```

开 PR。你应该看到：

- workflow `falsify-pr-review` 运行
- PR 评论 `<!-- falsify-pr-summary -->` 出现或更新
- artifact `falsify-report` 上传

无 API secret 时，真审查跳过，lint 仍运行（advisory 模式）。

## 步骤 3 — （可选）启用 BYOK 真审查（1 分钟）

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

添加：

| Secret | 示例 |
|---|---|
| `FALSIFY_API_BASE` | `https://api.deepseek.com/v1` |
| `FALSIFY_API_KEY` | `sk-...` |
| `FALSIFY_MODEL` | `deepseek-chat` |

重跑 PR workflow。有 key 时会跑真 `falsify review --json`。

## 步骤 4 — （可选）添加 policy 文件（1 分钟）

添加仓库 policy 文件（OSS）：

```text
.falsify/policy.yml
```

从此处起步：

```text
templates/falsify-policy.yml
```

Policy 记录团队的 globs、限制与执行意图。

说明：当前 workflow 原型从 workflow `env` 读取 `TARGET_GLOBS`。在原生 policy 加载落地前，请让 `TARGET_GLOBS` 与 `.falsify/policy.yml` 的 `targets.globs` 保持一致。

## 步骤 5 — 开启 required check（就绪后）

advisory 评论跑 3–7 天后：

1. 仓库 → **Settings** → **Branches** → branch protection rule
2. Require status check：`falsify-pr-review`（或你的 workflow job 名）
3. 团队还在调 globs 时，先保持 advisory 模式

## 验收清单

在第一个 PR 上跑这些检查：

- [ ] 干净的决策文档让 workflow 绿过
- [ ] PR 评论含裁决 + 按 cutline 分组 findings
- [ ] Artifact 含 `schema_version: falsify.report.v0.1` 的 `falsify-report.json`
- [ ] 启用真审查时，故意弱声明应返回 `BLOCK`
- [ ] `FALSIFY_STRICT_KNOWN_DEBT_TRIGGER=1` 时，Known Debt 缺 `upgrade_trigger` 应返回 `BLOCK`

## 模式

| 模式 | Secrets | 行为 |
|---|---|---|
| Advisory | 无 | 跑 lint，跳过真审查，仍发评论 |
| Live BYOK | 设 `FALSIFY_*` | 跑 review，`BLOCK` 可 fail check |
| Strict debt | 默认开 | Known Debt 缺 trigger 变 `BLOCK` |

## 排障

**没有文件被扫描**

- 改动文件不匹配 `TARGET_GLOBS`
- 修正 globs 或把决策文档移到覆盖路径

**Workflow 过了但评论说 skipped live review**

- 无 `FALSIFY_API_KEY` 时属预期
- 加 BYOK secrets 启用真审查

**Check 意外 BLOCK fail**

- 打开 `falsify-report.md` artifact
- 修 `Must Fix` 或给 Known Debt 补 `upgrade_trigger`

**Token 成本过高**

- 收紧 `TARGET_GLOBS`
- 减小改动文件体积
- 低风险仓库用 advisory 模式

## 延伸阅读

- [BYOK + Policy](./11-byok-and-policy.md)
- [Team 交付蓝图](./10-team-delivery-and-business-model.md)
- [Open Core 边界](./12-open-core-boundary.md)
