# Sentinel Mexico · Official Agent Skills Catalog

[![Specification](https://img.shields.io/badge/spec-agentskills.io-blue.svg)](https://agentskills.io/specification)
[![Version](https://img.shields.io/badge/version-0.10.0-blue.svg)](version.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-30%2B%20AI%20Runtimes-purple.svg)](#supported-providers--installation-targets)
[![Repository](https://img.shields.io/badge/repo-Cluster--Skills--for--Agents--STLMexico-red.svg)](https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico)

The official skills catalog of **Sentinel Mexico**. This repository hosts production-ready, source-grounded, and deterministic Agent Skills engineered under the [agentskills.io](https://agentskills.io/specification) standard. Designed for enterprise orchestration, minimal token consumption, and seamless cross-platform installation across Claude Code, Cursor, Antigravity, GitHub Copilot, and more than 30 AI execution environments.

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Supported Providers & Installation Targets](#supported-providers--installation-targets)
3. [Universal De-duplication Rule](#universal-de-duplication-rule)
4. [Installation & Deployment](#installation--deployment)
   - [Direct Remote Install from GitHub](#direct-remote-install-from-github)
   - [Antigravity Specific Step-by-Step Setup](#antigravity-specific-step-by-step-setup)
   - [Deterministic Shell Installer (`install-skill.sh`)](#deterministic-shell-installer-install-skillsh)
   - [Rust Engine CLI (`skillinstaller`)](#rust-engine-cli-skillinstaller)
   - [Native Agent Package Managers & Plugin Registries](#native-agent-package-managers--plugin-registries)
5. [Skill Architecture & Engineering Standards](#skill-architecture--engineering-standards)
   - [Directory Structure](#directory-structure)
   - [The `SKILL.md` Specification](#the-skillmd-specification)
   - [Progressive Disclosure & Token Optimization](#progressive-disclosure--token-optimization)
   - [Deterministic Scripts (Code-as-Skill)](#deterministic-scripts-code-as-skill)
6. [Creating & Contributing a New Skill](#creating--contributing-a-new-skill)
7. [Security, Governance & Audit Boundaries](#security-governance--audit-boundaries)
8. [Organization & Ownership](#organization--ownership)

---

## Architectural Overview

Skills in this repository are **not tools**[cite: 3]. While tools provide callable functions to take actions via APIs or external services[cite: 3, 16], **Skills** inject domain expertise, procedural instructions, guardrails, and execution playbooks into the agent's context[cite: 3, 16].

Every skill in this catalog implements:
- **Asymmetric Progressive Disclosure:** Initial discovery reads only metadata (~100 tokens); full instructions (<5,000 tokens) load only upon activation when relevant, while heavy reference documents and scripts execute on demand[cite: 3, 5, 12].
- **Code-as-Skill Determinism:** Complex operations, repetitive parsing, or regex routines are compiled into deterministic scripts inside `scripts/`, avoiding wasteful multi-turn LLM reasoning loops[cite: 2].
- **Hermetic Packaging:** Self-contained skill units with predictable routing targets across all major coding runtimes[cite: 1, 2].

---

## Supported Providers & Installation Targets

The installer maps skills from canonical subdirectories (`skills/<skill-name>/`) directly to target agent configuration trees[cite: 1, 2]. Paths are resolved relative to the active repository root (`project` scope) or the machine's user home directory (`user` scope)[cite: 1, 6].

| Provider / AI Platform | Slug (`--providers`) | Project Scope Path (`project`) | User Scope Path (`user`) |
| :--- | :--- | :--- | :--- |
| **Universal (Shared Target)** | `universal` | `.agents/skills/<name>/`[cite: 1] | `~/.config/agents/skills/<name>/`[cite: 1] |
| **AdaL** | `adal` | `.adal/skills/<name>/`[cite: 1] | `~/.adal/skills/<name>/`[cite: 1] |
| **Amp** | `amp` | `.agents/skills/<name>/`[cite: 1] | `~/.config/agents/skills/<name>/`[cite: 1] |
| **Antigravity** | `antigravity` | `.agent/skills/<name>/`[cite: 1] | `~/.gemini/antigravity/skills/<name>/`[cite: 1] |
| **Augment** | `augment` | `.augment/skills/<name>/`[cite: 1] | `~/.augment/skills/<name>/`[cite: 1] |
| **Claude Code** | `claude-code` | `.claude/skills/<name>/`[cite: 1] | `~/.claude/skills/<name>/`[cite: 1] |
| **Cline** | `cline` | `.agents/skills/<name>/`[cite: 1] | `~/.agents/skills/<name>/`[cite: 1] |
| **CodeBuddy** | `codebuddy` | `.codebuddy/skills/<name>/`[cite: 1] | `~/.codebuddy/skills/<name>/`[cite: 1] |
| **Codex** | `codex` | `.agents/skills/<name>/`[cite: 1] | `~/.codex/skills/<name>/`[cite: 1] |
| **Command Code** | `command-code` | `.commandcode/skills/<name>/`[cite: 1] | `~/.commandcode/skills/<name>/`[cite: 1] |
| **Continue** | `continue` | `.continue/skills/<name>/`[cite: 1] | `~/.continue/skills/<name>/`[cite: 1] |
| **Cortex Code (Snowflake)** | `cortex` | `.cortex/skills/<name>/`[cite: 1] | `~/.snowflake/cortex/skills/<name>/`[cite: 1] |
| **Crush** | `crush` | `.crush/skills/<name>/`[cite: 1] | `~/.config/crush/skills/<name>/`[cite: 1] |
| **Cursor** | `cursor` | `.agents/skills/<name>/`[cite: 1] | `~/.cursor/skills/<name>/`[cite: 1] |
| **Droid (Factory)** | `droid` | `.factory/skills/<name>/`[cite: 1] | `~/.factory/skills/<name>/`[cite: 1] |
| **Gemini CLI** | `gemini-cli` | `.agents/skills/<name>/`[cite: 1] | `~/.gemini/skills/<name>/`[cite: 1] |
| **GitHub Copilot** | `github-copilot` | `.agents/skills/<name>/`[cite: 1] | `~/.copilot/skills/<name>/`[cite: 1] |
| **Goose** | `goose` | `.goose/skills/<name>/`[cite: 1] | `~/.config/goose/skills/<name>/`[cite: 1] |
| **iFlow CLI** | `iflow-cli` | `.iflow/skills/<name>/`[cite: 1] | `~/.iflow/skills/<name>/`[cite: 1] |
| **Junie** | `junie` | `.junie/skills/<name>/`[cite: 1] | `~/.junie/skills/<name>/`[cite: 1] |
| **Kilo Code** | `kilo` | `.kilocode/skills/<name>/`[cite: 1] | `~/.kilocode/skills/<name>/`[cite: 1] |
| **Kimi Code CLI** | `kimi-cli` | `.agents/skills/<name>/`[cite: 1] | `~/.config/agents/skills/<name>/`[cite: 1] |
| **Kiro CLI** | `kiro-cli` | `.kiro/skills/<name>/`[cite: 1] | `~/.kiro/skills/<name>/`[cite: 1] |
| **Kode** | `kode` | `.kode/skills/<name>/`[cite: 1] | `~/.kode/skills/<name>/`[cite: 1] |
| **MCPJam** | `mcpjam` | `.mcpjam/skills/<name>/`[cite: 1] | `~/.mcpjam/skills/<name>/`[cite: 1] |
| **Mistral Vibe** | `mistral-vibe` | `.vibe/skills/<name>/`[cite: 1] | `~/.vibe/skills/<name>/`[cite: 1] |
| **Mux** | `mux` | `.mux/skills/<name>/`[cite: 1] | `~/.mux/skills/<name>/`[cite: 1] |
| **Neovate** | `neovate` | `.neovate/skills/<name>/`[cite: 1] | `~/.neovate/skills/<name>/`[cite: 1] |
| **OpenClaw** | `openclaw` | `skills/<name>/`[cite: 1] | `~/.openclaw/skills/<name>/`[cite: 1] |
| **OpenCode** | `opencode` | `.agents/skills/<name>/`[cite: 1] | `~/.config/opencode/skills/<name>/`[cite: 1] |
| **OpenHands** | `openhands` | `.openhands/skills/<name>/`[cite: 1] | `~/.openhands/skills/<name>/`[cite: 1] |
| **Pi** | `pi` | `.pi/skills/<name>/`[cite: 1] | `~/.pi/agent/skills/<name>/`[cite: 1] |
| **Pochi** | `pochi` | `.pochi/skills/<name>/`[cite: 1] | `~/.pochi/skills/<name>/`[cite: 1] |
| **Qoder** | `qoder` | `.qoder/skills/<name>/`[cite: 1] | `~/.qoder/skills/<name>/`[cite: 1] |
| **Qwen Code** | `qwen-code` | `.qwen/skills/<name>/`[cite: 1] | `~/.qwen/skills/<name>/`[cite: 1] |
| **Replit** | `replit` | `.agents/skills/<name>/`[cite: 1] | `~/.config/agents/skills/<name>/`[cite: 1] |
| **Roo Code** | `roo` | `.roo/skills/<name>/`[cite: 1] | `~/.roo/skills/<name>/`[cite: 1] |
| **Trae** | `trae` | `.trae/skills/<name>/`[cite: 1] | `~/.trae/skills/<name>/`[cite: 1] |
| **Trae CN** | `trae-cn` | `.trae/skills/<name>/`[cite: 1] | `~/.trae-cn/skills/<name>/`[cite: 1] |
| **Windsurf** | `windsurf` | `.windsurf/skills/<name>/`[cite: 1] | `~/.codeium/windsurf/skills/<name>/`[cite: 1] |
| **Zencoder** | `zencoder` | `.zencoder/skills/<name>/`[cite: 1] | `~/.zencoder/skills/<name>/`[cite: 1] |

---

## Universal De-duplication Rule

Platforms sharing the `.agents/skills/` specification (Cursor, Codex, GitHub Copilot, Gemini CLI, Cline, Amp, Replit, OpenCode, Kimi Code CLI) collapse into the `universal` target under project scope[cite: 1, 2]:

```text
Project Root/
└── .agents/
    └── skills/
        └── <skill-name>/   <--- Canonical physical target shared across compliant runtimes

```

The installer prevents creating separate copies for runtimes targeting `.agents/skills/`, avoiding filesystem bloat and duplicate indexing.

---

## Installation & Deployment

### Direct Remote Install from GitHub

Install specific skills directly from this GitHub repository without cloning the full catalog:

#### Option A: Using Universal Agent Skills Runner (`npx skills`)

```bash
# Project scope (install to current project)
npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <skill-name> --agent <agent-slug>

# User scope (install globally across all local projects)
npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <skill-name> --agent <agent-slug> -g

```

#### Option B: Git Sparse Checkout (No Node.js Dependency)

Extract only the targeted skill folder directly into your workspace:

```bash
# Set skill name and destination path
SKILL_NAME="<skill-name>"
DEST_DIR=".agent/skills" # Adjust based on target provider (e.g., .claude/skills or .agents/skills)

mkdir -p "$DEST_DIR"
git clone --depth 1 --filter=blob:none --sparse \
  [https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico.git](https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico.git) \
  .tmp-skills \
  && cd .tmp-skills \
  && git sparse-checkout set skills/$SKILL_NAME \
  && mv skills/$SKILL_NAME ../"$DEST_DIR"/ \
  && cd .. && rm -rf .tmp-skills

```

---

### Antigravity Specific Step-by-Step Setup

Antigravity isolates skill configurations to dedicated directories (`.agent/skills/` locally or `~/.gemini/antigravity/skills/` globally).

#### Step 1: Target Selection

* **Project Scope:** `<workspace-root>/.agent/skills/<skill-name>/`

* **User Scope:** `~/.gemini/antigravity/skills/<skill-name>/`


#### Step 2: Deployment

Execute using the local installer script:

```bash
# Local Project Scope (symlinked)
./scripts/install-skill.sh \
  --skill <skill-name> \
  --providers antigravity \
  --scope project \
  --target-dir /path/to/project \
  --method symlink \
  --force

# Global User Scope
./scripts/install-skill.sh \
  --skill <skill-name> \
  --providers antigravity \
  --scope user \
  --method symlink \
  --force

```

Or deploy directly via remote command:

```bash
npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill <skill-name> --agent antigravity

```

#### Step 3: Verification

Verify target directories on disk:

```bash
# Project scope verification
ls -la .agent/skills/<skill-name>/

# Global scope verification
ls -la ~/.gemini/antigravity/skills/<skill-name>/

```

#### Step 4: Execution

Start a new session in Antigravity. The agent indexes `name` and `description` frontmatter (~100 tokens) on boot and activates the skill workflow when matching instructions appear in prompt context.

---

### Deterministic Shell Installer (`install-skill.sh`)

Use the bundled POSIX-compliant deployment script located in `scripts/install-skill.sh`:

#### Syntax

```bash
./scripts/install-skill.sh \
  --skill <skill-name|comma-separated-list|all> \
  --providers <provider-slug|universal|all> \
  --scope <project|user> \
  --method <symlink|copy> \
  [--target-dir <path>] \
  [--force]

```

#### Target Resolution Examples

```bash
# 1. Install specific skill to current project via symlink for Claude and Antigravity
./scripts/install-skill.sh \
  --skill security-audit \
  --providers antigravity,claude-code \
  --scope project \
  --method symlink \
  --force

# 2. Deploy multiple specific skills to universal target
./scripts/install-skill.sh \
  --skill data-pipeline,code-reviewer \
  --providers universal \
  --scope project \
  --method symlink

# 3. Deploy all repository skills globally across all detected providers
./scripts/install-skill.sh \
  --skill all \
  --providers all \
  --scope user \
  --method copy

```

---

### Rust Engine CLI (`skillinstaller`)

If compiled within a Rust toolchain, use the native `skillinstaller` engine:

```bash
# Discover supported platforms on host
cargo run --bin install-skill -- providers

# Detect installed agent environments in project
cargo run --bin install-skill -- detect --project-root .

# Execute deterministic multi-target installation
cargo run --bin install-skill -- install \
  --source ./skills/vibe-tdd-pipeline \
  --providers antigravity,claude-code,cursor \
  --scope project \
  --project-root . \
  --method symlink \
  --force

```

---

### Native Agent Package Managers & Plugin Registries

```bash
# Universal Agent Skills Installer (Node.js)
npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill vibe-tdd-pipeline

# Claude Code CLI (Native Plugin Integration)
claude plugin marketplace add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico
claude plugin install vibe-tdd-pipeline@Sentinel-Mexico

# CrewAI Organizations & Projects
crewai skill install @sentinel-mexico/vibe-tdd-pipeline

```

---

## Skill Architecture & Engineering Standards

Every skill residing in `skills/` must strictly comply with the [agentskills.io specification](https://agentskills.io/specification).

### Directory Structure

```text
skills/<skill-name>/
├── SKILL.md                 # Required: Canonical instructions and YAML frontmatter (<500 lines)
├── scripts/                 # Optional: Deterministic code (Python, Bash, Node.js)
│   └── run.py
├── references/              # Optional: In-depth reference manuals loaded on demand
│   └── CHEAT_SHEET.md
└── assets/                  # Optional: Templates, JSON schemas, static resources
    └── schema.json

```

---

### The `SKILL.md` Specification

The `SKILL.md` file defines both the discovery contract and execution instructions[cite: 3, 5]:

```markdown
---
name: sample-task-runner
description: Validates and runs pipeline tests for containerized services. Use when verifying CI test integrity before production commits.
license: MIT
compatibility: Universal (Python 3.10+, Docker CLI)
metadata:
  author: Sentinel Mexico
  version: "1.0.0"
  repository: [https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico](https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico)
allowed-tools: Bash(git:*) Bash(pytest:*) Read
---

## Procedural Core

Follow this step-by-step workflow when validating CI pipelines:

1. **Verify Sandbox**: Confirm Docker daemon connectivity.
2. **Execute Gate**: Run `./scripts/run.py --target tests/`.
3. **Analyze Output**: Extract summary metrics and format output according to verification criteria.

## Verification & Guardrails

- All assertions in test suites must return exit code 0.
- If errors are discovered, consult `references/TROUBLESHOOTING.md` before prompting the user.

```

#### Mandatory Frontmatter Fields

* `name`: Max 64 chars. Lowercase alphanumeric characters and hyphens only (`^[a-z0-9-]+$`). Must match the directory name.


* `description`: 1 to 1024 chars. Must act as an **activation contract**—defining what the skill executes and when the agent should activate it.


* `metadata.author`: Must be attributed to `Sentinel Mexico`.


* `metadata.version`: Semantic version string (e.g., `"1.0.0"`).



---

### Progressive Disclosure & Token Optimization

1. **Discovery Footprint (~100 tokens):** At startup, agents load only the skill `name` and `description`.


2. **Body Ceiling (<500 lines / <5,000 tokens):** The body of `SKILL.md` must not exceed 500 lines.


3. **On-Demand Reference:** Shift detailed manuals, syntax tables, or long-form documentation into `references/`. The agent reads them via tools only when explicitly needed.



---

### Deterministic Scripts (Code-as-Skill)

Do not force the LLM to handle heavy arithmetic, large-scale string parsing, regex transformations, or repeated external lookups in multi-turn reasoning loops.

* Place executable logic inside `scripts/`.


* Scripts must include comprehensive error-handling and return exit codes (`0` for success, non-zero for failure).
* Outputs must be structured (JSON, TSV, or concise key-value lines) to minimize output token usage.



---

## Creating & Contributing a New Skill

Use the built-in template to scaffold a new skill:

```bash
# 1. Clone repository
git clone [https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico.git](https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico.git)
cd Cluster-Skills-for-Agents-STLMexico

# 2. Scaffold a new skill from template
cp -r templates/skill-template skills/<my-new-skill>
cd skills/<my-new-skill>

# 3. Rename frontmatter to match directory name
sed -i 's/skill-template/<my-new-skill>/g' SKILL.md

```

### Local Validation Check

Validate frontmatter compliance and token ceilings before opening a Pull Request:

```bash
bash ./scripts/validate-skills.sh

```

---

## Security, Governance & Audit Boundaries

Skills have operational access to local agent tools and shell environments. Sentinel Mexico enforces multi-layer audit boundaries:

1. **Static Analysis & Sanitization:** Automated GitHub Actions inspect incoming skills for:
* Hardcoded tokens, API keys, and credential leaks.


* Destructive shell patterns (`rm -rf /`, drive formatting, unvalidated piped executions).


* Prompt-injection payloads and unauthorized context override strings.




2. **Execution Sandboxing:** Any skill containing executable scripts in `scripts/` must be run in containerized, firewalled, or supervised environments.


3. **Supply-Chain Integrity:** Avoid installing skills from unverified origins. Production skills must originate from the main branch of `Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico`.



---

## Organization & Ownership

This repository is designed, maintained, and governed by **Sentinel Mexico**.

* **Repository:** [https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico](https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico)
* **License:** MIT License.
* **Support & Security Disclosures:** File an issue or security advisory directly via this GitHub repository.