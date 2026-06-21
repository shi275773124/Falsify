# 05. Adversarial Review (Layer 2)

Current public verdicts are `PASS`, `PASS_WITH_DEBT`, and `BLOCK`. Older examples in this repository may use `PROCEED`, `HOLD`, or `ARCHIVE`; the CLI maps legacy reviewer output into the current vocabulary.

[中文](./05-adversarial-review.zh-CN.md) · [Back to README](../README.md)

**This is Layer 2.** [Layer 1 — peer review](./03-collaboration.md) catches
*wrong numbers*; this catches *wrong conclusions*. It doesn't replace Layer 1 —
it goes one level deeper, for high-stakes calls.

Peer review (docs 03) catches **a wrong number written prettily**. It does
not catch the harder failure: **right facts, wrong conclusion** — the agent used
the wrong tool on the right data, or treated a partial truth as a finished verdict,
or "failed closed" by writing an ABORT file and calling it done.

This variant adds four things on top of v1. It's heavier; use it for high-stakes
calls — strategy/design go-no-go, production changes, anything where a confident
wrong *conclusion* (not just a wrong number) is expensive.

---

## 1. Verdict ladder — decisions are discrete, not a fuzzy score

A review doesn't output "looks good-ish." It outputs one of:

- **PASS** — evidence holds; move to the next step
- **PASS_WITH_DEBT** — no current blocker remains; Known Debt has an upgrade trigger
- **BLOCK** — rejected; lists the exact Must Fix items or missing evidence

`BLOCK` can repeat because review is **multi-round**:

```
Round 1: BLOCK  (2 kill-items + 5 fix-items)
  → author commits a fix version
Round 2: BLOCK  (fix-1 self-defeating, fix-3 cosmetic, fix-5 conflicts with fix-1)
  → author commits another fix version
Round 3: PASS
```

Rule: between rounds you don't append a counter-argument — you commit the fixed
version and the reviewer **re-judges independently**. "I already admitted the
problem" must not soften the next verdict. A fix is only real if it survives a
fresh attack.

## 2. Four precondition gates (G1–G4)

v1's three rules all ask "is this fact correct?" These four ask "is the *claim*
built on the fact even meaningful?" Run them before any outward assertion.

| Gate | Catches | One line |
|---|---|---|
| G1 entity disambiguation | "a part of X changed" → "X is dead" | Is the X I mean actually that X? |
| G2 unit / scale alignment | "−0.5% per 8h" *feels* fine (it's ~−547%/yr) | Convert to a human scale — still plausible? |
| G3 prior-conflict = brake | piling on citations when the operator doubts you | Operator disagrees → re-verify, don't double down |
| G4 ruler / object match | a dense-data test on a sparse signal | Do the tool's assumptions fit the data? |

Full fill-in template: [`templates/precondition-checklist.md`](../templates/precondition-checklist.md).
Worked example of G4: [`examples/wrong-tool-right-data.md`](../examples/wrong-tool-right-data.md).

## 3. Cross-model reviewer (independence without two machines)

You don't need two hosts. **Two different model families + isolated context** is
enough independence. The reviewer can be a one-shot call to a different model via
any OpenAI-compatible endpoint. The reviewer's system prompt must say: *find
holes, don't be polite, don't restate the author.*

How-to + a copy-paste call: [`examples/cross-model-rpc.md`](../examples/cross-model-rpc.md).

## 4. Verdict-as-file + step guards

For multi-step pipelines, make each step emit **one independent file**, and treat
a step verdict as `file + 3 checks`: it **exists**, it's **≥ a size floor**, and it
**doesn't start with an ABORT/ERROR marker**. A step that "fails closed" by writing
`ABORT` and exiting 0 looks successful to a scheduler — downstream steps then run
on missing input and stay internally consistent until a human notices hours later.

Guard each step with [`templates/step-verify.sh`](../templates/step-verify.sh):
fail loud (non-zero exit + alert), never fail silent.

---


## 5. GLOSSOPETRAE checks — audit the audit channel

Recent frontier-model work on procedural xenolinguistics and covert channels is a warning for Falsify: another model saying "I reviewed it" is not enough. AI systems can operate over text/code structures humans and monitors may not reliably audit.

Do **not** add a fourth layer. Fold these checks into adversarial review:

- **Human-auditability.** Does the verdict bottom out in raw artifacts, readable diffs, commands, fixtures, or source links a human can inspect? If it only depends on an AI summary, hold.
- **Semantic verdict nudge.** Is ordinary language pushing the reviewer toward `PASS`/`PASS_WITH_DEBT`/`Known Debt` without satisfying the gate? Examples: "not blocking", "enough evidence", "another model agrees", "just theoretical", or blocker→debt relabeling.
- **Prompt-only audit theater.** A line saying "watch for prompt injection" is not a defense. Prefer known-pattern checks, fixtures, or reproducer runs. A pattern library covers known modes only; it does not prove unknown channels absent.
- **Monitor-failure laundering.** Empty, unparseable, truncated, filtered, or confident-"no issue" outputs are not clean by default. When an LLM/API probe is used as evidence, keep the raw verdict, parse status, HTTP status, `finish_reason`, and token usage where the provider exposes them.

Cutline discipline: if the current claim depends on the missing evidence, it is Must Fix. If the work is read-only and does not claim the channel is absent, record it as Known Debt with an upgrade trigger.

---
## When to use which

| Situation | Use |
|---|---|
| Fact accuracy, fee tables, doc audits | v1 simple review (docs 03) |
| Go/no-go on a design, production change, strategy | this variant (verdict ladder + G1–G4) |
| Multi-step automated pipeline | + verdict-as-file + `step-verify.sh` |

## Open question

The remaining gap: **an agent manipulating its reviewer** — passing a *cosmetic*
fix (renaming the thing instead of fixing it) so the reviewer marks it resolved.
Should the reviewer also run its own claims through G1–G4? Unsolved.

## Next

- [Troubleshooting](./04-troubleshooting.md)
