# 12. Open Core 边界

[返回 README](../README.zh-CN.md)

本文定义什么保持开源、什么收费、什么刻意延后。

核心原则：

**协议开源，工作流系统收费。**

OSS / Pro / Team 三层地图（命名、导出策略、护城河）见 [Pro vs OSS](./18-pro-vs-oss.zh-CN.md)。

## 定位

Falsify 不是「AI 代码审查器」。  
Falsify 是 **AI 时代工作的决策闸门**。

代码审查与 lint 能拦住很多问题，但仍主要在问：「diff 看起来对吗？」  
Falsify 问：「这个决策站得住脚吗？」

## 开源 vs 付费边界（当前）

### 协议

- **开源**
  - 裁决语义：`PASS / PASS_WITH_DEBT / BLOCK`
  - Cutline 语义：`Must Fix / Known Debt / Delete`
  - `falsify review --json` 的 JSON schema
- **付费（预留）**
  - 超出核心 cutline 的企业自定义分类

### CLI

- **开源**
  - `falsify lint`
  - `falsify review --json`
  - `falsify demo`
- **付费（预留）**
  - 团队 runner 编排
  - 队列 / 并发控制

### GitHub / CI 闸门

- **开源**
  - 基础 workflow 模板
  - BYOK 执行
  - JSON + Markdown 产物
- **付费（预留）**
  - 托管 GitHub App
  - 组织级 rollout 控制与治理

### Policy

- **开源**
  - `.falsify/policy.yml` 基础字段
- **付费（预留）**
  - policy UI
  - 审批工作流
  - policy 版本历史与治理

### 报告

- **开源**
  - 本地/CI 产物（`falsify-report.json`、`falsify-report.md`）
- **付费（预留）**
  - 历史存储
  - 跨仓库聚合
  - 趋势与治理报告

### 集成

- **开源**
  - 示例与 webhook 模式
- **付费（预留）**
  - 生产级集成（Linear/Jira/Slack/SIEM）

### 部署

- **开源**
  - 本地 + CI 使用
- **付费（预留）**
  - 私有部署、SSO、RBAC、审计日志

## 当前刻意不做

- 过早拆仓库
- 完整 SaaS 仪表盘
- 托管计费复杂度
- 多模型投票系统

## 何时再考虑物理拆仓

仅当以下全部成立时，才拆成 `falsify` + `falsify-team`：

1. Team 功能对至少一个付费设计伙伴已稳定
2. API/schema 边界已版本化
3. 多仓开发开销低于单仓混淆成本

## Known Debt — 开源核心商业模式

**为何暂不阻塞：** OSS 协议与 MIT 模板已可自托管。dbt/Vault 式 open core 只是「协议开源、工作流收费」的类比，不是 Falsify Team 会转化的证据。

**升级触发：** 当营销写「open core 已验证」、发布漏斗/转化数据，或签下首个付费 Team 客户却未更新本节时，升为 Must Fix。