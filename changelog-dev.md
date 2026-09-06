# Changelog (Development)

All notable changes to this project during active development are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
