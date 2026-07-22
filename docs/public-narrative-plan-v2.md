# Falsify 产品叙事 + 官网 / GitHub 公版修改规划（v2）

**给谁看：** 外部审计。确认叙事对不对、边界守没守住、改动是不是只动公版表面。  
**管什么：** `falsify.site` + GitHub `shi275773124/Falsify`  
**不管什么：** Hermes Pro runtime、资金权限、HMAC 生产细节  
**一条原则：** 痛点说人话，术语退后面，边界一行小字带过。

**相对 v1 的硬修正：**

1. **生产首页真源** = `design/falsify-flow-candidate/`（根路径 `/`），不是 `web/static` + `web/templates`（那是 LEGACY `/legacy/home`）。
2. **Hero 定稿** = 痛点 | 解法 **两栏**（不是单段 `heroLead` prose）。
3. **状态** = 公版叙事与 craft 已在仓库落地；live 以 merge + VPS `falsify-web` 重启验收为准（事后审计 diff，不是「冻结后再动手」）。

---

## 0. 三十秒摘要

Falsify 是 AI 时代的决策闸门——先审 claim，再信结果。

它解决两个问题：

1. AI 幻觉和假绿混进生产。
2. 代码半年后烂掉，或者被「简化」过度。

对应三层：对抗审打第一个，框架审 + Cutline 打第二个。

公开版卖的东西很窄：能装、能跑、能留回执（PASS / DEBT / BLOCK）。不卖自动部署，不卖下单，不卖资金授权。

这次改的是**文案、信息架构、首页 craft 细节**。不换引擎，不开源 Pro。

成功长什么样：陌生人 10 秒说出「少幻觉、好维护」；工程师 60 秒知道怎么装 Action。

---

## 1. 产品叙事（定稿，审计以此为准）

### 1.1 是什么 / 不是什么

**是：** 高风险 AI 声明的决策门。拿证据和工程去找茬，输出一张可复现的回执。

**不是：** 又一个 AI code review。不是「另一个模型点头了」就算过。不是全开源等于全能力。装了 skill 不等于做过 Falsify。

### 1.2 两个痛点

**假绿。** AI 让产出变快，也让假自信变便宜。日志绿了，测试绿了，另一个 AI 说「没问题」——状态并没有被证明。幻觉和假绿就这么溜进生产。

**腐烂。** 没有框架约束，半年后没人敢动。审完要么全标 P0 谁也不改，要么拿「简化」把真风险删了。

### 1.3 三层解法

```text
Falsify = 对抗审 + 框架审 + Cutline
```

- **对抗审**（Adversarial Review）→ 打假绿。证据和工程两边找茬，压住幻觉。
- **框架审**（Framework / Brooks-Lint）→ 打腐烂。抓结构问题，让代码半年后还能改。
- **Cutline**（风险裁刀）→ 打过度工程。分清必须改、可记账、该删。

输出固定三态：`PASS` / `PASS_WITH_DEBT` / `BLOCK`。JSON 回执，可留、可 diff、可重跑。

### 1.4 口号

| 用在哪 | 说什么 |
|---|---|
| Hero 大标题 | Looks green isn't proof. / 看起来绿了，还不够。 |
| Hero 传播语 | Review first. Trust after. Evidence first. Ship after. / 先审，再信；先证据，再放行。 |
| Hero 两栏 | 见 §3.2（痛点 \| 解法） |
| 品牌卡片 | Challenge the claim. Verify the authority. Gate the action. |
| 脚注小字 | 审查签收，不替你部署下单。 |

规矩：主句不写免责声明。边界只占小字。

### 1.5 公开版 vs 内部版

公开版（site + GitHub）：给工程师和 agent 工作流。三层审 + 回执 + Action + skills。讲痛点 A 和 B。

内部版（不展开卖）：量化生产。权威分层、独立审计、sole gate。不在公网站主推。

对外一句话：开源版教你 Challenge → Verify → Gate；更深的生产强制在 Pro，不默认开源。

### 1.6 什么算「做过 Falsify」

跑过权威出口（CLI / Action），留了产物。

只装 skill、只看文档、只跑首页 format demo——不算。

---

## 2. 曾经的问题（已针对改）

- **协议压过痛点** → Hero 改为两痛点 + 两解法可扫结构。
- **三层翻译失败** → How 三卡用白话主标签（对抗 / 框架 / Cutline）。
- **框架审消失** → 与 Cutline 一起进 Hero「解法」栏与 How。
- **README 太重** → 第一屏痛点优先；open core / Pro 下移。
- **改错栈风险** → 生产只认 `design/falsify-flow-candidate/`。

**仍不动：** 产品边界、open core 政策、Pro 闭源、Action 主入口、裁决三词。

