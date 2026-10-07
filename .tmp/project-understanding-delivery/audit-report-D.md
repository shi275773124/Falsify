# 审计报告 D — project-understanding（安全）

> 记录说明（集成者 C 代录）：本报告由非作者独立审计 subagent（security-review，独立上下文，未参与实现）于 2026-10-07 生成；该审计会话为只读模式无法写文件，故由集成者按原文落盘，内容未改动。审计共两轮：第一轮覆盖 git diff 内 31 个文件；第二轮针对 untracked 新文件（`falsify/understanding.py`、`web/understanding/*`、`tests/test_understanding.py`、fixtures）按冻结清单 sha256 抽验。审计员自述的覆盖范围声明保留在第 7 节，不作全量逐行审的声明同样保留——这是本报告的诚实边界。

**结论：PASS（各分区均 PASS）。未发现中/高/危级别的安全漏洞。**

## 1. CLI 侧出口隔离 — PASS
`falsify/cli.py:1230-1244`：`_run_optional_understanding` 仅在非 dry-run 时执行，包在 `except Exception` 里只打 stderr；`sys.exit(exit_code_for_decision(decision))` 在其后仍由原 decision 决定。`main()` 中 usage guard（cli.py:1831-1838）拒绝孤儿参数。**审查裁决/退出码无被旁路路径。**

## 2. 材料/文件系统边界 — PASS
`falsify/understanding.py` 的 `load_materials`（已核对冻结清单 sha256 对应实现）：manifest ≤64KiB、单文件 ≤128KiB、总量 ≤512KiB；`(base / path).resolve()` 剥离 `..` 越界、拒绝 symlink、拒绝二进制、拒绝重复/保留 ID（SUBJECT/RECEIPT/BEFORE）。`_check_output_paths` 拒绝覆盖已存在产物、拒绝与 subject/materials/before/`--out` 别名；`tests/test_understanding.py:342-354` 断言 `refusing to overwrite` + 原文件内容不变。写盘走 `.tmp` + 原子替换。本地 CLI、路径由调用者自持 — 符合"用户自控 workspace 不构成边界"基线，且代码本身已收紧。

## 3. Web 服务器路由 — PASS
`web/serve.py:1066-1079`：`/understanding` 页面与 `/understanding/*` 资产为**固定 allowlist**（`UNDERSTANDING_FILES`，web/serve.py:485-491），显式拒绝 `..`、`/`、`\`，无目录遍历；POST 未实现 → 404（tests/test_web.py:89-117 覆盖 traversal/walk/POST）。缓存 `no-cache`，复用全局 CSP（serve.py:960-967：`script-src 'self'`、`object-src 'none'`）与 `X-Content-Type-Options: nosniff`。固定资产来自部署时仓库内容，非运行时用户输入。

## 4. 浏览器渲染 / XSS — PASS
`web/understanding/understanding.js` 全部经 `textContent` / `createTextNode` 渲染模型与用户文本；仅静态 sink（`btn.setAttribute("aria-label", …)`）；引用行号经 `Number.isInteger` + 边界校验（understanding.js:228-236）。**XSS 有执行级 PoC 验证为不触发**：`browser_acceptance.py:129-139` 注入 `<img src=x onerror=window.__xss=1>`，断言 `window.__xss === null` 且文本以纯文本显示（acceptance-report.json `xss not executed: ok`）。本地文件导入、无上传端点、无 localStorage。

## 5. 数据外发 / 凭据 — PASS
新增路径唯一网络调用是复用 review 已配置 provider 的一次 `llm()`；`generation_meta` 记录 provider/model/base，无密钥落盘或日志。`.tmp/` 演示脚本（`run_demo.py`、`browser_acceptance.py`、`debug_import.py`）仅绑 `127.0.0.1`、mock 模型，属开发残留，非生产面。

## 6. LLM 提示注入校准 — PASS（无发现）
产物是阅读层 side-artifact，epistemic_status 明示 claim/inference/unknown，`scope.not_covered` 明确不扩大权威；不构成对 verdict/authority 的自动升级或特权变更，不满足需报告的自治后果门槛。

## 7. 覆盖范围声明（审计员原文）
diff 为 46 文件中的 31 个；`falsify/understanding.py`、`web/understanding/*`、`tests/test_understanding.py`、docs 三篇及 5 个 fixture 未包含在 `<diff>` 中，通过冻结清单 hash + 局部 grep/Read 抽验（覆盖路径收容、覆写拒绝、DOM sink、CSP），未做全量逐行审。

---

## 集成者复核（C，按计划要求复核至少一个关键攻击）

复核攻击点：**「排除原话导出是否泄漏 before 文本」**（计划验收场景「导出排除原话/原文」）。

- 代码路径：`web/understanding/understanding.js` `buildExport(includeNotes=false, …)`。
- 攻击构造：artifact 含 `suggested_revisions[].before`（用户原话）、`user_notes.before_recorded`、`user_notes.answers[].answer`。
- 结果：三者均被清除（`before_recorded=null`、`answers=[]`、`suggested_revisions=[]`），且浏览器验收 `minimal drops notes` / `minimal withholds texts` 两项 PASS（`.tmp/project-understanding-demo/browser-acceptance/acceptance-report.json`）。
- 结论：与审计员判定一致，PASS。

冻结清单核对：`freeze.py` 重新运行比对 21 个文件 sha256 全部一致（见 `delivery-check.json`）。
