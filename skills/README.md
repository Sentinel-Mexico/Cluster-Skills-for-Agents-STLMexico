# Sentinel Mexico · Skills Directory

This directory contains the production agent skills catalog. Each skill resides in its own isolated subdirectory conforming to the [agentskills.io](https://agentskills.io/specification) open standard.

## Directory Structure

```text
skills/
├── <skill-name>/
│   ├── SKILL.md          # Canonical instructions & YAML frontmatter (<500 lines)
│   ├── scripts/          # Deterministic executable scripts (Code-as-Skill)
│   ├── references/       # Progressive disclosure reference manuals
│   └── assets/           # Static templates, schemas, and media
```

To create a new skill, copy `templates/skill-template/`:
```bash
cp -r templates/skill-template skills/<my-skill-name>
```
