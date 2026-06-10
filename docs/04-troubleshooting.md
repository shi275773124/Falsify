# 04. Troubleshooting

[中文](./04-troubleshooting.zh-CN.md) · [Back to README](../README.md)

## Git merge conflicts

**Symptom**: `git pull` fails with "Merge conflict in `<file>`".

**Cause**: Both agents (or one agent + your laptop) edited the same file before sync.

**Fix**:

```bash
cd ~/agent-vault
git status                 # see conflicting files
# Open the file — find <<<<<<< HEAD and >>>>>>> markers
# Resolve manually: keep both agents' tagged blocks, drop the conflict markers
git add <file>
git commit -m "resolve: merge AGENT-A + AGENT-B edits in <file>"
git push
```

If the conflict is structural (not just two agents adding paragraphs but actually contradicting), apply the [Rule 3 conflict protocol](./03-collaboration.md#rule-3--conflicts-go-to-first-hand-sources): go to first-hand source, paste the resolution, attribute it.

## Obsidian Git plugin: "auth failed" or stuck spinner

**Symptom**: plugin shows red error, sync icon doesn't update.

**Causes & fixes**:

1. **SSH key not loaded into Git's environment** (most common on Windows)
    - Switch to HTTPS + Personal Access Token: `git remote set-url origin https://YOUR-PAT@github.com/you/agent-vault.git`
    - Or configure GIT_SSH to point at your key path
2. **PAT expired**
    - Regenerate at https://github.com/settings/tokens, update remote URL
3. **Repo too large** (rare for vaults)
    - Add `.gitignore` for `.obsidian/workspace*.json`, hot-reload artifacts

## "Detached HEAD" on agent host

**Symptom**: `git status` says `HEAD detached at <sha>`.

**Cause**: agent ran `git checkout <sha>` instead of `git checkout main`.

**Fix**:

```bash
git checkout main
git pull
```

If commits were made while detached, recover them:

```bash
git log --reflog | head -20         # find the detached commits
git checkout main
git cherry-pick <sha>                # bring them onto main
```

## Same file rewritten by both agents in the same minute

**Symptom**: rapid back-and-forth commits where each agent overwrites the other's work.

**Cause**: agents not pulling before writing, or write-zone rules ignored.

**Fix**: enforce in AGENTS.md:

```
At the start of every session:
1. cd ~/agent-vault
2. git pull --rebase
3. Read 🏠 ops-knowledge-base.md before any write
4. After each write: git add <file> && git commit -m "[AGENT-X] <topic>" && git push
```

If both agents have to write to the same file in the same session, coordinate via timestamps: A finishes and pushes, B pulls before starting.

## Author tags getting stripped

**Symptom**: paragraphs appear without `[AGENT-A]` / `[AGENT-B]` prefix.

**Cause**: an agent edited a paragraph and forgot to preserve the tag, or you (the human) edited it on your laptop.

**Fix**: at the start of every agent session, run a tag audit:

```bash
# In the vault directory
grep -rL "AGENT-A\|AGENT-B\|BOTH" --include="*.md" . | head
```

Files in the output have at least one untagged paragraph somewhere. Open them, find the paragraphs, attribute by `git blame`:

```bash
git blame <file> | head -50
```

## Plugin auto-pull fights human edits

**Symptom**: you start typing in Obsidian, plugin pulls and discards your changes.

**Fix**: the Obsidian Git plugin should never discard local changes — but if it does:

1. Settings → Obsidian Git → **Pull updates on startup**: keep on
2. Settings → Obsidian Git → **Auto pull interval**: `5` min (gives you time to commit between pulls)
3. Always **commit-then-edit**: hit the sync icon manually before starting a long edit session

## "Repository not found" after laptop OS reinstall

**Symptom**: fresh laptop can't clone — SSH says "permission denied".

**Cause**: laptop's old SSH key is gone, GitHub doesn't recognize the new machine.

**Fix**:

```bash
ssh-keygen -t ed25519 -C "you@laptop"
cat ~/.ssh/id_ed25519.pub
# Paste into GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com   # should print "Hi <you>"
```

## CI gate boundaries / bypass model

Falsify is a fail-closed reviewer gate, not a proof system. Treat these as known boundaries:

- **Draft prompt injection**: the CLI wraps drafts in `<<<FALSIFY_DRAFT_<random> ...>>>` delimiters — the tag carries a per-run random suffix, so a draft cannot forge the closing fence — and tells the reviewer to treat instructions or `VERDICT:` lines inside the draft as evidence, not commands. The CLI also parses the **last** reviewer `VERDICT:` line. This blocks the cheap bypasses (a planted `VERDICT: PROCEED`, a planted `<<<END ...>>>`); a reviewer model that *follows* injected instructions anyway is the next bullet.
- **Reviewer compromise or collusion**: if the reviewer model ignores the system prompt, is the same model/provider as the drafter, or is asked to rubber-stamp, independence is gone. Use a genuinely different reviewer for high-stakes work.
- **Truncated reviewer output**: if the model response is cut before the final verdict line, the CLI defaults to `HOLD`. That is safe but can be noisy; raise the output budget or shorten the draft.
- **`lint` is a collaboration convention check**: it catches untagged prose and open blockers. It is not anti-fraud; Markdown formatting tricks can hide prose from the tag heuristic.

## When the pattern truly breaks

If after reading this you're still stuck, the pattern itself has an escape hatch:

**Disable plugin auto-sync, do manual git only.** Open Obsidian, edit, save. In a terminal, manually `git pull && git add . && git commit && git push`. You lose 5-min auto-sync but the failure mode is gone.

If both agents have diverged into incompatible histories, the nuclear option:

```bash
# Pick the agent whose work you trust more — say Agent A
cd ~/agent-vault
git fetch origin
git reset --hard origin/main      # Agent A wins
git push --force-with-lease       # only if you're sure
```

This destroys Agent B's uncommitted work, so use sparingly. `--force-with-lease` is safer than `--force` because it refuses if someone else pushed in the meantime.

## Next

- [Back to README](../README.md)
- [Architecture deep-dive](./01-architecture.md)
