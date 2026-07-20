# Falsify 根治架构（ROOTFIX）

> **日期**：2026-07-10  
> **目标**：根治白皮书 §10 八条缺口——结构一次钉死，不再靠口头纪律补丁。  
> **原则**：一份权威、一条版本轨（对外）、一套裁决词、一种 Claiming 定义、双仓只做分发不另起产品。  
> **开源纪律（Chris 2026-07-10）**：**不要全部开源。** Open core = 协议 + 可演示表面；**Pro 强制、真金抗体、hermes 运行时默认闭源。** 开源是产品策略，不是义务。  
> **状态**：契约已写；本地主仓可先落地文档/协议；hermes symlink **改生产前必须 Chris 授权**。

---

## 1. 终局一句话

```text
一个产品 Falsify · 默认不全开源
  ├── 公开（MIT，故意收窄）：协议 · 基础 CLI · 签收 packs · 脱敏案例 · 站点
  ├── 分发壳 falsify-skill：可装入口（薄）；不导出 Pro scripts
  └── 闭源 Pro 运行时（默认）：唯一 skill 树 · production/quant sole gates ·
        事故 fixture 库 · hermes 接线 · dual-model 生产签收
Claiming Falsify = 跑权威出口（公开 CLI 或 Pro sole gate），不是读散文
```

### 1.1 永远不要进公开 GitHub 的（denylist 摘要）

完整表见 [Pro vs OSS](./18-pro-vs-oss.md) Export denylist。硬记：

| 闭源 | 原因 |
|------|------|
| 完整 umbrella `falsify` skill + `scripts/*` 生产门 | 真金强制与抗体库 |
| 完整负向 fixture / 事故 raw | 付费更新面 + opsec |
| hermes 路径、账户、cron 接线 | 生产拓扑 |
| 未脱敏 vault 事故 | 隐私 |
| dual-model 生产签收合同细节 | 信任模型，非协议 |

**允许公开**：裁决词、Cutline、脱敏 case、pack 工作流骨架、基础 `falsify review`、**可选** quant 库的**已决定导出子集**（若某天收紧 quant 也不违反 ROOTFIX——公开面可再窄，不可再偷塞 Pro）。

---

## 2. 八条缺口 → 根治手段

| # | 缺口 | 根治（终局） | 非根治（禁止当完成） |
|---|------|--------------|---------------------|
| 1 | 多物理副本漂移 | **一份 canonical skill 树**；default/second/third **symlink 指向它** | 每次手抄 rsync「尽量同步」 |
| 2 | 版本号四套 | **对外只认主仓 semver**（`falsify/__init__.py`）；Pro/skill 分轨标注 | 一页里并列 0.6 / 0.9 / 0.1 当同一产品 |
| 3 | 裁决词两套 | **统一 schema**：核心三词 + 可选扩展 `KILL` 等；导出表写死 | 各仓各写各的 |
| 4 | A 强制真空 | pack **声明强制出口** = 主仓 CLI / CI Action；pack 只定义 claim 类型 | 假装装 skill = 过 Falsify |
| 5 | 双仓像两产品 | **主仓 = 产品**；falsify-skill = **分发/ASP 壳**；双向链 + 同源协议 | 两套独立叙事 |
| 6 | 叙事失焦 | 主仓/站点 **产品主轴固定**；quant 为深度域 | hero 堆 PBO |
| 7 | falsify-skill 假完成 | 端点/支付 **未 live 不得写成 live**；能跑则接主仓 quant CLI | example.com 装生产 |
| 8 | 启发式冒充论文 | 阈值 **config + `[heuristic]`**；hard BLOCK 须有验证 artifact 或降 WARN | 静默当 Bailey 级 |

---

## 3. 权威拓扑（治本图）

```text
                    ┌─────────────────────────────────────┐
                    │  Protocol authority                 │
                    │  falsify.review.v1 (+ extensions)   │
                    │  docs/verdict-vocabulary.md         │
                    └──────────────────┬──────────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ GitHub Falsify   │      │ falsify-skill    │      │ Pro runtime      │
│ (product OSS)    │◄─────│ (distribution)   │      │ (enforcement)    │
│ CLI · packs · web│ depends│ thin SKILL.md   │      │ ONE tree only    │
│ VERSION = public │      │ pins OSS version │      │ symlink profiles │
└──────────────────┘      └──────────────────┘      └────────▲─────────┘
                                                             │
                                                    sole: production_falsify_gate
                                                          quant_falsify_gate
                                                          l2_static_check
```

### 3.1 Canonical Pro 路径（终局）

推荐（hermes）：

```text
/home/ubuntu/.hermes/skills/automation/falsify   ← CANONICAL（唯一可写）
/home/ubuntu/.hermes/profiles/second/skills/automation/falsify → symlink → CANONICAL
/home/ubuntu/.hermes/profiles/third/skills/automation/falsify  → symlink → CANONICAL
```

Windows 本机：

```text
%USERPROFILE%\.grok\skills\falsify   与  %USERPROFILE%\.claude\skills\falsify
→ 终局：一个真身，另一个 junction/symlink（或明确「同步脚本从真身推」且 CI 校验 hash）
```

**写规则**：只写 CANONICAL；profile 副本只读。

### 3.2 分发仓 falsify-skill（终局）

```text
falsify-skill/
  SKILL.md          # 何时审回测、如何调主仓 CLI 或已声明 ASP
  plugin.yaml
  examples/
  # 禁止：复制整份 Pro scripts 当第二真相
```

- **短期**：诚实 Prototype；`audit` 未 live 则只暴露 `python -m falsify.quant_gate` 本地路径。  
- **中期**：主仓 monorepo `distribution/falsify-skill` → CI 推送到 `shi275773124/falsify-skill`（单源）。  
- **长期**：ASP 真端点 + 收据；仍依赖主仓协议版本号。

