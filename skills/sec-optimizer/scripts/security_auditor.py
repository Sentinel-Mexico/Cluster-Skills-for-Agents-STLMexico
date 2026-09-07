#!/usr/bin/env python3
"""
==============================================================================
Sentinel Mexico · Static Security Auditor & Performance Engine (sec-optimizer)
Standard: agentskills.io
Specification: Code-as-Skill static code audit, CWE/OWASP mapping, and performance scan
==============================================================================
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB ceiling

VALID_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".go",
    ".rs",
    ".php",
    ".html",
    ".css",
    ".scss",
    ".vue",
    ".svelte",
}

IGNORED_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    ".next",
    ".turbo",
    "__pycache__",
    ".agent",
    ".agents",
    ".github",
    ".vscode",
    ".idea",
}

# False positive heuristics for secrets
PLACEHOLDER_SUBSTRINGS = [
    "example",
    "your-",
    "your_",
    "changeme",
    "placeholder",
    "process.env",
    "import.meta.env",
    "os.environ",
    "getenv",
    "todo",
    "dummy",
    "localhost",
]


def is_binary_or_oversized(filepath: Path) -> bool:
    try:
        if filepath.stat().st_size > MAX_FILE_SIZE_BYTES:
            return True
        with open(filepath, "rb") as fh:
            chunk = fh.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        return True
    return False


def find_repo_root(start_dir: Optional[str] = None) -> str:
    current = Path(start_dir or os.getcwd()).resolve()
    while current != current.parent:
        if (
            (current / ".git").exists()
            or (current / "package.json").exists()
            or (current / "version.txt").exists()
        ):
            return str(current)
        current = current.parent
    return os.getcwd()


class SecurityAuditor:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.security_counter = 0
        self.performance_counter = 0
        self.findings: List[Dict[str, Any]] = []
        self.total_scanned_files = 0

    def next_sec_id(self) -> str:
        self.security_counter += 1
        return f"SEC-{self.security_counter}"

    def next_opt_id(self) -> str:
        self.performance_counter += 1
        return f"OPT-{self.performance_counter}"

    def audit_file(self, file_path: Path) -> None:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        lines = content.splitlines()
        rel_path = str(file_path.relative_to(self.root_dir))
        ext = file_path.suffix.lower()

        # Audit line by line
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            self._check_secrets(line, idx, rel_path)
            self._check_command_injection(line, idx, rel_path, ext)
            self._check_sql_injection(line, idx, rel_path)
            self._check_xss(line, idx, rel_path, ext)
            self._check_blocking_io(line, idx, rel_path, ext)
            self._check_high_freq_interval(line, idx, rel_path, ext)

        # Multi-line checks (e.g. nested loops)
        self._check_nested_loops(lines, rel_path, ext)

    def _check_secrets(self, line: str, line_no: int, rel_path: str) -> None:
        # Cryptographic private keys
        if re.search(r"-----BEGIN\s+(?:[A-Z0-9_\-\s]+)?PRIVATE\s+KEY-----", line):
            self.findings.append({
                "id": self.next_sec_id(),
                "category": "security",
                "rule_id": "hardcoded-private-key",
                "cwe": "CWE-798",
                "owasp": "A07:2021-Identification and Authentication Failures",
                "severity": "CRITICAL",
                "file": rel_path,
                "line": line_no,
                "snippet": line.strip()[:100],
                "diagnosis": "Hardcoded cryptographic private key exposed in source code.",
                "remediation": "Remove key immediately, revoke compromised certificate/key, and load via KMS or environment variable.",
            })
            return

        # AWS Access Key ID
        aws_match = re.search(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b", line)
        if aws_match:
            self.findings.append({
                "id": self.next_sec_id(),
                "category": "security",
                "rule_id": "hardcoded-aws-credential",
                "cwe": "CWE-798",
                "owasp": "A07:2021-Identification and Authentication Failures",
                "severity": "CRITICAL",
                "file": rel_path,
                "line": line_no,
                "snippet": line.strip()[:100],
                "diagnosis": "Potential AWS Access Key ID hardcoded in source file.",
                "remediation": "Store AWS credentials securely using IAM roles or environment variables (AWS_ACCESS_KEY_ID).",
            })
            return

        # Generic credentials / API tokens
        secret_pattern = re.compile(
            r"""(?i)(?:api_key|apikey|secret_key|app_secret|client_secret|access_token|auth_token|jwt_token|password|passwd|pwd)\s*[:=]\s*["']([a-zA-Z0-9_\-\.]{12,})["']"""
        )
        match = secret_pattern.search(line)
        if match:
            val = match.group(1).lower()
            if not any(ph in val for ph in PLACEHOLDER_SUBSTRINGS):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "hardcoded-secret",
                    "cwe": "CWE-798",
                    "owasp": "A07:2021-Identification and Authentication Failures",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Plaintext secret or API credential hardcoded in source code.",
                    "remediation": "Extract secret into .env or vault provider. Do not commit credentials to version control.",
                })

    def _check_command_injection(self, line: str, line_no: int, rel_path: str, ext: str) -> None:
        # JS/TS eval
        if ext in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}:
            if re.search(r"\beval\s*\(", line):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "unsafe-eval",
                    "cwe": "CWE-94",
                    "owasp": "A03:2021-Injection",
                    "severity": "CRITICAL",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Use of 'eval()' enables arbitrary code execution.",
                    "remediation": "Refactor logic to eliminate dynamic code evaluation (use JSON.parse or strict map lookups).",
                })
            elif re.search(r"\bchild_process\.exec\s*\(", line) or re.search(r"\bexec\s*\([^)]*\+", line):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "command-injection-exec",
                    "cwe": "CWE-78",
                    "owasp": "A03:2021-Injection",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Unsanitized command execution via child_process.exec() or exec().",
                    "remediation": "Use child_process.execFile or spawn with argument arrays without invoking a subshell.",
                })

        # Python os.system / subprocess shell=True
        elif ext == ".py":
            if re.search(r"\bos\.system\s*\(", line):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "python-os-system",
                    "cwe": "CWE-78",
                    "owasp": "A03:2021-Injection",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "os.system executes commands in a system shell without argument isolation.",
                    "remediation": "Replace with subprocess.run(['cmd', 'arg1'], check=True, shell=False).",
                })
            elif re.search(r"\bsubprocess\.(?:Popen|run|call|check_output)\s*\([^)]*shell\s*=\s*True", line):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "python-shell-true",
                    "cwe": "CWE-78",
                    "owasp": "A03:2021-Injection",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "subprocess invocation with shell=True exposes command injection risk.",
                    "remediation": "Pass arguments as a sequence of strings and set shell=False.",
                })

    def _check_sql_injection(self, line: str, line_no: int, rel_path: str) -> None:
        sql_pattern = re.compile(
            r"""(?i)(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+.*?\s+(?:WHERE|SET|VALUES)\s+.*?(?:\+|f["']|\.format\(|\$\{)"""
        )
        if sql_pattern.search(line):
            self.findings.append({
                "id": self.next_sec_id(),
                "category": "security",
                "rule_id": "dynamic-sql-concatenation",
                "cwe": "CWE-89",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "file": rel_path,
                "line": line_no,
                "snippet": line.strip()[:100],
                "diagnosis": "Dynamic SQL query formed via string concatenation or interpolation.",
                "remediation": "Use parameterized queries or prepared statements ($1, ?, or ORM binding).",
            })

    def _check_xss(self, line: str, line_no: int, rel_path: str, ext: str) -> None:
        if ext in {".jsx", ".tsx", ".js", ".ts", ".html", ".vue", ".svelte"}:
            if "dangerouslySetInnerHTML" in line:
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "xss-dangerously-set-inner-html",
                    "cwe": "CWE-79",
                    "owasp": "A03:2021-Injection",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Direct DOM HTML injection bypassing framework XSS sanitization.",
                    "remediation": "Sanitize HTML using DOMPurify before injection or use standard declarative JSX text nodes.",
                })
            elif re.search(r"\binnerHTML\s*=", line):
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "xss-dom-innerhtml",
                    "cwe": "CWE-79",
                    "owasp": "A03:2021-Injection",
                    "severity": "HIGH",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Direct assignment to innerHTML introduces Cross-Site Scripting vulnerabilities.",
                    "remediation": "Use textContent, createElement, or sanitize input through a certified library.",
                })
            elif "v-html" in line:
                self.findings.append({
                    "id": self.next_sec_id(),
                    "category": "security",
                    "rule_id": "xss-vue-v-html",
                    "cwe": "CWE-79",
                    "owasp": "A03:2021-Injection",
                    "severity": "MEDIUM",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": "Vue v-html directive renders unescaped HTML.",
                    "remediation": "Sanitize bound content or prefer template interpolation {{ content }}.",
                })

    def _check_blocking_io(self, line: str, line_no: int, rel_path: str, ext: str) -> None:
        if ext in {".js", ".jsx", ".ts", ".tsx"}:
            sync_match = re.search(r"\b(?:fs\.)?(readFileSync|writeFileSync|appendFileSync)\s*\(", line)
            if sync_match:
                method = sync_match.group(1)
                self.findings.append({
                    "id": self.next_opt_id(),
                    "category": "performance",
                    "rule_id": "blocking-sync-io",
                    "cwe": "CWE-400",
                    "owasp": "Resource Exhaustion",
                    "severity": "MEDIUM",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": f"Synchronous file I/O '{method}' blocks the event loop thread.",
                    "remediation": "Migrate to fs.promises (e.g. await fs.readFile) or non-blocking async stream.",
                })

    def _check_high_freq_interval(self, line: str, line_no: int, rel_path: str, ext: str) -> None:
        if ext in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html"}:
            interval_match = re.search(r"\bsetInterval\s*\([^,]+,\s*([0-9]{1,2})\s*\)", line)
            if interval_match:
                delay = interval_match.group(1)
                self.findings.append({
                    "id": self.next_opt_id(),
                    "category": "performance",
                    "rule_id": "high-frequency-timer",
                    "cwe": "CWE-400",
                    "owasp": "Resource Exhaustion",
                    "severity": "MEDIUM",
                    "file": rel_path,
                    "line": line_no,
                    "snippet": line.strip()[:100],
                    "diagnosis": f"Sub-100ms interval ({delay}ms) can cause thread starvation and high CPU utilization.",
                    "remediation": "Throttle timer frequency (>=100ms) or employ requestAnimationFrame for visual updates.",
                })

    def _check_nested_loops(self, lines: List[str], rel_path: str, ext: str) -> None:
        loop_pattern = re.compile(
            r"^\s*(?:for\s*\(|while\s*\(|for\s+[a-zA-Z0-9_,\s]+\s+in\s+|for\s+[a-zA-Z0-9_,\s]+\s+of\s+|\b\w+\.(?:forEach|map)\s*\()"
        )
        active_loops: List[Tuple[int, int, str]] = []

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Remove loops that have finished because current indentation is equal or less
            while active_loops and indent <= active_loops[-1][1]:
                active_loops.pop()

            if loop_pattern.match(line):
                if active_loops:
                    outer_line_no, outer_indent, outer_snippet = active_loops[-1]
                    self.findings.append({
                        "id": self.next_opt_id(),
                        "category": "performance",
                        "rule_id": "quadratic-nested-loop",
                        "cwe": "CWE-400",
                        "owasp": "Algorithmic Complexity",
                        "severity": "LOW",
                        "file": rel_path,
                        "line": idx,
                        "snippet": stripped[:100],
                        "diagnosis": f"Nested loop at line {idx} inside outer loop at line {outer_line_no}; potential O(N^2) complexity.",
                        "remediation": "Pre-index items using a Map/Set or dictionary lookup to achieve O(N) complexity.",
                    })
                active_loops.append((idx, indent, stripped[:100]))

    def scan(self) -> Dict[str, Any]:
        candidates = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
            for f in files:
                fp = Path(root) / f
                if fp.suffix.lower() in VALID_EXTENSIONS:
                    if not is_binary_or_oversized(fp):
                        candidates.append(fp)

        self.total_scanned_files = len(candidates)
        for fp in candidates:
            self.audit_file(fp)

        sec_issues = sum(1 for f in self.findings if f["category"] == "security")
        opt_issues = sum(1 for f in self.findings if f["category"] == "performance")

        return {
            "status": "audited",
            "summary": {
                "target_directory": str(self.root_dir),
                "total_files_scanned": self.total_scanned_files,
                "security_issues": sec_issues,
                "performance_issues": opt_issues,
                "total_issues": len(self.findings),
            },
            "findings": self.findings,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Static security vulnerability auditor and runtime performance optimizer."
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Execute deterministic static security and performance audit.",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Path to project workspace to scan (defaults to detected repository root).",
    )
    parser.add_argument(
        "--category",
        choices=["all", "security", "performance"],
        default="all",
        help="Filter findings by category.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (json or human-readable table).",
    )

    args = parser.parse_args()
    root_dir = args.target or find_repo_root()

    auditor = SecurityAuditor(root_dir)
    report = auditor.scan()

    if args.category != "all":
        report["findings"] = [f for f in report["findings"] if f["category"] == args.category]

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        findings = report["findings"]
        print(f"\nAudit completed: {report['summary']['total_files_scanned']} files scanned.")
        print(f"Findings: {len(findings)} ({report['summary']['security_issues']} security, {report['summary']['performance_issues']} performance)\n")
        if not findings:
            print("No vulnerabilities or performance bottlenecks detected.")
            return

        print(f"{'ID':<8} | {'Type':<12} | {'Severity':<10} | {'Location':<35} | {'Diagnosis'}")
        print("-" * 100)
        for f in findings:
            loc = f"{f['file']}:{f['line']}"
            print(f"{f['id']:<8} | {f['category']:<12} | {f['severity']:<10} | {loc:<35} | {f['diagnosis']}")


if __name__ == "__main__":
    main()
