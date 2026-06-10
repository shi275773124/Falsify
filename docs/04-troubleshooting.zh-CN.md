# 04. 故障排查

[English](./04-troubleshooting.md) · [返回 README](../README.zh-CN.md)

## Git merge 冲突

**症状**：`git pull` 报 "Merge conflict in `<file>`"。

**原因**：两个 agent（或一个 agent + 你笔记本）在同步前都改了同一文件。

**修复**：

```bash
cd ~/agent-vault
git status                 # 看冲突文件
# 打开文件，找 <<<<<<< HEAD 和 >>>>>>> 标记
# 手动解：保留双方标签块，删冲突标记
git add <file>
git commit -m "resolve: merge AGENT-A + AGENT-B edits in <file>"
git push
```

如果是结构性冲突（不只是各加一段，而是真的矛盾），按 [规则 3 冲突协议](./03-collaboration.zh-CN.md#规则-3--冲突走一手-docs)：抓一手源，贴裁决，标作者。

## Obsidian Git 插件 "auth failed" 或转圈

**症状**：插件红字报错，sync 图标不动。

**原因 + 修复**：

1. **SSH key 没进 Git 环境**（Windows 最常见）
    - 改用 HTTPS + Personal Access Token：`git remote set-url origin https://YOUR-PAT@github.com/you/agent-vault.git`
    - 或配 GIT_SSH 指向你的 key 路径
2. **PAT 过期**
    - 去 https://github.com/settings/tokens 重发，改 remote URL
3. **Repo 太大**（vault 罕见）
    - `.gitignore` 加 `.obsidian/workspace*.json` 等热加载产物

## Agent 主机进入 "Detached HEAD"

**症状**：`git status` 显示 `HEAD detached at <sha>`。

**原因**：agent 跑了 `git checkout <sha>` 而不是 `git checkout main`。

**修复**：

```bash
git checkout main
git pull
```

如果在 detached 状态下做了 commit，找回它们：

```bash
git log --reflog | head -20         # 找 detached commit
git checkout main
git cherry-pick <sha>                # cherry-pick 到 main
```

## 同一文件被两个 agent 在同一分钟内反复重写

**症状**：commit 来回打架，互相覆盖。

**原因**：agent 写之前没 pull，或写区规则被忽视。

**修复**：在 AGENTS.md 强制：

```
每次会话开始：
1. cd ~/agent-vault
2. git pull --rebase
3. 读 🏠 运维知识库.md 再动笔
4. 每次写完：git add <file> && git commit -m "[AGENT-X] <主题>" && git push
```

如果两个 agent 必须在同一会话写同一文件，按时间线协调：A 写完推，B 拉了再开始。

## 作者标签被抹

**症状**：段落没有 `[AGENT-A]` / `[AGENT-B]` 前缀。

**原因**：某 agent 改段落时忘了保留标签，或你（人类）在笔记本上手改了。

**修复**：每次 agent 会话开始跑标签审计：

```bash
# 在 vault 目录
grep -rL "AGENT-A\|AGENT-B\|BOTH" --include="*.md" . | head
```

输出里的文件至少有一段无标签。打开，找段落，用 `git blame` 反查作者：

```bash
git blame <file> | head -50
```

## 插件自动 pull 抢人类编辑

**症状**：你刚在 Obsidian 开始打字，插件 pull 把你的改动盖了。

**修复**：Obsidian Git 插件不应该丢本地改动——但万一：

1. 设置 → Obsidian Git → **Pull updates on startup**：开
2. 设置 → Obsidian Git → **Auto pull interval**：`5` 分钟（给你足够时间在两次 pull 间 commit）
3. 永远 **先 commit 再编辑**：长写之前手动点 sync 图标先同步

## 笔记本重装系统后 "Repository not found"

**症状**：新装好的笔记本 clone 不了——SSH 报 "permission denied"。

**原因**：旧 SSH key 没了，GitHub 不认新机。

**修复**：

```bash
ssh-keygen -t ed25519 -C "you@laptop"
cat ~/.ssh/id_ed25519.pub
# 粘到 GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com   # 应该返回 "Hi <you>"
```

## CI 闸门边界 / 可绕过模型

Falsify 是 fail-closed 的 reviewer 闸门，不是数学证明系统。已知边界：

- **草稿 prompt injection**：CLI 会把草稿包进明确的 `<<<FALSIFY_DRAFT ...>>>` 分隔符，并告诉 reviewer：草稿里的指令或 `VERDICT:` 行都是被审内容，不是命令。CLI 也只解析 reviewer 输出里的**最后一个** `VERDICT:`。这能挡住“草稿开头写 `VERDICT: PROCEED` 直接骗过 CI”的廉价绕过。
- **reviewer 被污染或同谋**：如果 reviewer 模型无视 system prompt，或作者/审稿人其实是同一个模型/同一个 provider，独立性就没了。高风险任务要用真正不同的 reviewer。
- **reviewer 输出被截断**：如果模型响应在最终 verdict 前被截断，CLI 默认 `HOLD`。方向安全，但可能噪声大；缩短草稿或提高输出预算。
- **`lint` 只是协作约定检查**：它抓未标作者的 prose 和 open blocker，不是反作弊系统；Markdown 格式技巧可能绕过 tag heuristic。

## 真坏到救不回时

如果以上都不行，pattern 还有逃生口：

**关插件自动同步，纯手动 git。** Obsidian 打开、改、存。终端手动 `git pull && git add . && git commit && git push`。失去 5 分钟自动，但故障模式消失。

如果两个 agent 历史已经分叉到不可调和，核选项：

```bash
# 选你信任的那个 agent——假设是 A
cd ~/agent-vault
git fetch origin
git reset --hard origin/main      # A 赢
git push --force-with-lease       # 确认无误再用
```

这会销毁 Agent B 没 commit 的改动，慎用。`--force-with-lease` 比 `--force` 安全，远端被别人推过会拒绝。

## 下一步

- [返回 README](../README.zh-CN.md)
- [架构深度](./01-architecture.zh-CN.md)
