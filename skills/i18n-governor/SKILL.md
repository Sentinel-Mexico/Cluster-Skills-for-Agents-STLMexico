---
name: i18n-governor
description: "Expert internationalization (i18n) and localization auditor. Detects locale directories across workspaces (frontend, backend, api), enforces zero-hardcoded strings, verifies 100% key parity against canonical English ground truth, and translates missing keys without English fallback placeholders. Use when adding UI strings, validating translations, or expanding languages."
license: MIT
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/i18n-governor"
allowed-tools: Bash(git:*) Bash(python3:*) Read Write
---

# i18n Governor (`i18n-governor`)

Canonical operational contract for repository-wide internationalization, key parity auditing, and token-diff localization under Sentinel Mexico engineering governance.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `i18n-governor` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill i18n-governor --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## Core Governance Policies

### 1. Zero-Hardcoding Policy (Hard Invariant)
* No visible UI label, error message, toast notification, email copy, or user-facing string may be hardcoded directly inside templates, components, or source files (`.tsx`, `.vue`, `.html`, `.py`, `.go`).
* All user-facing text must strictly resolve dynamically via dictionary keys in the appropriate environment locale directory (e.g., `t('auth.login.submit')`).

### 2. Strict Prohibition of Untranslated English Fallbacks
* Foreign locale files (`es.json`, `fr.json`, `de.json`, `pt.json`, etc.) must **never** contain raw English placeholder copies as provisional stand-ins.
* Any untranslated string identical to canonical English is rejected by audit unless specifically permitted under the Whitelist Standard.

### 3. Universal Whitelist Standards (Exempt Identifiers)
The following terms are whitelisted and exempt from localized translation:
* **Protocols & Technical Acronyms:** `HTTP`, `HTTPS`, `WebRTC`, `REST`, `GraphQL`, `UUID`, `IP`, `TCP`, `UDP`, `JSON`, `YAML`, `XML`, `SQL`, `HTML`, `CSS`, `JWT`, `API`, `SDK`, `CLI`.
* **Registered Trademarks & Brand Names:** `Sentinel Mexico`, `GitHub`, `Docker`, `Kubernetes`, `Node.js`, `Python`, `Linux`, `PostgreSQL`, `Redis`.

---

## Execution Flow

```
[Trigger i18n-governor]
          │
          ▼
[Phase 1: 100% Parity Audit]
python3 scripts/i18n_manager.py --audit
          │
          ├── status == "synced" ──► [EXIT] (Full parity confirmed)
          │
          └── status == "missing_keys"
                    │
                    ▼
          [Phase 2: Token-Diff Extraction & Translation]
          python3 scripts/i18n_manager.py --get-diff --env <workspace> --target <lang>
          (Translate ONLY the extracted micro-payload preserving variables)
                    │
                    ▼
          [Phase 3: Deterministic Patch Injection & Verification]
          python3 scripts/i18n_manager.py --apply-patch '<JSON>' --env <workspace> --target <lang>
          python3 scripts/i18n_manager.py --audit (Confirm 0 missing keys)
```

---

### Phase 1: 100% Parity Audit (Zero-Context Ingestion)

Execute the deterministic auditor to discover translation directories and verify key symmetry without loading large dictionary files into LLM context:

```bash
python3 scripts/i18n_manager.py --audit
```

#### Expected Verdicts:
1. **Fully Synchronized (`status: "synced"`, Exit Code 0):**
   - 100% key parity verified across all domains. No action required.
2. **Missing Keys Detected (`status: "missing_keys"`, Exit Code 1):**
   - Emits structured report detailing affected workspaces and missing key identifiers. Proceed to Phase 2.

---

### Phase 2: Token-Diff Extraction & Translation

Extract **only** the missing keys for the targeted domain and language, avoiding redundant processing of already-translated keys:

```bash
python3 scripts/i18n_manager.py --get-diff --env <workspace> --target <target_lang>
```

Sample Diff Output:
```json
{
  "status": "ok",
  "domain": "frontend::locale",
  "target": "es",
  "target_file": "frontend/locale/es.json",
  "missing_count": 2,
  "diff": {
    "dashboard.metrics.total_users": "Total Active Users: {count}",
    "dashboard.actions.export": "Export CSV Report"
  }
}
```

#### Translation Invariants:
* Translate each value contextually and idiomatically into the target language.
* Preserve interpolation tokens and placeholders verbatim (e.g., `{count}`, `{{username}}`, `%s`).

---

### Phase 3: Deterministic Patch Injection & Verification

Inject the localized patch payload into the destination dictionary:

```bash
python3 scripts/i18n_manager.py --apply-patch '{
  "dashboard.metrics.total_users": "Total de Usuarios Activos: {count}",
  "dashboard.actions.export": "Exportar Reporte CSV"
}' --env <workspace> --target <target_lang>
```

#### Verification Gate:
Re-run the audit engine to confirm zero missing keys and 100% parity:

```bash
python3 scripts/i18n_manager.py --audit
```

---

## Token Economy Guardrails

1. **Never Load Full Dictionaries:** Do not read or write raw `en.json` or `es.json` in prompt context when auditing or fixing missing translations. Always use `--get-diff` and `--apply-patch`.
2. **Domain Context Lock:** Keep monorepo domains isolated (`frontend::locale`, `backend::locale`, `api::locale`). Never mix frontend UI copy with backend error codes.
3. **Reference on Demand:** Consult `references/REFERENCE.md` for complete path detection matrices and monorepo domain separation principles.
