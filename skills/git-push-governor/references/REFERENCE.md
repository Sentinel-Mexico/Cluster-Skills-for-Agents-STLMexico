# Technical Reference: Git Push Coordination & Dual Changelog Governance

This document establishes the operational policies governing interactive push targeting and changelog lifecycle synchronization under Sentinel Mexico engineering standards.

---

## 1. Branch vs. Changelog Synchronization Matrix

To preserve clear audit trails between active development work and production releases, updates are strictly mapped to corresponding changelog authorities:

| Target Option | Target Git Remote | Updated Changelog | Lifecycle Purpose | Access Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **`dev`** | `origin/dev` | `changelog-dev.md` | Active sprint iterations, internal refactoring, incremental features, and task deliverables. | Unrestricted for active agent sessions. |
| **`main`** | `origin/main` | `changelog.md` | Official production releases, stable releases, customer-facing delivery. | Requires explicit, unambiguous user confirmation. |
| **`both` / `all`**| `origin/dev` & `origin/main` | `changelog-dev.md` & `changelog.md` | Full release promotion consolidating unreleased iteration notes into production history. | Requires explicit user release instruction. |
| **`none`** | None | None | Working tree preserved locally for multi-session or offline verification. | Zero network transmission. |

---

## 2. Anti-Inflation Lifecycle Policies (Preventing Micro-Edit Sprawl)

### The Problem of Version Inflation
In autonomous agent workflows, triggering a commit, version bump, or remote push for every individual file edit creates severe operational drawbacks:
1. **Noisy Git History:** Dozens of low-value commits obscuring meaningful architectural changes.
2. **Artificial Version Drift:** Semantic versions incrementing rapidly over minor cosmetic tweaks.
3. **CI/CD Resource Saturation:** Redundant trigger storms across automated test and security pipelines.
4. **Token Burn:** Incurring unnecessary LLM context overhead analyzing intermediate, uncommitted states.

### Policy Rules Enforced by `git-push-governor`:
1. **Single-Push-Per-Prompt Rule:** Exactly one push cycle is permitted at the conclusion of a completed user request or task objective.
2. **Precondition Gating:** If `push_governor.py --discover` reveals zero uncommitted or unpushed changes, the cycle aborts silently without prompting.
3. **Coordinated Changelog Injection:** Changelog entries group all commits and summaries generated during the session into a single, cohesive release note rather than separate entries per file touch.
