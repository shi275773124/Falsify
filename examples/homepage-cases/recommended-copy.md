# Homepage case copy drafts (artifact-first, 4 lines each)

> Generated 2026-06-25 from vault mining. Do not paste into `home.html` until Chris approves.

---

## Case 1 — Sharpe 4.06 / fictional horizon (recommended)

### zh-CN

**Claim:** 单 AI 正式 7 门审计 — Sharpe 4.06，PBO 0.000，6/7 PASS，下一步 shadow live。  
**Artifact:** 第二 AI 用不同再平衡机制重跑同 panel → SR 崩至 ≈0.77；regime 80% 时间为 1–2 天 chop，回测 horizon=14 在 live 里几乎从未成立。  
**Verdict:** BLOCK — NOT_VIABLE；SR 是成本÷虚构持仓期的会计幻象，不是 alpha。  
**Must Fix:** 任何升级 paper/live 前必须 mechanic 实证对照 + 成本/天 explicit；PBO=0 ≠ live-safe。

### en

**Claim:** Single-AI formal audit — Sharpe 4.06, PBO 0.000, 6/7 gates PASS, ready for shadow live.  
**Artifact:** Second AI reran the same panel with a different rebalance mechanic → SR collapsed to ≈0.77; 80% of history is 1–2 day regime chop, so backtest horizon=14 rarely exists in live.  
**Verdict:** BLOCK — NOT_VIABLE; the Sharpe is a cost-over-fictional-hold accounting artifact, not alpha.  
**Must Fix:** Before any paper/live promotion: mechanic ground-truth vs live journal + explicit cost-per-day; PBO=0 ≠ live-safe.

**Source:** `examples/real-cases/01-fictional-horizon-quant-audit.zh-CN.md`

---

## Case 2 — Horizontal fee comparison / 4 pricing errors (recommended)

### zh-CN

**Claim:** ~12 家 venue 横向费率表，双 Agent 不同模型族，<30 分钟出报告 + 80+ 分级 URL。  
**Artifact:** 审计 Agent 逐格对照官方 docs — A 抄错基数（2×）、B maker 符号反了（+1.5 bps 实为 −1.5 rebate）、C 过早放弃「未公开」、D 选错 collateral 行。  
**Verdict:** 4 critical errors caught — 全部有 verification path，冲突写进 log 而非静默覆盖。  
**Must Fix:** 表格每个数字必须 cite 一手 docs + fetch date；web-search 合成「大概费率」是主要泄漏面。

### en

**Claim:** Horizontal fee table across ~12 venues, dual agents on different model families, report + 80+ graded URLs in under 30 minutes.  
**Artifact:** Auditor checked each cell against official docs — A wrong base (2×), B flipped maker sign (+1.5 bps charge vs −1.5 rebate), C gave up on "unpublished" tier, D wrong collateral row.  
**Verdict:** 4 critical errors caught — each with a verification path; conflicts logged, never silently overwritten.  
**Must Fix:** Every table cell must cite first-hand docs + fetch date; web-search synthesis of "probable fees" is the main leak.

**Source:** `examples/comparison-case-study/README.md`

---

## Alternate — Logs ≠ state (already on homepage proof strip)

### zh-CN

**Claim:** `reports/deploy.md` —「部署成功，systemd active，curl 200」。  
**Artifact:** Falsify review v1 — 验收链把 deploy 日志当状态证明，无 read-after-write probe。  
**Verdict:** BLOCK — Logs ≠ state proof。  
**Must Fix:** 附 post-deploy 探测输出；从 acceptance chain 移除「另一个 AI 审过」。

### en

**Claim:** `reports/deploy.md` — "deploy succeeded, systemd active, curl 200".  
**Artifact:** Falsify review v1 — acceptance chain treats deploy logs as state verification; no read-after-write probe.  
**Verdict:** BLOCK — Logs ≠ state proof.  
**Must Fix:** Attach post-deploy probe output; remove "another AI reviewed it" from the acceptance chain.

**Source:** `examples/sample-block-report.json`
