# Technical Reference: Universal Version Detection Patterns & Protected Targets

This reference catalogs the contextual regular expressions, file classifications, and protected targets scanned by `version-sync` across Sentinel Mexico repositories.

---

## 1. Supported Universal Detection Patterns

Unlike conventional tools that only parse `package.json`, `version-sync` recursively indexes and synchronizes all text files across every tier of the application.

### 1.1 Dedicated Plaintext Version Files & Environment Variables
* **Root Plaintext Files:** `version.txt`, `VERSION`, `.version`, `version`.
  - Replaces the exact version line or file content while preserving trailing newline.
* **Environment Files & Templates:** `.env.example`, `.env.local.example`, `.env.template`.
  - Replaces declarations such as `APP_VERSION="1.2.0"`, `VERSION=1.2.0`, `REACT_APP_VERSION="1.2.0"`.

---

### 1.2 Configuration Manifests & Serialized Dictionaries
Supported file types: `.json`, `.toml`, `.yaml`, `.yml`, `.xml`, `.ini`, `.properties`

* **JSON Declarations:**
  `"version": "1.2.0"`, `"app_version": "1.2.0"`
* **TOML Manifests (`Cargo.toml`, `pyproject.toml`):**
  `version = "1.2.0"`
* **YAML Declarations (`pubspec.yaml`, `helm.yaml`, `config.yml`):**
  `version: "1.2.0"`, `version: 1.2.0`
* **XML Project Files (`pom.xml`, `package.manifest`):**
  `<version>1.2.0</version>`
* **INI & Properties (`settings.ini`, `gradle.properties`):**
  `version=1.2.0`, `appVersion = "1.2.0"`

---

### 1.3 Source Code Constants & Exported Variables
Supported file types: `.ts`, `.js`, `.py`, `.go`, `.rs`, `.php`, `.java`, `.c`, `.cpp`, `.cs`

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
* **Java / C#:**
  `public static final String VERSION = "1.2.0";`
  `public const string Version = "1.2.0";`

---

### 1.4 Frontend UI Components, Footers & Templates
Supported file types: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.astro`, `.blade.php`

* **HTML & JSX Tags:**
  `<span>v1.2.0</span>`
  `<footer>Version: 1.2.0</footer>`
  `<small>App v1.2.0</small>`
  `<strong>Release: 1.2.0</strong>`
* **Visual Headers and Footers:**
  Replaces version strings embedded in template markup without altering tag attributes, class names, or component styling.

---

### 1.5 Badges & Living Documentation
Supported file types: `.md`, `.markdown`, `.rst`, `.txt`, `SKILL.md`

* **Shields.io Markdown Badges:**
  `[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](version.txt)`
  `version-1.2.0-blue.svg`
* **Skill Metadata Headers:**
  `version: "1.2.0"`

---

## 2. Safety Guards & Crawling Boundaries

The crawler traverses the entire workspace while strictly applying the following defensive boundaries:

1. **Size Ceiling (2 MB):** Files larger than 2 MB are automatically omitted to protect memory.
2. **Binary Guard:** Inspects the first 1024 bytes of each file for null bytes (`\x00`). Binary media (images, videos, fonts, compiled binaries) are safely skipped.
3. **Excluded Folders:** Strictly ignores:
   `node_modules/`, `.git/`, `dist/`, `build/`, `coverage/`, `.next/`, `.turbo/`, `__pycache__/`, `.agent/`, `.agents/`, `.venv/`, `env/`, `out/`.
4. **Historical Changelog Protection:** `changelog.md` and `changelog-dev.md` are protected from bulk search-and-replace to preserve chronological release archives.
