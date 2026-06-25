# Falsify：一种让 AI 结论在被信任之前先存活于攻击的对抗式验证协议

*草案 v0.2 — 2026-06-25*

> **范围声明（先于一切阅读）.** 本文是一份**协议规范（specification）**，不是一个实现完成、已部署、已上线的系统。文中描述的能力分两种：标注为 **[规范]** 的是协议**应当**保证的性质（如"中立编排""独立裁判""live 越权防护"），目前由流程纪律执行、**尚未全部由工具强制（not yet enforced in code）**；标注为 **[已实现]** 的才是当前 CLI / 运行环境里已经跑起来的部分。规范级主张不等于已交付能力——这条边界在第 12 节逐项列清。把"规范"当"已实现"来读，正是本协议要消灭的那类错误。

## 摘要

当前对 AI 输出的信任，建立在一个隐藏假设之上：**产出结论的系统，可以同时为这个结论担保。** 自我验证（self-verification）、单模型复核、以及"另一个模型也同意"，都共享这个假设——出错方与验收方同源，因而共享同一盲区。本文提出 Falsify：一个不依赖任何单一来源担保的验证协议。在 Falsify 中，一个结论不被"接受"，它必须**存活于一次独立的对抗攻击之下**。

攻击分三层：框架审检测工程结构的腐烂，对抗审攻击会致命的隐藏假设，Cutline 把所有发现裁成"现在必须改 / 暂不阻塞但带升级触发器 / 删除"三类离散裁决。关键在于，**审计通道本身也必须被审计**——"另一个 AI 说通过了"在协议内不构成证据；只有人类可读、机器可复现的 raw artifact 才算。最后，审稿人必须与作者**跨厂商独立**。正如比特币移除了支付中的可信第三方，Falsify 移除了 AI 结论验收中的可信单一裁判。

---

## 1. 引言：信任的问题

电子支付曾经依赖金融机构作为可信第三方。这套体系能用，但它的弱点是结构性的：信任本身成了攻击面。比特币的贡献不是更快的支付，而是**用证明替代信任**——你不再信任付款方，你验证链。

AI 时代正在重演同一个问题，只是标的从钱变成了结论。

今天，一个 AI 产出研究结论、回测判断、策略 go/no-go、生产变更方案，我们凭什么相信它？现行的答案几乎全部是某种形式的"信任同源担保"：

- **自我验证**：让同一个模型检查自己（"请复核上面的结论"）。
- **单模型复核**：让同厂商的另一个实例审查（self-consistency、reflexion）。
- **社交背书**：另一个 agent 回了一句"看起来没问题"。

这三者共享同一个致命缺陷：**审查者与被审查者来自同一来源，因而继承同一组盲区。** 一个模型在训练中学错的因果关系、对某个机制的系统性误解，它自己审自己时不会发现——因为那个错误对它而言不是错误，是常识。

这就像让付款人自己证明他没有双花。

---

## 2. 难的失败不是错误的数字，是错误的结论

必须区分两类失败，因为它们需要完全不同的防御。

**第一类：错误的数字写得很漂亮。** 费率抄错一位、正负号反了、表格读错行。这类错误传统的同行评审（peer review）能抓——核对来源、重算一遍即可。

**第二类：正确的事实，错误的结论。** 数字全对、来源全在，但模型用错了工具、把片面真相当成完整裁决、或者"fail-close"地写了个 ABORT 文件就当任务完成。这类失败核对数字抓不到，因为每个数字单独看都对。

第二类才是昂贵的那一类。一个自信的错误结论——不是错误的数字——上了生产、上了真钱，代价是数量级的。而恰恰是第二类，自审和单模型复核**最容易失手**——原因在第 3 节展开。

Falsify 整个协议是为第二类失败设计的。

---

## 3. 为什么自审与单模型复核结构性失效

先把直觉讲清楚（以下是设计论证，非实证测量；量化验证见第 12 节列为待办）。设结论 C 由模型 M 在盲区集合 B(M) 下产出。自审是用 M 检查 C；任何源自 B(M) 的错误，M 都看不见，因为 B(M) 的定义就是"M 看不见的地方"。

