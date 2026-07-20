# Real case: a Sharpe 4.06 strategy that died after 5 rounds of dual-AI cross-audit

> This is a **real audit log** from production use of Falsify on a quant
> strategy, not a planted demo. All venue / account / path identifiers
> are sanitized; numbers and the timeline are unedited.
>
> Domain: quantitative trading / regime-switching momentum
> Run length: ~2.5h wall-clock, 5 rounds, 3 commits
> Outcome: a `PAPER_CANDIDATE / SR ≈ 4.06 / PBO 0.000` strategy was
> reclassified as **NOT_VIABLE** before any live promotion.

## TL;DR

A single AI produced a "formal 7-gate audit pass" for a regime-switching
breakout strategy:

```
Sharpe 4.06–4.31 across 4 universes
PBO 0.000
DSR p < 1e-7
6/7 gates PASS (gate 7 intentionally False because it's a historical-only
panel audit — live execution evidence cannot be proven offline)
```

Under a single-AI workflow this would have rolled into shadow / tiny-live.

Falsify forces a second, adversarial AI to re-audit. Five rounds in:

- 1 lookahead bias, missed by the author (caught by reviewer)
- 1 wrong attribution by the reviewer (caught by reviewer themselves on
  re-run)
- 1 wrong assumption about live mechanic (caught by reviewer themselves
  after pulling production journal)
- 1 implementation bug in the reviewer's counter-test (caught by reviewer)
- 1 **fictional-horizon mechanic flaw** in the original audit — the actual
  killer — only surfaced because both AIs ran *different mechanics* on the
  same panel and the reviewer was forced to inspect regime distribution
  after their numbers blew up

The Sharpe 4.06 was not alpha. It was cost-amortization over a holding
period that **the strategy's own design never actually held**.

## Round 1 — author's lookahead bias

The 7-gate script computed regime quantile thresholds like this:

```python
ql = m.quantile(.33)   # full-sample constant
qh = m.quantile(.67)
vh = v.quantile(.67)
```

Day-100 was deciding "is today risk_off?" using the 33rd percentile of
days 100→1836. Every regime label was clairvoyant.

The reviewer submitted a fix: rolling 252-day quantile with `shift(1)`.

## Round 2 — reviewer self-reverses

Reviewer's first claim: "lookahead is the cause of SR ≈ 4."

After actually running the fixed version on all four universes:

```
universe A:  SR 4.06 → 3.66
universe B:  SR 4.08 → 3.96
universe C:  SR 4.31 → 4.20
universe D:  SR 3.06 → 2.67
```

SR drops only 0.1–0.4. Lookahead is real but **not the main contributor**.
The reviewer retracts the claim. Without the empirical re-run, this
incorrect diagnosis would have been pushed to the user.

This is the first **adversarial-audit self-reversal**: the value of forcing
your reviewer to ship numeric evidence, not just rhetoric.

## Round 3 — reviewer's wrong assumption about live

Reviewer's next claim: "The live executor does daily K=3 rebalancing,
so the realistic cost is ~5 bps/day."

Reviewer pulls the production journal:

```
journal events: 2 (initial + cap-fill, same basket)
current plan:   verdict=MATCH, actions=[], no rotation
ledger:         1 basket flip in 6 days
```

The live executor is **hold-until-flip**, not daily rebalance. The
reviewer's mechanic-B assumption was wrong. Retracted.

## Round 4 — implementation bug in reviewer's counter-test

Reviewer rewrites mechanic B to hold-until-flip, runs it:

```
universe A mechanic B: SR -0.28, MDD -87.5%, 1403 flips / 1836 days,
                       median hold = 1.0 day
```

Median hold = 1 day. Flip rate 76%. The reviewer hadn't actually
implemented hold-until-flip — daily ranking noise made bottom-3 churn
every day, so it became daily rebal in disguise.

Reviewer adds `min_hold=7` and re-runs.

## Round 5 — the fictional horizon

Even with `min_hold=7` enforced, mechanic B still produces:

```
universe A: SR -0.22, MDD -83.7%, median hold STILL 1.0 day
```

The reviewer runs a quick regime-distribution probe:

```
risk_off run-length across 4 universes:
  universe A:  median 1.0d, mean 1.51d, max 5d, 87% of runs ≤ 2 days
  universe B:  median 1.0d, mean 1.64d, max 4d, 83% of runs ≤ 2 days
  universe C:  median 1.0d, mean 1.73d, max 4d, 80% of runs ≤ 2 days
  universe D:  median 1.0d, mean 1.57d, max 4d, 86% of runs ≤ 2 days
```