---

## 3. Site 怎么改（定稿结构）

### 3.1 生产真源

| 角色 | 路径 |
|---|---|
| **Production homepage** | [`design/falsify-flow-candidate/`](../design/falsify-flow-candidate/) → `/` via `web/serve.py`（`/assets/flow/home.css` ← `candidate.css`，`home.js` ← `candidate.js`） |
| LEGACY only | `web/templates/home.html` + `web/static/js/home.js` → `/legacy/home`；可镜像叙事，**不是**公网主入口 |
| 说明 | [`web/LEGACY_HOMEPAGE.md`](../web/LEGACY_HOMEPAGE.md) |

### 3.2 Hero 定稿（两栏，不是单段 sub）

```text
eyebrow:  TWO PAINS · THREE LAYERS / 两个痛点 · 三层白话
h1:       Looks green isn't proof. / 看起来绿了，还不够。
thesis:   Review first. Trust after. … / 先审，再信；…

┌ THE PAIN / 痛点              ┌ THE FIX / 解法
│ AI 幻觉和假绿照样进生产        │ 对抗审 — 专打「看起来没问题」
│ 代码长期腐烂，或过度工程       │ 框架审 + Cutline — 好维护、不过度工程
└                              └

CTA: Install GitHub Action · Watch a claim get blocked
小字: Sign-off only. Does not deploy or trade for you.
```

**EN keys（candidate.js）：** `heroPainLabel/1/2`, `heroSolveLabel/1/2`  
**ZH keys：** 痛点 / 解法 同上语义。

DOM：`index.html` 内 `.hero-ps` / `.hero-ps-col.is-pain` / `.is-fix`。

### 3.3 How 三卡

| 标签 | 一句话说完 | 副标 |
|---|---|---|
| 对抗审 | 证据 + 工程红队，压幻觉、拦假绿 | Adversarial |
| 框架审 | 结构不烂，半年后还能改 | Framework / Brooks-Lint |
| Cutline | Must Fix / Debt / Delete，不过度工程 | 风险裁刀 |

底部保留三态。Contract 不当主标签。

### 3.4 Proof / Demo / Install

- Proof：假绿案例对齐痛点 A；可补链到框架审 docs（痛点 B）。
- Demo：format demo only，不冒充完整门禁。
- Install：主 CTA 仍是 GitHub Action。

### 3.5 Meta

- title: Falsify — Looks green isn't proof.
- description: 对抗审压幻觉与假绿；框架审 + Cutline 管长期可维护。PASS / DEBT / BLOCK 可复现回执。
- og 跟 lang 走。

### 3.6 Craft（Emil 审查落地）

| 项 | 要求 |
|---|---|
| Receipt 阶段动画 | 只用 opacity + transform；不动画 max-height/padding 导致 layout thrash |
| Button | hover 不抢 `translateY`；`:active` 保留 `scale(0.97)` |
| Spotlight | CSS vars 写在 `.hero`，不写 `documentElement` |
| Lenis 锚点 | 锚点滚动约 0.4–0.5s |

### 3.7 Site 验收

- [ ] 首屏 5 秒读出两个痛点 + 两解法（两栏可见）
- [ ] 三层名称和最初设计一致（框架 / 对抗 / cutline）
- [ ] 主句没有内部黑话
- [ ] 边界只是小字
- [ ] 没承诺自动部署 / 交易 / 资金
- [ ] 中英对齐
- [ ] 改的是 flow-candidate，不是只改 LEGACY
- [ ] CTA 导向 Action / Demo / Docs / GitHub

---

## 4. GitHub 公版

### 4.1 目标

README 第一屏：痛点 + 三层 + 30 秒上手。open core / Pro 表下移，不删。

### 4.2 结构

一句话 → 两个痛点 → 三层表 → Quick start → Skills → What you get today（缩短）→ Open core → Quant optional → Docs

### 4.3 README 顶部（EN 定稿意图）

```markdown
# Falsify

> **Looks green isn't proof.**
>
> AI made teams faster — and false confidence cheaper.
> Falsify is an open-core decision gate for high-stakes AI claims.

**Two problems it attacks:**

1. **Hallucination & false-green.** Logs green, tests green, another AI
   agreed — none of that is proof. Adversarial review red-teams evidence
   and engineering before you trust a production claim.

2. **Rot & over-engineering.** Framework review keeps systems maintainable.
   Cutline stops "everything is P0" and "delete real risk as simplicity."

Falsify = Framework review + Adversarial review + Cutline

Output: PASS / PASS_WITH_DEBT / BLOCK — a receipt you can keep, diff, re-run.

MVP: GitHub Action on PR / deploy / decision claims.
Gates review, not payments or live deploy.
```

中文 README 同结构。