单模型复核用 M' 检查，但若 M' 与 M 同厂商、同训练谱系，则 B(M') 与 B(M) **可能高度重叠**。当盲区重叠时，增加更多同源审稿人，倾向于把同一个盲区重复投票，而非真正扩大覆盖——这是一个**结构性失败模式**（不是必然定理，但在共享训练谱系下风险显著），类比比特币里的算力垄断：当多数节点同源，多数本身不再是安全保证。这是一个待实证量化的方向，不是已证结论（见第 12 节）。

由此得到 Falsify 的**核心赌注**（hypothesis，非定理）：要更可能覆盖 B(M)，审稿人与作者的盲区交集应尽可能小；在实践中这指向**跨厂商**——让 A 厂的模型起稿，B 厂的模型攻击。这条赌注的方向有第 11 节的实例支持，但尚无大样本评测量化（错误发现率、假阳/假阴），因此本文不把它写成"已证明"，而是写成一个**可被证伪的设计选择**。OpenAI 不会把 Claude 作为自家输出的最终裁判——这个商业边界，是 Falsify 的结构性立足点之一（见第 9 节，含对该护城河的诚实限定）。

---

## 4. 协议概览

Falsify 不是"让另一个 AI 批评一下"。那是 prompt。Falsify 是 protocol——有固定的角色契约、固定的输出形态、固定的裁决词表。

一个完整的 Falsify = **框架审 + 对抗审 + Cutline**，三层缺一层只能叫 partial 或 ad-hoc，不能叫 Falsify。

```
   结论 C
     |
     v
[  框架审   ]   第 1 层：承载结论的系统结构能不能被信任？
     |
     v
[  对抗审   ]   第 2 层：这个结论怎么会错 / 怎么会死人？
     |
     v
[  Cutline  ]   第 3 层：现在到底要不要挡？
     |
     v
 Verdict: PASS / PASS_WITH_DEBT / BLOCK
```

每一层各司其职，下面分述。

---

## 5. 第一层：框架审 —— 结构能否被信任，而非逻辑是否正确

框架审不问"这个结论对不对"——那是第二层的事。它问一个更靠前的问题：**承载这个结论的系统结构，本身能不能被信任？** 一个结论无论多正确，如果它跑在一套权力路径不清、无法回滚、人类无法审计的系统上，它就不该被放行。

它的判据来自一条工程常识：**腐烂发生在表面之下。** 不在行数或圈复杂度里，而在权力如何隐藏、回滚是否存在、人类能否独立验证。表面指标全绿（LOC 正常、覆盖率达标、测试全过），系统照样可以处在一个无法被安全操作的状态。这条洞见本身是公共财产——可追溯到 Brooks、Fowler、Martin、Evans 等工程经典，不属于任何单一工具。

但框架审审的不是"代码好不好维护"，而是一个更窄、更要命的问题：**这个系统会执行一个高风险动作（下单、改配置、动真钱），它的权力、可逆性、可审计性，是否经得起一次事故。** 它的七类猎物：

| 风险 | 一句话 |
|---|---|
| 隐式状态 | 系统行为依赖一个看不见的状态 |
| 隐式权力源 | 谁有权执行说不清 |
| 权力源冲突 | 多个入口都能改同一件事，彼此互不知道 |
| 回滚缺失 | 出事了没有可执行的 rollback 命令 |
| 验证缺失 | 无法用一条命令确认当前真实状态 |
| 所有权模糊 | 没人明确拥有，没有锁，生命周期含糊 |
| 不可人审 | 人类无法独立验证，只能信 AI 摘要 |

在 live / production 场景，框架审的硬要求是把权力路径**具体化到可执行**：

```
cron / service
venue / account
signing key / env boundary
rollback command
verification command
```

说不清这条链，就是一个框架审发现。代码评审会说"这段函数太长"；框架审会说"这条 cron 用的是哪个 profile、哪个账户、出事用什么命令回滚——说不清就不能上线"。这是一个为"会动手的系统"设计的结构审，不是为"好不好读的代码"设计的可维护性审。

> **相关工作（正交，非依赖）.** 开源项目 brooks-lint（`github.com/hyhmrright/brooks-lint`）在相邻方向上做"代码可维护性衰败"的结构审，把工程经典编码成代码审查标准（六类生产代码衰败 + 六类测试衰败）。框架审与它正交：brooks-lint 审代码可读性/可维护性，框架审审 action-capable 系统的**权力、可逆性、可审计性**——两者审的是不同的东西，可叠加使用，互不替代。

---

## 6. 第二层：对抗审 —— 失败模式攻击者

对抗审攻击的是"这个结论怎么会错"。它系统性地寻找：

- **false truth**：结论本身是假的
- **false risk**：风险判断是假的
- **silent failure**：失败了但没人知道
- **live / action 越权**
- **permission boundary drift**：权限边界漂移
- **data staleness**：当前状态与结论不一致
- **reproducibility gap**：无法复现
- **fake acceptance**：把 submitted / order_id / log 当成 account state

对交易与回测，它额外攻击：PIT（point-in-time）泄漏、survivorship、stale data、成本/资金费/滑点方向、mechanic mismatch、PBO/DSR 滥用、单窗口脆弱、universe leakage、live execution mismatch。

硬性规则：每一个反对意见都必须附**验证路径**——官方 URL、API endpoint、源码位置。"我不确定"不构成一个发现；必须落到具体疑点。

---

## 7. 第三层：Cutline —— 风险裁刀

前两层负责"发现风险"，Cutline 负责"切现在要不要挡"。所有发现只能进三个出口：

```
Must Fix   = 阻塞当前交付
Known Debt = 真实风险，当前不阻塞，但必须带升级触发器
Delete     = 没有具体的当前失败模式
```

**Must Fix 的硬条件**：一个发现若会导致当前交付出现以下任一项，即为 Must Fix——false truth、false risk、silent failure、live/action 越权、不可复现、当前验证断裂、维护性腐烂已妨碍当前可验收。Must Fix 不是"我不喜欢"，是"当前交付会因此错、死、或不可验收"。

**Known Debt 的合格条件**：必须有升级触发器。

```
Known Debt: <问题>
Why not blocking now: <原因>
Upgrade trigger: 当 <具体事件> 发生时升为 Must Fix
```

没有触发器的 Known Debt 不合格——要么升 Must Fix，要么 Delete。这一条消灭了审计中最常见的逃逸："这个风险记一下"然后永远悬空。

---

## 8. 元层：审计通道本身必须被审计

这是 Falsify 与一切"对抗审工具"的分水岭。三层审完了内容，还有一个问题没答：**这次审计本身，是真的，还是在演？**

协议内强制检查四种"审计作秀"：

- **semantic verdict nudge**：文字把审计员推向 PASS，但证据没过。红旗包括："not blocking" 却无证据、"已经足够证据" 但 gate 没过、把 blocker 改名成 caveat/debt。
- **prompt-only audit theater**：只写"注意 prompt injection / 注意风险"不算防御。要有 known-pattern check、fixture、reproducer、raw artifact、machine evidence。
- **monitor-failure laundering**：不能把空输出、不可解析输出、截断输出、被内容过滤的输出、或 LLM 自信地说"没问题"当作 clean。
- **human-auditability break**：只有 AI 摘要、没有 raw artifact，权力路径不可读，没有 diff / fixture / command output / source link。

核心教训一句话：**另一个模型说"我审过了"不够。高风险结论必须落到人类可读、机器可复现的证据。** 这一层把"信任审计员"也变成了"验证审计产物"——与比特币把"信任节点"变成"验证链"同构。

---

## 9. 跨厂商独立性：为什么审稿人不能与作者同源

承接第 3 节的核心赌注：若跨厂商能减小审稿人与作者的盲区交集，最强的实现就是 A 厂起稿、B 厂攻击、裁判不归任何一个选手所有。

**诚实限定（本节按 Falsify 自身纪律标注）.** "跨厂商互审只有我们能做"这个旧主张已被证伪。一手反例：`openai/codex-plugin-cc`——OpenAI 官方发布的 Claude Code 插件（Apache-2.0，约 2 万 star 量级，源 `github.com/openai/codex-plugin-cc`），在 Claude Code 内调用 Codex/GPT 审代码，自带 `/codex:adversarial-review`，即一家厂商的模型在另一家的工具内做对抗式代码审。因此 Falsify 的护城河不能再表述为"独此一家的跨厂商能力"。仍然成立的两条边界是：

1. **领土**：竞品审的是代码 diff；Falsify 审的是分析、判断、回测结论这类**文字结论**——代码评审抓不到 mechanic 假设本身的错误（见第 11 节实例）。
2. **裁判归属 [规范]**：协议**要求**审稿方与作者方都可替换、不绑定被审的那一家，裁判不归任何一个选手所有。**这是规范级目标，不是已强制的机制**——"跨厂商调用"本身不等于"独立"：同一操作者、同一 prompt、同一数据裁剪、同一 orchestrator 都可能让独立性失效。要让"独立"可验收，需要一组机器可检查字段（author/reviewer 的 model+vendor、orchestrator owner、prompt 不可变性、artifact 保管、谁能改 verdict、谁选 reviewer、利益冲突标记）。这组 enforcement 字段尚未固化（见第 12 节，列为已知缺口）。

这两条里，"领土"是当前事实，"裁判归属"是**规范主张**——不是"独家能力"主张，也不是"已强制的独立性保证"。[立场 + 规范，非实证测量]

---

## 10. 裁决与授权的分离

Falsify 只输出风险分类，它**不自动授予 live 权限**。这是协议刻意保留的一道闸。

对真钱、生产配置、cron、网关、可下单的变更：

- 当前 profile 可以跑 Falsify、修复、准备证据；
- 但 final judgment 必须由**另一个独立 profile / 模型**给出（self-Falsify 不能当 live final judgment，必须标注 Boundary: not independent final judgment）；
- 不可逆动作由人类最终授权，历史授权不继承。

此外，对被调度的 live executor，仅跑 wrapper dry-run 不够，还要跑 **scheduler-context dry-run**——因为调度器可能用错 profile、scripts 目录、HOME、workdir、account boundary 或 fail-close 路径。验收至少记录：job id/schedule、profile/home/scripts dir、direct dry-run 输出、scheduler-context dry-run 输出、account/venue boundary、失败时的 job 暂停状态。

把"审了"和"可以上线"分成两件事——在认识论上的 PASS 与现实中的不可逆操作之间，插入一个人类与独立裁判的双锁。

**[规范] 实现状态.** 本节描述的是协议**要求**的闸，目前**由流程纪律执行，尚未由工具强制**：CLI/CI 还不会自动拦截一个 self-Falsify 冒充 live final judgment，也不会强制要求 scheduler-context dry-run artifact 存在才放行。要把它从"政策"变成"协议保证"，需要把上述每一项落成 policy-as-code 的 required manifest 字段与 BLOCK 条件（`boundary:not_independent_final_judgment`、human approval id、scheduler job id、direct/scheduler-context dry-run 输出、rollback/verification command 等）。这是已知缺口，列入第 12 节。在补齐前，本节是**规范要求，不是已强制的越权防护**。

---

## 11. 一个实例：Sharpe 4 幻象

一个单 AI 跑出的 paper-candidate 策略：Sharpe 4.06–4.31、PBO 0.000、DSR p<1e-7、六到七道门全 PASS。差一步上真钱。

五轮跨 AI 对抗审之后，它降为 NOT_VIABLE。关键发现不是 code bug——代码是对的。关键是 **mechanic 假设本身错了**：那个 Sharpe 不是 alpha，是把成本摊到一个**虚构的持有期**上产生的幻象。可验算的计算链如下：

```
单边成本 ≈ 9 bps（固定）
作者假设 horizon = 14 天 → 成本摊销 = 9bps / 14d ≈ 0.64 bps/day
实测有效持有期 ≈ 1.5 天 → 真实成本 = 9bps / 1.5d  ≈ 6 bps/day
成本低估倍数 = 6 / 0.64 ≈ 9.4×
```

实测持有期来自对同一历史 panel 的 regime 分布检查：median 1.0d、mean 1.51d、87% 的持仓 ≤ 2 天——没有任何 14 天的持有。**SR 4.06 的真正来源不是 alpha，是把成本摊到一个不存在的 14 天持有期上。**

这正是第 2 节说的"正确的数字，错误的结论"。每个数字单独看都对，PBO/DSR 全过——但这些指标都在**同一个 mechanic 假设下**测稳定性；当假设本身错时，它们只测到"假设内部一致"，测不到"假设本身合不合理"。这一层只有对抗审打得到，代码评审和自审都漏。审稿人在过程中还三次自打脸、撤回自己的断言，演示了协议对 sycophancy 的抵抗：**修复只有在存活于一次全新攻击后才算数，"我已经承认问题了"不能软化下一轮裁决。**

**证据边界（按 Falsify 纪律标注）.** 本节是一个**真实内部案例的摘要**，非可公开复现的 artifact。完整五轮 transcript、回测代码、数据快照、`inspect_regime.py` 输出与逐轮 verdict 存于内部记录 `方法论/Falsify Case Study 01 — breakout20 五轮打脸 fictional horizon`；上方数字引自该记录。公开版尚未附带可一键复现的脚本与脱敏数据——这是本白皮书已知的证据缺口（见第 12 节）。

---

## 12. 边界与诚实声明

按 Falsify 自身纪律，本白皮书标注自己的边界。每条主张标注证据等级：**[已实现]** = 当前 CLI / 运行环境已跑起来、有 run artifact；**[假设]** = 设计赌注，待评测；**[立场]** = 定义性主张，非测量；**[规范-未强制]** = 协议要求但尚未由工具自动强制。

先说**已交付、不容含糊**的部分（不要把"没有打磨好的产品页"误读成"没实现"）：

- **审查能力本身已实现并已运行。[已实现]** Falsify CLI（`falsify review`）会跑完框架审 + 对抗审 + Cutline，输出带退出码的离散 verdict（PASS=0 / PASS_WITH_DEBT=1 / BLOCK=2）。**本白皮书自己就是被它审出来的**：作者方 Claude、审稿方 GPT-5.5，真实跨厂商，两轮 BLOCK 的原始 verdict 存于 `examples/whitepaper-self-audit/`，附一条可复现命令。这不是规范，是已发生的运行。
- **机器可解析 verdict 已实现。[已实现]** `falsify review --json` 输出 `falsify-report.json`（含 `schema_version`），可被 CI 解析与 gate。

再说**确实还没做完**的部分（诚实列，不藏）：

- 第 4–8 节的协议机制是**定义**，按定义成立。[立场]
- 第 3、9 节"跨厂商减小盲区交集 ⇒ 审计更有效"是**核心赌注**，方向有第 11 节支持，但尚无大样本评测量化（错误发现率、假阳/假阴、样本量、统计检验）。[假设]
- 第 9、10 节的"独立性保证""live 越权防护"目前**由流程纪律执行，尚未落成 policy-as-code 的自动 gate**。[规范-未强制] 升级触发器：用于自动化拦截 live 资金动作前，必须补全 required manifest 字段与 BLOCK 条件。
- verdict schema 虽存在，但尚未固化"parse 失败/截断/空输出一律 BLOCK"与"审稿人模型/厂商/HTTP status/finish_reason/token 用量"为强制字段。[规范-未强制] 同上触发器。
- 第 11 节是**真实内部案例的摘要**，数字可验算（计算链见正文），但完整回测代码 + 脱敏数据的公开复现包尚未发布。[内部记录]
- 本协议不声称能发现所有风险；Cutline 的职责是切出**当前**必须挡的，不是穷举。[立场]

一句话分清：**审查工具已交付且跨厂商跑通；尚未交付的是"自动拦截 live 越权"的强制 gate 和大样本有效性评测**。前者不是 vaporware，后者不假装已完成。

---

## 13. 结论

我们提出了一个不依赖单一来源担保的 AI 结论验证协议。一个结论不被信任，除非它存活于一次独立的对抗攻击：框架审检测工程腐烂，对抗审攻击致命假设，Cutline 切出离散裁决；审计通道本身被元层审计，审稿人与作者按规范跨厂商独立，裁决与授权被刻意分离。这些是协议的**规范**；把规范变成工具强制的保证，是 v0.3 的工程任务，本文已诚实列出尚未闭合的缺口（附录 A）。

差异不在功能，在认识论。竞品回答"谁来批评"；Falsify 定义"什么叫一个可信的结论"。难复制的不是三层结构，是对"什么算证据、什么算审计通过"的定义本身。

正如比特币让你无需信任付款人即可接受支付，Falsify 让你无需信任模型即可接受它的结论——因为这个结论，已经活过了攻击。

---

## 参考与延伸

公开源（一手，repo `github.com/shi275773124/Falsify`，链接指向 main 分支当前版，非固定 commit）：

- 对抗审（第 2 层）：`github.com/shi275773124/Falsify/blob/main/docs/05-adversarial-review.md`
- 风险裁刀 / Cutline（第 3 层）：`github.com/shi275773124/Falsify/blob/main/docs/06-risk-scalpel.md`
- 审计通道风险（元层）：`github.com/shi275773124/Falsify/blob/main/docs/07-audit-channel-risks.md`
- 框架审参考：`github.com/shi275773124/Falsify/blob/main/docs/09-brooks-lint.md`
- 角色契约模板：`github.com/shi275773124/Falsify/blob/main/templates/prompts/agent-a.md`、`.../agent-b.md`
- 机器可解析 verdict：`falsify review --json` → `falsify-report.json`

相关工作（正交）：

- brooks-lint（代码可维护性结构审）：`github.com/hyhmrright/brooks-lint`
- codex-plugin-cc（跨厂商代码 diff 互审）：`github.com/openai/codex-plugin-cc`

内部记录（非公开，作者私有环境，列出以标明证据来源而非供外部复现）：

- Sharpe 4 幻象完整案例：`方法论/Falsify Case Study 01 — breakout20 五轮打脸 fictional horizon`

---

## 附录 A：本白皮书自身的对抗审记录（dogfooding）

本文没有豁免自己。它被 Falsify CLI 用 GPT-5.5（跨厂商：作者方为 Claude）对抗审了两轮：

- **v0.1 → BLOCK**（7 Must Fix + 1 Known Debt）：抓出 Sharpe 案例缺 raw artifact、`[实测]`标签无运行记录、brooks-lint 二手当一手（一手核对后订正为 12 类风险）、竞品未指名、第 3 节论证自撞等。本版逐条处理。
- **v0.2 → BLOCK**（8 Must Fix）：进一步要求把"中立编排""独立裁判""live 越权防护"从规范级降为明确"未强制"，并要求竞品/案例附 commit/复现包。本版做了**范围声明 + 能力主张 [规范]/[已实现] 分级**，并诚实保留两类未闭合缺口（见下）。

**已闭合：** 两轮的原始 verdict 已作为公开 run artifact 落在 `examples/whitepaper-self-audit/`（`v0.1-verdict.txt`、`v0.2-verdict.txt`、`README.md` 含可复现命令）。"无公开运行记录"这条 v0.1 的指控，至此用真实运行直接闭合——审查工具不是规范，是已跑通的。

**仍未闭合（v0.3 工程路线，非文档措辞能解决）：**

1. verdict schema 未固化"parse 失败/截断/空输出一律 BLOCK"与"审稿人模型/厂商/HTTP status/finish_reason/token 用量"为强制字段。
2. 独立性与 live 越权防护尚为流程纪律，未落成 policy-as-code 的自动 gate。
3. 跨厂商有效性尚无大样本评测（错误发现率、假阳/假阴）。

**把闭合的与未闭合的分开摆，本身就是协议第 8 节"审计通道必须可被人类审计"的应用——包括审计这份白皮书自己。**

> 此处披露两轮 BLOCK 是**过程透明**，不构成对本版质量的背书——一份文档被审过，不等于它通过了审。但"被自己的工具审出真缺陷并修掉"与"工具根本没跑过"是两回事：前者是已交付工具的证据，后者才是 vaporform。本文属前者。
