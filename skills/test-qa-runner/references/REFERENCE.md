# Test & QA Runner Reference Manual (`test-qa-runner`)

Standard: `agentskills.io`  
Author: Sentinel Mexico  
Governance: `Cluster-Skills-for-Agents-STLMexico`  

---

## 1. Test Framework Auto-Detection Hierarchy

The `qa_runner.py` deterministic engine resolves execution commands in priority order by inspecting configuration manifests:

### Language & Runtime Detection Matrix

| Ecosystem | Manifest / Indicator | Priority Runner Command | Fallback Runner Command |
| :--- | :--- | :--- | :--- |
| **Node.js / TS** | `package.json` (`scripts.test`) | `pnpm test` (if `pnpm-lock.yaml`)<br>`yarn test` (if `yarn.lock`)<br>`bun test` (if `bun.lockb`) | `npm test` |
| **Node.js Linters** | `package.json` (`scripts.lint`) | `pnpm run lint` / `yarn lint` | `npm run lint` |
| **Python** | `pytest.ini`, `setup.cfg`, `pyproject.toml`, `tests/` | `pytest -q --tb=short` (if `pytest` installed) | `python3 -m unittest discover -s tests -p "test_*.py"` |
| **Python Linters** | `pyproject.toml`, `.ruff.toml`, `setup.cfg` | `ruff check .` | `flake8 .` |
| **Rust** | `Cargo.toml` | `cargo test` | — |
| **Go** | `go.mod`, `*_test.go` | `go test ./...` | — |

---

## 2. Token Reduction Pattern (Anti-Context Bloat)

Conventional test runners output thousands of lines containing environment details, memory addresses, dependency call stacks, and ANSI color codes. Dumping these raw logs into an LLM context causes:
- Immediate token exhaustion.
- Lost-in-the-middle degradation where the LLM misses the actual assertion cause.
- Hallucinated fixes targeting internal library code rather than the user's project file.

### Raw Log vs. Pruned Diagnostic Comparison

```
[Raw Jest Output: ~3,500 Tokens]
FAIL src/auth/jwt.test.ts
  ● Auth Suite › verifies token expiration
    TypeError: Cannot read properties of undefined (reading 'exp')
      at verifyToken (src/auth/jwt.ts:42:18)
      at Object.<anonymous> (src/auth/jwt.test.ts:25:12)
      at Promise.then.completed (node_modules/jest-circus/...:300:15)
      ... 45 lines of node_modules stack trace ...

                   │
                   ▼ (Regex Isolation & Pruning)
                   
[Pruned Token-Optimized Diagnostic: ~35 Tokens]
{
  "test": "Auth Suite › verifies token expiration",
  "file": "src/auth/jwt.test.ts:25",
  "error": "TypeError: Cannot read properties of undefined (reading 'exp')"
}
```

### Extraction Specifications
1. **Assertion Boundary:** Isolates only the expected vs. received diff or explicit assertion statement.
2. **First-Party File Localization:** Resolves the first line inside the repository tree, filtering out foreign framework stack frames (`node_modules`, `site-packages`, internal standard library).
3. **5-Failure Ceiling:** Truncates failure lists at 5 entries. Fixing the top failure typically resolves cascading downstream failures.

---

## 3. The Pre-Commit Quality Gate in the Agent Lifecycle

Under Sentinel Mexico governance, the agent's task lifecycle flows linearly through strict verification barriers:

```
┌────────────────────────────────────────────────────────┐
│ 1. Code-as-Skill Development & Implementation          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. PRE-COMMIT QUALITY GATE (test-qa-runner)            │
│    Runs test suite & linters                           │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
          [qa: failed]                [qa: passed]
               │                           │
               ▼                           ▼
┌──────────────────────────────┐ ┌───────────────────────────────────────┐
│ Fix code via compact         │ │ 3. SemVer Governance (semver-governor)│
│ diagnostic & retry gate      │ └───────────────────┬───────────────────┘
└──────────────────────────────┘                     │
                                                     ▼
                                 ┌───────────────────────────────────────┐
                                 │ 4. Push Governance (git-push-governor)│
                                 └───────────────────────────────────────┘
```

The gate guarantees that broken builds, failing assertions, or unformatted code cannot be packaged into release versions or pushed to remote branches.
