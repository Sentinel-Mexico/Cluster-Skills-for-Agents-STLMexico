---
name: version-sync
description: "Universal repository version synchronizer. Recursively scans and updates all occurrences of the application version across plaintext version files (version.txt), frontend UI components, configuration manifests, code constants, and documentation prior to git push."
license: Apache-2.0
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.1.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# Universal Version Synchronizer (`version-sync`)

Canonical operational contract for recursively discovering, tracking, and propagating the application version across plaintext version files, visual frontend components, source code constants, configuration manifests, and documentation without LLM context token consumption.

---

## Execution Flow & Lifecycle Gate

> [!IMPORTANT]
> Universal version synchronization is **mandatory prior to executing any commit or push cycle** coordinated by `git-push-governor`.
> - **Sequence Invariant:** Run `semver-governor` (calculate bump) ➔ `version-sync` (propagate across all files) ➔ `git-push-governor` (commit & push).

```
[SemVer Bump Applied via semver-governor]
                    │
                    ▼
[Step 1: Universal Discovery & Indexing]
python3 scripts/sync_version.py --discover
                    │
                    ▼
[Step 2: Atomic Cross-Tier Propagation]
python3 scripts/sync_version.py --sync
                    │
                    ▼
[Release Coordination: Trigger git-push-governor]
```

---

### Step 1: Universal Discovery (`--discover`)

Recursively scans all project files without static extension constraints (supporting `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.php`, `.ts`, `.js`, `.py`, `.go`, `.rs`, `.json`, `.md`, `.toml`, `.yaml`, `.xml`, `.ini`, `.env.example`, etc.):

```bash
python3 scripts/sync_version.py --discover
```

#### Safe Filtering & Discovery Rules:
* **Binary & Size Guards:** Automatically skips non-text binary files (null-byte detection in first 1024 bytes) and files exceeding 2 MB.
* **Ignored Boundaries:** Strictly ignores `node_modules/`, `.git/`, `dist/`, `build/`, `coverage/`, `.next/`, `.turbo/`, `__pycache__/`, `.agent/`, `.agents/`.
* **Persistent Manifest:** Registers discovered file paths in `assets/version-manifest.json`.

Expected JSON Output:
```json
{
  "status": "discovered",
  "count": 6,
  "files": [
    ".env.example",
    "README.md",
    "VERSION",
    "package.json",
    "src/views/Home.vue",
    "version.txt"
  ]
}
```

---

### Step 2: Atomic Propagation (`--sync`)

Propagates the canonical active version across all tracked occurrences while preserving surrounding markup, indentation, and tags:

```bash
python3 scripts/sync_version.py --sync
```

Or propagate an explicit target version override:

```bash
python3 scripts/sync_version.py --sync --new-version "1.3.0"
```

Expected JSON Output:
```json
{
  "status": "synced",
  "target_version": "1.3.0",
  "files_updated": 6,
  "updated_paths": [
    ".env.example",
    "README.md",
    "VERSION",
    "package.json",
    "src/views/Home.vue",
    "version.txt"
  ]
}
```

---

## Token Economy Guardrails

1. **Zero LLM Prompt Rewrites:** Never request the model to manually edit or rewrite files just to update version strings. All substitution is handled deterministically by `scripts/sync_version.py`.
2. **Contextual Preservation:** Plaintext files (`version.txt`, `VERSION`) are replaced cleanly while UI elements and code constants preserve surrounding syntax.
3. **Deep Reference:** For supported regex patterns and category examples, consult `references/REFERENCE.md`.
