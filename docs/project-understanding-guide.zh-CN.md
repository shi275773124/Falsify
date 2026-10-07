# 项目理解（Project Understanding）使用说明

状态：本机功能已实现并通过回归；非作者独立审计见交付包记录。本文描述的命令以当前 CLI 为准。

## 这是什么

`falsify review` 之后，可选地生成一页**可追溯的项目理解**：它怎样运转、靠哪些假设成立、这次审查发现了什么（机制含义）、你原先的解释需要哪些修正、还有哪些没弄清。然后在本地阅读页里查来源、写下自己的话、确认或改写、导出带走。

**它不是**：不是重新裁决，不是权威升级，不是掌握度评分。原 review 的 verdict、authority、退出码、签名完全不变。

## 生成

```powershell
python -m falsify review .tmp/project-understanding-demo/subject.md --json `
  --understanding-out .tmp/project-understanding-demo/result `
  --understanding-materials .tmp/project-understanding-demo/materials.json `
  --understanding-before .tmp/project-understanding-demo/before.md
```

参数（均针对 `review` 子命令）：

| 参数 | 作用 |
|---|---|
| `--understanding-out DIR` | 启用理解生成，产物写入 DIR（`understanding.json` + `understanding.md`）。不提供时行为与原 review 完全一致 |
| `--understanding-materials FILE` | 补充材料清单 JSON。路径相对清单所在目录；拒绝越界路径、符号链接、二进制、单文件 >128 KiB、合计 >512 KiB、重复或保留 ID |
| `--understanding-before FILE` | 你在审查前亲自写的解释或疑问，原样记录 |

规则：

- 启用后**最多多一次** `llm()` 调用，用 review 已配置的 provider/model/base，不新增任何注册或密钥。
- 材料清单/原话文件单独提供（不启用生成）会得到用法错误。
- stdout 仍只有一个可解析 JSON（原 review payload）；理解进度、错误、输出路径全部走 stderr；退出码仍由原 decision 决定。
- 材料仅作解释输入，标为「补充材料，未被本次审查核验」，不扩大原审查范围。
- 已有 `understanding.json/md` 的目录拒绝覆盖；重跑用新目录。输出路径与输入、材料、before、`--out` 别名时拒绝写入。
- 模型失败（provider 不可用、非 JSON、截断、引用校验失败）→ 写一个 `generation_status = unavailable/invalid` 的诚实失败产物（含 `failure_reason`），不伪造完整解释。

### 材料清单格式

```json
{
  "sources": [
    {"id": "ARCH", "path": "architecture.md", "kind": "document"},
    {"id": "CODE", "path": "billing.py", "kind": "code"},
    {"id": "PROBE", "path": "probe-output.txt", "kind": "raw_output"}
  ]
}
```

保留 ID：`SUBJECT`（审查文本）、`RECEIPT`（原审查记录）、`BEFORE`（用户原话）不能被材料占用。

## 阅读

```powershell
python web/serve.py
# 打开 http://127.0.0.1:8000/understanding?lang=zh （英文 ?lang=en）
```

- 用文件选择器导入 `understanding.json`；浏览器本地读取，服务器不碰你的磁盘路径。
- 页面按 schema/引用/哈希校验；未知版本或伪造引用直接给可读错误，不按成功展示。
- 五块内容：怎样运转 / 靠什么成立 / 这次发现了什么 / 我的解释与修正 / 还有什么没弄清。
- 每条解释带认识状态徽章（source_observation / claim / inference / unknown）与来源引用，点击引用打开带行号的原文快照并高亮。
- 来源区可重新选择当前磁盘文件，与快照 SHA256 比对：一致 / 变化 / 未提供。展示的是「来源快照；当前文件未复核」。
- 修正建议可逐条**确认**、**撤销**（恢复为建议）或**改写后确认**；只影响该项，不碰其他。推演题答案仅记录为用户表达，不判分。
- 刷新清空未导出的编辑（无 localStorage、无上传）。

## 导出

- 「包含我的原话/笔记/全文」两个开关 + 预览；确认后本地下载 JSON / Markdown。
- 排除原话时同步移除相关私人引文与以其为依据的修正记录；省略原文的来源按 `content_state = withheld` 导出（无 text，引用无 quote，标记无法核对）。
- 省略原文**不是自动脱敏**：解释文字里仍可能含私人信息。首版不宣称导出物可公开。

## 认识状态契约

| 状态 | 含义 |
|---|---|
| `source_observation` | 材料里直接可见（「报告说成功」≠「实际成功」） |
| `claim` | 项目方或审查记录提出的主张 |
| `inference` | 基于材料的解释/因果推断；有引用也不升级为事实 |
| `unknown` | 证据不足；附所缺证据 |

引用 = `source_id + start_line + end_line + quote`（行号从 1 起，quote 必须逐字出现在该范围）。程序校验存在性与一致性；引文是否**支持**结论由人工阅读核对。

## 契约与测试

- Schema 契约：`docs/contracts/project-understanding.schema.json`（`falsify.understanding.v1`）。
- 测试：`python -m pytest tests/test_understanding.py`（26 项，覆盖材料拒绝、伪造引用、截断、BLOCK 保留、dry-run、覆写拒绝、withheld 往返等验收场景）。
- 阅读页路由测试在 `tests/test_web.py::test_understanding_routes_serve_fixed_allowlist_only`。

## 已知限制（首版）

1. 无自动评判用户答案的第二轮模型调用（有意）。
2. 只导入 JSON，不承诺导入 Markdown。
3. 引用校验是机械一致性，不判断语义支持。
4. 基线仓库存在与本功能无关的既有失败测试（已记录，未顺手修改）。
5. 真实 provider 烟测取决于本机配置；未执行时如实记录，不作为已验证主张。
