# Architectural Reference & Technical Rationale: `project-init`

This document outlines the architectural rationale behind the repository patterns enforced by the `project-init` skill under Sentinel Mexico engineering governance.

---

## 1. Modular Localization Separation (`<env>/locale/`)

### Context
Modern multi-tenant and multi-tier systems often suffer from coupled copy and hardcoded strings within source files, causing translation drift, costly refactors, and excessive LLM context token overhead.

### Technical Rationale
- **Zero Hardcoded Strings:** Encapsulating user-facing text in discrete `<env>/locale/<lang>.json` dictionaries prevents string fragmentation across components.
- **Symmetric Key Parity:** Having a dedicated schema ensures that any added or modified key can be validated automatically across 100% of the active locales (`en.json`, `es.json`, etc.) prior to merging.
- **Token Efficiency:** Agents can read only the dictionary key map without ingesting thousands of lines of UI markup, reducing token usage by up to 80% during copy adjustments.

---

## 2. Directory Layout & Static Asset Segregation (`<env>/src/img/`, `<env>/src/video/`)

### Context
Mixing raw media assets with compiled source logic causes repository clutter, slow git indexing, and messy build artifacts.

### Technical Rationale
- **Predictable Asset Bundling:** Separating static raster/vector graphics into `src/img/` and rich media into `src/video/` establishes a standard path resolution convention across frontend, mobile, and backend view engines.
- **Git Hygiene & LFS Readiness:** Binaries and video streams are segregated from code trees, facilitating easy integration with Git LFS or object storage buckets (S3, Cloud Storage) when asset volumes grow.
- **Hermetic Scaffolding:** Initializing these subdirectories with `.gitkeep` ensures the layout is preserved in version control without polluting git with placeholder sample files.

---

## 3. Dual Changelog Governance (`changelog.md` vs. `changelog-dev.md`)

### Context
Single-file changelogs in active development teams either lead to frequent merge conflicts on `main` or premature publication of internal sprint work to end users.

### Technical Rationale
- **Production Truth (`changelog.md`):** Strictly read-only during ongoing sprint iterations. It is modified only during official, verified production releases when merging `dev` into `main`. It contains curated, customer-facing notes.
- **Active Iteration Tracking (`changelog-dev.md`):** Captures all intermediate changes, micro-refactors, internal fixes, and sprint progress made on the `dev` branch.
- **Release Consolidation:** During release cycles, the engineering agent or release manager aggregates completed items from `changelog-dev.md`, promotes them into a clean semantic version entry in `changelog.md`, and prepares the production tag.

---

## 4. Deterministic Pre-Execution Guard & Run-Once Lockfile

### Context
Re-initializing a non-empty workspace risks overwriting existing configuration files, corrupting git branch history, or wiping local work. Conversely, false positives from initial GitHub repository creation (e.g. `.gitignore`, `LICENSE`, `README.md`) prematurely blocked scaffolding.

### Technical Rationale
- **Run-Once Lockfile (`.sentinel-init.lock`):** Upon completing initialization, a metadata lockfile is sealed in the project root. Subsequent invocations detect this lock and halt immediately (`reason: already_initialized`) with zero side-effects.
- **GitHub Bootstrap Whitelist:** The engine safely allows standard bootstrap entries (`.git`, `.gitignore`, `.gitattributes`, `.agent`, `.agents`, `.github`, `readme.md`, `license`, `copying`, system files). If and only if real application code or dependency definitions exist outside this whitelist does the guard halt (`reason: existing_codebase`).
- **Deterministic Verdict:** Returning a structured JSON response allows orchestrators and LLM agents to halt cleanly without hallucinations or erroneous retries.

