# 01. 架构

[English](./01-architecture.md) · [返回 README](../README.zh-CN.md)

## 问题

单 agent 写研究稿会静默出错。Agent 笃定地写出费率表、配置片段、API 合约——30% 概率某个具体数字错了。没有第二双眼睛，这种错就发出去了。

人工 review 能抓到一部分，但人没耐心逐段追每一条引用 URL。

第二个 agent 有。

## 这套模式

跑两个 agent，**提示词不同，模型不同（最好），上下文独立**，但指向**同一个可写知识库**。轮流来：

1. Agent A 起稿
2. Agent B 读、审、行内备注、改错
3. Agent A 看 B 的改动，接受或反驳
4. 两轮都活下来的冲突 → 走一手 docs 裁决

共享知识库选 **Obsidian vault**：
- 纯 markdown（git diff 友好）
- 双向链接（wikilink）
- 本地优先（不绑云）
- 给人类读的桌面 app 免费

同步层选 **git**：
- 开发者都会
- 每 commit 有作者身份（审计轨迹）
- 想分支就分支
- GitHub 私有 repo 免费

本地 Obsidian 自动同步用 **Obsidian Git 插件**（社区版，免费），定时 poll 自动 pull/push。

## 拓扑

```
            ┌──────────────────────────────────┐
            │   GitHub 私有 repo                │
            │   = 唯一真相源                    │
            └──────────────────────────────────┘
              ▲          ▲           ▲
              │          │           │
       git    │   git    │   Obsidian Git 插件
       push   │   push   │   （自动 pull/push）
              │          │           │
       ┌──────┴──┐  ┌────┴────┐  ┌───┴────────┐
       │ Agent A │  │ Agent B │  │ 本地 Obsidian│
       │ (VPS 1) │  │ (VPS 2) │  │             │
       └─────────┘  └─────────┘  └─────────────┘
```

三个写入者，一份真相。每个写入者有自己的 git author，`git log` 就是完整 provenance。

## 为什么胜过 Obsidian Sync / Notion / Google Docs

| 关注点 | 本方案 | Obsidian Sync | Notion | Google Docs |
|---|---|---|---|---|
| 多 agent 写权限 | ✓ | ✗（付费，单用户）| 部分（API 限制）| 部分（重 auth）|
| 段级作者归属 | ✓（标签 + git blame）| ✗ | 仅评论 | 仅建议 |
| 可 diff 历史 | ✓（git）| 仅版本 | 部分 | 仅建议 |
| 离线优先 | ✓ | ✓ | ✗ | ✗ |
| 免费 | ✓ | ✗（$4-8/月）| freemium | 免费 |
| 自托管 | ✓ | ✗ | ✗ | ✗ |

杀手锏是 **段级可 diff 作者历史**。出问题时，`git blame` + `[AGENT-X]` 标签直接告诉你谁、什么时候写的。

## 为什么这套有效（无聊的原因）

两个 agent 对一个事实分歧 → 形成 **结构化冲突**，便于仲裁。仲裁规则（一手 docs）把 "agent 嘴硬" 变成 "官方文档怎么写"。

单 agent 没这种强制机制。它会用笃定的语气抹平自己的不确定。

## 这套能抓到的错误

- **编造的费率档** → 另一 agent 读同一来源抓到
- **过期缓存** → 另一 agent 实抓抓到
- **单位错乱**（bps vs %，日 vs 年化）→ 段级审计抓到
- **过时的 API 端点** → 另一 agent 真去请求抓到

## 这套抓不到的

- 两个 agent 共享同一个错误前提（罕见但可能——比如训练数据都过时）
- 两个 agent 都跳过一手核查（这个靠规则约束，不靠模式）
- 共享知识库本身被污染（git 历史可救）

第一个加第三 agent 或人工抽查。第二个要在 prompt 层强制——见 [03-collaboration.zh-CN.md](./03-collaboration.zh-CN.md)。

## 下一步

- [部署](./02-setup.zh-CN.md) — 30 分钟跑起来
- [协作规范](./03-collaboration.zh-CN.md) — 标签 + 冲突协议
