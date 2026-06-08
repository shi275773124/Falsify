# 02. 部署

[English](./02-setup.md) · [返回 README](../README.zh-CN.md)

零到运行的全流程。SSH key 已配好的话约 30 分钟，没配约 45。

## 前置

- 两台跑 agent 的机器（VPS / 容器 / 本地都行，能 shell + git 即可）
- 一台装了 Obsidian 的笔记本/台式机
- GitHub 账号
- GitHub SSH key 认证（推荐，比 HTTPS token 稳）

## Step 1 — 建 GitHub repo

1. 去 https://github.com/new
2. **Repository name**：随意，比如 `agent-vault`
3. **Visibility**：**Private**（你的笔记不该公开——即使这个模板 repo 是公开的）
4. 不要勾 README。本地推。

记下 SSH URL：`git@github.com:you/agent-vault.git`

## Step 2 — 在 Agent A 的机器上初始化

```bash
# 在 Agent A 的机器上
mkdir -p ~/agent-vault
cd ~/agent-vault
git init -b main

# 从本 repo 拉模板
curl -fsSL https://raw.githubusercontent.com/shi275773124/Falsify/main/templates/AGENTS.md \
    -o AGENTS.md
curl -fsSL https://raw.githubusercontent.com/shi275773124/Falsify/main/templates/.gitignore \
    -o .gitignore

# 推荐目录结构（可改）
mkdir -p "当前真相" "方法论" "系统地图" "操作手册" "事故记录" "变更记录" "研究"
echo "# 🏠 运维知识库" > "🏠 运维知识库.md"
echo "首页。两个 agent 上来都先读这里。" >> "🏠 运维知识库.md"

# 设 Agent A 的 git 身份——必须与 Agent B 不同
git config user.name  "Agent A"
git config user.email "agent-a@yourdomain.local"

# 首次 commit + push
git add .
git commit -m "init: dual-agent vault skeleton"
git remote add origin git@github.com:you/agent-vault.git
git push -u origin main
```

**验收**：在 GitHub 上打开 repo，应该能看到 `AGENTS.md`、`.gitignore` 和空目录。

## Step 3 — 在 Agent B 的机器上 clone

```bash
# 在 Agent B 的机器上
git clone git@github.com:you/agent-vault.git ~/agent-vault
cd ~/agent-vault

# 设 Agent B 的 git 身份——name + email 都要与 A 不同
git config user.name  "Agent B"
git config user.email "agent-b@yourdomain.local"

# 烟雾测试：小改一下推上去
echo "" >> README.md
git add README.md
git commit -m "[AGENT-B] connectivity test"
git push
```

切回 Agent A 跑 `git pull`，应该能看到 Agent B 的 commit，作者归属正确。

## Step 4 — 笔记本 clone

```bash
# macOS / Linux
git clone git@github.com:you/agent-vault.git "$HOME/Documents/Obsidian Vault"

# Windows（Git Bash 或 PowerShell + Git）
git clone git@github.com:you/agent-vault.git "$HOME/Documents/Obsidian Vault"

# 设你自己的身份（不要叫 Agent A/B）
cd "$HOME/Documents/Obsidian Vault"
git config user.name  "你的名字"
git config user.email "you@yourdomain.com"
```

## Step 5 — Obsidian 打开 + 装 Git 插件

1. Obsidian → **Open folder as vault** → 选 `Documents/Obsidian Vault`
2. 设置 → **Community plugins** → **打开社区插件**
3. **Browse** → 搜 **Obsidian Git**（作者 Vinzent）→ Install → Enable
4. 设置 → Obsidian Git：
    - **Vault backup interval (minutes)**：`10`（自动 push）
    - **Auto pull interval (minutes)**：`5`
    - **Pull updates on startup**：开
    - **Disable push**：关
    - **Sync method**：`merge`（最简单；想要线性历史用 `rebase`）
    - **Commit message**：`vault backup: {{date}}` 或你喜欢的模板

5. 测试：在 Obsidian 改一处小内容，等 10 分钟（或点左侧 ribbon 的 sync 图标），看 GitHub。

精确配置见 `templates/obsidian-git-settings.md`。

## Step 6 — 让每个 agent 知道规则

两个 agent 每次开会话都要读 `AGENTS.md`。怎么读看 agent：

- **Hermes Agent**：把 `AGENTS.md` 放进 agent 启动时读的目录（通常 `~/.hermes/profiles/<profile>/`）
- **Claude Code**：repo 根目录 `CLAUDE.md`（Claude Code 自动加载）
- **Cursor**：repo 根目录 `.cursorrules`
- **自研 agent**：把 `AGENTS.md` 内容塞进 system prompt

**关键**：每个 agent 必须知道**自己是谁**（`AGENT-A` 还是 `AGENT-B`）和对方是谁，否则标签会乱。

## Step 7 — 跑通闭环

1. Agent A 建 `research/test-topic.md`，写一段 `[AGENT-A]` 然后 push
2. Agent B pull，加一行 `[AGENT-B audit]:` 行内备注，push
3. 等 5 分钟，看笔记本 Obsidian——应该看到两人贡献，标签正确
4. 笔记本上改个错字，等 10 分钟，看 GitHub repo——你的改动应该在那

四步都成功就 live 了。

## 常见坑

- **两个 agent 用同一个 `user.email`** → `git log` 分不清谁是谁。修复：设不同 email
- **Agent 会话开始忘记 `git pull`** → 分支发散、merge 痛。修复：agent prompt 第一件事就是 `git pull`
- **Obsidian Git 插件 push 太勤**（比如 1 分钟）→ commit 刷屏。10 分钟够用
- **私有 vault 推到公开 repo** → 泄露风险。建 repo 时务必勾 Private

## 下一步

- [协作规范](./03-collaboration.zh-CN.md) — 跑起来后 agent 实际怎么做
- [故障排查](./04-troubleshooting.zh-CN.md) — 出问题怎么办
