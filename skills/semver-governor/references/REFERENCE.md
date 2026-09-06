# Technical Reference: SemVer Governance & Production Milestones

This reference defines the impact classification rules and production milestone enforcement applied by `semver-governor` across Sentinel Mexico repositories.

---

## 1. Impact Decision Matrix

When analyzing the cumulative delta from `git diff --stat`, map modifications to the highest applicable SemVer tier:

| Change Category | Trigger Description | Target Level | Numerical Example |
| :--- | :--- | :---: | :---: |
| **Bug Fix** | Correcting erroneous runtime logic, handling null pointer exceptions, boundary checks. | **PATCH** | `2.1.0` ➔ `2.1.1` |
| **Security Patch** | Updating vulnerable dependencies, sanitizing inputs, addressing CVE alerts. | **PATCH** | `2.1.1` ➔ `2.1.2` |
| **Refactoring** | Code quality improvements, dead code removal, type annotations with no API delta. | **PATCH** | `2.1.2` ➔ `2.1.3` |
| **Performance** | Database indexing, caching layer addition, query optimization. | **PATCH** | `2.1.3` ➔ `2.1.4` |
| **Documentation** | Updating README, inline docstrings, API docs, changelogs. | **PATCH** | `2.1.4` ➔ `2.1.5` |
| **UI Tweaks** | CSS adjustments, spacing corrections, non-structural style updates. | **PATCH** | `2.1.5` ➔ `2.1.6` |
| **New Feature** | New REST/GraphQL endpoint, new interactive UI component, new CLI option. | **MINOR** | `2.1.6` ➔ `2.2.0` |
| **Localization** | Adding a new locale file (e.g. `fr.json`, `de.json`) or new i18n keys. | **MINOR** | `2.2.0` ➔ `2.3.0` |
| **Agent Skill Addition**| Integrating a new canonical agent skill into the catalog. | **MINOR** | `2.3.0` ➔ `2.4.0` |
| **Breaking Change** | Modifying existing endpoint request/response contracts, deleting public interfaces. | **MAJOR** | `2.4.0` ➔ `3.0.0` |
| **Schema Redesign** | Database migration requiring table drop or non-backward-compatible column renames. | **MAJOR** | `3.0.0` ➔ `4.0.0` |
| **Architecture Revamp**| Complete rewrite of underlying framework or protocol change (e.g. REST to gRPC). | **MAJOR** | `4.0.0` ➔ `5.0.0` |

---

## 2. Sentinel Mexico Post-1.0.0 Production Milestone Policy

### Rationale
In enterprise operations, versions `< 1.0.0` signal preliminary, unstable, or exploratory prototyping phases (zero-major SemVer caveats). Once an enterprise service or skill catalog transitions into active use or shared pipelines:

1. **Zero-Major Deprecation:** Protracted `0.x.y` iteration creates ambiguity around breaking changes, as `0.x` allows arbitrary breaking shifts under classical SemVer specs.
2. **Production Baseline (`>= 1.0.0`):** Sentinel Mexico policy mandates that as soon as a project passes its initial release validation, all subsequent bumps must transition to `>= 1.0.0`.
3. **Automated Promotion:**
   - Any bump requested on a repository with current version `< 1.0.0` (e.g., `0.1.0`, `0.8.2`) will automatically promote the version to `1.0.0`.
   - Subsequent changes then adhere strictly to standard post-1.0.0 SemVer rules (`1.0.1`, `1.1.0`, `2.0.0`).
