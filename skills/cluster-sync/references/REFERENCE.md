# Technical Reference · Cluster Sync Engine (`cluster-sync`)

## Architecture & Discovery Mechanics

`cluster-sync` is engineered to maintain version alignment across distributed agent installations without token expenditure or runtime dependencies.

### Provider Paths Matrix

The synchronization engine actively scans the following canonical provider directories:

| Provider Ecosystem | Project Scope Path | User Scope Path |
| :--- | :--- | :--- |
| **Universal / Standard** | `.agents/skills/` | `~/.config/agents/skills/` |
| **Antigravity** | `.agent/skills/` | `~/.gemini/antigravity/skills/` |
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` |
| **Cursor** | `.cursor/skills/` or `.agents/skills/` | `~/.cursor/skills/` |
| **GitHub Copilot / Codex**| `.agents/skills/` | `~/.codex/skills/` |
| **OpenHands / Roo / Cline**| `.agents/skills/` | `~/.agents/skills/` |

### Deterministic Update Rules

1. **Symlink Mode:** When skills are installed via symlinks to a local cluster clone, updates occur atomically via `git -C <cluster_root> pull`.
2. **Copy / Standalone Mode:** Independent skill directories are fetched and replaced using `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <name> --force`.
3. **Cache Policy:** Each skill's `check_update.py` enforces a 24-hour cache in `assets/.update_cache.json` unless overridden with `--force`.
