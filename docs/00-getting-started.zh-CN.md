# 快速开始

Falsify 是针对 AI 生成代码、研究与生产决策的对抗审框架。

产出三种裁决之一：

- `PASS`
- `PASS_WITH_DEBT`
- `BLOCK`

## 安装

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]
```

## 运行本地 demo

Demo 不调用模型。它对 fixture 跑确定性本地规则，返回真实 Falsify 形态的裁决。

```bash
python falsify.py demo
```

预期输出形态：

```text
[AGENT-B audit] logs are treated as state verification
Cutline: Must Fix
VERDICT: BLOCK
```

## 用模型审查文件

```bash
export DEEPSEEK_API_KEY=sk-...
python falsify.py review report.md --provider deepseek
```

也可用本地 agent CLI：

```bash
python falsify.py review report.md --provider claude
python falsify.py review report.md --provider codex
```

## 跑完整闭环

```bash
python falsify.py run brief.md --drafter claude --reviewer deepseek
```

尽量让作者与审查者上下文独立。若两角色落到同一模型或 agent 命令，Falsify 会警告独立性被削弱。

## 启动本地网站

```bash
python web/serve.py
```

打开 `http://127.0.0.1:8000`。

首页介绍框架。审查面板调用真实配置的后端；若无 provider/key 会返回 setup 错误。

## 裁决语义

`PASS` 表示当前决策证据足够。

`PASS_WITH_DEBT` 表示当下无阻塞项，但记录了真实 Known Debt，且带有具体升级触发条件。

`BLOCK` 表示仍有 Must Fix、当前证据缺失，或审计结果无法解析。
