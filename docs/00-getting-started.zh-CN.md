# 快速开始

**看起来绿了，还不够。**

两个痛点：**AI 幻觉与假绿** → 对抗审；**长期腐烂 / 过度工程** → 框架审 + Cutline（该改改、该记记、该删删）。

Falsify 是本地 BYOK 审查工具链，产出签收回执：`PASS` / `PASS_WITH_DEBT` / `BLOCK`。只做审查签收，不自动部署、不下单。

## 安装

```bash
git clone https://github.com/shi275773124/Falsify.git
cd Falsify
python -m pip install -e .[dev]
```

## 运行本地 demo

Demo 不调用模型。它对 fixture 跑确定性本地规则，返回真实 Falsify 形态的裁决。

```bash
python -m falsify demo
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
python -m falsify review report.md --provider deepseek
```

也可用本地 agent CLI：

```bash
python -m falsify review report.md --provider claude
python -m falsify review report.md --provider codex
```

## 跑完整闭环

```bash
python -m falsify run brief.md --drafter claude --reviewer deepseek
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

每张回执还带 `claim_scope` 与 `authority_ceiling`。开源回执为 `EPISTEMIC_ONLY`、`capital_authority: NONE`：它只记录该范围内证明了什么，永远不授权付款、部署或其他实时动作。能授权动作的 `PASS` 还需要 authority adapter 与统一 kernel。
