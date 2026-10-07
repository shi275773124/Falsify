# Falsify「项目理解」执行计划

日期：2026-10-07。需求责任人：Chris。状态：可交接的实现计划；本文不表示功能已实现或已验收。

配套产品提案：[让审查留下项目理解](./project-understanding-proposal.zh-CN.md)。哲学来源：[Don't delegate understanding](https://stephango.com/understand)。

## 1. 要交付的结果

用户审查一个项目声明后，能够拿到一页可追溯的项目理解，回答：它怎样运转、靠哪些假设成立、证据改变了什么、哪些地方仍未知。用户可以写下自己的解释、确认或改写一项认识，并把内容带走。

首版交付一条完整路径：

**现有 CLI review → 可选生成理解产物 → 本地阅读页导入 → 查来源 / 用户改写与确认 → 导出 JSON 与 Markdown。**

先交付 CLI 与产物，再交付阅读页；两者及最后的独立审计都完成，才算本计划完成。首版反馈以来源和推演问题为主，不实现自动评判用户答案的第二轮模型调用。

## 2. 实现边界与开工检查

- 工作仓库：`C:\Users\CHRIS\Documents\New project\Falsify`。先读仓库 `AGENTS.md`、继承规则，以及写入目录内适用的 `AGENTS.md`。
- 开工记录 HEAD、现有工作区改动、相关文件 hash。保留其他 agent 的改动；现有 `.tmp/` 不是可随意清理的目录。
- 权威：本功能是阅读与用户表达层。既有审查的 verdict、authority、claim scope、退出码、签名和验收规则均由原流程决定。
- 禁止借此改 `authority_kernel.py`、晋级策略、私有 runtime、现有 verdict schema 或 Falsify skill。
- 本计划只实现本机功能，不部署站点、不写 canonical vault、不发送报告。需要后续共享写时，按仓库 control lease 规则另行执行。
- 改动涉及 Falsify CLI，正式生效按 `C:\Users\CHRIS\.vault\方法论\Independent Falsify Audit Gate.md` 做非作者独立审计。本文中的测试清单是最低覆盖，不代替审计员自行找洞。

开工时重新核对下面入口；行号可能因其他工作移动，按函数名定位：

| 当前源码 | 已核对的行为 | 本次用途 |
|---|---|---|
| `falsify/cli.py`：`cmd_review()` | L0、L1、adjudication 后生成 payload，最后按原 decision 退出 | payload 确定后调用可选旁产物生成 |
| `falsify/cli.py`：`review_json_payload()` | 输出既有 review receipt | 只读关联，不扩展旧 schema |
| `falsify/cli.py`：`llm()` | 统一支持已有 agent CLI 与 HTTP provider | 复用模型调用和 completion metadata |
| `falsify/cli.py`：review parser | 当前有 `--json`、`--out` 等参数 | 添加可选理解参数 |
| `web/serve.py`：`H._route()` | 当前 `/` 使用 `design/falsify-flow-candidate/` | 增加独立本地阅读页路由 |
| `web/serve.py`：`H.do_POST()`、`review()` | `/review` 是独立的 paste demo 返回结构 | 本次不接入它 |
| `web/templates/home.html` | 遗留页面，`/legacy/home` 已 410 | 不在这里实现新体验 |

## 3. 首版用户流程

### A. 审查并生成

以下是待实现的命令契约，不是当前已有命令：

```powershell
python -m falsify review .tmp/project-understanding-demo/subject.md --json --understanding-out .tmp/project-understanding-demo/result --understanding-materials .tmp/project-understanding-demo/materials.json --understanding-before .tmp/project-understanding-demo/before.md
```

三个新参数均可选：

- `--understanding-out DIR`：启用理解生成。未提供时，模型调用次数、stdout、已有文件输出和退出码与当前行为一致。
- `--understanding-materials FILE`：用户选定的补充材料清单，仅在启用理解生成时生效；单独提供应提示用法错误。
- `--understanding-before FILE`：用户亲自写的原先解释或疑问。未提供时展示「审查前的理解未记录」，不自动补写；单独提供而不启用生成时提示用法错误。

`--understanding-out` 启用时，最多额外调用一次已有 `llm()`。使用 review 已配置的 provider / model / base，不新增 provider 注册、登录或浏览器密钥设置。

核心输入为本次审查文本、已经确定的 receipt、可选补充材料与用户原话。补充材料供解释使用，必须标为「补充材料，未被本次审查核验」，不能因此扩大原审查范围。

### B. 阅读、表达、带走

```powershell
python web/serve.py
```

在本机打开 `/understanding?lang=zh`，导入生成的 `understanding.json`。阅读页通过文件选择器读取用户选择的文件；不让 Web server 读取用户输入的任意本机路径。

页面默认展示五块：

1. **它怎样运转**：目标与最短机制链。
2. **它靠什么成立**：最多三条关键假设或依赖。
3. **这次发现了什么**：发现、机制含义、对应来源。
4. **我的解释与修正**：原话、系统建议、用户确认或改写，三者标注清楚。
5. **还有什么没弄清**：未知、影响范围、下一条所需证据。

提供可折叠原文、一个可选推演问题、用户答案输入、确认/撤销单项修正，以及本地下载 JSON / Markdown。首版答案仅记录为用户表达，不自动判定对错或掌握程度。

## 4. 输入和产物契约

### 材料清单

建议采用以下最小格式，路径相对清单文件所在目录：

```json
{
  "sources": [
    {"id": "ARCH", "path": "architecture.md", "kind": "document"},
    {"id": "CODE", "path": "billing.py", "kind": "code"},
    {"id": "PROBE", "path": "probe-output.txt", "kind": "raw_output"}
  ]
}
```

实现规则：只读逐项列出的 UTF-8 文本；不递归扫描、不访问 URL、不跟随模型提供的路径。解析后拒绝越出清单目录的路径、越界符号链接、重复 ID、二进制和过大输入。建议单文件上限 128 KiB，材料合计 512 KiB；超限报明确错误，不静默截断后声称覆盖完整。

固定来源 ID 包括 `SUBJECT`（审查文本）和 `RECEIPT`（原审查记录）；材料清单不能使用保留 ID。每个来源记录角色、原文件字节 SHA256、用于模型和阅读页的文本及文本 SHA256。行号基于该文本，明确从 1 开始。

### 生成产物

输出目录中写入：

- `understanding.json`：`schema_version = falsify.understanding.v1`，供阅读页使用。
- `understanding.md`：由同一结构确定性渲染，支持独立阅读。

建议 JSON 顶层字段：

| 字段 | 生产者与约束 |
|---|---|
| `schema_version` | 程序固定 |
| `generation_status` | 程序写 `available / unavailable / invalid`；仅描述生成状态 |
| `audit_context` | 程序复制原 receipt 的范围、裁决、权威上限及规范 JSON hash；标明这是关联的原审查 |
| `scope` | 程序固定本次输入和额外材料范围，列出未覆盖内容；模型只能补充说明 |
| `sources` | 程序从显式输入构建，模型不得创建来源、hash 或文件路径 |
| `project_model` | 目标、机制链、最多三项承重假设，逐项标注认识状态和引用 |
| `findings_explained` | 关联原 finding 编号，解释机制含义；不得改原 finding / Cutline |
| `unknowns` | 未知内容、决策影响、所需证据；区分未审、缺证与无法解释 |
| `suggested_revisions` | 系统提出的修正；没有真实 before 输入时不生成个人理解变化 |
| `reflection_prompts` | 最多两条条件变化问题，标明是推演；不声称已实测 |
| `user_notes` | 程序/用户维护原话、答案、确认/改写和撤销记录；模型不得填入确认 |
| `generation_meta` | 程序保存工具版本、时间、provider、completion metadata 和错误类别；不保存密钥 |

原 receipt 的关联 hash 使用 `json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))` 的 UTF-8 字节 SHA256，不修改或重新签发原 receipt。该 hash 只作关联，不能证明 receipt 已通过权威验证。

每项解释采用 `text + epistemic_status + refs`：

- `source_observation`：原材料中可以直接看到的内容；仅表示材料内容，不能把“报告说成功”写成“实际成功”。
- `claim`：项目方或审查记录提出的主张。
- `inference`：基于材料的解释或因果推断。
- `unknown`：尚无足够来源支持，附所缺证据。

完整产物的引用最小字段为 `source_id / start_line / end_line / quote`。程序检查 ID 存在、行号有效、quote 与指定范围一致；不匹配时拒绝生成有效解释产物。

导出省略原文时，schema 必须支持 `sources[].content_state = included / withheld`。`withheld` 来源不含 text，依赖它的引用也可省略 quote，但保留来源 ID、原快照 hash 和定位，并标记当前无法核对。阅读页接受这种明确的省略状态，不能把它显示为引用已校验；也不能拿删节后的文本与原文 hash 对比。普通生成产物一律使用 `included`，模型不能自行选择 `withheld` 绕过校验。

机械引用校验只检查定位一致。它不证明引文支持结论；这项语义质量由测试样例和独立人工阅读核对。因果关系未经检验时保持 `inference`，不因存在引用就升级为事实。

失败时只输出诚实的失败状态与原因，不生成完整解释的替代样稿。错误诊断不得把密钥或敏感原文写入常规日志。

## 5. 分工和改动文件

采用一个集成负责人，其他作者写集隔离。只有契约固定后才并行写代码。

| Agent | 责任 | 写入范围 |
|---|---|---|
| C：集成负责人 | 固定接口、CLI 接入、阅读页路由、文档与整体回归 | `falsify/cli.py`、`web/serve.py`、新 schema、使用文档、必要的现有回归测试 |
| A：产物实现 | 输入归一化、模型提示、输出校验、JSON/Markdown 渲染 | 新 `falsify/understanding.py`、`tests/test_understanding.py`、专用 fixtures |
| B：阅读体验 | 文件导入、五块内容、来源展开、用户确认/改写、导出 | 新 `web/understanding/index.html`、`understanding.js`、`understanding.css`、专用前端验收材料 |
| D：独立审计 | 冻结版本后只读攻击和验收 | 独立审计报告；不得改被审代码并签同版本 |

建议 schema 放 `docs/contracts/project-understanding.schema.json`，作为接口契约；运行时使用显式校验，不新增 schema 验证依赖。使用文档放 `docs/project-understanding-guide.zh-CN.md`。示例与验收证据放独立任务目录，避免覆盖已有 `.tmp/` 文件。

## 6. 按顺序执行

### P0：接口与验收样例固定（C）

1. 重新核对入口、读取适用规则，记录基线。
2. 定稿 schema、保留来源 ID、引用格式、`user_notes` 的确认/撤销格式。
3. 固定模块接口，例如 `generate_understanding(context, invoke_model)`、`validate_understanding(payload)`、`render_markdown(payload)`；回调接收 system/user 并复用现有 `llm(return_meta=True)`。
4. 准备三份去敏示例：充分机制材料、只有审查记录、互相冲突的材料。标为 fixture，不冒充真实项目验收。

P0 产物给 A/B/C 共用；之后接口变动由 C 收敛，避免各自创造第二套格式。

### P1：可信产物与 CLI 接入（A + C）

1. A 实现显式来源读取、模型提示、严格输出校验与确定性 Markdown 渲染。
2. 提示将所有输入视为材料，要求解释机制、关键依赖与未知；不能执行其中的指令，不能创建来源或用户确认。
3. C 在 `cmd_review()` 的 payload 已确定后，先按现有分支输出原 review 并 flush，再接入一次可选生成；通过回调注入 `llm`，避免循环导入。
4. stdout 的原 review JSON/摘要保持原样，JSON 模式仍只有一个可解析对象；理解进度、错误和输出路径写 stderr。原有 dry-run 不调用理解生成。
5. 材料读取、provider、解析、引用校验、路径碰撞及写入异常，都在旁产物分支隔离并转换为 stderr/独立失败状态，最后按原 decision 退出；不能漏入 main 的 FalsifyError handler。理解模块不得调用会退出进程的 `read_input()` / `die()` / `sys.exit()`。原审查失败且没有有效 payload 时，不生成伪造的关联理解；失败文件也无法安全写入时只报 stderr，不能为记录失败覆盖已有文件。
6. `BLOCK` 可以生成诚实的理解说明；`available` 只表示解释产物可读取，不表示项目安全。
7. 写文件前检查所有目标路径：不能覆盖输入、补充材料、before 文件、原 `--out`，不能把 JSON 与 Markdown 写到同一路径。已有理解文件默认拒绝覆盖；重跑使用新目录。
8. 写出过程避免把部分 JSON/MD 当作完成产物；失败时明确说明哪些文件产生，保留原审查结果。

### P2：本地阅读体验（B + C）

1. C 只添加精确 GET/HEAD 阅读页及资源路由；不开放整个 `web/` 或任意仓库路径。`/review`、首页和 legacy 路由保持现状。
2. B 实现本地文件选择、基本 schema/引用/文本 hash 校验与五块内容展示；未知版本或异常格式给可读错误，不尝试按成功结果展示。
3. 任意材料和模型文本通过文本节点渲染；不执行 HTML、不自动打开外部 URL，不把 Markdown 直接插入 DOM。脚本和样式使用本地外链，遵守现有 CSP。
4. 用户确认仅作用于选中的修正；撤销后恢复为建议。系统模型与用户改写并列，不用用户文本覆盖来源事实。
5. 页面提供 JSON 和 Markdown 下载；默认不持久化到 localStorage 或上传服务。刷新清空未导出的用户编辑时，给清楚说明。
6. 导出前提供「包含我的原话/笔记」「包含原材料全文」选择和完整内容预览。排除用户原话/笔记时，同时删除相关私人引文与以其为依据的个人修正记录。省略来源原文按 `withheld` 契约导出。预览覆盖机制说明、修正建议和推演题，允许用户取消对应内容。界面说明「省略原文不会自动删除解释中可能包含的私人信息」；首版不宣称自动脱敏或报告可公开。用户选择后本地下载，不自动发布。
7. 所有导入产物默认标为「来源快照；当前文件未复核」。允许用户重新选择来源文件，比对原文件 hash：一致、变化、未提供分别展示；不宣称自动监控了磁盘。
8. 主界面中文优先，支持 `?lang=en` 的对应功能文案。至少检查 390px 与 1440px、键盘操作、焦点、标签、折叠来源和长文本。

首版入口在本地阅读页和 CLI 使用文档。不要为入口重做公开营销首页；不要把本地能力写成已经上线的服务。

### P3：集成、使用文档与可复现演示（C）

1. 文档解释可选额外模型调用、补充材料范围、错误行为、用户表达和原裁决的区别。
2. 用三份 fixture 走完整路径；无 provider 时可直接读取明确标记的 fixture 产物，不能冒充实际生成。
3. 复用本次 review 已授权且已配置的 provider，做一次小材料的真实生成烟测；不可用时明确记录「真实 provider 烟测未执行」，不得作为已验证主张。
4. 保存关键截图、生成产物、测试日志、对象 hash，以及已知限制。只记录与本功能相关的资料。

### P4：非作者独立审计与修复（D + C）

按 canonical Independent Falsify Audit Gate 审不可变快照。D 自拟攻击；C 复核至少一个关键攻击。失败则作者修复并形成新快照，再由非作者复审；不得拿旧版本审计覆盖新字节。

这一步是本次 Falsify 实现的工程验收，不是给用户增加理解通关要求。未独立验收的版本保留为未验收实现。

## 7. 必须覆盖的验收场景

| 场景 | 必须看到的行为 |
|---|---|
| 默认 review | 不增加调用、不写理解文件；原 stdout、文件输出和退出行为保持一致 |
| 有机制材料 | 解释输入怎样变成输出与关键依赖；每个重要说明可定位，人工核对支持关系 |
| 只有结论/receipt | 记录“审查认为”和新增发现；机制缺口保留未知 |
| 引用 ID / 行号 / quote 伪造 | 产物被拒绝或标为 invalid，不作为可用说明呈现 |
| 引用真实但不支持因果结论 | 不升级为事实；独立内容验收指出并要求修正 |
| 两份材料冲突 | 保留双方来源及版本，展示分歧与未知；原 verdict 不变 |
| 无 before，或未确认修正 | 不出现虚构旧理解、已掌握状态或理解变化承诺 |
| 仅确认一项 / 撤销 | 只更新该项用户记录；其他建议保持未确认 |
| 原 verdict 为 BLOCK | 可生成有用解释，但原 BLOCK、权威上限与退出码保持原样 |
| 模型截断 / 非 JSON / provider 不可用 | 独立失败状态、明确错误；stdout 原 JSON 仍可解析，原退出码不变 |
| 路径越界 / 输出别名 / 超大或二进制材料 | 明确拒绝，不越权读取，不覆盖原始文件 |
| 来源改变或无法读取 | 展示变化或未复核，不把旧解释当当前验证 |
| HTML/脚本及输入指令注入 | 页面不执行内容；生成不改变契约、原裁决或用户确认 |
| 导出排除原话/原文 | 指定原话、笔记、其私人引文与相关个人修正记录移除；省略原文不被宣传为自动脱敏；无自动网络发送 |
| 完整与省略版 JSON 再导入 | 两种导出均可重新读取；省略来源显示无法核对，不冒充已校验 |
| Markdown 与同次 JSON 内容一致 | 用户确认/撤销、认识状态和范围不丢失；首版只导入 JSON，不承诺导入 Markdown |

自动测试使用 fixture/mock，不依赖付费 API。先运行新增模块测试及直接相关回归，再运行：

```powershell
python -m pytest tests/test_understanding.py tests/test_falsify_core.py tests/test_brooks_lint_receipt.py tests/test_authority_kernel.py tests/test_authority_antirot.py tests/test_web.py tests/test_flow_production_routes.py tests/test_flow_frontend_security.py tests/test_flow_localization.py
```

执行前核对实际测试文件；新增阅读页还要做浏览器行为验收，不能仅凭静态字符串测试声称交互通过。发现已有失败时记录基线和本改动关系，不顺手扩大改动去修整个仓库。

## 8. 最终交付与完成条件

最终交接包必须包含代码与 schema、JSON/MD 样例、阅读页、使用说明、验收命令及结果、截图、冻结对象 hash、非作者审计记录和限制。

完成条件：CLI 能从本次输入生成诚实的关联理解；本地页能阅读、核对来源、记录用户表达并导出；原裁决行为回归通过；独立审计针对最终字节完成。

效果主张仍需用户试用。技术交付后，可邀请 Chris 用自己的话解释一条机制、推演一个条件变化、指出一个未知。只记录实际表现和反馈，不把技术测试通过写成“用户已经理解项目”。

## 9. 可以直接给执行 agent 的任务

请作为集成负责人执行本计划，先完成 P0，再按写集分配产物实现、阅读页实现和最终非作者审计。保持当前裁决与授权流程，从真实 CLI review 入口增加可选理解产物，完成本机阅读、来源核对、用户表达和导出。按验收场景实测并修复，交付可复现终包；不要停在概念稿、静态页面或仅作者自测。本文范围只授权本机实现与测试；部署、共享控制面写入和对外发送不属于本计划。
