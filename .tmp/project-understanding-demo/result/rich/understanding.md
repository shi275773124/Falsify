# 项目理解（falsify.understanding.v1）

- 生成状态：available
- 关联原审查裁决：BLOCK
- 权威上限：EPISTEMIC_CLAIM
- 主张范围：document_logic
- 原审查关联哈希：1ea075bb57660b22216d41a2b33e3b8212b89f21bb90aa05a919fa9e15128bca
- 说明：以上为关联信息，仅表示与原审查的对应关系，不代表已通过权威验证。

## 1 · 它怎样运转

**目标**（source_observation）：Turn weekly platform order exports into a finance-ready billing table.
 〔SUBJECT:1-3“The pipeline fetches orders, applies refunds, and renders the report.”〕

**最短机制链**：
1. （source_observation）Raw order events are pulled from the platform export. 〔ARCH:7-7“`fetch_orders()` pulls raw order events”〕
2. （source_observation）Refunds are split into pre-shipment and post-shipment buckets. 〔ARCH:8-8“`apply_refunds()` splits refunds into pre-shipment and post-shipment buckets”〕
3. （inference）The weekly table renders from the split results; window correctness is assumed, not checked. 〔PROBE:4-5“rows outside requested window: 391”〕

## 2 · 它靠什么成立

- （claim）The platform export covers exactly the requested window. 〔ARCH:13-13“The platform export is assumed complete for the requested window”〕
  - 若不成立：weekly totals silently include or miss rows (probe saw 391 outside-window rows)
- （claim）Refund status is final once the export marks it settled. 〔ARCH:14-14“Refund status is assumed final once the export marks it settled”〕
  - 若不成立：late refunds leak between weeks and totals drift
- （claim）The rate table in use is current for the report month. 〔CODE:21-21“return RATE_TABLE.get(month_key) or list(RATE_TABLE.values())[-1]”〕
  - 若不成立：stale currency conversion silently misstates amounts

## 3 · 这次发现了什么

- #1 [Must Fix] （source_observation）The 391 out-of-window rows measured by the probe mean weekly totals are computed over a fuzzy window, so 'numbers match the platform' is not yet a safe statement. 〔PROBE:4-4“rows outside requested window: 391  (0.94%)”〕
- #2 [Known Debt] （source_observation）rate_for() falls back to the last dict entry for unknown months, so a stale table is used without error — the Known Debt is a real silent failure mode. 〔CODE:21-21“return RATE_TABLE.get(month_key) or list(RATE_TABLE.values())[-1]”〕

## 4 · 我的解释与修正

> 审查前的理解（用户原话）：我认为周报数字直接来自平台后台，平台给的口径就是我们的口径，不需要再核对。退款率我们只看一个总数字。

- 建议 rev0：我认为周报数字直接来自平台后台，平台给的口径就是我们的口径，不需要再核对。 → 导出口径与请求窗口存在实测偏差（0.94% 行落在窗口外），周报合计在加窗口核对前不能当作平台口径。（依据：probe output measured rows outside the requested window）
- 建议 rev1：退款率我们只看一个总数字。 → 退款分 pre/postshipment 两桶，晚到退款会在周与周之间漂移，单看总数会掩盖这种漂移。（依据：architecture splits refunds into two buckets; lateness unknown）

## 5 · 还有什么没弄清

- [missing_evidence] Whether long windows get silently truncated by the export API.
  - 影响：weekly totals could be systematically low
  - 下一条证据：row-count parity check against platform UI for one week
- [not_reviewed] How often late refunds settle after the export marks them settled.
  - 影响：week-over-week totals may not be additive
  - 下一条证据：refund status changelog sample over 4 weeks

## 推演问题（条件变化思考，非实测）

- 如果平台把导出从「滚动 7 天」切换成「自然周」，哪个假设最先失效，哪个数字会最先暴露差异？（推演，非实测）
- 如果汇率表一个月没更新，报告里哪些列会错、错多少取决于什么？（推演，非实测）

## 来源快照

- `SUBJECT` role=subject kind=document 全文包含
  - bytes_sha256: `6d6b3c49fb0848f5b2360a4709aa88d81a05aceb6843da15370d27457df84a0b`
- `RECEIPT` role=receipt kind=review_receipt 全文包含
  - bytes_sha256: `1ea075bb57660b22216d41a2b33e3b8212b89f21bb90aa05a919fa9e15128bca`
- `ARCH` role=material kind=document 全文包含
  - bytes_sha256: `6d035917763378df11231feea643024fbd4c18c3758a2fe4041ea981f3865a9f`
- `CODE` role=material kind=code 全文包含
  - bytes_sha256: `a2125b69357ab273639173f50ec41a3f02eab4667965cd99894397abd15323c0`
- `PROBE` role=material kind=raw_output 全文包含
  - bytes_sha256: `b43c7bd3143f532603f522aaa87df56cc5f6a33319a37d07502346272c9336a7`
- `BEFORE` role=user_before kind=document 全文包含
  - bytes_sha256: `d757e043a26a766adf5a90a2c218c5c9238437bca336f795f9d6b4a21abeffeb`

---
生成：2026-10-07T13:38:47Z · tool=falsify.understanding · provider= · model=
认识状态：source_observation=材料可见 / claim=主张 / inference=推断 / unknown=未知。
