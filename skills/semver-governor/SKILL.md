---
name: semver-governor
description: "Evaluates codebase modifications to calculate and bump semantic versioning (MAJOR.MINOR.PATCH) in package.json. Strictly enforces production post-1.0.0 SemVer rules for backward compatibility, features, and fixes. Use whenever completing a task, closing a pull request, or before creating a commit."
license: Apache-2.0
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# SemVer Governor (`semver-governor`)

Canonical operational contract for atomic, deterministic semantic versioning bumps in `package.json` under Sentinel Mexico engineering governance.

## Execution Flow

```
[Trigger semver-governor]
        │
        ▼
[Phase 1: Diff Inspection]
python3 scripts/semver_bump.py --diff-stat
        │
        ▼
[Phase 2: Impact Classification]
Map cumulative changes: PATCH vs MINOR vs MAJOR
        │
        ▼
[Phase 3: Deterministic Bump Execution]
python3 scripts/semver_bump.py --bump [patch|minor|major] --reason "<brief_reason>"
```

---

### Phase 1: Diff Inspection (Token-Efficient)

Execute the deterministic diff inspector to assess changed subsystems and impact metrics without loading full file contents into the LLM context:

```bash
python3 scripts/semver_bump.py --diff-stat
```

Expected JSON Output:
```json
{
  "status": "ok",
  "files_changed": 3,
  "insertions": 45,
  "deletions": 12,
  "files": [
    "src/controllers/auth.ts",
    "src/locales/en.json",
    "src/locales/es.json"
  ],
  "summary": "3 files changed, 45 insertions(+), 12 deletions(-)"
}
```

---

### Phase 2: Impact Classification

Classify the cumulative modification using the strict SemVer hierarchy. Determine the single highest level of change:

| Level | Classification Criteria | SemVer Effect |
| :--- | :--- | :--- |
| **PATCH** | Backward-compatible bug fixes, security patches, minor UI styling tweaks, internal refactoring, performance improvements, doc updates, or dependency maintenance. | `X.Y.Z` ➔ `X.Y.(Z+1)` |
| **MINOR** | Backward-compatible new functionality (new tools, endpoints, UI views, locale translations, or non-breaking API additions). Resets PATCH to 0. | `X.Y.Z` ➔ `X.(Y+1).0` |
| **MAJOR** | Breaking changes, incompatible API/schema redesigns, removed public endpoints, or architectural overhauls. Resets MINOR and PATCH to 0. | `X.Y.Z` ➔ `(X+1).0.0` |

#### Production Milestone Clause
If the project's current version is `< 1.0.0` (beta phase completed), any subsequent bump automatically establishes the production baseline at `>= 1.0.0`.

---

### Phase 3: Deterministic Bump Execution

Invoke `scripts/semver_bump.py` with the determined level and concise rationale:

```bash
python3 scripts/semver_bump.py --bump [patch|minor|major] --reason "<brief_explanation>"
```

The script atomically updates `package.json` preserving 2-space indentation and returns:

```json
{
  "status": "ok",
  "previous_version": "2.1.0",
  "new_version": "2.1.1",
  "level": "patch",
  "reason": "Fix token expiration edge case in auth controller"
}
```

---

## Guardrails & Constraints

1. **Token Preservation:** Never load entire file diffs into context when evaluating versions. Always utilize `python3 scripts/semver_bump.py --diff-stat`.
2. **Atomic Integrity:** Do not manually edit `package.json` strings or calculate digit arithmetic in prompt turns.
3. **Deep Rationale:** For complete impact matrices and milestone policies, consult `references/REFERENCE.md`.
