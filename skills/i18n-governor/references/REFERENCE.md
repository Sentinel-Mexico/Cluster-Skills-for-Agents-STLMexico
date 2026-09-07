# Technical Reference: i18n Governance & Domain Context Lock

This reference establishes the path detection patterns, monorepo domain isolation rules, and term whitelisting enforced by `i18n-governor` across Sentinel Mexico codebases.

---

## 1. Candidate Path Discovery Matrix

The discovery crawler recursively scans for translation directories adhering to standard web and backend frameworks:

| Candidate Folder | Common Framework / Architecture | Typical Nesting Paths |
| :--- | :--- | :--- |
| **`locale/`** | Standard Sentinel Mexico convention, Python, Go | `<env>/locale/`, `src/locale/` |
| **`locales/`** | Next.js (i18next), Vue (vue-i18n), Nuxt | `locales/`, `src/locales/`, `public/locales/` |
| **`i18n/`** | Angular, SvelteKit, Docusaurus | `src/i18n/`, `i18n/` |
| **`translations/`** | Symfony, Drupal, Django Rosetta | `translations/`, `resources/translations/` |
| **`messages/`** | Next-intl, FormatJS, Crowdin | `messages/`, `src/messages/` |
| **`lang/` / `languages/`**| Laravel, Flutter, Android | `resources/lang/`, `lib/languages/` |

### Ignored Directories (Crawling Boundaries)
The crawler strictly ignores third-party dependencies, build caches, and agent metadata:
`node_modules/`, `.git/`, `dist/`, `.next/`, `build/`, `coverage/`, `__pycache__/`, `.turbo/`, `.agent/`, `.agents/`, `.venv/`, `env/`, `out/`.

---

## 2. Domain Context Lock Architecture

### The Risk of Monorepo Cross-Pollination
In multi-package workspaces, combining all translation dictionaries into a single monolithic store creates major failure modes:
1. **Context Pollution:** Frontend agents translating UI copy may inadvertently overwrite backend error strings or database validation codes.
2. **Schema Conflicts:** A key such as `auth.unauthorized` might require an informal user prompt in frontend (`"Please log in to continue"`) but a structured machine-readable error in backend API (`"Missing Bearer authentication token"`).

### Domain Isolation Contract
The `i18n_manager.py` crawler generates a unique domain key for every discovered directory:
```text
<workspace_subsystem>::<directory_path>
```
* **Frontend Domain:** `frontend::locale` ➔ Operates only on `frontend/locale/*.json`.
* **Backend Domain:** `backend::locale` ➔ Operates only on `backend/locale/*.json`.
* **API Service Domain:** `api::src/locales` ➔ Operates only on `api/src/locales/*.json`.

During extraction (`--get-diff`) and injection (`--apply-patch`), the `--env` parameter locks execution strictly into the specified domain. Cross-domain mutations are rejected.

---

## 3. Whitelist Standards for Technical Terms & Brands

To ensure translation authenticity while preventing false positives, terms meeting specific operational criteria are exempt from localized translation:

### Protocols & Web Standards
`HTTP`, `HTTPS`, `WebRTC`, `REST`, `GraphQL`, `gRPC`, `WebSocket`, `TCP`, `UDP`, `IP`, `IPv4`, `IPv6`, `UUID`, `GUID`, `JSON`, `YAML`, `XML`, `SQL`, `HTML`, `CSS`, `JWT`, `OAuth`, `SAML`, `CORS`, `DNS`, `SSL`, `TLS`.

### Developer Tools & Runtimes
`Docker`, `Kubernetes`, `Node.js`, `Python`, `TypeScript`, `JavaScript`, `Rust`, `Go`, `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `Git`, `GitHub`, `GitLab`, `Linux`, `Nginx`.

### Organization & Brand Authorities
`Sentinel Mexico`, `Google DeepMind`, `Antigravity`, `OpenAI`, `Anthropic`, `AWS`, `Azure`, `Cloudflare`, `Vercel`.
