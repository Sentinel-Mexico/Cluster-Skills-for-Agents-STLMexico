# Security & Performance Optimizer Reference Manual (`sec-optimizer`)

Standard: `agentskills.io`  
Author: Sentinel Mexico  
Governance: `Cluster-Skills-for-Agents-STLMexico`  

---

## 1. CWE & OWASP Taxonomic Mapping

Every security finding identified by `security_auditor.py` maps to recognized industry standards:

| Rule Identifier | CWE Standard | OWASP Top 10 (2021) | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`hardcoded-secret`** | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | A07:2021 - Identification & Auth Failures | HIGH | Hardcoded API keys, JWT tokens, and passwords in source files. |
| **`hardcoded-private-key`** | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | A07:2021 - Identification & Auth Failures | CRITICAL | Plaintext RSA, EC, or OpenSSH cryptographic private keys. |
| **`hardcoded-aws-credential`** | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) | A07:2021 - Identification & Auth Failures | CRITICAL | AWS Access Key IDs (`AKIA...`, `ASIA...`) in code. |
| **`unsafe-eval`** | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) | A03:2021 - Injection | CRITICAL | Direct invocation of `eval()` allowing arbitrary code execution. |
| **`command-injection-exec`** | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | A03:2021 - Injection | HIGH | Unsanitized shell execution via `child_process.exec()`. |
| **`python-os-system`** | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | A03:2021 - Injection | HIGH | Use of `os.system()` lacking shell argument isolation. |
| **`python-shell-true`** | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | A03:2021 - Injection | HIGH | Python `subprocess` spawned with `shell=True`. |
| **`dynamic-sql-concatenation`** | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | A03:2021 - Injection | CRITICAL | SQL queries constructed with string concatenation/interpolation. |
| **`xss-dangerously-set-inner-html`** | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | A03:2021 - Injection | HIGH | Direct DOM HTML injection bypassing framework sanitization. |
| **`xss-dom-innerhtml`** | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | A03:2021 - Injection | HIGH | Raw assignment to `innerHTML` or `outerHTML`. |
| **`xss-vue-v-html`** | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | A03:2021 - Injection | MEDIUM | Vue `v-html` binding raw untrusted markup. |

---

## 2. Resource Optimization & Aesthetic Preservation Invariants

Sentinel Mexico engineering principles strictly reject the "brute-force" optimization pattern of deleting CSS design tokens to reduce load. Visual excellence is a first-class citizen.

### The Browser Rendering Pipeline

```
[JavaScript] ──► [Style Calc] ──► [Layout / Reflow] ──► [Paint] ──► [Composite]
                                         ▲
                                 Heavy CPU Bottleneck!
```

### Layout Triggers vs. Composite Optimization

When optimizing animations, never eliminate movement or transitions. Migrate CSS properties from Layout to Composite:

| Destructive Approach (Prohibited) | Optimized Composite Alternative (Mandatory) |
| :--- | :--- |
| Changing `top`, `left`, `right`, `bottom` | Use `transform: translate3d(x, y, 0);` |
| Changing `width` and `height` in transitions | Use `transform: scale(x, y);` |
| Toggling `visibility` or `display` in loops | Use `opacity` with `pointer-events: none` |
| Removing `backdrop-filter: blur(...)` | Isolate layer via `will-change: transform` or assign `contain: paint;` |
| Removing box shadows or ambient glows | Use pre-baked pseudo-element `:after` opacity transitions |

### Timing & Thread Invariants

1. **`requestAnimationFrame` over `setInterval`:**
   - Sub-100ms intervals in JavaScript monopolize the event loop and desynchronize from the display refresh rate (60Hz / 120Hz).
   - Visual animations must always bind to `window.requestAnimationFrame()`.
2. **Non-Blocking File I/O:**
   - Synchronous operations (`fs.readFileSync`) block Node.js worker threads completely.
   - Production web services must strictly employ `fs.promises.readFile()` or non-blocking streaming.
3. **Algorithmic Lookups:**
   - Replace quadratic array scans (`array.find()` inside `array.forEach()`) with pre-indexed `Map` or `Set` structures to achieve $O(N)$ execution.

---

## 3. Human-in-the-Loop Gate Protocol

Autonomous code agents must never modify application source files without explicit human authorization when conducting security or performance remediations.

### Phase Gate States

```
[Phase 1: Scan] ──► [Phase 2: Human Gate (Read-Only)]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     User Authorizes                       User Cancels
            │                                     │
            ▼                                     ▼
[Phase 3: Surgical Patching]               [Abort Workflow]
            │                              No files altered
            ▼
[Phase 4: Post-Verification]
```

### Response Lexicon

The human operator controls execution with three explicit inputs:
1. **`APROBAR TODO`:** Authorizes surgical application of all identified remediations in the action plan.
2. **`APROBAR <ID_LIST>`:** (e.g. `APROBAR SEC-1, OPT-2`) Restricts modification strictly to the specified IDs. All unlisted findings remain untouched.
3. **`CANCELAR`:** Immediately terminates the remediation workflow without modifying any file.