### 4.4 其它文件

- `docs/00-getting-started`（+ zh）— 开头两痛点
- `docs/github-action-share-pack.md` — 传播句白话
- `examples/real-cases/SHARE-CARDS.md` — 标题对齐 A/B
- `docs/12` / `18` / ROOTFIX — **不动**
- `skills/*/SKILL.md` — 可选顶注

### 4.5 验收

- [ ] 不读 docs 也能懂两个痛点
- [ ] 三层和站点一致
- [ ] Open core 还在，没暗示 clone = 全能力
- [ ] Claiming 定义还在
- [ ] Quant 标 optional
- [ ] 中英同步

---

## 5. 不改（红线）

- 裁决三词 `PASS` / `PASS_WITH_DEBT` / `BLOCK`
- Open core 边界、Pro 闭源
- Hermes / HMAC / Calvin 不进 hero
- Site 不变成托管 SaaS（self-host + BYOK）
- 不借文案改引擎行为
- 「审查 ≠ 自动执行」不删

---

## 6. 执行状态（相对 v1 时间表）

| 阶段 | v1 计划 | v2 现实 |
|---|---|---|
| P0 叙事冻结 | 审计后再动 | 叙事已定稿于本文 + 已实现文案 |
| P1 Site | home.js LEGACY | **flow-candidate** hero 两栏 + craft |
| P2 README | 待做 | 已改第一屏 |
| P3 入口件 | 待做 | getting-started / share-pack / SHARE-CARDS |
| P4 可选 | skills 顶注 | 按需 |
| P5 上线 | 运维 | merge main + VPS `git pull` + `systemctl restart falsify-web`；curl 验收 hero-ps |

回滚：git revert 相关 commit；无 schema 迁移。

---

## 7. 审计检查表

**叙事：**

- [ ] 痛点是人话，覆盖三层
- [ ] 没有「保证永不翻车」之类绝对化
- [ ] 公开 / Pro 边界清楚

**Site：**

- [ ] 执行了 §3（含两栏 Hero + 正确栈）
- [ ] 中英对齐
- [ ] 没只改 LEGACY 当完成

**GitHub：**

- [ ] 第一屏痛点优先
- [ ] open core 在，位置合理
- [ ] 和 site 同一套口号

**回归：**

- [ ] `python -m falsify demo` 没断
- [ ] Action 安装路径没坏
- [ ] 没泄漏密钥或内网路径
- [ ] live `https://falsify.site/` 可见痛点/解法两栏（部署后）

**判定：**

- [ ] **PASS** — 实现与本文一致，可合入/可上线
- [ ] **PASS_WITH_DEBT** — 可上线，列出 Must Fix
- [ ] **BLOCK** — 栈错误或叙事回退到协议腔

---

## 8. 最小 diff（v2 路径）

```text
Must change (production surface):
  design/falsify-flow-candidate/index.html
  design/falsify-flow-candidate/candidate.js
  design/falsify-flow-candidate/candidate.css
  design/falsify-flow-candidate/flow-motion.js   # craft: spotlight + Lenis
  README.md
  README.zh-CN.md

Should change:
  docs/00-getting-started.md
  docs/00-getting-started.zh-CN.md
  docs/github-action-share-pack.md
  examples/real-cases/SHARE-CARDS.md
  web/static/js/home.js              # LEGACY mirror only
  web/templates/home.html            # LEGACY mirror only

Do not change:
  docs/12-open-core-boundary.md
  docs/18-pro-vs-oss.md
  docs/ROOTFIX-architecture.md
  falsify/ engine code
  Pro / Hermes skill tree
```

---

## 9. 贴 PR 用的一段话

Falsify 拦两件事：AI 幻觉和假绿进生产；代码烂掉或被过度工程。

三层——对抗审、框架审、Cutline——输出 PASS / DEBT / BLOCK。

公开版只卖「能装、能审、能留回执」。深的生产强制在 Pro。

这次改的是公版叙事与生产首页（flow-candidate）：Hero 两栏痛点/解法 + README 第一屏白话 + craft 修。引擎不动，Pro 不开源。

---

## 10. 实现对照（给审计）

| 规划要求 | 仓库落点 |
|---|---|
| 两痛点 + 三层 | `candidate.js` i18n + README 首屏 |
| Hero 两栏 | `index.html` `.hero-ps` |
| 边界小字 | `heroNote` / footer |
| Craft Top3 | `candidate.css` / `candidate.js` delays / `flow-motion.js` |
| LEGACY 镜像 | `web/static/js/home.js` 等（非 live 主路径） |

---

**状态：** v2 定稿（路径 + Hero + 时序已修正）。  
**下一步：** 外部审计按 §7；live 以 P5 curl 证据关闭。
