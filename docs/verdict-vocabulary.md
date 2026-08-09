# Verdict vocabulary（统一裁决词）

> 根治白皮书缺口 #3。详见 [ROOTFIX-architecture.md](./ROOTFIX-architecture.md)。

## Core（OSS 协议必须支持）

| Verdict | 含义 | 退出码建议（CLI） |
|---------|------|-------------------|
| `PASS` | 证据成立，当前范围无 Must Fix | 0 |
| `PASS_WITH_DEBT` | 无当前阻塞；每笔 Known Debt 有 upgrade trigger | 0 或 1（策略可选；文档须固定） |
| `BLOCK` | 有 Must Fix / 缺证据 / 不可审计 | 1 |

Cutline（与 verdict 正交）：`Must Fix` | `Known Debt` | `Delete`。

Schema 名：`falsify.review.v1`（核心三词）。

## Receipt authority fields（回执权威字段，必备）

每张回执除 Core verdict 外，必须同时可见以下字段；缺任何一个，回执视为不完整：

| 字段 | 含义 | 示例 |
|------|------|------|
| `claim_scope` | 本裁决覆盖的声明范围；范围外不保证 | `deployment_revision` |
| `llm_semantic_verdict` | LLM 对抗审查层的语义裁决 | `PASS` |
| `evidence_verdict` | 可执行证据检查层的裁决 | `BLOCK` |
| `final_verdict` | kernel 合成的最终裁决（取更保守者） | `BLOCK` |
| `authority_ceiling` | 该裁决的权威上限 | `EPISTEMIC_ONLY`（OSS 默认） |
| `capital_authority` | 该裁决可动用的资金权限 | `NONE` |

规则：

1. `authority_ceiling: EPISTEMIC_ONLY` 的回执只界定「该范围内证明了什么」，**不授权任何动作**（合并、付款、部署、live 均不授权）。
2. action-bearing `PASS` 必须同时满足：authority adapter 接入 + 可执行证据通过 + 统一 kernel 签发；三者缺一，ceiling 停留在 `EPISTEMIC_ONLY`。
3. 页面、文档、样例回执不得只展示裸 `PASS`/`BLOCK` 而不带 `claim_scope` 与 `authority_ceiling`。

## Extensions（Pro / ASP 可发出）

| Verdict | 含义 | 导出到 Core 时 |
|---------|------|----------------|
| `KILL` | thesis 死；同证据窗禁止拧旋钮救活 | → `BLOCK` + `findings[].class = thesis_dead` |
| `CANDIDATE_NEEDS_NEXT_GATE` | 允许存在，但无 live 权威；须点名下一闸 | → `PASS_WITH_DEBT` 若债务可写清 trigger；否则 `BLOCK` |
| `NO_DECISION_INSUFFICIENT_EVIDENCE` | 证据不够下判断 | → `BLOCK` + `class = insufficient_evidence` |
| claim_ceiling 等 | 主张上限（DIAGNOSTIC_ONLY…） | 进 `meta.claim_ceiling`；verdict 仍用 Core/Extension |

## 规则

1. **对外消费者默认只保证 Core。**  
2. 发出 Extension 时 JSON 必须可被 Core 解析器 **安全降级**（未知 enum → 当 `BLOCK` 或映射表）。  
3. 禁止第三套同义词（如 PROCEED/HOLD 仅作 legacy 输入映射进 Core）。  

## Legacy 输入映射（已有 CLI）

| 旧 | 新 |
|----|-----|
| PROCEED | PASS |
| HOLD | BLOCK 或 PASS_WITH_DEBT（按实现；当前 web 多映 BLOCK） |
| ARCHIVE | BLOCK |

## 测试要求（落地时）

- 未知 extension → 不崩溃  
- KILL 降级 → BLOCK + class  
- Core round-trip 样例 fixtures 保持绿  
