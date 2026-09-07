# Sentinel Mexico · Skills Directory

This directory contains the production agent skills catalog. Each skill resides in its own isolated subdirectory conforming to the [agentskills.io](https://agentskills.io/specification) open standard.

## Canonical Skills Directory

| Skill | Category | Version | Description |
| :--- | :--- | :--- | :--- |
| [`project-init`](project-init/SKILL.md) | Scaffolding | `1.1.0` | Deterministic monorepo/polyrepo generator with Existing Project Guard and dev branch resolution. |
| [`semver-governor`](semver-governor/SKILL.md) | Governance | `1.0.0` | Atomic SemVer manager with `--diff-stat` analysis and production milestone enforcement ($\ge 1.0.0$). |
| [`git-push-governor`](git-push-governor/SKILL.md) | Release | `1.1.0` | Interactive push coordinator and dual changelog synchronizer (`dev` vs. `main`). |
| [`i18n-governor`](i18n-governor/SKILL.md) | Localization | `1.0.0` | Multi-domain translation crawler, 100% key parity auditor, and token-diff patch injector. |
| [`version-sync`](version-sync/SKILL.md) | Automation | `1.1.0` | Universal version synchronizer scanning plaintext files, UI components, manifests, and documentation badges. |
| [`readme-generator`](readme-generator/SKILL.md) | Documentation | `1.1.0` | Institutional README generator with 5-change cadence, Shields.io badges, and sanitized directory tree. |
| [`sec-optimizer`](sec-optimizer/SKILL.md) | Security & Performance | `1.0.0` | Static code vulnerability auditor (CWE/OWASP) and runtime optimizer with Aesthetic Protection Invariant. |
| [`test-qa-runner`](test-qa-runner/SKILL.md) | Quality Assurance | `1.0.0` | Automated test runner and Pre-Commit Quality Gate with multi-ecosystem auto-detection and token-efficient triage. |

---

## Directory Structure

```text
skills/<skill-name>/
├── SKILL.md                 # Canonical instructions & YAML frontmatter (<500 lines)
├── scripts/                 # Deterministic executable scripts (Code-as-Skill)
├── references/              # Progressive disclosure reference manuals
└── assets/                  # Static templates, schemas, and media
```

To create a new skill, copy `templates/skill-template/`:
```bash
cp -r templates/skill-template skills/<my-skill-name>
```