The strategy is `regime → switched_kill`: when the regime flips, positions
**must exit immediately**. `min_hold=7` is moot because the regime itself
force-exits in 1–2 days, 80%+ of the time.

This exposes the fatal flaw in the **original** mechanic A — which uses a
nominal `horizon=14` overlapping-portfolio convention:

```
mechanic A's cost amortization assumption:
  cost = 9 bps / 14 days  ≈  0.64 bps/day

actual effective hold under regime-chop:
  cost = 9 bps / 1.5 days ≈  6 bps/day

cost was understated by a factor of ~9.4×
```

**SR 4.06 wasn't alpha.** It was an accounting artifact of dividing real
trading cost by a holding period the strategy's own design never realized.

The live executor's "6 days, 1 flip" snapshot only happened because we
sampled a stable risk_off window. Historically, 80%+ of the time would
chop in 1–2 days, and the live system would be hit by mechanic-B-shaped
losses just like the backtest.

## Final verdict

```
REJECT_DAILY_LIVE_EQUIVALENT
SWITCHED_KILL_MECHANIC_NOT_VIABLE
SR_IS_COST_OVER_AMORTIZATION_ARTIFACT
NO_LIVE / NO_CAP_INCREASE / NO_AUTO_PROMOTION
```

Allowed follow-ups:

1. Replace the regime classifier with something smoother (longer rolling
   window, hysteresis), and re-audit from zero.
2. Accept that this alpha does not exist in daily live-equivalent form.
3. **No** local patches that turn this version into production.

## Discoverability matrix — why dual-AI matters

| # | Bug | Type | Single-AI catches it? |
|---|---|---|---|
| 1 | Full-sample quantile lookahead | Author blind spot | Rarely — authors don't audit themselves on this |
| 2 | "Lookahead is the main cause" | Reviewer overreach | Only with numeric re-run discipline |
| 3 | Wrong live-mechanic assumption | Cross-system blind spot | Only by inspecting production artifacts |
| 4 | min_hold not implemented | Reviewer impl bug | Sometimes — needs a sanity-check field |
| 5 | **Fictional horizon × regime chop** | **Mechanic assumption bypass** | **Almost never** |

Bug 5 is the killer. It only surfaced because:

- Author and reviewer ran *different mechanics* on the *same panel*
- Reviewer's mechanic blew up
- That forced a regime-distribution probe
- Which revealed that the author's assumed `horizon=14` was fictional in 80% of history

When author and reviewer share a mechanic assumption, PBO=0 and DSR p<1e-7
both look great — but they only test stability *within* the assumption.
They cannot test whether the assumption itself is realistic. **Forcing the
reviewer onto a different mechanic is the only way that question gets
asked.**

## Six audit disciplines this case validated

For any backtest going to paper-candidate / shadow / tiny-live:

1. **Lookahead hygiene**: every quantile / rank / threshold must be
   rolling-only with `shift(1)`.
2. **Mechanic-empirical match**: the backtest's horizon / hold / rebalance
   must be reverse-checkable from the live executor's actual journal.
3. **Regime run-length must be inspected**: if the strategy depends on
   regime classification, you must know the empirical distribution of how
   long each regime label persists.
4. **Cost amortization must be explicit**: report cost-per-hold *and*
   cost-per-day, not only cost-per-hold.
5. **PBO interpretation must be conservative**: PBO=0 means
   "neighborhood-stable inside this mechanic and grid". It does not mean
   "no overfit" or "live-safe".
6. **Dual AIs must use different mechanics**: when both reviewers share an
   assumption, the audit only tests internal consistency, not whether the
   assumption holds.

## Reproduction

This was a real run, not a curated demo. The full sanitized timeline, the
two backtest scripts (mechanic A vs mechanic B), and the regime-inspector
are kept in the original audit's artifact directory. Numbers above are
verbatim.

If you want the full audit harness adapted to your strategy, see the
[Falsify reviewer prompt templates](https://github.com/shi275773124/Falsify/tree/main/templates/prompts) and the
[main case library](https://github.com/shi275773124/Falsify/tree/main/examples/cases) for how to wire two adversarial
reviewers in your own workflow.

> Bottom line: a single AI happily produced a "Sharpe 4 paper-candidate".
> Forcing a second AI onto a different mechanic killed it in 2.5 hours
> with five independent findings. The killer wasn't a math bug — it was
> a mechanic assumption that no single auditor would ever question.
