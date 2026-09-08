---
name: project-init
description: "Initializes brand-new software projects from scratch with strict Sentinel Mexico governance. Executes deterministic pre-checks, checks out or creates the dev branch, runs a batch architectural interview, and scaffolds clean monorepo or polyrepo foundations with dual changelogs, locale dictionaries, and static asset trees."
license: MIT
compatibility: Universal (Python 3.8+, Git 2.25+)
metadata:
  author: "Sentinel Mexico"
  version: "1.1.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/project-init"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# Project Initialization Workflow (`project-init`)

Canonical operational contract for bootstrapping clean repositories under Sentinel Mexico engineering governance.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `project-init` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill project-init --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## Execution Flow

```
[Trigger project-init]
        │
        ▼
[Phase 1: Precondition Guard]
python3 scripts/scaffold.py --check-git
        │
        ├── can_initialize == false ──► [ABORT IMMEDIATELY] (No questions, no changes)
        │
        └── can_initialize == true
                    │
                    ▼
        [Phase 2: Batch Grill-Me Interview]
        (Present architectural questions in a single round with recommendations)
                    │
                    ▼
        [Phase 3: Deterministic Scaffolding]
        python3 scripts/scaffold.py --manifest '<JSON>'
                    │
                    ▼
        [Verification & Next Steps Report]
```

---

### Phase 1: Precondition & Existing Project Guard

Before taking any action, asking questions, or altering repository state, execute the deterministic guard:

```bash
python3 scripts/scaffold.py --check-git
```

#### Guard Invariants:
1. **Existing Project Detected (`can_initialize == false`):**
   - If the output contains `{"can_initialize": false, "reason": "existing_project"}`, the workspace already contains existing files or subsystems.
   - **Hard Stop:** Halt the workflow immediately. Do **not** ask architectural questions. Do **not** run git commands or alter files. Report that initialization was safely aborted because an active project already exists.
2. **Clean Project Confirmed (`can_initialize == true`):**
   - The script automatically checks out an existing development branch (`dev`, `developer`, `devel`, `development`) or branches `dev` from the current HEAD.
   - Proceed directly to Phase 2.

---

### Phase 2: Batch Architectural Interview ("Grill-Me")

When authorized by Phase 1, ask the user all required architecture decisions in a **single turn** with sensible defaults tagged with `➡️ Recomendado`. Do not spread questions across multiple conversational steps.

#### Standard Interview Template:

```text
Para inicializar la arquitectura de tu proyecto bajo los estándares de Sentinel Mexico, por favor confirma las siguientes decisiones técnicas:

1. ¿Estructura de repositorio?
   [A] Monorepo con workspaces centralizados ➡️ Recomendado
   [B] Aplicación única / Polyrepo

2. ¿Qué entornos o subsistemas deseas configurar?
   [A] frontend, backend ➡️ Recomendado
   [B] api, web, shared
   [C] Personalizado (especifica los nombres)

3. ¿Qué idiomas base requiere la internacionalización (locale)?
   [A] Español e Inglés (es, en) ➡️ Recomendado
   [B] Solo Español (es)
   [C] Solo Inglés (en)

4. ¿Deseas incluir la plantilla base de CI/CD para GitHub Actions?
   [A] Sí (.github/workflows/deploy.yml) ➡️ Recomendado
   [B] No por el momento
```

---

### Phase 3: Deterministic Execution (Code-as-Skill)

Compile the user's choices into a structured JSON manifest and invoke the deterministic engine:

```bash
python3 scripts/scaffold.py --manifest '{
  "project_name": "<project-name>",
  "is_monorepo": true,
  "environments": ["frontend", "backend"],
  "locales": ["es", "en"],
  "include_ci": true
}'
```

#### Deterministic Invariants Created:
* **Root Governance:**
  - `readme.md`: Base living specification with project overview.
  - `changelog.md`: Production-ready release notes (Keep a Changelog format).
  - `changelog-dev.md`: Sprint tasks and active iterations.
  - `.gitignore`: Standard exclusion for dependencies, secrets (`.env`), build outputs, and multimedia binaries.
  - `.github/workflows/deploy.yml`: Base pipeline (when `include_ci: true`).
  - `package.json`: Workspaces definition (when `is_monorepo: true`).
* **Per-Environment Invariants (`<env>/`):**
  - `<env>/locale/<loc>.json`: Symmetric translation dictionaries.
  - `<env>/src/img/.gitkeep`: Dedicated static image directory.
  - `<env>/src/video/.gitkeep`: Dedicated static media directory.

---

## Guardrails & Token Limits

1. **Token Economy:** Never ask the LLM to write out boilerplate templates or directory trees via repetitive multi-turn reasoning. All generation logic is delegated to `scripts/scaffold.py`.
2. **References on Demand:** For deep technical rationale regarding the `/locale/` isolation, asset structures, or dual changelog standards, inspect `references/REFERENCE.md`.
