# CLI 与产物参考

## 命令

| 命令 | 需要你的密钥？ | 用途 |
|---|---:|---|
| `falsify demo` | 否 | 用确定性的假绿 fixture 确认本地安装。 |
| `falsify lint FILE` | 否 | 检查协作标签和 ship-blocker 约定。 |
| `falsify review FILE --provider NAME --json` | 是，供 provider 支持的审查使用 | 为一个文件生成机器可读的裁决。 |
| `falsify run BRIEF --drafter NAME --reviewer NAME` | 通常需要 | 运行起草—审查循环；尽可能保持作者与审查者的上下文独立。 |
| `falsify init` | 否 | 写入本地配置模板。 |

provider 支持的审查可以使用你的 provider API key，也可以使用已在本机认证的兼容 agent CLI。`demo` 和 `lint` 不会调用模型。

## 保存一次审查

```bash
mkdir -p artifacts
falsify review report.md --provider deepseek --json > artifacts/falsify-review.json
```

保存输入、JSON、命令和 provider 上下文，以及用于支持声明的所有原始证据。一份结果只是某次运行针对某个输入的证据；它不构成持续保证。

## GitHub Action 产物

PR 模板会写入并上传：

- `falsify-report.json`，供工具和下游检查使用；
- `falsify-report.md`，供阅读 PR 的人使用；
- 当 workflow 在 pull request 上运行时，生成一条 PR 摘要评论。

未设置 `FALSIFY_API_KEY` 时，模板会报告已跳过实时审查，并保持在仅 lint 的模式。这是一种明确的 advisory 状态，而不是模型裁决。

## 退出行为

`PASS` 和 `PASS_WITH_DEBT` 会成功退出；`BLOCK` 会以非零状态退出。CI 可以据此使检查失败，但应先在自己的文档上观察模板表现，再将分支保护设为必需。
