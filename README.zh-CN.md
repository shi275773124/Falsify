# Falsify

> **别再相信自信的 AI。**

Falsify 是一个面向 AI 时代的对抗式审计框架。它攻击错误信心，逼出真实证据，并把每一个风险切成 **Must Fix**、**Known Debt** 或 **Delete**。

Falsify 不是“另一个模型说看起来没问题”。它是一个决策框架，用来把真正的阻塞项和噪音分开。

[English](./README.md) · [Getting Started](./docs/00-getting-started.md) · [Adversarial Review](./docs/05-adversarial-review.md) · [Risk Scalpel](./docs/06-risk-scalpel.md)

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
Falsify = Brooks-Lint + Adversarial Review + Risk Scalpel
```

| 层 | 发现什么 | 产出 |
|---|---|---|
| Brooks-Lint | hidden state、implicit authority、duplicated control paths、brittle rollback、unverifiable acceptance、AI summary 替代 raw evidence | 结构性审计目标 |
| Adversarial Review | false truth、false risk、silent failure、stale data、permission drift、fake acceptance evidence、semantic verdict nudge、prompt-only audit theater、monitor failure laundering | 对抗式 findings |
| Risk Scalpel | 把所有风险都当 P0，或用“简化”删除真实风险 | Must Fix / Known Debt / Delete |

最终输出：

- `PASS`：证据成立，没有当前阻塞项。
- `PASS_WITH_DEBT`：没有当前阻塞项，且每个 Known Debt 都有升级触发条件。
- `BLOCK`：仍有 Must Fix，当前决策缺证据，或审计结果不可解析。

## 快速开始

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]

# 无 API key：本地 fixture demo。
python falsify.py demo

# 无 API key：本地 tag/blocker lint。
python falsify.py lint examples/comparison-case-study/05-final-excerpt.md

# 真实模型审计。
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md --provider deepseek

# 一个模型写，另一个模型审。
python falsify.py run brief.md --drafter claude --reviewer deepseek
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

## 继续关注

Falsify 会继续围绕 AI agent、代码审查和生产风险工作流演进。如果你也在做类似问题，欢迎关注或联系。

- GitHub: https://github.com/shi275773124/Falsify
- X / Twitter: https://x.com/YOUR_HANDLE
- Email: YOUR_EMAIL@example.com

## License

MIT. See [LICENSE](./LICENSE).
