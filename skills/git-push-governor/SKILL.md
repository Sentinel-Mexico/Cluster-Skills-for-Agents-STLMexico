---
name: git-push-governor
description: "Interactive Git push coordinator and changelog synchronizer. Discovers branches, prompts user for push destination (specific branch, all, or none) strictly at the end of a completed task/prompt cycle, and deterministically updates changelog.md and/or changelog-dev.md according to SemVer rules."
license: MIT
compatibility: Universal (Git CLI, Python 3.10+)
metadata:
  author: "Sentinel Mexico"
  version: "1.1.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/git-push-governor"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# Git Push Governor (`git-push-governor`)

Canonical operational contract for coordinating interactive Git pushes, branch targeting, and dual changelog synchronization under Sentinel Mexico engineering governance.

---

## Activation Precondition Gate (Critical Constraint)

> [!IMPORTANT]
> The agent **MUST** activate this skill **EXCLUSIVELY at the conclusion of a completed task or user prompt cycle**.
> - **Prohibited:** Never invoke during intermediate file edits, troubleshooting rounds, or internal multi-turn reasoning steps.
> - **Push Frequency Invariant:** Exactly one coordinated push cycle per completed requirement or user prompt. Incremental micro-pushes during work-in-progress are strictly prohibited.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `git-push-governor` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill git-push-governor --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## Execution Flow

```
[Completed Task Cycle]
          │
          ▼
[Phase 1: State Discovery]
python3 scripts/push_governor.py --discover
          │
          ├── has_uncommitted == false && unpushed_commits == 0 ──► [EXIT] (No action required)
          │
          └── Changes Detected
                    │
                    ▼
          [Phase 2: Single-Turn Branch Inquiry]
          Prompt user: [Branch choices] + [A] Todos + [N] Ninguno
                    │
                    ▼
          [Phase 3: Changelog Sync & Network Push]
          - dev     ──► sync-changelog dev  ──► git push origin dev
          - main    ──► sync-changelog main ──► git push origin main
          - todos   ──► sync-changelog both ──► git push origin dev && git push origin main
          - ninguno ──► Keep local, abort push
```

---

### Phase 1: State Discovery (Token-Efficient)

Execute the deterministic discovery routine to inspect working tree status and branch topology:

```bash
python3 scripts/push_governor.py --discover
```

Expected JSON Output:
```json
{
  "has_uncommitted": true,
  "unpushed_commits": 1,
  "current_branch": "dev",
  "branches": ["dev", "main"]
}
```

* **Early Exit Verdict:** If `has_uncommitted` is `false` and `unpushed_commits` is `0`, the repository is fully synchronized. Conclude the turn without interrupting the user.

---

### Phase 2: Single-Turn Interactive Branch Inquiry

If uncommitted changes or unpushed commits exist, formulate a single structured query presenting all discovered branches alongside bulk options:

```text
Se han detectado cambios listos para sincronización. Por favor selecciona el destino del push:

[1] dev (Rama de desarrollo activo) ➡️ Recomendado
[2] main (Rama de producción - release verificado)
[A] Todos (dev y main)
[N] Ninguno (Mantener cambios locales únicamente)
```

Wait for the user's explicit response before initiating any network transmission.

---

### Phase 3: Changelog Synchronization & Push Execution

Based on the user's destination choice:

#### 1. Target: `dev`
```bash
python3 scripts/push_governor.py --sync-changelog dev --reason "<summary_of_changes>"
git push origin dev
```
* Updates `changelog-dev.md` with current sprint deliverables.
* Preserves `changelog.md` intact.

#### 2. Target: `main`
```bash
python3 scripts/push_governor.py --sync-changelog main --reason "<summary_of_changes>"
git push origin main
```
* Updates `changelog.md` adhering to Keep a Changelog standards.

#### 3. Target: `todos` / `both`
```bash
python3 scripts/push_governor.py --sync-changelog both --reason "<summary_of_changes>"
git push origin dev && git push origin main
```
* Atomically synchronizes both `changelog-dev.md` and `changelog.md`.
* Pushes both branches to remote origin.

#### 4. Target: `ninguno`
* Aborts network push. Changes remain securely in the local working tree/branch.

---

## Guardrails & Token Economy

1. **Zero LLM Manual Editing:** Never attempt to parse or edit markdown changelogs manually via LLM prompt generation. Always delegate injection to `scripts/push_governor.py`.
2. **Deterministic Version Resolution:** Version numbers are extracted automatically from the Version Authority File (`package.json` / `version.txt`).
3. **Deep Rationale:** For comprehensive operational policies and branch mapping rules, consult `references/REFERENCE.md`.
