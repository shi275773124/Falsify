# 项目理解 · Falsify

- 原审查裁决: BLOCK
- 原审查关联哈希: 2d5dbdf8c2ff92f08a65d7171745eab64ec310969f32b593080cd5800a7fcbfc

## 1 · 它怎样运转
- 目标: Turn weekly platform order exports into a finance-ready billing table. (source_observation)
- 1. Raw order events are pulled from the platform export. (source_observation)
- 2. Refunds are split into pre-shipment and post-shipment buckets. (source_observation)
- 3. The weekly table renders from the split results; window correctness is assumed, not checked. (inference)

## 2 · 它靠什么成立
- The platform export covers exactly the requested window.
- Refund status is final once the export marks it settled.
- The rate table in use is current for the report month.

## 3 · 这次发现了什么
- [#1] The 391 out-of-window rows measured by the probe mean weekly totals are computed over a fuzzy window, so 'numbers match the platform' is not yet a safe statement. (source_observation)
- [#2] rate_for() falls back to the last dict entry for unknown months, so a stale table is used without error — the Known Debt is a real silent failure mode. (source_observation)

## 5 · 还有什么没弄清
- (missing_evidence) Whether long windows get silently truncated by the export API.
- (not_reviewed) How often late refunds settle after the export marks them settled.

## 4 · 我的解释与修正
- 审查前的理解: 我认为周报数字直接来自平台后台，平台给的口径就是我们的口径，不需要再核对。退款率我们只看一个总数字。

- rev0: retracted
- prompt1: 如果切自然周，窗口完整性假设最先失效。

## 推演问题（可选）
- 如果平台把导出从「滚动 7 天」切换成「自然周」，哪个假设最先失效，哪个数字会最先暴露差异？（推演，非实测）
- 如果汇率表一个月没更新，报告里哪些列会错、错多少取决于什么？（推演，非实测）