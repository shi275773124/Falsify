# 02. Setup

[中文](./02-setup.zh-CN.md) · [Back to README](../README.md)

End-to-end deployment from zero. Total time ~30 min if SSH keys already exist, ~45 if not.

## Prerequisites

- Two hosts where your agents run (VPS, container, local — anywhere with shell + git)
- One laptop or desktop with Obsidian installed
- A GitHub account
- SSH key authentication to GitHub (recommended over HTTPS tokens)

## Step 1 — Create the GitHub repo

1. Go to https://github.com/new
2. **Repository name**: anything, e.g. `agent-vault`
3. **Visibility**: Private (your notes shouldn't be public — even if this repo template is)
4. Don't initialize with README. We'll push from local.

Note the SSH URL: `git@github.com:you/agent-vault.git`

## Step 2 — Bootstrap on Agent A's host

```bash
# On Agent A's machine
mkdir -p ~/agent-vault
cd ~/agent-vault
git init -b main

# Copy templates from this repo
curl -fsSL https://raw.githubusercontent.com/shi275773124/Falsify/main/templates/AGENTS.md \
    -o AGENTS.md
curl -fsSL https://raw.githubusercontent.com/shi275773124/Falsify/main/templates/.gitignore \
    -o .gitignore

# Create the standard folder layout (optional but recommended)
mkdir -p "current-truth" "methodology" "system-map" "runbooks" "incidents" "change-log" "research"
echo "# 🏠 Ops Knowledge Base" > "🏠 ops-knowledge-base.md"
echo "Index page. Both agents read this first." >> "🏠 ops-knowledge-base.md"

# Set the agent's git identity — distinct from the other agent
git config user.name  "Agent A"
git config user.email "agent-a@yourdomain.local"

# First commit + push
git add .
git commit -m "init: dual-agent vault skeleton"
git remote add origin git@github.com:you/agent-vault.git
git push -u origin main
```

**Verify**: open the repo on GitHub. You should see `AGENTS.md`, `.gitignore`, and the empty folders.

## Step 3 — Clone on Agent B's host

```bash
# On Agent B's machine
git clone git@github.com:you/agent-vault.git ~/agent-vault
cd ~/agent-vault

# Set Agent B's git identity — different name + email from Agent A
git config user.name  "Agent B"
git config user.email "agent-b@yourdomain.local"

# Smoke test: make a tiny commit and push
echo "" >> README.md
git add README.md
git commit -m "[AGENT-B] connectivity test"
git push
```

Switch back to Agent A's host and run `git pull`. You should see Agent B's commit, attributed correctly.

## Step 4 — Clone on your laptop

```bash
# macOS / Linux
git clone git@github.com:you/agent-vault.git "$HOME/Documents/Obsidian Vault"

# Windows (Git Bash or PowerShell with Git installed)
git clone git@github.com:you/agent-vault.git "$HOME/Documents/Obsidian Vault"

# Set your own identity (not "Agent A" or "Agent B")
cd "$HOME/Documents/Obsidian Vault"
git config user.name  "Your Name"
git config user.email "you@yourdomain.com"
```

## Step 5 — Open in Obsidian + install Git plugin

1. Open Obsidian → **Open folder as vault** → select `Documents/Obsidian Vault`
2. Settings → **Community plugins** → **Turn on community plugins**
3. **Browse** → search **Obsidian Git** (by Vinzent) → Install → Enable
4. Settings → Obsidian Git:
    - **Vault backup interval (minutes)**: `10` (auto push)
    - **Auto pull interval (minutes)**: `5`
    - **Pull updates on startup**: `on`
    - **Disable push**: `off`
    - **Sync method**: `merge` (simplest; `rebase` if you prefer linear history)
    - **Commit message**: `vault backup: {{date}}` or your preferred template

5. Test: make a small edit in Obsidian, wait 10 min (or click the sync icon in left ribbon), check GitHub.

See `templates/obsidian-git-settings.md` for the exact config snippet.

## Step 6 — Tell each agent the rules

Both agents need to read `AGENTS.md` at the start of every session. How depends on the agent:

- **Hermes Agent**: drop `AGENTS.md` in the directory the agent reads at startup (typically `~/.hermes/profiles/<profile>/`)
- **Claude Code**: `CLAUDE.md` in repo root works (Claude Code auto-loads)
- **Cursor**: `.cursorrules` file in repo root
- **Custom agent**: include `AGENTS.md` content in the system prompt

**Critical**: each agent must be told **its own identity** (`AGENT-A` or `AGENT-B`) and the other agent's identity. Otherwise they won't tag correctly.

## Step 7 — Smoke test the loop

1. Have Agent A create `research/test-topic.md` with a `[AGENT-A]` paragraph and push.
2. Have Agent B pull, add a `[AGENT-B audit]:` inline note, push.
3. Wait 5 min, check Obsidian on your laptop — you should see both contributions, properly tagged.
4. Edit a typo on your laptop, wait 10 min, check the GitHub repo — your edit should be there.

If all four work, you're live.

## Common setup mistakes

- **Both agents using same `user.email`** → git can't tell them apart in `git log`. Fix: set distinct emails.
- **Forgetting `git pull` before agent's session starts** → diverging branches, merge headaches. Fix: agent prompt should always `git pull` first thing.
- **Obsidian Git plugin set to push too aggressively** (e.g. 1 min) → spam commits. 10 min is plenty.
- **Pushing private vault to public repo** → leak risk. Double-check **Private** at repo creation.

## Next

- [Collaboration rules](./03-collaboration.md) — what the agents actually do once it's running
- [Troubleshooting](./04-troubleshooting.md) — when things break
