```markdown
# Sentinel Mexico · Official Agent Skills Catalog

[![Specification](https://img.shields.io/badge/spec-agentskills.io-blue.svg)](https://agentskills.io/specification)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-30%2B%20AI%20Runtimes-purple.svg)](#supported-providers--installation-targets)
[![Organization](https://img.shields.io/badge/org-Sentinel--Mexico-red.svg)](https://github.com/orgs/Sentinel-Mexico/repositories)

The official skills catalog of **Sentinel Mexico**[cite: 12]. This repository hosts production-ready, source-grounded, and deterministic Agent Skills engineered under the [agentskills.io](https://agentskills.io/specification) standard[cite: 3, 5, 22]. Designed for enterprise orchestration, minimal token consumption, and seamless cross-platform installation across Claude Code, Cursor, Antigravity, GitHub Copilot, and more than 30 AI execution environments[cite: 2, 5, 14].

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Supported Providers & Installation Targets](#supported-providers--installation-targets)
3. [Universal De-duplication Rule](#universal-de-duplication-rule)
4. [Installation & Deployment](#installation--deployment)
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

Skills in this repository are **not tools**[cite: 1]. While tools provide callable endpoints or APIs (e.g., executing a web search or running a database query), **Skills** inject procedural workflows, domain guardrails, structured policies, and execution playbooks into the agent's contextual memory[cite: 1, 11, 28].

Every skill in this catalog implements:
- **Asymmetric Progressive Disclosure:** Initial discovery uses metadata (~100 tokens); full instructions (<5,000 tokens) load only upon activation, while heavy reference documents and deterministic scripts execute on demand[cite: 3, 5, 10, 17].
- **Code-as-Skill Determinism:** Non-heuristic tasks are offloaded to standalone scripts (Python, Bash, Node.js) in `scripts/`, avoiding wasteful multi-turn LLM reasoning loops[cite: 2, 3, 24].
- **Hermetic Packaging:** Zero runtime external dependencies for search and deterministic targets for multi-agent environments[cite: 2, 22].

---

## Supported Providers & Installation Targets

The installer maps skills from the source canonical directory (`skills/<skill-name>/`) directly to the target agent configuration trees[cite: 1, 2]. Paths are resolved relative to the active repository root (`project` scope) or the machine's user home directory (`user` scope)[cite: 2, 5].

| Provider / AI Platform | Slug (`--providers`) | Project Scope Path (`project`) | User Scope Path (`user`) |
| :--- | :--- | :--- | :--- |
| **Universal (Shared Target)** | `universal` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.config/agents/skills/<name>/`[cite: 2, 5] |
| **AdaL** | `adal` | `.adal/skills/<name>/`[cite: 2, 5] | `~/.adal/skills/<name>/`[cite: 2, 5] |
| **Amp** | `amp` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.config/agents/skills/<name>/`[cite: 2, 5] |
| **Antigravity** | `antigravity` | `.agent/skills/<name>/`[cite: 2, 5] | `~/.gemini/antigravity/skills/<name>/`[cite: 2, 5] |
| **Augment** | `augment` | `.augment/skills/<name>/`[cite: 2, 5] | `~/.augment/skills/<name>/`[cite: 2, 5] |
| **Claude Code** | `claude-code` | `.claude/skills/<name>/`[cite: 2, 5] | `~/.claude/skills/<name>/`[cite: 2, 5] |
| **Cline** | `cline` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.agents/skills/<name>/`[cite: 2, 5] |
| **CodeBuddy** | `codebuddy` | `.codebuddy/skills/<name>/`[cite: 2, 5] | `~/.codebuddy/skills/<name>/`[cite: 2, 5] |
| **Codex** | `codex` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.codex/skills/<name>/`[cite: 2, 5] |
| **Command Code** | `command-code` | `.commandcode/skills/<name>/`[cite: 2, 5] | `~/.commandcode/skills/<name>/`[cite: 2, 5] |
| **Continue** | `continue` | `.continue/skills/<name>/`[cite: 2, 5] | `~/.continue/skills/<name>/`[cite: 2, 5] |
| **Cortex Code (Snowflake)** | `cortex` | `.cortex/skills/<name>/`[cite: 2, 5] | `~/.snowflake/cortex/skills/<name>/`[cite: 2, 5] |
| **Crush** | `crush` | `.crush/skills/<name>/`[cite: 2, 5] | `~/.config/crush/skills/<name>/`[cite: 2, 5] |
| **Cursor** | `cursor` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.cursor/skills/<name>/`[cite: 2, 5] |
| **Droid (Factory)** | `droid` | `.factory/skills/<name>/`[cite: 2, 5] | `~/.factory/skills/<name>/`[cite: 2, 5] |
| **Gemini CLI** | `gemini-cli` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.gemini/skills/<name>/`[cite: 2, 5] |
| **GitHub Copilot** | `github-copilot` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.copilot/skills/<name>/`[cite: 2, 5] |
| **Goose** | `goose` | `.goose/skills/<name>/`[cite: 2, 5] | `~/.config/goose/skills/<name>/`[cite: 2, 5] |
| **iFlow CLI** | `iflow-cli` | `.iflow/skills/<name>/`[cite: 2, 5] | `~/.iflow/skills/<name>/`[cite: 2, 5] |
| **Junie** | `junie` | `.junie/skills/<name>/`[cite: 2, 5] | `~/.junie/skills/<name>/`[cite: 2, 5] |
| **Kilo Code** | `kilo` | `.kilocode/skills/<name>/`[cite: 2, 5] | `~/.kilocode/skills/<name>/`[cite: 2, 5] |
| **Kimi Code CLI** | `kimi-cli` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.config/agents/skills/<name>/`[cite: 2, 5] |
| **Kiro CLI** | `kiro-cli` | `.kiro/skills/<name>/`[cite: 2, 5] | `~/.kiro/skills/<name>/`[cite: 2, 5] |
| **Kode** | `kode` | `.kode/skills/<name>/`[cite: 2, 5] | `~/.kode/skills/<name>/`[cite: 2, 5] |
| **MCPJam** | `mcpjam` | `.mcpjam/skills/<name>/`[cite: 2, 5] | `~/.mcpjam/skills/<name>/`[cite: 2, 5] |
| **Mistral Vibe** | `mistral-vibe` | `.vibe/skills/<name>/`[cite: 2, 5] | `~/.vibe/skills/<name>/`[cite: 2, 5] |
| **Mux** | `mux` | `.mux/skills/<name>/`[cite: 2, 5] | `~/.mux/skills/<name>/`[cite: 2, 5] |
| **Neovate** | `neovate` | `.neovate/skills/<name>/`[cite: 2, 5] | `~/.neovate/skills/<name>/`[cite: 2, 5] |
| **OpenClaw** | `openclaw` | `skills/<name>/`[cite: 2, 5] | `~/.openclaw/skills/<name>/`[cite: 2, 5] |
| **OpenCode** | `opencode` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.config/opencode/skills/<name>/`[cite: 2, 5] |
| **OpenHands** | `openhands` | `.openhands/skills/<name>/`[cite: 2, 5] | `~/.openhands/skills/<name>/`[cite: 2, 5] |
| **Pi** | `pi` | `.pi/skills/<name>/`[cite: 2, 5] | `~/.pi/agent/skills/<name>/`[cite: 2, 5] |
| **Pochi** | `pochi` | `.pochi/skills/<name>/`[cite: 2, 5] | `~/.pochi/skills/<name>/`[cite: 2, 5] |
| **Qoder** | `qoder` | `.qoder/skills/<name>/`[cite: 2, 5] | `~/.qoder/skills/<name>/`[cite: 2, 5] |
| **Qwen Code** | `qwen-code` | `.qwen/skills/<name>/`[cite: 2, 5] | `~/.qwen/skills/<name>/`[cite: 2, 5] |
| **Replit** | `replit` | `.agents/skills/<name>/`[cite: 2, 5] | `~/.config/agents/skills/<name>/`[cite: 2, 5] |
| **Roo Code** | `roo` | `.roo/skills/<name>/`[cite: 2, 5] | `~/.roo/skills/<name>/`[cite: 2, 5] |
| **Trae** | `trae` | `.trae/skills/<name>/`[cite: 2, 5] | `~/.trae/skills/<name>/`[cite: 2, 5] |
| **Trae CN** | `trae-cn` | `.trae/skills/<name>/`[cite: 2, 5] | `~/.trae-cn/skills/<name>/`[cite: 2, 5] |
| **Windsurf** | `windsurf` | `.windsurf/skills/<name>/`[cite: 2, 5] | `~/.codeium/windsurf/skills/<name>/`[cite: 2, 5] |
| **Zencoder** | `zencoder` | `.zencoder/skills/<name>/`[cite: 2, 5] | `~/.zencoder/skills/<name>/`[cite: 2, 5] |

