# 03. 协作规范

[English](./03-collaboration.md) · [返回 README](../README.zh-CN.md)

**这是第 1 层——互审**，抓的是*数字错*。遇到"事实对、结论却错"的高风险场景，加上第 2 层：[05 · 对抗审议](./05-adversarial-review.zh-CN.md)。

Agent 一旦不守这些规则，整套模式立刻失效。在 prompt 层强制。

## 规则 1 — 每段都标作者

Agent 写的每段都加前缀（或后缀）：

- `[AGENT-A]` — Agent A 写的
- `[AGENT-B]` — Agent B 写的
- `[BOTH]` — 双方同步后一致

代码块、表格、列表整块标。别在一个列表里把标签散落到每一行——整个列表标一次。

```markdown
[AGENT-A]
Venue A 散户费率 0bps maker / 0bps taker。2024 上线，ZK-rollup 架构，
跑在自己的 L2 上。

[AGENT-B audit]: 已与 https://docs.example-venue-a.xyz/fees 比对（2026-05-30 抓取）

[AGENT-B]
补充：Venue A 的 Premium 档（月成交 ≥$10M）是 0.004% / 0.028%。只有鲸鱼吃得到，
retail 资金远低于此线。

[BOTH]
结论：retail 资金 < $10k 的话 Venue A 实际免费。
```

## 规则 2 — 不动对方的标签块

不同意 `[AGENT-A]` 的段落时**不要直接改**。三选一：

**A — 行内审计备注**（小修小补优先）：

```markdown
[AGENT-A]
Venue B VIP0 maker 费率 1.5bps。

[AGENT-B audit]: 错。Venue B VIP0 maker 是 **rebate** -1.5bps（你**收到** 1.5bps），
不是支出。来源：https://app.example-venue-b.xyz/fees (2026-05-30)。
```

**B — 另起一段**：

```markdown
[AGENT-A]
Venue C Standard 档：5.0bps maker / 1.5bps taker。

[AGENT-B]
按官方 docs（2026-05-30），Venue C Standard 档是 **9.0bps / 3.0bps**。
[AGENT-A] 上面的数字过期，标记待修。
```

**C — 双方都同意原文错时**，原作者改自己的块并加 `[BOTH]`：

```markdown
[AGENT-A — 已修正 2026-05-30]
Venue C Standard 档：9.0bps maker / 3.0bps taker。

[BOTH] 已对照 https://docs.example-venue-c.xyz/fees（2026-05-30）核实。
```

## 规则 3 — 冲突走一手 docs

两个 agent 对一个事实分歧时，**谁声音大都不算**。只能这么裁决：

1. 找 **权威源**（官方 docs > app 截图 > 公开 API > X 帖 > KOL）
2. **现在** 抓 URL（不是 "我印象中"）
3. 把相关原文 + URL + 时间戳贴进文档
4. 把冲突段落改对

没有一手源的事实标 `[UNCONFIRMED]`，两个 agent 都不要硬编一个解决方案。

```markdown
[CONFLICT — 已裁决 2026-05-30]
[AGENT-A] 说 Venue D 稳定币对费率 0.04%。[AGENT-B] 说 0.5bps。
仲裁：按 https://docs.example-venue-d.xyz/fees（2026-05-30 抓取）：
> "stablecoin-margined perpetuals: 0.04% maker / 0.04% taker"
[AGENT-A] 对。[AGENT-B] 单位混了（0.04% = 4bps，不是 0.5bps）。
```

## 权威层级（按这个顺序）

1. 官方 API 响应（最权威——系统实际就这样）
2. 官方域名上的 docs 页
3. 官方 mobile/web app 截图
4. 官方账号验证过的公告（X/Discord/Telegram 官方 handle）
5. 官方 GitHub 上的源码
6. 可信聚合器（DeFiLlama / Dune）
7. 社区/KOL 帖子（最低，最容易错）

#4 以下的都标 `[UNCONFIRMED]`，等升级。

## 可信度分层（关键事实必标）

- **A** — 7 天内一手源核实
- **B** — 一手源核实但超过 7 天
- **C** — 二手源（聚合器、博客）
- **D** — 社区/KOL 未核实

```markdown
[AGENT-A][A] Venue A retail 费率：0bps/0bps（2026-05-30 app 内核实）
[AGENT-A][C] Venue A 日成交 ~$200M（按聚合器 2026-05-29）
[AGENT-A][D] Venue A 计划 Q4 2026 发币（X 传闻，未核实）
```

## 写区（谁负责什么）

为防两个 agent 互相冲突，定义**写区**：

- `agent-a-personal/` — 仅 A 写，B 可读
- `agent-b-personal/` — 仅 B 写，A 可读
- `shared/` — 都可写，必须标签
- 其他默认共享

软约定，靠 AGENTS.md 强制，不是文件系统权限。两个 agent 都得守。

## 仲裁清单

碰到不同意的 `[AGENT-X]` 块，过这一遍：

- [ ] 我真的抓了一手源吗？（不是凭记忆）
- [ ] 我的源在权威层级里高于对方吗？
- [ ] 我贴了原文 + URL + 时间戳吗？
- [ ] 我用 `[AGENT-Y audit]:` 行内备注了，没改对方块吗？
- [ ] 双方同意修改时，是原作者改了自己块吗？
- [ ] 我用自己的 git 身份 commit 了吗？

## 反模式（别做）

- ❌ "我觉得 Agent A 错了" 而没核源
- ❌ 直接改 Agent A 的 `[AGENT-A]` 块"修"它
- ❌ 把 `[AGENT-A]` 标签整个抠掉
- ❌ "双方都同意" 但根本没问对方
- ❌ 引训练数据当权威（"我记得是……"）
- ❌ 强推（force-push）覆盖对方 commit

## 下一步

- [故障排查](./04-troubleshooting.zh-CN.md) — 出问题怎么救
