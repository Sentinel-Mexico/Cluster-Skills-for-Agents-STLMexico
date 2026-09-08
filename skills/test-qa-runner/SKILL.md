---
name: test-qa-runner
description: "Automated test executor and pre-commit regression gate. Auto-detects project test frameworks (pytest, npm test, cargo test), isolates failure stack traces into minimal token diagnostics, and enforces build integrity. Mandatory gate before invoking semver-governor or git-push-governor."
license: MIT
compatibility: Universal (Python 3.10+, Node.js, Git CLI)
metadata:
  author: "Sentinel Mexico"
  version: "1.0.0"
  repository: "https://github.com/Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
  skill-origin: "skills/test-qa-runner"
allowed-tools: Bash(python3:*) Bash(npm:*) Bash(pnpm:*) Bash(pytest:*) Read Write
---

# Test & QA Runner (`test-qa-runner`)

Canonical operational contract for automated functional testing, linter validation, and pre-commit regression gating under Sentinel Mexico engineering governance and the `agentskills.io` standard.

---

## Stage 0: Version Freshness Gate (Optional Update)
Before executing procedural logic, run:
```bash
python3 scripts/check_update.py
```

If the script returns `update_available: true`, halt execution and prompt the user:
> "⚠️ Se detectó una nueva versión de la skill `test-qa-runner` (v<latest_version> disponible, v<current_version> instalada). ¿Deseas actualizar antes de continuar? [S/N]"

If the user responds 'S' (Yes):
- If installed via symlink: run `git pull` in the cluster repository.
- If installed as standalone/copy: execute:
  `npx skills add Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico --skill test-qa-runner --agent <active-agent> --force`
If the user responds 'N' (No), proceed immediately to Stage 1.

---

## 1. Pre-Commit Quality Gate (Inviolable Invariant)

> [!CRITICAL]
> **Strict Lifecycle Precondition Gate:**
> Neither `semver-governor` nor `git-push-governor` may be executed if `test-qa-runner` reports a failure status.
>
> - **Inviolable Invariant:** Code versioning and remote repository synchronization are strictly conditional upon passing all configured functional tests and linters.
> - **Failure Protocol:** If `qa_status == "failed"`, the agent **MUST** halt any push/release operations, inspect the minimal `diagnostics` block, fix the root cause in the affected source code, and re-run `test-qa-runner` until obtaining `passed`.

---

## 2. Procedural Execution: 3-Phase Regression Pipeline

```
[Task / Code Completed]
          │
          ▼
[Phase 1: Deterministic Test Execution]
python3 scripts/qa_runner.py --run
          │
          ├── qa_status == "failed"
          │         │
          │         ▼
          │   [Phase 2: Token-Efficient Triage]
          │   Analyze compact diagnostics:
          │   - Failed assertion / error message
          │   - File and exact line number
          │   Apply targeted surgical fixes
          │         │
          │         └──► Re-run Phase 1 (Loop until passed)
          │
          └── qa_status == "passed" (or no_tests_configured)
                    │
                    ▼
              [Phase 3: Pipeline Authorization]
              Proceed to semver-governor & git-push-governor
```

---

## 3. Operational Phases

### Phase 1: Test Suite Execution

Execute the deterministic QA runner over the active workspace:

```bash
python3 scripts/qa_runner.py --run
```

*To include project linters in the evaluation:*
```bash
python3 scripts/qa_runner.py --run --lint
```

#### Expected JSON Output (Success):
```json
{
  "qa_status": "passed",
  "total_tests": 42,
  "duration_seconds": 1.45,
  "runner": "pytest -q --tb=short"
}
```

*When no test runner is configured, the script outputs exit code 0:*
```json
{
  "status": "no_tests_configured",
  "qa_status": "passed",
  "total_tests": 0,
  "duration_seconds": 0.0,
  "message": "No test runner configured in repository manifests."
}
```

---

### Phase 2: Token-Efficient Failure Triage

If tests fail, `qa_runner.py` emits exit code 1 with pruned, token-efficient diagnostics:

#### Expected JSON Output (Failure):
```json
{
  "qa_status": "failed",
  "stage": "test",
  "failed_count": 1,
  "duration_seconds": 0.82,
  "runner": "npm test",
  "diagnostics": [
    {
      "test": "authService.verifyToken",
      "file": "src/services/auth.test.ts:48",
      "error": "Expected: true | Received: false"
    }
  ]
}
```

**Agent Triage Rules:**
1. **Never Re-run Tests with Raw Output Flags:** Do not run verbose flags like `npm test -- --verbose` or `pytest -vvv` which saturate context window tokens.
2. **Direct Code Remediation:** Open the exact file and line cited in `diagnostics[i].file` and resolve the discrepancy highlighted in `error`.
3. **Loop Until Passed:** Re-execute `python3 scripts/qa_runner.py --run`.

---

### Phase 3: Pipeline Authorization

Only when `qa_status` evaluates to `"passed"`:
1. Authorization is formally granted to proceed with SemVer calculation (`semver-governor`).
2. Version strings can be propagated across manifests and badges (`version-sync`).
3. Changes may be committed and pushed to remote origin (`git-push-governor`).

---

## 4. Guardrails & Token Optimization

1. **Deterministic Auto-Detection:** The runner identifies test frameworks (Node.js/TS, Python pytest/unittest, Rust cargo test, Go test) automatically from project manifests.
2. **Strict Stack Trace Pruning:** Raw console dumps are filtered to extract only the failed test title, exact location (`file:line`), and the expected vs. received diff, capped at 5 failures.
3. **Reference Manual:** For complete ecosystem framework hierarchies and log-reduction patterns, consult `references/REFERENCE.md`.
