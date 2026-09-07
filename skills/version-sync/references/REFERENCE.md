# Technical Reference: Universal Version Detection Patterns

This reference document catalogs the contextual regular expressions and structural formats scanned by `version-sync` across Sentinel Mexico repositories.

---

## 1. Supported Universal Detection Patterns

Unlike rigid tools that only inspect `package.json`, `version-sync` scans source code, visual components, config files, and documentation.

### 1.1 Configuration Manifests & Serialized Dictionaries
Supported file types: `.json`, `.toml`, `.yaml`, `.yml`

* **JSON Declarations:**
  `"version": "1.2.0"`, `"app_version": "1.2.0"`
* **TOML Manifests (`Cargo.toml`, `pyproject.toml`):**
  `version = "1.2.0"`
* **YAML Declarations (`pubspec.yaml`, `helm.yaml`, `config.yml`):**
  `version: "1.2.0"`, `version: 1.2.0`

---

### 1.2 Source Code Variables & Exported Constants
Supported file types: `.ts`, `.js`, `.py`, `.go`, `.rs`, `.php`, `.rb`, `.cs`, `.java`

* **TypeScript / JavaScript:**
  `export const APP_VERSION = "1.2.0";`
  `export const version = "1.2.0";`
  `const appVersion = "1.2.0";`
* **Python:**
  `__version__ = "1.2.0"`
  `VERSION = "1.2.0"`
* **Go / Rust:**
  `const Version = "1.2.0"`
  `pub const VERSION: &str = "1.2.0";`

---

### 1.3 UI Components, Footers & Templates
Supported file types: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.blade.php`

* **HTML & JSX Tags:**
  `<span>v1.2.0</span>`
  `<footer>Version: 1.2.0</footer>`
  `<small>App v1.2.0</small>`
  `<strong>Release: 1.2.0</strong>`
* **Template Interpolation:**
  `App v1.2.0`, `Version 1.2.0`

---

### 1.4 Badges & Living Documentation
Supported file types: `.md`, `.markdown`, `.rst`

* **Shields.io Markdown Badges:**
  `[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](version.txt)`
  `version-1.2.0-blue.svg`
* **Standalone Text Authorities:**
  `version.txt` (exact single-line match)
* **Skill Metadata Headers:**
  `version: "1.2.0"`

---

## 2. Directory Crawling Boundaries

The engine scans the entire tree while safely ignoring:
- Dependency vendors (`node_modules/`, `vendor/`, `.venv/`, `env/`)
- Build and compilation outputs (`dist/`, `build/`, `out/`, `.next/`, `.turbo/`)
- Test coverage reports (`coverage/`)
- Git internals (`.git/`)
- Agent caches (`.agent/`, `.agents/`)
- Historical changelogs (`changelog.md`, `changelog-dev.md` are protected from historical corruption)
- Binary media formats (images, videos, fonts, compressed archives)
