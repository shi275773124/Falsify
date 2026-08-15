# 18. 安装 Falsify DeepSeek 插件（3 步）

[返回 README](../README.zh-CN.md) · [BYOK + Policy](./11-byok-and-policy.md) · [Skills](./17-skills.md) · [GitHub Action](./14-github-action-install.md)

DeepSeek 负责写。Falsify 只问一件事：**证据在哪里。**

装好后，对 agent 说「falsify 这个文件」或「gate 这个 PR」。
你会拿到回执：`PASS` / `PASS_WITH_DEBT` / `BLOCK`。
Agent 说「看起来没问题」不是回执。Lint 变绿也不是放行。

本指南在 **DeepSeek Harness** 里安装 [falsify-dsh](https://github.com/shi275773124/falsify-dsh) 插件。这是一条并行的本地路径，不是 [GitHub Action](./14-github-action-install.md) 的替代。

## 你将得到

安装后，agent 可以调用三个包装公开 Falsify CLI 的工具：

- `falsify_lint` — 静态检查；`L2_CLEAN` / `L2_DIRTY`；不是放行授权
- `falsify_review` — 审查声明或文件；`PASS` / `PASS_WITH_DEBT` / `BLOCK`；BYOK；只做文档逻辑
- `falsify_gate` — 对照 `origin/main` 闸门 PR；公开 CLI；`production` / `quant` fail-closed

插件不决定裁决。它只提供路径、运行 `python -m falsify`，并返回回执。

OSS 插件是**对抗审查层**，不是 production/deployment authority。它不能签发 claim-bearing production PASS；后者需要另行部署的 authority adapter、signer 与 sandbox。`claim_bearing` 仍为 false。

## 前置条件

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（开发者预览，会有破坏性变更）
- Python 3.12+，并已安装公开 Falsify CLI
- 一个可以重启的 DSH profile（本指南使用 `--profile web`）
- （可选）用于真模型审查的 provider key（BYOK）

## 步骤 1 — 安装公开 CLI（1 分钟）

```sh
pip install "falsify @ git+https://github.com/shi275773124/Falsify.git"
python -m falsify --help
```

若带 Falsify 的解释器不是 `python`，设置 `FALSIFY_PYTHON`。

## 步骤 2 — 添加插件（30 秒）

```sh
dsh plugin --profile web add "github:shi275773124/falsify-dsh#v0.1.1"
```

只有声明了 `dsh.bundle.patch` 的包才会成为生效的 profile 层。本包有此声明。

## 步骤 3 — 重启并对 agent 说（30 秒）

```sh
dsh --profile web
```

然后对 agent 说下面任一句话：

| 对 agent 说 | 应发生的事 |
|---|---|
| `falsify this file` | 对当前文件跑 `falsify_review`；回执为 `PASS` / `PASS_WITH_DEBT` / `BLOCK` |
| `gate this PR` | 对照 `origin/main` 跑 `falsify_gate`；公开 CLI 上 `production` / `quant` fail-closed |
| `lint this file` | 只跑 `falsify_lint`；`L2_CLEAN` 不是放行信号 |

没有 provider key 时，真审查不可用。缺证据应得到 `BLOCK` 或 `CLI_ERROR`，不能静默变绿。

## 上限

| 工具 | 允许的含义 | 不允许 |
|---|---|---|
| `falsify_lint` | 静态标签 + blocker 标记。ceiling = `NONE`。 | 把 `L2_CLEAN` 当成 PASS 或放行授权 |
| `falsify_review` | 认知层文档审查。BYOK。`claim_bearing=false`。 | live / production / 资金授权 |
| `falsify_gate` | 公开闸门回执。`production` / `quant` fail-closed。 | Pro adapter、HMAC signer，或可承载动作的 PASS |

看起来绿，不是证明。插件回执仍是 OSS 审查。

## 验收清单

- [ ] 插件将调用的同一解释器上，`python -m falsify --help` 可用
- [ ] 重启后，agent 暴露 `falsify_lint`、`falsify_review`、`falsify_gate`
- [ ] 「lint this file」返回 `L2_CLEAN` 或 `L2_DIRTY`，绝不是放行 PASS
- [ ] 无 key 时，「falsify this file」不会编造 `PASS`
- [ ] 「gate this PR」在公开 CLI 的 `production` / `quant` 上 fail-closed

## 模式

| 模式 | Secrets | 行为 |
|---|---|---|
| 仅 lint | 无 | 跑 `falsify_lint`；不是审查回执 |
| 审查但无 key | 无 | 真审查不能跑；不得编造 PASS |
| Live BYOK | `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | 跑模型 OSS 审查；仍非权威 |
| 公开闸门 | 无 | 无 Pro adapter 时，`production` / `quant` fail-closed |

## 排障

**`verdict=CLI_ERROR`**

- `python -m falsify` 缺失，或进程拉起失败
- 安装公开 CLI，或设置 `FALSIFY_PYTHON`

**插件已列出但没有工具**

- profile 未加载 `dsh.bundle.patch`
- 重新安装插件并重启 profile

**`L2_CLEAN` 看起来像通过**

- 不是。lint 只做静态检查，不能据此放行。

**`production` / `quant` 闸门 BLOCK**

- 公开 CLI 上属预期。Pro adapter 未开放。

卸载：

```sh
dsh plugin --profile web remove falsify-dsh
```

## 延伸阅读

- [BYOK + Policy](./11-byok-and-policy.md)
- [使用 Falsify workflow packs](./17-skills.md)
- [安装 GitHub Action](./14-github-action-install.md)
- [Open Core 边界](./12-open-core-boundary.md)