---

## Universal De-duplication Rule

To prevent filesystem sprawl and eliminate duplicate token loading during agent indexing, platforms sharing the `.agents/skills/` specification (Cursor, Codex, GitHub Copilot, Gemini CLI, Cline, Amp, Replit, OpenCode, and Kimi Code CLI) are collapsed by default into the `universal` target under project scope[cite: 2].

```text
Project Root/
└── .agents/
    └── skills/
        └── <skill-name>/   <--- Single physical target shared by all compliant runtimes

```

When targeting multiple agents within the same workspace, our installation engine creates a single canonical directory or symlink, avoiding redundant disk storage and context collisions.

---

## Installation & Deployment

### Deterministic Shell Installer (`install-skill.sh`)

Use the bundled POSIX-compliant deployment script located in `scripts/install-skill.sh`.

#### Syntax

```bash
./scripts/install-skill.sh \
  --skill <skill-name|all> \
  --providers <slug1,slug2|universal|all> \
  --scope <project|user> \
  --method <symlink|copy> \
  [--target-dir <path>] \
  [--force]

```

#### Common Examples

```bash
# 1. Install a specific skill for Antigravity & Claude Code in the current project (via symlinks)
./scripts/install-skill.sh \
  --skill security-audit \
  --providers antigravity,claude-code \
  --scope project \
  --method symlink \
  --force

# 2. Deploy all skills in this repo globally for Universal and Windsurf runtimes
./scripts/install-skill.sh \
  --skill all \
  --providers universal,windsurf \
  --scope user \
  --method copy

# 3. Deploy all skills to every supported provider detected on your machine
./scripts/install-skill.sh \
  --skill all \
  --providers all \
  --scope project \
  --method symlink

```

