# Falsify real cases — forwardable share cards

**Looks green isn't proof.**

Three documented **false-greens**. Same shape every time:

```text
APPARENT GREEN → REAL FAILURE → AUTHORITY / FALSIFY REQUIRED → VERDICT
```

Adversarial red-teams "looks fine." Framework + Cutline catch what will rot later. Review first. Trust after.

Copy a card into a PR, chat, or post. Deep links open the full public-safe writeup on [falsify.site](https://falsify.site/).

---

## Card 01 — Derived freshness

**Link:** https://falsify.site/examples/real-cases/02-derived-freshness-stale-panel  
**Domain:** Live executor · scheduled bot

| | |
|--|--|
| **Apparent green** | Cron OK, today's signal timestamp, executor `--verify` PASS |
| **Real failure** | Underlying panel CSVs stopped updating weeks earlier; signal was fresh on stale history |
| **Authority / Falsify** | Refresh + coverage gate before signal; incident replay through the **real** production wrapper; input provenance manifest |
| **Verdict** | Production-looking green without upstream freshness = **BLOCK** until gates close |

**One-liner:** *Today's signal, weeks-old inputs.*

---

## Card 02 — Evidence integrity reversal

**Link:** https://falsify.site/examples/real-cases/04-round3b-evidence-integrity-reversal  
**Domain:** Quant research · saved returns

| | |
|--|--|
| **Apparent green** | Saved returns passed DSR, PBO, permutation (headline SR ~3.95) |
| **Real failure** | Missing-feature policy (implicit zero-fill) shaped the matrix; coverage as low as ~36%; variants collapsed the green |
| **Authority / Falsify** | Calendar contract, row-loss audit, coverage manifest, explicit missing-policy variants **before** metric gates |
| **Verdict** | Statistical PASS withdrawn as authority → **BLOCK** / no live authority |

**One-liner:** *A strict PASS overturned by hidden input assumptions.*

---

## Card 03 — Mirror vs runtime

**Link:** https://falsify.site/examples/real-cases/05-second-runtime-v068-sync-false-green  
**Domain:** Runtime · deployment parity

| | |
|--|--|
| **Apparent green** | Vault mirror contained the v0.6.8 return-basis fix |
| **Real failure** | Executable second-profile runtime still ran the old tree (orphan “fixed” mirror) |
| **Authority / Falsify** | Resolve **executable** path; compare runtime vs mirror; same semantic fixtures in both trees |
| **Verdict** | Clean mirror ≠ runtime PASS → pre-fix **BLOCK** until parity proven |

**One-liner:** *The mirror was fixed. The runtime was not.*

---

## Paste block (all three)

```text
Falsify — Looks green isn't proof.
1) Fresh signal / stale panel — https://falsify.site/examples/real-cases/02-derived-freshness-stale-panel
2) Stats PASS / missing-data policy — https://falsify.site/examples/real-cases/04-round3b-evidence-integrity-reversal
3) Mirror fixed / runtime not — https://falsify.site/examples/real-cases/05-second-runtime-v068-sync-false-green
Review first. Trust after. Install: https://falsify.site/docs/14-github-action-install.html
```

## Full sources

- `02-derived-freshness-stale-panel.md`
- `04-round3b-evidence-integrity-reversal.md`
- `05-second-runtime-v068-sync-false-green.md`
