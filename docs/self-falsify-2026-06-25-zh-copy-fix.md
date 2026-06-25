# Self-Falsify audit — 2026-06-25 (中文文案打磨)

**Scope:** self-Falsify (same agent/repo author; not independent final judgment)  
**Targets:** Chinese documentation copy fixes — 5 files, 47 lines changed  
**Method:** Brooks-Lint → Adversarial Review (Claude Sonnet 4.6 via cliproxy) → Cutline  
**Reviewer model:** claude-sonnet-4-6 (independent model family)  
**Reviewer prompt:** Falsify SKEPTIC_SYSTEM (adversarial, no politeness)  

---

## 改动范围

| 文件 | 改动 | 内容 |
|---|---|---|
| `docs/01-architecture.zh-CN.md` | 38 行 | 中英混杂→中文, 生硬翻译修正 |
| `docs/03-collaboration.zh-CN.md` | 8 行 | 口语化修正, "反 pattern"→"反模式" |
| `docs/05-adversarial-review.zh-CN.md` | 23 行 | reviewer→审议者, 术语加中文注释 |
| `docs/06-risk-scalpel.zh-CN.md` | 21 行 | silent failure 加注释, review findings→审查发现 |
| `web/static/js/home.js` | 2 行 | "几分钟试出裁决"→"几分钟跑一次裁决" |

**总改动:** 5 files changed, 47 insertions(+), 45 deletions(-)

---

## Verification table

| Gate | Command | Result |
|---|---|---|
| Lint (改动后) | `falsify.py lint docs/01-architecture.zh-CN.md` | ✓ no open ship-blockers (untagged prose = 文档文件固有,非 agent 协作稿) |
| Lint (原版对比) | `git stash && falsify.py lint docs/01-architecture.zh-CN.md` | 原版同样结果 — **改动未引入新 lint 问题** |
| Demo | `falsify.py demo` | ✓ PASS (exit 1, VERDICT: BLOCK — 预期行为) |
| Pytest | `pytest tests/ -q` | 50 passed, 1 failed (预存版本号不匹配,与改动无关) |
| 残留 grep | 全问题词扫描 | ✓ 所有目标词已清除或合理保留 |

---

## Adversarial Review findings (Claude Sonnet 4.6)

Reviewer 输出 8 个 findings + **VERDICT: BLOCK**。

### Cutline table

| # | Finding | Failure mode | Class | 改动引入? | Minimal action | Upgrade trigger |
|---|---|---|---|---|---|---|
| F1 | Obsidian Sync 定价 "$4-8/月" 未核实, "单用户" 描述可能不准 | 读者可能引用错误定价 | **Known Debt** | ❌ 原版 | 核实 obsidian.md/pricing 当前价格 | 如果读者引用本文定价做采购决策 |
| F2 | "30% 概率某个具体数字错了" 无来源 | 虚构统计数据做说服锚点 | **Known Debt** | ❌ 原版 | 加来源或改为"根据经验,错误率显著" | 如果被引用为实测基准 |
| F3 | 跨文件链接 (02/03/README) 未审 | 链接可能断裂或内容不一致 | **Delete** | ❌ 原版 | 已验证: 4 个文件均存在 ✓ | N/A — 已验证存在 |
| F4 | "罕见" 描述共享前提错误, 无引用 | 低估已知风险 | **Known Debt** | ❌ 原版 | 删"罕见"或改为"难以检测" | 如果同模型族部署场景被忽略 |
| F5 | Obsidian Git 多写者冲突未说明 | 数据丢失风险 | **Known Debt** | ❌ 原版 | 文档化冲突解决策略 | 如果实际部署出现冲突 |
| F6 | Notion/Google Docs 对比描述模糊 | 对比不公平 | **Delete** | ❌ 原版 | 不足以阻断当前交付 | N/A |
| F7 | "GitHub 私有 repo 免费" 无限定条件 | 读者可能误解组织账户限制 | **Delete** | ❌ 原版 | 不足以阻断当前交付 | N/A |
| F8 | 架构无 PoC 证据, 纯设计文档 | 架构 theater | **Known Debt** | ❌ 原版 | 加"这是提议架构"声明 | 如果用于采购决策 |

---

## Verdict

**PASS_WITH_DEBT**

### 理由

1. **本次改动范围 = 中文文案打磨**(中英混杂→中文, 生硬翻译修正, 口语化修正)。8 个 finding **全部是原版已存在的内容/证据问题**,没有一个是文案改动引入的。

2. **改动未引入新的 failure mode:**
   - lint 结果与原版一致(untagged prose 是文档文件固有状态)
   - demo + pytest 结果不变
   - 所有链接文件验证存在
   - 翻译改动不改变任何技术声明或数字

3. **Known Debt items (F1/F2/F4/F5/F8)** 都是架构文档层面的证据问题,属于产品 roadmap 而非文案翻译 scope。已登记升级触发条件。

4. **Delete items (F3/F6/F7)** 不足以阻断本次文案改动交付。

### 本次改动不覆盖的 scope

- 架构文档的事实核查(定价、统计数字、冲突策略)
- 英文版文档的同等问题(本次只改 zh-CN)
- 代码逻辑改动(本次纯文案)

---

## 反思:对抗审发现了什么

Claude Sonnet 审出的问题质量很高——特别是 F2(30% 无来源)和 F5(Obsidian Git 多写者冲突)。这些是**原作者(Chris)写的架构文档里的内容问题**,不是翻译问题。

这次 self-falsify 证明了:
1. **文案打磨不引入新风险** — 翻译改动是 surface-level,不改技术声明
2. **独立模型能审出原作者的盲区** — F2/F5 是 Chris 写文档时的认知盲点
3. **Cutline 的价值** — 8 个 BLOCK-level findings 裁成 0 个 Must Fix,因为都不在本次改动 scope 内

---

## 下一步

1. **本次文案改动可 ship** — patch 在 `/tmp/falsify-docs`,可直接 `git push`
2. **F2/F5 建议单独 issue** — "30% 无来源"和"Obsidian Git 冲突策略"是真实风险,值得原作者修
3. **英文版文档有同等问题** — 如果要改,应 EN + zh-CN 同步
