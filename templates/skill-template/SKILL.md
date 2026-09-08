---
name: skill-template
description: "Canonical template for Sentinel Mexico Agent Skills compliant with agentskills.io standard. Use this template when creating new agent skills."
license: MIT
compatibility: Universal
metadata:
  author: "Sentinel Mexico"
  version: "0.1.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "templates/skill-template"
allowed-tools: Bash Read
---

# Skill Template

## Overview
Concise overview of what this skill accomplishes and its execution criteria.

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `<skill-name>` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <skill-name> --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

## Workflow & Procedural Core
Step-by-step instructions for the agent when executing this skill:

1. **Prerequisites Check**: Validate environment state and required tools.
2. **Execute Deterministic Scripts**: Use helper scripts in `scripts/` rather than multi-turn LLM reasoning loops.
3. **Analyze and Respond**: Formulate structured response.

## Guardrails & Verification
- Ensure `SKILL.md` body does not exceed 500 lines / 5,000 tokens.
- Offload long documentation, schemas, and troubleshooting guides to `references/`.
- Ensure non-zero exit codes in scripts are surfaced clearly.
