# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2026-09-07

### Features
- Added canonical meta-skill `cluster-sync` (v1.0.0) compliant with `agentskills.io` standard for fleet-wide skill auditing and batch synchronization across 40+ AI runtime targets.
- Implemented deterministic fleet audit and sync engine `skills/cluster-sync/scripts/sync_all.py` supporting dry-run inspection (`--check`), structured JSON export (`--json`), and automated batch updates (`--sync-all`).
- Implemented deterministic Update Check Gate `scripts/check_update.py` in all catalog skills and templates with 24-hour local caching (`assets/.update_cache.json`), 2-second timeout, and zero-token silent fallback.
- Injected `Stage 0: Version Freshness Gate (Optional Update)` into all canonical `SKILL.md` contracts and templates.

### Licensing & Governance
- Executed global repository licensing migration to canonical MIT License across `LICENSE`, `package.json`, root `README.md`, and all `skills/*/SKILL.md` frontmatters while preserving institutional authorship (Sentinel Mexico).
- Added `skill-origin` metadata attribute to all skill frontmatters and canonical templates.
- Added repository `.gitignore` for update cache files and Python bytecode artifacts.
- Synchronized repository Version Parity Quartet to `0.10.0`.

## [0.9.0] - 2026-09-06

### Features
- Added canonical skill `project-init` (v1.1.0): Deterministic monorepo/polyrepo scaffolding engine with Existing Project Guard, dev branch resolution, and automated Grill-Me architecture interview.
- Added canonical skill `semver-governor` (v1.0.0): Atomic SemVer manager with `--diff-stat` analysis, strict regex validation, and production milestone enforcement ($\ge 1.0.0$).
- Added canonical skill `git-push-governor` (v1.1.0): Interactive Git push coordinator and dual changelog synchronizer (`dev` vs. `main`) with single-turn branch query pattern.
- Added canonical skill `i18n-governor` (v1.0.0): Recursive translation crawler, Domain Context Lock architecture, 100% key parity auditing, and token-diff patch injection.
- Added canonical skill `version-sync` (v1.1.0): Universal repository version synchronizer scanning plaintext files (`version.txt`, `VERSION`), UI components, manifests, and documentation badges with binary defense guards.
- Added canonical skill `readme-generator` (v1.1.0): Institutional README generator with 5-change cadence accumulation ($\Delta \ge 5$), Shields.io `style=for-the-badge` generator, and sanitized directory tree.
- Added canonical skill `sec-optimizer` (v1.0.0): Static code security auditor (CWE-798, CWE-78/94, CWE-89, CWE-79) and runtime optimizer with strict Aesthetic Protection Invariant and Plan-Validate-Execute Human-in-the-Loop gate.
- Added canonical skill `test-qa-runner` (v1.0.0): Automated test suite executor and Pre-Commit Quality Gate with multi-ecosystem auto-detection (Node.js/npm/pnpm/yarn/bun, Python pytest/unittest, Rust cargo, Go) and token-efficient failure triage.

### Refactoring & Improvements
- Enhanced `version-sync` deterministic engine with universal non-restricted file crawling and defensive guards against binary files (`\x00`) and files >2 MB.
- Updated `skills/README.md` catalog with full index of canonical production skills.
- Synchronized repository Version Parity Quartet to `0.9.0`.

## [0.1.1] - 2026-09-06

### Documentation
- Updated README.md with complete specification citations, enhanced installation commands, and cleaned markdown formatting.

## [0.1.0] - 2026-09-06

### Features
- Initial release of Sentinel Mexico Agent Skills Catalog compliant with `agentskills.io`.
- Canonical skill template in `templates/skill-template/`.
- Multi-platform deterministic installer `scripts/install-skill.sh` supporting 30+ AI platforms.
- Automated validation engine `scripts/validate-skills.sh` and GitHub Actions CI.
- Full documentation and provider routing matrix in `README.md`.
