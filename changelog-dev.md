# Changelog (Development)

All notable changes to this project during active development are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
