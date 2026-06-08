# Falsify · 证伪

> **你的 unfair advantage:让两个不同厂商的顶尖 AI 互相审查，你只取站得住脚的结论。**
> 一次提问，它们替你死磕。花 token，省心力——而且这是单厂商一个 `--verify` 复制不了的:OpenAI 不会让你用 Claude 当审稿人,跨厂商互查只有你能做。

[![falsify](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml/badge.svg)](https://github.com/shi275773124/Falsify/actions/workflows/falsify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![English](https://img.shields.io/badge/lang-English-blue.svg)](./README.md)

[English](./README.md) · [部署](./docs/02-setup.zh-CN.md) · [第 1 层 · 互审](./docs/03-collaboration.zh-CN.md) · [第 2 层 · 对抗审议](./docs/05-adversarial-review.zh-CN.md)

<p align="center">
  <img src="./assets/flow-card.png" alt="Falsify 证伪：Agent A 起稿 → Agent B 审计 → 分歧 → 一手资料仲裁 → Git 留证据链 → Ship" width="820">
</p>

> 🙏 致谢 **Hermes Agent**、**Claude Code**、**Codex**——这套工作流在它们上面跑通并打磨出来。

---

单 AI 写完，你得自己验。**Falsify 让第二个、不同的顶尖模型把它的活拆一遍**——错的数字、站不住的结论，到不了你眼前。一个写，一个审，Git 留证据链。

<p align="center">
  <img src="./assets/demo.gif" alt="falsify review 实跑：Skeptic 抓出 4+ 处问题 → Verdict: HOLD" width="760">
</p>

> 真实运行:DeepSeek 当 Skeptic 审一份草稿,把埋的错一个个抓出来,给出 `Verdict: HOLD`。逐字记录见 [examples/.../06](./examples/comparison-case-study/06-real-review-deepseek.md)。

---

## 为什么值

- **省事** —— 一次劳动,拿到一份已经过两个顶尖大脑审视的报告。
- **1 + 1 > 2** —— 两个不同模型互查,一个的盲区被另一个补上。
- **不是感觉稳,是真能验证** —— 它确实抓得出单模型会 ship 的错。下面有真实案例。

适合:用 AI 做研究/竞品/技术选型的工程师、要可靠输出又不想逐字核对的人、想把 AI 决策做得可审计的团队——以及想快速上手的新用户(fork [`demo-vault/`](./demo-vault/) 填空就能跑)。

---

## 真实案例:一个 Sharpe 4.06 的策略,在上真钱前被拦下

单 AI 跑出一个量化策略,所有指标全过——`Sharpe 4.06–4.31`、`PBO 0.000`、`DSR p < 1e-7`、7 门审计过 6 门。工作流的下一步,就是小仓位**上真钱实测**。

Falsify 强制第二个模型(不同厂商)对抗复审。5 轮之后,策略被改判 `NOT_VIABLE`:这个 Sharpe 不是 alpha——是把交易成本摊到一个**策略自己设计上从未真正持有过**的持有期上(假设约 14 天,真实约 1.5 天 → **成本被低估约 9 倍**)。把成本按真实持有期摊回去,edge 就没了。

而且过程中,reviewer **三次自己打脸**——先下一个结论,重跑数字,再在数据对不上时撤回自己的断言。一个审自己活的模型只会维护它写的东西;一个独立的模型会重新推导、把自己拉回来。

> 为什么必须两个厂商:当作者和审稿人是同一个模型,`PBO=0`、`DSR p<1e-7` 只能证明结果**在它自己的假设内部**自洽——证明不了那个假设本身是不是真的。只有一个盲区不同的审稿人,才会去质疑假设本身。

**→ 完整脱敏审计日志,数字原样:** [examples/real-cases/01](./examples/real-cases/01-fictional-horizon-quant-audit.zh-CN.md)

<details>
<summary>另外——一份约 12 家竞品费率横评里抓出的 4 个错(可复现逐字记录)</summary>

两个独立 Agent(不同模型)做了约 12 家同品类竞品的费率横评,80+ 引用 URL,约 30 分钟出报告。Agent B 抓出 4 处本来会 ship 的关键费率错:

| 被拦下的问题 | 单 Agent 会怎样 | 双 Agent 互审后 |
|---|---|---|
| Venue A 费率沿用了同行数字 | 表看着完整,实际差 2 倍 | B 异议,回官方 docs 仲裁 |
| Venue B VIP0 maker 方向反了 | 返佣写成支出,进报告 | B 复核 fee schedule,要求改 |
| Venue C 高级档"未公开" | 其实 docs 已写,被过早放弃 | B 查证并标冲突 |
| Venue D base 费率读错行 | 错误行混进对比表 | B 审表,要求回源 |

逐字记录:[examples/.../06](./examples/comparison-case-study/06-real-review-deepseek.md)

</details>

---

## 一键开跑

```bash
pip install -e .                       # 或直接 python falsify.py
export DEEPSEEK_API_KEY=sk-...         # 或 OPENAI_API_KEY / OPENROUTER_API_KEY…
falsify review report.md -p deepseek   # 第二个模型审一遍 → Verdict（PROCEED/HOLD/ARCHIVE）
```

`-p` 是 provider 预设(deepseek / openai / openrouter / moonshot / siliconflow / local),自动填好 endpoint 和模型——**你只给 key**。嫌每次敲麻烦就 `falsify init` 存一次,之后 `falsify review report.md` 即可;也能 `cat report.md | falsify review -` 粘贴即跑。

`review` 的**退出码就是 Verdict**(`PROCEED=0 / HOLD=1 / ARCHIVE=2`)——直接塞进 CI。
不用 key 先试 `lint`(纯本地、零 API):

```bash
falsify lint examples/comparison-case-study/05-final-excerpt.md   # → SHIPPABLE
```

---

## 两层审查

- **[第 1 层 · 互审](./docs/03-collaboration.zh-CN.md)** —— 抓**数字错**(便宜、默认):每段标作者、不覆盖对方、冲突走一手资料。
- **[第 2 层 · 对抗审议](./docs/05-adversarial-review.zh-CN.md)** —— 抓**结论错**(高风险时):verdict ladder(`PROCEED/HOLD-N/ARCHIVE`)+ 多轮 + G1–G4 闸门 + 跨模型独立性。

| | 第 1 层 · 互审 | 第 2 层 · 对抗审议 |
|---|---|---|
| 抓什么 | 错的事实 | 对的事实 + 错的结论 |
| 一句话 | "这个数字对不对?" | "这个结论凭什么成立?" |

---

## 仓库里还有什么

- [`web/`](./web/) —— 浏览器粘贴即审 POC:一个框一个按钮 → Verdict + top 风险(`python web/serve.py`)
- [`templates/`](./templates/) —— 即拿即用:`AGENTS.md`、三个 prompt、kickoff/retro、conflict/resolution log、CI 模板
- [`demo-vault/`](./demo-vault/) —— 可直接 fork 的空壳工作区,改 `00-brief.md` 就能跑
- [`examples/comparison-case-study/`](./examples/comparison-case-study/) —— 脱敏端到端样例(draft→audit→冲突→仲裁→上线 + 一次真实运行)
- [`examples/cases/`](./examples/cases/) —— 跨行业案例库(技术选型 / 市场调研…),每个证明"没 Falsify 这个错会 ship"
- [`docs/`](./docs/) —— [架构](./docs/01-architecture.zh-CN.md) · [部署](./docs/02-setup.zh-CN.md) · [协作](./docs/03-collaboration.zh-CN.md) · [对抗审议](./docs/05-adversarial-review.zh-CN.md) · [故障排查](./docs/04-troubleshooting.zh-CN.md)

---

## Roadmap

- [x] CLI 引擎 `falsify`(lint / review / verdict 闸门)
- [x] 一键化:provider 预设(`-p deepseek`)/ `.falsify` 配置 / 粘贴即跑
- [x] Web 粘贴即审 POC（[`web/`](./web/)）
- [x] GitHub Action:PR 没过 verdict 就 block([模板](./templates/github-action-falsify.yml))
- [x] 可 fork 的 demo vault · 脱敏案例 · 流程图 · 真实运行 GIF
- [x] 跨行业案例库起步（[`examples/cases/`](./examples/cases/)):技术选型 / 市场调研
- [ ] 托管 web:免 key 试 3 次(粘贴即审、零安装)
- [ ] Chrome 插件:在 ChatGPT / Claude / Gemini 页面一键 Falsify
- [ ] 补更多行业案例:法律 / 医疗 / 产品 / 学术

## Contributing

欢迎:新场景模板、脱敏案例、更会找错的 prompt、更多 agent 接入示例、翻译。Fork → 小步改 → 提 PR(说清你解决的痛点)。想先聊就开 Issue。

---

## License

MIT —— 随便 fork、随便 ship、欢迎写文章传播。

<details>
<summary>支持作者</summary>

- 🐦 [@aishikejian](https://x.com/aishikejian) · ☕ [Buy me a coffee](https://buymeacoffee.com/chris168) · ⭐ Star

</details>
