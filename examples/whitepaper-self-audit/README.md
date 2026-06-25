# 白皮书自审 run artifact（公开可复现）

本目录是 Falsify 对它自己的白皮书做对抗审的**真实运行记录**。它存在的意义：证明 Falsify skill 不是规范文档，是一个能跑、已跑、跨厂商的工具。

## 这是什么

`docs/WHITEPAPER.zh-CN.md` 被 Falsify CLI 审了两轮。作者方是 Claude（Sonnet），审稿方（Skeptic）是 GPT-5.5——**真实跨厂商独立**，不是同一模型自审。

- `v0.1-verdict.txt` — 第一轮，BLOCK，7 Must Fix + 1 Known Debt
- `v0.2-verdict.txt` — 第二轮（修复 v0.1 后），BLOCK，8 Must Fix（升级到要求 enforcement 代码）

## 如何自己复现

```bash
git clone https://github.com/shi275773124/Falsify
cd Falsify
export FALSIFY_API_KEY=<你的 OpenAI 兼容 key>
python3 falsify.py review docs/WHITEPAPER.zh-CN.md \
  --base <你的 endpoint>/v1 -m gpt-5.5
```

退出码 = verdict：PASS=0 / PASS_WITH_DEBT=1 / BLOCK=2。可直接 gate CI。

## 为什么两轮都 BLOCK 还要公开

这正是 dogfooding 的诚实形态。两点：

1. **工具有效**：它在自己作者的文档里抓出了二手当一手（brooks-lint 6 类 vs 实际 12 类）、论证自撞、能力 overclaim——这些是真实缺陷，已逐条修。
2. **工具的边界也暴露了**：v0.2 的 BLOCK 里有几条把"白皮书"当"上线真钱系统"审，要求正文内附 enforcement 代码——这说明无 Cutline 锚的对抗审会无限升级。这本身是 Falsify 第 3 层（Cutline）存在的理由，也写进了白皮书附录 A。

一份文档被审过，不等于它通过了审。公开这两份 BLOCK，是把审计通道交给人类复核（白皮书第 8 节），包括复核 Falsify 自己。
