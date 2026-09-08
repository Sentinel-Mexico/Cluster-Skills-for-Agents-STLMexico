---
name: sec-optimizer
description: "Specialized code security auditor and performance optimizer. Scans codebase deterministically for security vulnerabilities (injection, hardcoded secrets, unsafe deserialization) and runtime inefficiencies (blocking I/O, memory leaks). Produces a formal remediation action plan and waits for explicit user approval before applying patches. Preserves UI design and visual aesthetics. Use when auditing code quality, hardening security, or optimizing resource consumption."
license: MIT
compatibility: Universal (Python 3.10+, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/sec-optimizer"
allowed-tools: Bash(python3:*) Read Write
---

# Security & Performance Optimizer (`sec-optimizer`)

Canonical operational contract for automated static security vulnerability auditing, runtime resource optimization, and Human-in-the-Loop remediation under Sentinel Mexico engineering governance and the `agentskills.io` standard.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `sec-optimizer` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill sec-optimizer --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## 1. Aesthetic Protection Invariant (UX Guardrail)

> [!CRITICAL]
> **Aesthetic Integrity Guarantee:**
> Security hardening and runtime optimization are critical requirements, but **NEVER at the expense of degrading interface aesthetics, key animations, typography, or visual quality**.
>
> 1. **Prohibition of Degradation:** It is strictly prohibited to strip modern design tokens (e.g., backdrop filters, glassmorphism, soft volumetric shadows, micro-interactions, smooth bezier transitions) under the pretext of superficial optimization.
> 2. **Hardware Acceleration Alternative:** If an animation or visual component causes measurable CPU/GPU layout thrashing or memory retention, the agent **MUST** preserve visual fidelity by transitioning from layout-triggering properties (`width`, `height`, `top`, `left`) to composite-only hardware-accelerated transforms (`transform`, `opacity`, `will-change`).

---

## 2. Procedural Execution: Plan-Validate-Execute

```
[Auditing Triggered]
         │
         ▼
[Phase 1: Deterministic Scan]
python3 scripts/security_auditor.py --scan
         │
         ▼
[Phase 2: Remediation Plan & Human Gate] ◄─── STRICT READ-ONLY MODE
Format structured finding table:
| ID | Tipo | Severidad / Impacto | Archivo:Línea | Diagnóstico Breve | Solución Propuesta (Respetando Estética) |
Prompt user for explicit authorization:
"¿Deseas autorizar la aplicación de estas mejoras? Responde 'APROBAR TODO', indica IDs específicos (ej. 'APROBAR SEC-1, OPT-1') o 'CANCELAR'."
         │
         ├── User: "CANCELAR" ──► [ABORT] (No modifications made)
         │
         └── User: "APROBAR TODO" or specific IDs (e.g., SEC-1, OPT-2)
                   │
                   ▼
         [Phase 3: Controlled Surgical Patching]
         Apply minimal diffs for approved IDs only
                   │
                   ▼
         [Phase 4: Post-Remediation Verification]
         python3 scripts/security_auditor.py --scan
```

---

## 3. Operational Phases

### Phase 1: Deterministic Static Scan (Token-Efficient)

Execute the security and performance auditor script over the codebase:

```bash
python3 scripts/security_auditor.py --scan
```

*Optional scoped scanning by category or directory:*
```bash
python3 scripts/security_auditor.py --scan --category security
python3 scripts/security_auditor.py --scan --target src/
```

Expected JSON Output:
```json
{
  "status": "audited",
  "summary": {
    "total_files_scanned": 84,
    "security_issues": 2,
    "performance_issues": 1,
    "total_issues": 3
  },
  "findings": [
    {
      "id": "SEC-1",
      "category": "security",
      "rule_id": "dynamic-sql-concatenation",
      "cwe": "CWE-89",
      "owasp": "A03:2021-Injection",
      "severity": "CRITICAL",
      "file": "src/db/users.ts",
      "line": 42,
      "snippet": "db.query(\"SELECT * FROM users WHERE id = \" + id)",
      "diagnosis": "Dynamic SQL query formed via string concatenation.",
      "remediation": "Use parameterized queries ($1) with prepared statements."
    }
  ]
}
```

---

### Phase 2: Remediation Action Plan & Human-in-the-Loop Gate

> [!IMPORTANT]
> **READ-ONLY PHASE:** The agent is strictly prohibited from writing, editing, or deleting any project files during this phase.

1. Synthesize the findings into a clear, scannable Markdown table:

```markdown
### Plan de Remediación de Seguridad y Rendimiento

| ID | Tipo | Severidad / Impacto | Archivo:Línea | Diagnóstico Breve | Solución Propuesta (Respetando Estética) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SEC-1** | Seguridad | CRITICAL (CWE-89) | `src/db/users.ts:42` | Concatenación dinámica en SQL query | Parametrizar con `$1` usando `db.query(sql, [id])` |
| **OPT-1** | Rendimiento | MEDIUM (CWE-400) | `src/ui/banner.tsx:18` | Intervalo de 20ms en animación visual | Reemplazar por `requestAnimationFrame` manteniendo fluidez idéntica |
```

2. Present the mandatory interactive inquiry to the user:
```text
¿Deseas autorizar la aplicación de estas mejoras? Responde 'APROBAR TODO', indica IDs específicos (ej. 'APROBAR SEC-1, OPT-1') o 'CANCELAR'.
```

3. Halt execution and await the user's explicit instructions. Do not assume or extrapolate approval.

---

### Phase 3: Controlled Surgical Patching

Upon receiving explicit user authorization:
1. **Targeted Diffs:** Apply patches **strictly** to the authorized IDs (e.g., if user approves `SEC-1`, leave `OPT-1` unmodified).
2. **Minimal Invasiveness:** Modify only the exact lines necessary to mitigate the vulnerability or bottleneck.
3. **Preserve Surrounding Syntax & Aesthetics:** Maintain variable names, formatting standards, and visual styles.

---

### Phase 4: Post-Remediation Verification

Re-execute the deterministic auditor to confirm that the targeted vulnerabilities are resolved:

```bash
python3 scripts/security_auditor.py --scan
```

Verify that the authorized findings no longer appear in the report without introducing regressions.

---

## 4. Guardrails & Token Economy

1. **Zero Raw File Loading:** Never load entire source files into LLM context solely for vulnerability scanning. Delegate all static regex analysis to `scripts/security_auditor.py`.
2. **Strict CWE/OWASP Classification:** All reported findings must be classified with valid CWE identifiers and OWASP Top 10 categories.
3. **Architectural Reference:** For detailed CWE mappings, GPU vs. CPU rendering rules, and reflow mitigation strategies, consult `references/REFERENCE.md`.
