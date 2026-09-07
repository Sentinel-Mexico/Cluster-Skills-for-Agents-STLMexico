# README Generator Technical Reference (`readme-generator`)

Standard: `agentskills.io`  
Author: Sentinel Mexico  
Governance: `Cluster-Skills-for-Agents-STLMexico`  

---

## 1. Architectural Role & Separation of Concerns

The `readme-generator` skill automates the production, structural validation, and periodic synchronization of repository documentation (`README.md`).

### Boundary with `version-sync`
To prevent redundant work and race conditions between autonomous skills, a strict division of responsibility is enforced:

| Skill | Trigger Responsibility | Modification Scope |
| :--- | :--- | :--- |
| **`version-sync`** | SemVer increment / task completion | Synchronizes version strings across manifests, code constants, UI components, and the version badge in `README.md`. |
| **`readme-generator`** | Empty README, user request, or $\ge 5$ changelog entries | Refactors, rewrites, or enriches narrative sections, key features, architecture, and technology badges in `README.md`. |

> [!WARNING]
> `readme-generator` is strictly prohibited from running purely due to version bumps. Version bumps are managed in single-string replacements by `version-sync`.

---

## 2. The 5-Change Cadence Rule

Continuous rewriting of documentation introduces review fatigue and repository churn. Documentation should refresh when substantial functional delta has accumulated.

### Cadence Formula
$$\Delta = \text{total\_entries} - \text{last\_sync\_entries}$$

* **`total_entries`**: Distinct version releases identified via `^##\s*\[.*?\]` in `changelog.md` and `changelog-dev.md`.
* **`last_sync_entries`**: Counter stored persistently in `assets/readme-state.json`.
* **Activation Threshold**: When $\Delta \ge 5$, `can_generate` evaluates to `true` with reason `"changelog_delta_5"`.

### State Lifecycle
1. **Initial State:** `assets/readme-state.json` initialized with `{"last_sync_entries": 0}`.
2. **Delta Evaluation:** `scripts/readme_engine.py --inspect` compares total discovered entries against `last_sync_entries`.
3. **Execution Gate:** If $\Delta < 5$, `can_generate: false` unless `README.md` is empty or `--force` is provided.
4. **Counter Reset:** Following generation, running `scripts/readme_engine.py --reset-counter` sets `last_sync_entries = total_entries`, resetting $\Delta = 0$.

---

## 3. Shields.io Badge Standards (`style=for-the-badge`)

All badges injected into Sentinel Mexico documentation must use the `for-the-badge` style for visual consistency and institutional branding.

### Badge Formats
Shields.io requires escaping hyphens in badges as double hyphens (`--`):

1. **Version Badge:**
   ```markdown
   [![Version](https://img.shields.io/badge/version-<version>-blue?style=for-the-badge)](version.txt)
   ```
   *Target links to `package.json` if present; otherwise `version.txt`.*

2. **License Badge:**
   ```markdown
   [![License](https://img.shields.io/badge/License-Apache--2.0-red?style=for-the-badge)](LICENSE)
   ```

3. **Standard Specification Badge:**
   ```markdown
   [![Standard](https://img.shields.io/badge/Standard-agentskills.io-black?style=for-the-badge)](https://agentskills.io)
   ```

4. **Runtime & Language Badges:**
   * **Node.js:** `[![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org)`
   * **Python:** `[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)`
   * **TypeScript:** `[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)`
   * **Bash:** `[![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)`
   * **Electron:** `[![Electron](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://electronjs.org)`

---

## 4. Sanitized Repository Tree Generation

The deterministic engine provides a clean, 2-level directory tree representation:

### Exclusions
* **Version Control & Artifacts:** `.git/`, `.github/`, `.vscode/`, `.idea/`
* **Dependencies & Builds:** `node_modules/`, `dist/`, `build/`, `coverage/`, `.next/`, `.turbo/`, `__pycache__/`
* **Agent Context Directories:** `.agent/`, `.agents/`
* **Hidden Files:** Any file or folder starting with a leading dot (`.*`).

### Format
Clean unicode branch lines:
```text
.
├── scripts/
│   ├── install-skill.sh
│   └── validate-skills.sh
├── skills/
│   ├── git-push-governor/
│   ├── i18n-governor/
│   ├── project-init/
│   ├── readme-generator/
│   ├── semver-governor/
│   └── version-sync/
├── templates/
│   └── skill-template/
├── LICENSE
├── README.md
├── changelog-dev.md
├── changelog.md
└── version.txt
```

---

## 5. Standard Section Blueprint

Every generated `README.md` must follow this sequential structure:

```markdown
# <PROJECT_NAME>

<!-- Shields.io Badges -->

## DESCRIPCIÓN DEL PROYECTO
Brief institutional statement describing purpose and target audience.

## OVERVIEW
Architectural summary of problems solved and operational model.

## KEY FEATURES
- Capability 1
- Capability 2

## COMPARATIVE ANALYSIS (Optional)
Feature matrix contrasting against alternative tools.

## ARCHITECTURE & SECURITY (Optional)
Isolation guarantees, threat models, or execution boundaries.

## REPOSITORY STRUCTURE
Sanitized 2-level directory tree.

## INSTALLATION & SETUP / GETTING STARTED
Prerequisites, package installation, and quickstart commands.

## TECH STACK
Primary runtimes, frameworks, and foundational libraries.

## DOCUMENTATION
Links to specifications, guides, and manuals in `docs/`.

## CONTRIBUTING
Contribution workflow, branch policies, and testing commands.

## LICENSE
License information and copyright notice.
```
