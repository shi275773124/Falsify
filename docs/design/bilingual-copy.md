# Falsify Bilingual Copy Map

The page keeps a true bilingual system. The language toggle switches visible homepage copy through a single content map. The founder quote remains the original Chinese source evidence in both modes.

## English

Hero eyebrow: Adversarial sign-off workspace

Hero headline: One AI review isn't enough.

Hero subtitle: Falsify turns high-risk AI conclusions into attacks, cutlines, verdicts, and raw artifacts before they reach production.

Primary CTA: Run sample review

Secondary CTA: View raw artifact

Product loop: Submit / Attack / Cutline / Verdict / Artifact

Product loop title: From claim to sign-off.

Sign-off stack title: The Adversarial Sign-off Stack.

Use-case title: Where AI conclusions need sign-off.

Sharpe headline:
Sharpe 4.06.
6/7 gates passed.
Still BLOCKED.

Sharpe subline: The math passed. The assumption failed.

Archive title: Raw artifact or it didn't happen.

Product reality title: What exists today.

Final CTA title: Run the gate before trust.

## Chinese

Hero eyebrow: 对抗签署工作区

Hero headline: 一次 AI 审查还不够。

Hero subtitle: Falsify 在高风险 AI 结论进入生产前，把它们转成攻击、分界线、裁决和原始证据。

Primary CTA: 运行示例审查

Secondary CTA: 查看原始证据

Product loop: 提交 / 攻击 / 分界线 / 裁决 / 证据

Product loop title: 从结论到签署。

Sign-off stack title: Falsify 对抗签署栈。

Use-case title: 哪些 AI 结论需要签署。

Sharpe headline:
Sharpe 4.06。
6/7 关通过。
仍然 BLOCK。

Sharpe subline: 数学通过了。假设失败了。

Archive title: 没有原始证据，就不算发生。

Product reality title: 今天已经存在的能力。

Final CTA title: 先过关，再信任。

## Founder field note

Quote:
「六道关全过了。距离上实盘只差一个机制——直到第二轮重跑，Sharpe 直接崩了。」

Identity:
Chris Shi

Treatment:
- The quote uses Chinese sans, not mono.
- The label and metadata may use mono.
- It is origin evidence, not a testimonial.

## Implementation rule

Use one content map:

```js
content = {
  en: { ... },
  zh: { ... }
}
```

Do not scatter new hardcoded copy across HTML after the system is stabilized.
