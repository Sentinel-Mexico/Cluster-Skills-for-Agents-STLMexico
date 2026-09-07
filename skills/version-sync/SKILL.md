---
name: version-sync
description: "Universal repository version synchronizer. Recursively discovers and updates all occurrences of the application version across frontend UI components, configuration manifests, source constants, and documentation prior to git push."
license: Apache-2.0
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# Universal Version Synchronizer (`version-sync`)

Canonical operational contract for discovering, tracking, and propagating semantic versions across multi-tier repositories without LLM context token consumption.

---

## Execution Flow

```
[SemVer Bump Applied via semver-governor]
                    │
                    ▼
[Step 1: Universal Discovery & Tracking]
python3 scripts/sync_version.py --discover
                    │
                    ▼
[Step 2: Atomic Cross-Tier Propagation]
python3 scripts/sync_version.py --sync
                    │
                    ▼
[Ready for Final Push: Trigger git-push-governor]
```

---

### Step 1: Universal Discovery (`--discover`)

Scans all project text files (supporting `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.php`, `.ts`, `.js`, `.py`, `.json`, `.md`, `.toml`, `.yaml`, etc.) to locate version declarations, constants, UI footer labels, and documentation badges:

```bash
python3 scripts/sync_version.py --discover
```

Expected JSON Output:
```json
{
  "status": "ok",
  "ground_truth_version": "1.2.0",
  "manifest_path": ".../assets/version-manifest.json",
  "discovered_count": 4,
  "tracked_files": [
    "README.md",
    "package.json",
    "src/components/Footer.tsx",
    "version.txt"
  ]
}
```

The discovery step persists tracked file locations inside `assets/version-manifest.json` for deterministic tracking.

---

### Step 2: Atomic Propagation (`--sync`)

Propagates the canonical active version across all tracked occurrences while preserving surrounding markup, indentation, and tags:

```bash
python3 scripts/sync_version.py --sync
```

Or pass an explicit version override if desired:

```bash
python3 scripts/sync_version.py --sync --new-version "1.3.0"
```

Expected JSON Output:
```json
{
  "status": "synced",
  "target_version": "1.3.0",
  "files_updated": 4,
  "updated_paths": [
    "README.md",
    "package.json",
    "src/components/Footer.tsx",
    "version.txt"
  ]
}
```

---

## Integration with Repository Governance

* **Pre-Push Invariant:** Always execute `version-sync` immediately after a `semver-governor` bump and **prior** to activating `git-push-governor`.
* **Zero Token Ingestion:** Never ask the LLM to inspect whole files or substitute strings manually; all pattern matching is offloaded to `scripts/sync_version.py`.
* **Deep Reference:** For supported regex patterns and category examples, consult `references/REFERENCE.md`.
