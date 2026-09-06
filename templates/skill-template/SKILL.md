---
name: skill-template
description: "Canonical template for Sentinel Mexico Agent Skills compliant with agentskills.io standard. Use this template when creating new agent skills."
license: Apache-2.0
compatibility: Universal
metadata:
  author: "Sentinel Mexico"
  version: "0.1.0"
  repository: "https://github.com/Sentinel-Mexico/skills"
allowed-tools: Bash Read
---

# Skill Template

## Overview
Concise overview of what this skill accomplishes and its execution criteria.

## Workflow & Procedural Core
Step-by-step instructions for the agent when executing this skill:

1. **Prerequisites Check**: Validate environment state and required tools.
2. **Execute Deterministic Scripts**: Use helper scripts in `scripts/` rather than multi-turn LLM reasoning loops.
3. **Analyze and Respond**: Formulate structured response.

## Guardrails & Verification
- Ensure `SKILL.md` body does not exceed 500 lines / 5,000 tokens.
- Offload long documentation, schemas, and troubleshooting guides to `references/`.
- Ensure non-zero exit codes in scripts are surfaced clearly.