---

### Rust Engine CLI (`skillinstaller`)

For enterprise environments with Rust toolchains, you can run the native `skillinstaller` engine:

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

If you are using external orchestration tools or official agent CLIs, install Sentinel Mexico skills directly using remote URLs:

```bash
# Universal Agent Skills Installer (Node.js)
npx skills add Sentinel-Mexico/skills/vibe-tdd-pipeline

# Claude Code CLI (Native Plugin Integration)
claude plugin marketplace add Sentinel-Mexico/skills
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
├── SKILL.md                 # Required: Canonical instructions and YAML frontmatter
├── scripts/                 # Optional: Standalone deterministic code (Python, Bash, JS)
│   └── run.py
├── references/              # Optional: In-depth reference docs loaded on demand
│   └── CHEAT_SHEET.md
└── assets/                  # Optional: Templates, JSON schemas, static resources
    └── schema.json

```

---

### The `SKILL.md` Specification

The `SKILL.md` file defines both the discovery contract and execution instructions.

```markdown
---
name: sample-task-runner
description: Validates and runs pipeline tests for containerized services. Use when verifying CI test integrity before production commits.
license: Apache-2.0
compatibility: Universal (Python 3.10+, Docker CLI)
metadata:
  author: Sentinel Mexico
  version: "1.0.0"
  repository: [https://github.com/Sentinel-Mexico/skills](https://github.com/Sentinel-Mexico/skills)
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

* `name`: Max 64 chars. Lowercase alphanumeric characters and hyphens only (`^[a-z0-9-]+$`). Must strictly match the parent directory name.


* `description`: 1 to 1024 chars. Must act as an **activation contract**—clearly defining what the skill executes and when the agent must load it.


* `metadata.author`: Must be attributed to `Sentinel Mexico`.


* `metadata.version`: Semantic version string (e.g., `"1.0.0"`).



---

### Progressive Disclosure & Token Optimization

To prevent agent token degradation and reduce execution costs, skills must adhere to strict size ceilings:

1. **Discovery Footprint (~100 tokens):** At startup, agents load only the skill `name` and `description`. Descriptions must remain concise and trigger-focused.


2. **Body Ceiling (<500 lines / <5,000 tokens):** The body of `SKILL.md` must not exceed 500 lines.


3. **On-Demand Reference:** Shift detailed reference manuals, data tables, or long-form documentation into `references/`. The agent accesses them via tool calls (e.g., `read_skill_resource`) only if explicitly needed.



---

### Deterministic Scripts (Code-as-Skill)

Do not ask the LLM to perform arithmetic, complex string parsing, regex transformations, or repeated external API lookups in multi-turn reasoning prompts.

* Place executable code inside `scripts/`.


* Scripts must include their own error-handling and return exit codes (`0` for success, non-zero for failure).


* Outputs must be structured (JSON, TSV, or key-value verdicts), minimizing output tokens fed back into the agent context.



---

## Creating & Contributing a New Skill

Use the built-in scaffolding template to initiate a new skill:

```bash
# 1. Clone repository
git clone [https://github.com/Sentinel-Mexico/skills.git](https://github.com/Sentinel-Mexico/skills.git)
cd skills

# 2. Scaffold a new skill from standard template
cp -r templates/skill-template skills/<my-new-skill>
cd skills/<my-new-skill>

# 3. Rename frontmatter name to match folder
sed -i 's/skill-template/<my-new-skill>/g' SKILL.md

```

### Local Validation Check

Run the repository validation suite prior to pushing or opening a Pull Request:

```bash
# Validate frontmatter rules, regex paths, and token ceilings
bash ./scripts/validate-skills.sh

```

---

## Security, Governance & Audit Boundaries

Skills possess deep access to agent actions and local shell environments. Sentinel Mexico strictly isolates and audits each skill through automated workflows:

1. **Static Analysis & Sanitization:** All submissions are scanned via automated GitHub Actions for:
* Hardcoded tokens, API keys, and private credentials.


* Destructive shell invocation (`rm -rf /`, formatting commands, unsafe piped bash).


* Prompt-injection payloads and jailbreak trigger strings.




2. **Execution Sandboxing:** Any skill leveraging executable binaries in `scripts/` is designated as **Tier-3 (Supervised / Sandboxed)**. Agents must execute scripts in isolated runtimes (containers, firejail, or workspace-isolated runners).


3. **Supply-Chain Integrity:** Never install skills from unverified forks. All production skills must originate from the protected branches of the `Sentinel-Mexico` organization.



---

## Organization & Ownership

This repository is designed, maintained, and governed by **Sentinel Mexico**.

* **Organization Repositories:** [https://github.com/orgs/Sentinel-Mexico/repositories](https://github.com/orgs/Sentinel-Mexico/repositories)
* **License:** Apache-2.0 open-source license.
* **Support & Security Disclosures:** File an issue or security advisory directly via the GitHub repository.



```

```