# 本地使用与 BYOK

Falsify 是本地工具链。它不提供托管模型网关，也不保管你的 provider 密钥。你可以自行选择提供商、凭据以及执行审查的机器。

## 无需密钥也能使用的功能

以下命令不会调用模型：

```bash
falsify demo
falsify lint report.md
```

可用它们验证安装和本地结构检查。demo 不能替代模型审查；它只能证明本地检查路径可用。

## 需要你的凭据的功能

一次实时的 `falsify review` 需要以下任一条件：

- 为 OpenAI 兼容端点配置的 provider key；或
- 已在本机完成认证的兼容 agent CLI。

DeepSeek 示例：

```bash
export DEEPSEEK_API_KEY=sk-...
falsify review report.md --provider deepseek --json
```

对于 GitHub Actions，请将下列值设为仓库密钥：

- `FALSIFY_API_BASE`
- `FALSIFY_API_KEY`
- `FALSIFY_MODEL`

未设置 `FALSIFY_API_KEY` 时，随附 workflow 会保持在仅 lint 的 advisory 模式，不会消耗模型 token。

## 本地配置与数据边界

使用环境变量或 `falsify init` 创建的本地模板，避免重复配置。不要提交包含密钥的配置文件或环境变量。

Falsify 不会：

- 托管你的组织、项目或审查历史；
- 在用户之间共享回执或报告；
- 自动连接或读取你没有明确提供的权威系统；
- 代表你部署、合并或执行生产操作。

如果一项声明依赖外部状态，请在审查输入与产物中附上可检查的输出、链接、命令结果或清晰的验证路径。

## 当前 policy 文件的作用

模板将 `.falsify/policy.yml` 作为仓库内的说明，用于描述：

- 哪些路径存放决策产物；
- 文件数量和大小限制；
- 预期的 lint、实时审查和产物行为。

当前 GitHub Action 模板从 workflow 配置读取 `TARGET_GLOBS`。请使其与 policy 目标保持一致；不要把该文件当成已实现的通用 policy 引擎。

## 下一步

- [快速开始](./00-getting-started.zh-CN.md)
- [GitHub Action 模板](./14-github-action-install.zh-CN.md)
- [CLI 与产物参考](./20-cli-and-artifacts.zh-CN.md)
