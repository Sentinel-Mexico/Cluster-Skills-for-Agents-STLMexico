#!/usr/bin/env python3
"""
==============================================================================
Sentinel Mexico · Deterministic QA & Test Runner (test-qa-runner)
Standard: agentskills.io
Specification: Pre-commit regression gate, framework auto-detection, and token-efficient triage
==============================================================================
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_repo_root(start_dir: Optional[str] = None) -> Path:
    current = Path(start_dir or os.getcwd()).resolve()
    while current != current.parent:
        if (
            (current / ".git").exists()
            or (current / "package.json").exists()
            or (current / "version.txt").exists()
            or (current / "pyproject.toml").exists()
            or (current / "Cargo.toml").exists()
            or (current / "go.mod").exists()
        ):
            return current
        current = current.parent
    return Path(os.getcwd()).resolve()


def detect_test_runner(repo_root: Path) -> Optional[List[str]]:
    # 1. Node.js / TypeScript (package.json)
    pkg_json_path = repo_root / "package.json"
    if pkg_json_path.exists():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as fh:
                pkg = json.load(fh)
            scripts = pkg.get("scripts", {})
            if "test" in scripts and str(scripts["test"]).strip():
                test_cmd = scripts["test"].strip()
                # Ignore dummy default "echo \"Error: no test specified\" && exit 1"
                if "no test specified" not in test_cmd:
                    if (repo_root / "pnpm-lock.yaml").exists():
                        return ["pnpm", "test"]
                    if (repo_root / "yarn.lock").exists():
                        return ["yarn", "test"]
                    if (repo_root / "bun.lockb").exists() or (repo_root / "bun.lock").exists():
                        return ["bun", "test"]
                    return ["npm", "test"]
        except Exception:
            pass

    # 2. Python (pytest, unittest)
    has_pytest_config = (
        (repo_root / "pytest.ini").exists()
        or (repo_root / "setup.cfg").exists()
        or (repo_root / "pyproject.toml").exists()
    )
    has_test_files = False
    for pattern in ["test_*.py", "*_test.py", "tests"]:
        if list(repo_root.glob(pattern)) or list((repo_root / "tests").glob("test_*.py") if (repo_root / "tests").is_dir() else []):
            has_test_files = True
            break

    if has_pytest_config or has_test_files:
        import shutil
        if shutil.which("pytest"):
            return ["pytest", "-q", "--tb=short"]
        start_dir = "tests" if (repo_root / "tests").is_dir() else "."
        return ["python3", "-m", "unittest", "discover", "-s", start_dir, "-p", "test_*.py"]

    # 3. Rust (Cargo.toml)
    if (repo_root / "Cargo.toml").exists():
        return ["cargo", "test"]

    # 4. Go (go.mod or *.go)
    if (repo_root / "go.mod").exists():
        return ["go", "test", "./..."]

    return None


def detect_linter(repo_root: Path) -> Optional[List[str]]:
    pkg_json_path = repo_root / "package.json"
    if pkg_json_path.exists():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as fh:
                pkg = json.load(fh)
            scripts = pkg.get("scripts", {})
            if "lint" in scripts and str(scripts["lint"]).strip():
                if (repo_root / "pnpm-lock.yaml").exists():
                    return ["pnpm", "run", "lint"]
                if (repo_root / "yarn.lock").exists():
                    return ["yarn", "lint"]
                return ["npm", "run", "lint"]
        except Exception:
            pass

    if (repo_root / "pyproject.toml").exists() or (repo_root / ".ruff.toml").exists():
        return ["ruff", "check", "."]

    return None


def parse_pass_count(output: str) -> int:
    # Pytest / Jest / Vitest: "12 passed"
    m = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Python unittest: "Ran 12 tests in 0.05s"
    m = re.search(r"Ran (\d+) tests?", output, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Mocha: "5 passing (120ms)"
    m = re.search(r"(\d+)\s+passing", output, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Cargo: "test result: ok. 4 passed;"
    m = re.search(r"test result:\s*ok\.\s*(\d+)\s+passed", output, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Go: count of "--- PASS:"
    go_passes = len(re.findall(r"---\s*PASS:", output))
    if go_passes > 0:
        return go_passes

    return 1


def parse_failure_diagnostics(output: str) -> List[Dict[str, str]]:
    diagnostics: List[Dict[str, str]] = []

    # 1. Pytest style failures
    pytest_blocks = re.findall(
        r"_{5,}\s*([^\n_]+)\s*_{5,}\n([\s\S]*?)(?=\n_{5,}|\n={5,}|$)", output
    )
    if pytest_blocks:
        for name, body in pytest_blocks:
            test_name = name.strip()
            loc_match = re.search(r"([a-zA-Z0-9_\-/\\]+\.py):(\d+):", body)
            file_loc = f"{loc_match.group(1)}:{loc_match.group(2)}" if loc_match else "unknown"
            err_lines = [l.strip() for l in body.splitlines() if l.strip().startswith("E ") or "AssertionError" in l or "Error:" in l]
            error_msg = " | ".join(err_lines[:3]) if err_lines else "Assertion failed"
            diagnostics.append({
                "test": test_name,
                "file": file_loc,
                "error": error_msg[:250],
            })
            if len(diagnostics) >= 5:
                return diagnostics

    # 1b. Python unittest failures
    unittest_matches = re.findall(
        r"(?:FAIL|ERROR):\s*([^\n]+)\n-+\n([\s\S]*?)(?=\n(?:FAIL|ERROR):|\n-{50,}|\nRan|\Z)", output
    )
    if unittest_matches:
        for name, body in unittest_matches:
            test_name = name.strip()
            loc_match = re.search(r'File "([^"]+)", line (\d+)', body)
            file_loc = f"{loc_match.group(1)}:{loc_match.group(2)}" if loc_match else "unknown"
            err_lines = [l.strip() for l in body.splitlines() if "AssertionError" in l or "Error:" in l or "Exception:" in l]
            error_msg = " | ".join(err_lines[:2]) if err_lines else body.strip().splitlines()[-1]
            diagnostics.append({
                "test": test_name,
                "file": file_loc,
                "error": error_msg[:250],
            })
            if len(diagnostics) >= 5:
                return diagnostics

    # 2. Jest / Vitest style failures
    # e.g.:
    # ● Math utils › calculates sum correctly
    #   expect(received).toBe(expected)
    #   Expected: 4
    #   Received: 5
    #   at Object.<anonymous> (src/math.test.ts:18:22)
    jest_blocks = re.findall(
        r"(?:●|FAIL)\s+([^\n]+)\n([\s\S]*?)(?=\n(?:●|FAIL)|Test Suites:|$)", output
    )
    if jest_blocks:
        for name, body in jest_blocks:
            test_name = name.strip()
            loc_match = re.search(r"at\s+.*?\((.*?:\d+:\d+)\)|at\s+(.*?:\d+:\d+)|❯\s+(.*?:\d+:\d+)", body)
            file_loc = "unknown"
            if loc_match:
                file_loc = loc_match.group(1) or loc_match.group(2) or loc_match.group(3)
            diff_match = re.findall(r"(?:Expected:.*|Received:.*|Error:.*)", body)
            error_msg = " | ".join(diff_match[:3]) if diff_match else body.strip().splitlines()[-1]
            diagnostics.append({
                "test": test_name,
                "file": file_loc,
                "error": error_msg[:250],
            })
            if len(diagnostics) >= 5:
                return diagnostics

    # 3. Cargo test failures
    # e.g.:
    # ---- tests::test_add stdout ----
    # thread 'tests::test_add' panicked at 'assertion failed: `(left == right)` ...', tests/test.rs:10:5
    cargo_blocks = re.findall(
        r"----\s+([^\s]+)\s+stdout\s+----\n([\s\S]*?)(?=\n----\s+|$)", output
    )
    if cargo_blocks:
        for name, body in cargo_blocks:
            test_name = name.strip()
            loc_match = re.search(r"panicked at.*?, (.*?:\d+:\d+)", body)
            file_loc = loc_match.group(1) if loc_match else "unknown"
            err_match = re.search(r"panicked at '(.*?)'", body)
            error_msg = err_match.group(1) if err_match else "Test panicked"
            diagnostics.append({
                "test": test_name,
                "file": file_loc,
                "error": error_msg[:250],
            })
            if len(diagnostics) >= 5:
                return diagnostics

    # 4. Go test failures
    # e.g.:
    # --- FAIL: TestAdd (0.00s)
    #     add_test.go:12: Add(2, 2) = 5; want 4
    go_blocks = re.findall(r"---\s*FAIL:\s*([^\s]+)\s*\([^\)]*\)\n\s*([a-zA-Z0-9_\-\.]+:\d+):\s*(.*)", output)
    if go_blocks:
        for name, loc, err in go_blocks:
            diagnostics.append({
                "test": name.strip(),
                "file": loc.strip(),
                "error": err.strip()[:250],
            })
            if len(diagnostics) >= 5:
                return diagnostics

    # 5. Generic fallback: line matching path:line: error
    if not diagnostics:
        generic_matches = re.findall(r"([a-zA-Z0-9_\-/\\]+\.[a-zA-Z0-9]+):(\d+)(?::\d+)?:?\s*(.*(?:error|fail|Error|FAIL|assert).*)$", output, re.MULTILINE)
        for fpath, line_no, msg in generic_matches[:5]:
            diagnostics.append({
                "test": "qa_assertion",
                "file": f"{fpath}:{line_no}",
                "error": msg.strip()[:250],
            })

    if not diagnostics:
        # Fallback to last non-empty line of output
        lines = [l.strip() for l in output.splitlines() if l.strip()]
        last_line = lines[-1] if lines else "Process exited with non-zero status"
        diagnostics.append({
            "test": "qa_execution",
            "file": "root",
            "error": last_line[:250],
        })

    return diagnostics[:5]


def run_qa(repo_root: Path, check_lint: bool = False) -> Tuple[int, Dict[str, Any]]:
    runner = detect_test_runner(repo_root)
    if not runner:
        return 0, {
            "status": "no_tests_configured",
            "qa_status": "passed",
            "total_tests": 0,
            "duration_seconds": 0.0,
            "message": "No test runner configured in repository manifests.",
        }

    start_time = time.time()
    cmd_str = " ".join(runner)

    try:
        proc = subprocess.run(
            runner,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180,
        )
        duration = round(time.time() - start_time, 2)
        raw_output = proc.stdout or ""

        if proc.returncode == 0:
            # Check linter if requested
            if check_lint:
                linter = detect_linter(repo_root)
                if linter:
                    lint_proc = subprocess.run(
                        linter,
                        cwd=str(repo_root),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=120,
                    )
                    if lint_proc.returncode != 0:
                        diag = parse_failure_diagnostics(lint_proc.stdout or "")
                        return 1, {
                            "qa_status": "failed",
                            "stage": "lint",
                            "failed_count": len(diag),
                            "duration_seconds": round(time.time() - start_time, 2),
                            "runner": " ".join(linter),
                            "diagnostics": diag,
                        }

            total_tests = parse_pass_count(raw_output)
            return 0, {
                "qa_status": "passed",
                "total_tests": total_tests,
                "duration_seconds": duration,
                "runner": cmd_str,
            }
        else:
            diagnostics = parse_failure_diagnostics(raw_output)
            return 1, {
                "qa_status": "failed",
                "stage": "test",
                "failed_count": len(diagnostics),
                "duration_seconds": duration,
                "runner": cmd_str,
                "diagnostics": diagnostics,
            }

    except subprocess.TimeoutExpired:
        return 1, {
            "qa_status": "failed",
            "stage": "timeout",
            "failed_count": 1,
            "duration_seconds": 180.0,
            "runner": cmd_str,
            "diagnostics": [
                {
                    "test": "timeout_gate",
                    "file": "test_suite",
                    "error": "Test suite execution exceeded 180 seconds timeout.",
                }
            ],
        }
    except Exception as exc:
        return 1, {
            "qa_status": "failed",
            "stage": "execution_error",
            "failed_count": 1,
            "duration_seconds": round(time.time() - start_time, 2),
            "runner": cmd_str,
            "diagnostics": [
                {
                    "test": "runtime_error",
                    "file": "system",
                    "error": str(exc),
                }
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic QA and test runner with token-optimized failure isolation."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the detected project test suite and optional linter.",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Include configured project linter in QA evaluation.",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target workspace root directory.",
    )

    args = parser.parse_args()

    repo_root = Path(args.target).resolve() if args.target else find_repo_root()
    exit_code, result = run_qa(repo_root, check_lint=args.lint)

    print(json.dumps(result, indent=2))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
