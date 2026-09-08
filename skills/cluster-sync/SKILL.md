---
name: cluster-sync
description: "Audits all installed Sentinel Mexico agent skills against the remote GitHub catalog. Identifies outdated skills and synchronizes them in batch. Use when maintaining or updating agent skills."
license: MIT
compatibility: Universal (Python 3.10+, Git CLI, npx)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/cluster-sync"
allowed-tools: Bash(git:*) Bash(python3:*) Bash(npx:*) Read Write
---

# Cluster Sync (`cluster-sync`)

Canonical operational contract for auditing installed Sentinel Mexico agent skills across workspaces and user environments against the remote GitHub catalog, triaging outdated skills, and executing batch synchronization.

---

## Overview

As agent skills evolve with performance optimizations, security hardening, and framework updates, agents must maintain parity with the canonical repository. `cluster-sync` provides automated discovery, non-invasive version auditing, and zero-token batch updates across more than 40 AI runtime environments.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `cluster-sync` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill cluster-sync --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## Execution Flow

```text
[Initiate Sync Audit]
         │
         ▼
[Stage 1: Fleet Discovery & Audit]
python3 scripts/sync_all.py --check
         │
         ├── All skills synchronized ──► [EXIT] (No action required)
         │
         └── Outdated Skills Detected
                   │
                   ▼
         [Stage 2: Version Parity Triage]
         Display comparison table to user
                   │
                   ▼
         [Stage 3: Interactive or Batch Synchronization]
         - [A] All skills ──► python3 scripts/sync_all.py --sync-all
         - [1..N] Single  ──► npx skills add ... --skill <name> --force
         - [Q] Cancel     ──► Abort operation
```

---

## Operational Stages

### Stage 1: Fleet Discovery & Audit (Zero-Context Ingestion)

Execute the deterministic audit engine without consuming LLM reasoning tokens:

```bash
python3 scripts/sync_all.py --check
```

For programmatic analysis, append `--json`:
```bash
python3 scripts/sync_all.py --check --json
```

The script inspects standard provider locations (`.agents/skills/`, `.agent/skills/`, `.claude/skills/`, etc.) and compares local `SKILL.md` version tags against the GitHub `main` branch.

### Stage 2: Audit Triage & Human-in-the-Loop Confirmation

If outdated skills are found, review the structured comparison table:
- Identify backward-compatible upgrades (PATCH/MINOR).
- Highlight major upgrades or deprecated arguments.
- Prompt the user for approval prior to network synchronization.

### Stage 3: Batch Synchronization

Synchronize outdated skills with zero manual editing:

1. **Automated Batch Execution:**
   ```bash
   python3 scripts/sync_all.py --sync-all
   ```

2. **Targeted Single-Skill Update:**
   ```bash
   npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <skill-name> --force
   ```

3. **Symlink Installations:**
   If the local skills are symlinked to a cloned catalog repository, pull the latest changes directly:
   ```bash
   git pull origin main
   ```

---

## Guardrails & Token Optimization

- **Line Count Ceiling:** `SKILL.md` body strictly complies with `<500` lines standard.
- **Cache Invariant:** 24-hour cache prevents excessive network requests and API rate-limiting.
- **Graceful Fallback:** If GitHub is unreachable or repository is private, returns unverified status without breaking agent workflows.
