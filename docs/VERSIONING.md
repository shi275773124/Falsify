# Versioning（对外唯一产品版本轨）

> 根治白皮书缺口 #2。详见 [ROOTFIX-architecture.md](./ROOTFIX-architecture.md)。

## Public product version（唯一对外）

| 项 | 规则 |
|----|------|
| **权威** | `falsify/__init__.py` → `VERSION`（当前示例：`0.6.0`） |
| **徽章** | README / 站点 / PyPI 只展示此版本 |
| **语义** | semver：协议或 CLI 破坏性变更 → major；功能 → minor；修复 → patch |
| **packs** | 不设独立 public 版本；变更写入主仓 CHANGELOG / release notes |

## 禁止

- 在对外材料中把 **Pro skill `0.9.x`**、**falsify-skill `0.1.x`** 与 **`VERSION`** 并列成「Falsify 现在是 x.y.z」的同一数字。  
- 用 star 数或 commit 数冒充版本。

## 分轨（对内 / 分发）

| 轨 | 文件 | 如何提及 |
|----|------|----------|
| Pro skill | Pro `SKILL.md` `metadata.version` | 「Pro runtime v0.9.15」仅 cockpit / 运维 |
| falsify-skill | 其 frontmatter `version` | 「Agent skill package v0.1.0，**requires Falsify ≥ 0.6.0**」 |
| 协议 schema | `falsify.review.v1` | 协议代；破坏性改 v2 |

## Release checklist（主仓）

1.  bump `VERSION`  
2.  release notes：协议 / CLI / packs / quant  
3.  若 falsify-skill 依赖变：更新其 `requires` 并 bump 壳版本  
4.  不 bump Pro 除非私有 runtime 同步发布（对内）

## 读者速查

| 问题 | 答案 |
|------|------|
| Falsify 产品现在几版？ | 看主仓 `VERSION` |
| 我机器上 hermes 风险裁刀几版？ | 看 Pro SKILL.md |
| npx 装的 skill 几版？ | 看 falsify-skill package version + requires |