---

## 4. 版本轨（治本）

详见 [`VERSIONING.md`](./VERSIONING.md)。

| 轨 | 权威文件 | 对外？ |
|----|----------|--------|
| **Public product** | `falsify/__init__.py` → `VERSION` | **是**（唯一徽章） |
| **OSS packs** | 随 public product；changelog 写 packs 变更 | 不单独立徽章 |
| **Pro skill** | Pro `SKILL.md` metadata.version | **否**（对内 cockpit） |
| **falsify-skill** | 其 `version` + `depends_on: falsify==X.Y.Z` | 分发壳版本，README 写「requires Falsify X.Y」 |

---

## 5. 裁决词（治本）

详见 [`verdict-vocabulary.md`](./verdict-vocabulary.md)。

```text
Core (OSS 必实现):  PASS | PASS_WITH_DEBT | BLOCK
Extensions (Pro/ASP 可发): KILL | CANDIDATE_NEEDS_NEXT_GATE | NO_DECISION_INSUFFICIENT_EVIDENCE | …
导出到仅支持 Core 的通道时:
  KILL → BLOCK + finding.class=thesis_dead
  CANDIDATE_* → PASS_WITH_DEBT 或 BLOCK（按是否允许 next gate）— 见映射表
```

---

## 6. Claiming Falsify（治本定义）

```text
Claiming Falsify =
  (1) 跑了权威出口之一，且
  (2) 保留命令行 + 退出码/JSON artifact，且
  (3) 裁决词落在统一词汇表

权威出口:
  · 主仓: python -m falsify … / quant_gate / CI Action
  · Pro:  production_falsify_gate | quant_falsify_gate | l2_static_check
  · ASP:  仅当端点返回可验证 receipt 且声明 gate_version

非 Claiming:
  · 只读了 SKILL.md / 白皮书
  · 另一个模型「同意」
  · proxy 脚本 / 手写 PASS
```

packs 每个 `SKILL.md` 必须含本节链接（落地时批量加）。

---

## 7. 启发式阈值（治本）

```text
config/heuristics.yaml  (或 contract 字段)
  calmar_floor: 0.3
  edge_cost_ratio: 1.5
  label: heuristic
  paper_backed: false

gate 行为:
  · paper_backed=false 且无 validation_artifact → 默认 WARN 或 BLOCK 但 finding 标 heuristic
  · 升 hard BLOCK 前必须有 permutation/fixture 路径
```

---

## 8. 实施阶段

### Phase 0 — 契约（本机主仓，无生产） 

- [x] ROOTFIX-architecture.md  
- [x] VERSIONING.md  
- [x] verdict-vocabulary.md  
- [x] 主仓 README / README.zh-CN 产品族 + Claiming  
- [x] 白皮书 §10 指向 ROOTFIX  
- [x] open-core-boundary 链到 ROOTFIX  

### Phase 1 — 主仓结构（本地 OSS，可 PR）

- [x] `skills/README.md`：Claiming 定义  
- [x] 五 pack 各加 Authority exit 段  
- [x] verdict-vocabulary 文档（schema 代码改可随后 PR）  
- [ ] heuristics 标签进 quant 代码注释 / config（下一刀）  

### Phase 2 — 分发仓诚实化（falsify-skill）

- [ ] README 顶部：依赖主仓 + Prototype 边界（推 skill 仓）  
- [ ] 去掉/降级假 live 端点  
- [ ] 本地默认：`pip install falsify[quant]` + quant_gate  

### Phase 3 — Pro 单副本（**生产，需 Chris 授权**）

- [ ] 选定 CANONICAL  
- [ ] second/third（及 default 若适用）改 symlink  
- [ ] 删第二物理树前备份 + sha 验收  
- [ ] watchdog 检查「是 symlink 且目标正确」而非只 diff 内容  

### Phase 4 — 单源发布（仍可闭源 Pro）

- [ ] monorepo 仅含 **已批准公开子集** + 壳；**禁止**把 Pro scripts 扫进公开 tree  
- [ ] ASP 真端点若上线：闭源服务 + 公开协议版本绑定  
- [ ] 定期 denylist 审计：`rg` 扫公开仓无 hermes 绝对路径 / 账户 id / 未脱敏事故  

### Phase 0 补充 — 开源边界自检

- [x] ROOTFIX 写明 **不全开源**  
- [ ] README 一句：**Open core ≠ full dump of production Falsify**  
- [ ] 评估主仓 `falsify/quant*` 是否保持开源或移入闭源（**产品决策，默认维持现状直到你改口**）

---

## 9. 验收总闸（根治完成的定义）

| 检查 | 通过标准 |
|------|----------|
| 版本 | 对外页面/README **只有一个** product version 徽章 |
| 双仓 | 10 秒能说清主仓 vs 壳；无第二套世界观 |
| Claiming | 任意「Falsify 过了」能贴出命令+artifact |
| Pro 副本 | `readlink -f` 三 profile 同一 inode/target |
| 裁决词 | OSS consumer 永不因 KILL 解析失败；映射表有测 |
| 启发式 | 无「假装 paper」的 hard gate 静默路径 |
| 叙事 | hero 通用闸门；quant 深链 |

---

## 10. 回滚

- 文档/README：git revert  
- symlink：恢复备份目录（Phase 3 前必须 tar）  
- 不在未备份时 `rm -rf` profile skill  

---

## 11. 与「真金路径 / 血统」关系

- 血统与真金路径解释 **为什么这些门存在**（白皮书 §7）。  
- ROOTFIX 解决 **工程分裂让先进性不可见、不可维护**。  
- 两者一起才是「既先进又根治」。

---

*Chris 授权 Phase 3 前，只做 Phase 0–2。*
