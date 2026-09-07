# Changelog (Development)

All notable changes to this project during active development are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-09-06

### Refactoring
- Enhanced `version-sync` deterministic engine (`sync_version.py`) with universal non-restricted file crawling.
- Added strict defensive guards against binary files (null byte scan in first 1024 bytes) and oversized files (>2 MB).
- Expanded contextual regex to support plaintext version files (`version.txt`, `VERSION`, `.version`), environment templates (`.env.example`), case-insensitive constants across all major programming languages, XML manifests (`pom.xml`), and multi-framework UI templates (React, Vue, Svelte, Astro).
- Updated `skills/version-sync/SKILL.md` (v1.1.0) and technical reference documentation in `skills/version-sync/references/REFERENCE.md`.

## [0.6.0] - 2026-09-06

### Features
- Added canonical skill `version-sync` compliant with `agentskills.io` standard.
- Implemented deterministic universal version synchronization engine `skills/version-sync/scripts/sync_version.py` with multi-tier discovery (`--discover`) and atomic propagation (`--sync`).
- Supported pattern detection across frontend UI components, configuration manifests (JSON/TOML/YAML), source code variables, and markdown badges.
- Created persistent tracking manifest `skills/version-sync/assets/version-manifest.json`.
- Authored canonical operational contract `skills/version-sync/SKILL.md` (<110 lines) and technical reference manual `skills/version-sync/references/REFERENCE.md`.

## [0.5.0] - 2026-09-06

### Features
- Added canonical skill `i18n-governor` compliant with `agentskills.io` standard.
- Implemented deterministic i18n management engine `skills/i18n-governor/scripts/i18n_manager.py` with multi-domain recursive discovery, 100% key parity auditing (`--audit`), differential extraction (`--get-diff`), and hierarchical patch injection (`--apply-patch`).
- Enforced Domain Context Lock architecture isolating translation domains across monorepo subsystems (`frontend::locale`, `backend::locale`, etc.).
- Standardized Zero-Hardcoding Policy, strict ban on untranslated English fallbacks, and technical whitelist standards in `skills/i18n-governor/SKILL.md` (<135 lines).
- Authored reference manual in `skills/i18n-governor/references/REFERENCE.md` detailing crawler boundaries and whitelist specifications.

## [0.4.0] - 2026-09-06

### Features
- Added canonical skill `git-push-governor` compliant with `agentskills.io` standard.
- Implemented deterministic push discovery and changelog injector `skills/git-push-governor/scripts/push_governor.py` with `--discover` and `--sync-changelog [dev|main|both]`.
- Enforced strict activation precondition gate in `skills/git-push-governor/SKILL.md` (<135 lines) executing exclusively at task completion.
- Formulated single-turn interactive branch query pattern with `[A] Todos` and `[N] Ninguno` options.
- Authored technical reference in `skills/git-push-governor/references/REFERENCE.md` detailing branch-to-changelog routing and anti-inflation policies.

## [0.3.0] - 2026-09-06

### Features
- Added canonical skill `semver-governor` compliant with `agentskills.io` standard.
- Implemented deterministic SemVer calculation engine `skills/semver-governor/scripts/semver_bump.py` with `--diff-stat`, strict regex checking, atomic `package.json` updates, and production milestone enforcement (>= 1.0.0).
- Created canonical skill instruction contract `skills/semver-governor/SKILL.md` (<110 lines).
- Authored technical reference in `skills/semver-governor/references/REFERENCE.md` detailing change classification matrices and production milestone rules.

## [0.2.0] - 2026-09-06

### Features
- Added canonical skill `project-init` compliant with `agentskills.io` standard.
- Implemented deterministic scaffolding engine `skills/project-init/scripts/scaffold.py` with Existing Project Guard and dev branch resolution.
- Integrated batch Grill-Me architecture interview in `skills/project-init/SKILL.md` (<130 lines).
- Enforced invariants per environment: localized dictionaries in `<env>/locale/` and media segregation in `<env>/src/img/` and `<env>/src/video/`.
- Created comprehensive architecture and technical rationale guide in `skills/project-init/references/REFERENCE.md`.

## [0.1.1] - 2026-09-06

### Documentation
- Updated README.md with complete specification citations, enhanced installation commands, and cleaned markdown formatting.

## [0.1.0] - 2026-09-06

### Features
- Initial repository setup as official Sentinel Mexico Agent Skills Catalog conforming to `agentskills.io`.
- Canonical skill template in `templates/skill-template/` with `SKILL.md`, `scripts/`, `references/`, and `assets/`.
- Multi-platform deterministic installer `scripts/install-skill.sh` supporting 30+ AI runtimes, symlink/copy modes, and universal deduplication.
- Local validation engine `scripts/validate-skills.sh` enforcing <500 lines limit, kebab-case naming, and metadata attribution.
- GitHub Actions CI workflows for SKILL.md schema validation and Gitleaks security scanning.
- Complete documentation in `README.md` with full provider matrix, technical standards, and governance policies.
