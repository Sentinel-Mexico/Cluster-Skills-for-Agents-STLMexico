---
name: readme-generator
description: "Generates or refactors the root README.md following Sentinel Mexico standard layout. Activates when README.md is empty, upon explicit user request, or every 5 accumulated changes in changelogs. Strictly prohibited from triggering due to version bumps (governed by version-sync)."
license: MIT
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.1.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/readme-generator"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# README Generator (`readme-generator`)

Canonical operational contract for creating, refactoring, and maintaining the institutional root `README.md` under Sentinel Mexico engineering governance and the `agentskills.io` standard.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `readme-generator` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill readme-generator --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## 1. Activation Preconditions & Cadence Gate

> [!IMPORTANT]
> The agent must strictly evaluate activation triggers before modifying `README.md`.
> Unscheduled or spontaneous README rewrites are strictly prohibited.

The skill activates **EXCLUSIVELY** under one of three conditions:
1. **Empty or Scaffolded README:** `README.md` (or `readme.md`) does not exist, has 0 bytes, or contains only 1 to 3 initial lines (`empty_readme`).
2. **Explicit User Request:** The user directly requests creating, updating, or rewriting the README (invoking `--force`).
3. **5-Change Cadence Accumulation:** The unreflected change count delta ($\ge 5$) since the last synchronization:
   $$\Delta = \text{total\_entries} - \text{last\_sync\_entries} \ge 5$$

### Strict Exclusion Clause (Critical Guardrail)
* **Prohibited:** Never trigger `readme-generator` solely due to a version bump or SemVer increment.
* **Separation of Concerns:** Updating version numbers and badges in `README.md` is strictly and exclusively governed by `version-sync`.

---

## 2. Execution Flow

```
[Trigger Evaluation]
        │
        ▼
[Phase 1: Deterministic Inspection]
python3 scripts/readme_engine.py --inspect [--force]
        │
        ├── can_generate == false ──► [EXIT] (No action required)
        │
        └── can_generate == true
                  │
                  ▼
        [Phase 2: Content Synthesis & Interactive Inquiry]
        Formulate batch inquiry for optional sections:
        - Comparative matrix with competing projects
        - Architecture & security specifications
        - Clean repository structure tree
                  │
                  ▼
        [Phase 3: README.md Generation]
        Write standard layout with for-the-badge Shields
                  │
                  ▼
        [Phase 4: Counter Reset & Cycle Closure]
        python3 scripts/readme_engine.py --reset-counter
```

---

## 3. Operational Phases

### Phase 1: State & Metadata Inspection (Token-Efficient)

Execute the deterministic inspection engine:

```bash
python3 scripts/readme_engine.py --inspect
```

*For user-mandated runs prior to reaching 5 changelog changes, append `--force`:*
```bash
python3 scripts/readme_engine.py --inspect --force
```

Expected JSON Output:
```json
{
  "can_generate": true,
  "reason": "changelog_delta_5",
  "unreflected_changes": 5,
  "total_entries": 12,
  "last_sync_entries": 7,
  "target_readme": "README.md",
  "metadata": {
    "name": "project-name",
    "version": "1.2.0",
    "version_file": "version.txt",
    "license": "Apache-2.0",
    "badges": [
      "[![Version](https://img.shields.io/badge/version-1.2.0-blue?style=for-the-badge)](version.txt)",
      "[![License](https://img.shields.io/badge/License-Apache--2.0-red?style=for-the-badge)](LICENSE)",
      "[![Standard](https://img.shields.io/badge/Standard-agentskills.io-black?style=for-the-badge)](https://agentskills.io)"
    ]
  },
  "sanitized_tree": ".\n├── scripts/\n├── skills/\n..."
}
```

* If `can_generate` is `false`, immediately conclude the turn without altering `README.md`.

---

### Phase 2: Interactive Batch Inquiry

Before generating content for new or comprehensively overhauled repositories, present a single consolidated question block to the user to incorporate tailored domain details:

```text
Se procederá con la generación/actualización institucional de README.md. Por favor confirma o proporciona los siguientes datos opcionales:
1. Tabla Comparativa: ¿Existen herramientas, librerías o repositorios de referencia con los que desees contrastar el proyecto?
2. Arquitectura y Seguridad: ¿Deseas resaltar algún modelo de amenazas, política de aislamiento o diagrama arquitectónico específico?
3. Árbol de Directorios: Se incluirá la estructura sanitizada de 2 niveles detectada automáticamente.
```

If user input is skipped or defaults are accepted, proceed directly with standard discovery metadata.

---

### Phase 3: Standard README.md Architecture

Structure `README.md` following the canonical Sentinel Mexico layout:

1. `# <NOMBRE_REPOSITORIO>` (Clean repository title)
2. **Badges:** Insert all shields from `metadata.badges` formatted with `style=for-the-badge`.
3. `## DESCRIPCIÓN DEL PROYECTO` (Executive overview and mission statement)
4. `## OVERVIEW` (High-level architectural narrative and problem solved)
5. `## KEY FEATURES` (Bulleted breakdown of capabilities and guardrails)
6. **Optional Modules (confirmed via Phase 2):**
   * `## COMPARATIVE ANALYSIS` (Feature parity table against reference solutions)
   * `## ARCHITECTURE & SECURITY` (Design principles, invariants, isolation boundaries)
   * `## REPOSITORY STRUCTURE` (Inject `sanitized_tree` block)
7. `## INSTALLATION & SETUP / GETTING STARTED` (Deterministic setup instructions)
8. `## TECH STACK` (Languages, runtimes, package managers, and dependencies)
9. `## DOCUMENTATION` (Links to `docs/`, references, specifications)
10. `## CONTRIBUTING` (Contribution guidelines, PR etiquette, branch policies)
11. `## LICENSE` (License name and link to `LICENSE`)

---

### Phase 4: Cycle Closure & Counter Reset

> [!CRITICAL]
> Immediately upon writing or updating `README.md`, the agent **MUST** reset the changelog change counter.

```bash
python3 scripts/readme_engine.py --reset-counter
```

Expected JSON Output:
```json
{
  "status": "counter_reset",
  "last_sync_entries": 12,
  "unreflected_changes": 0
}
```

This ensures future runs accurately calculate accumulated deltas from this baseline forward.

---

## 4. Guardrails & Token Optimization

1. **Zero Raw Traversal by LLM:** Never traverse file trees or scan changelog diffs using LLM prompts. Always read the JSON emitted by `scripts/readme_engine.py`.
2. **Strict Badge Formatting:** All Shields.io badges must specify `style=for-the-badge` and escape hyphens (`--`).
3. **Deep Reference Manual:** For exhaustive badge palettes, full markdown templates, and cadence policies, consult `references/REFERENCE.md`.
