---
name: project-init
description: "Deterministic project scaffolder. Enforces single-run execution per project via lockfile, verifies/creates the dev branch, conducts a compact requirements interview (Grill-Me style), and scaffolds monorepo/polyrepo workspaces with strict /locale/ and /src/ asset rules. Use exactly once when starting a new repository."
license: MIT
compatibility: Universal (Git CLI, Python 3.10+)
metadata:
  author: "Sentinel Mexico"
  version: "1.2.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/project-init"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# Project Initialization Workflow (`project-init`)

Canonical operational contract for bootstrapping clean repositories under Sentinel Mexico engineering governance. Adheres strictly to the `agentskills.io` open standard and Code-as-Skill methodology.

---

## Execution Flow Overview

```
[Trigger project-init]
        │
        ▼
[Stage 0: Version Freshness Gate]
python3 scripts/check_update.py
        │
        ├── update_available == true ──► [Prompt User: Update or Proceed?]
        │
        ▼
[Stage 1: Precondition Gate & Run-Once Lock]
python3 scripts/scaffold.py --check-git
        │
        ├── can_initialize == false ──► [HALT IMMEDIATELY] Display reason/message
        │                               (already_initialized OR existing_codebase)
        └── can_initialize == true
                    │
                    ▼
        [Stage 2: Batch Architectural Interview ("Grill-Me")]
        (Present architectural questions in a single round with recommendations)
                    │
                    ▼
        [Stage 3: Deterministic Scaffolding & Lock Sealing]
        python3 scripts/scaffold.py --manifest '<JSON>'
                    │
                    ▼
        [Verification & Ready Report]
```

---

## Stage 0: Version Freshness Gate

Before executing procedural logic, verify if an updated version exists in the official catalog:

```bash
python3 scripts/check_update.py
```

- If `update_available: true`, halt execution and prompt the user:
  > "⚠️ Se detectó una nueva versión de la skill `project-init` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"
  - If the user confirms (`S`):
    - When installed via symlink: run `git pull` in the cluster repository.
    - When installed standalone: run `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill project-init --agent <active-agent> --force`.
  - If the user declines (`N`), proceed immediately to Stage 1.
- If `update_available: false`, proceed directly to Stage 1.

---

## Stage 1: Precondition Gate & Run-Once Lock

Before asking questions or altering any repository state, execute the deterministic precondition guard:

```bash
python3 scripts/scaffold.py --check-git
```

### Gate Invariants:
1. **Run-Once Lockfile Check (`already_initialized`):**
   - If `.sentinel-init.lock` exists in the repository root:
     ```json
     {
       "can_initialize": false,
       "reason": "already_initialized",
       "message": "El proyecto ya fue inicializado previamente con project-init (lockfile detectado)."
     }
     ```
   - **Hard Stop:** Halt the workflow immediately. Do **not** ask architectural questions. Do **not** modify files or git branches. Display the message and abort cleanly.
2. **Existing Codebase Guard (`existing_codebase`):**
   - The engine evaluates the root tree against the GitHub/Agent bootstrap whitelist:
     - Version control & Agent metadata: `.git`, `.gitignore`, `.gitattributes`, `.agent`, `.agents`, `.github`
     - Base documentation & legal: `readme.md`, `license`, `licence`, `copying` (case-insensitive with any extension)
     - System hidden files: `.ds_store`, `thumbs.db`
   - If any directories or files outside this whitelist are present (e.g., `package.json`, `src/`, `node_modules/`, `app/`, `main.py`):
     ```json
     {
       "can_initialize": false,
       "reason": "existing_codebase",
       "message": "Se detectó código o dependencias existentes en el repositorio (...). project-init solo debe ejecutarse en repositorios nuevos."
     }
     ```
   - **Hard Stop:** Halt the workflow immediately. Display the message and exit.
3. **Clean Environment Confirmed (`can_initialize: true`):**
   - Resolves or creates the development branch (`dev`, `developer`, `devel`, `development`).
   - Proceed directly to Stage 2.

---

## Stage 2: Batch Architectural Interview ("Grill-Me")

When authorized by Stage 1, ask the user all required architecture decisions in a **single turn** with sensible defaults tagged with `➡️ Recomendado`. Do not scatter questions across multiple conversational turns.

### Standard Interview Template:

```text
Para inicializar la arquitectura de tu proyecto bajo los estándares de Sentinel Mexico, por favor confirma las siguientes decisiones técnicas:

1. ¿Estructura de repositorio?
   [A] Monorepo con workspaces centralizados ➡️ Recomendado
   [B] Polyrepo / Aplicación individual

2. ¿Qué entornos o subsistemas deseas configurar?
   [A] frontend, backend ➡️ Recomendado
   [B] api, web, shared
   [C] Personalizado (especifica los nombres de entornos)

3. ¿Qué frameworks o tecnologías base empleará cada entorno?
   [A] React / Next.js (frontend), FastAPI / Node (backend) ➡️ Recomendado
   [B] Vite + TypeScript (frontend), Express / NestJS (backend)
   [C] Personalizado (indica tecnologías preferidas)

4. ¿Qué idiomas base requiere la internacionalización (/locale/)?
   [A] Español e Inglés (es, en) ➡️ Recomendado
   [B] Solo Español (es)
   [C] Solo Inglés (en)

5. ¿Deseas incluir la plantilla base de CI/CD para GitHub Actions?
   [A] Sí (.github/workflows/deploy.yml) ➡️ Recomendado
   [B] No por el momento
```

---

## Stage 3: Deterministic Scaffolding & Lock Sealing

Compile the user's responses into a structured JSON manifest and invoke the deterministic engine:

```bash
python3 scripts/scaffold.py --manifest '{
  "project_name": "<project-name>",
  "is_monorepo": true,
  "environments": ["frontend", "backend"],
  "locales": ["es", "en"],
  "include_ci": true
}'
```

### Deterministic Artifacts Created:
- **Root Governance:**
  - `readme.md`: Living specification with architecture overview.
  - `changelog.md`: Production-ready release notes ([Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard).
  - `changelog-dev.md`: Sprint backlog and active iterations tracker.
  - `.gitignore`: Standard exclusion for dependencies, secrets, binaries, and `.sentinel-init.lock`.
  - `.github/workflows/deploy.yml`: Base validation pipeline (when `include_ci: true`).
  - `package.json`: Workspaces root declaration (when `is_monorepo: true`).
- **Per-Environment Invariants (`<env>/`):**
  - `<env>/locale/<loc>.json`: Symmetric translation dictionaries for zero hardcoded UI strings.
  - `<env>/src/img/.gitkeep`: Segregated raster/vector assets.
  - `<env>/src/video/.gitkeep`: Segregated rich media directory.
- **Run-Once Lock Sealing:**
  - Writes `.sentinel-init.lock` containing ISO initialization timestamp, architecture model, and configured environments, sealing the project against duplicate re-runs.

---

## Guardrails & Token Limits

1. **Token Economy:** Never delegate boilerplate creation or directory trees to LLM text generation. All scaffolding is executed by `scripts/scaffold.py`.
2. **References on Demand:** For in-depth architectural rationale regarding `/locale/` isolation, asset structures, dual changelogs, or lockfile mechanics, refer to `references/REFERENCE.md`.
