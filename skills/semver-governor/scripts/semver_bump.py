#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Deterministic SemVer Governor
Skill: semver-governor
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

SEMVER_REGEX = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def run_git_cmd(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    res = subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def inspect_diff_stat(cwd: Path) -> Dict[str, Any]:
    """
    Executes git diff --stat and git diff --cached --stat to produce
    a compact summary of modified files without loading full file diffs.
    """
    _, unstaged_stat, _ = run_git_cmd(["git", "diff", "--stat"], cwd)
    _, staged_stat, _ = run_git_cmd(["git", "diff", "--cached", "--stat"], cwd)

    _, unstaged_files, _ = run_git_cmd(["git", "diff", "--name-only"], cwd)
    _, staged_files, _ = run_git_cmd(["git", "diff", "--cached", "--name-only"], cwd)

    files_set = set()
    if unstaged_files:
        files_set.update([f.strip() for f in unstaged_files.splitlines() if f.strip()])
    if staged_files:
        files_set.update([f.strip() for f in staged_files.splitlines() if f.strip()])

    combined_files = sorted(list(files_set))

    # Parse insertions and deletions if available
    _, numstat_unstaged, _ = run_git_cmd(["git", "diff", "--numstat"], cwd)
    _, numstat_staged, _ = run_git_cmd(["git", "diff", "--cached", "--numstat"], cwd)

    total_ins = 0
    total_del = 0

    for block in [numstat_unstaged, numstat_staged]:
        for line in block.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                ins, dels = parts[0], parts[1]
                if ins.isdigit():
                    total_ins += int(ins)
                if dels.isdigit():
                    total_del += int(dels)

    summary = f"{len(combined_files)} files changed, {total_ins} insertions(+), {total_del} deletions(-)" if combined_files else "No changes detected"

    return {
        "status": "ok",
        "files_changed": len(combined_files),
        "insertions": total_ins,
        "deletions": total_del,
        "files": combined_files,
        "summary": summary
    }


def find_package_json(project_root: Path) -> Optional[Path]:
    target = project_root / "package.json"
    if target.exists() and target.is_file():
        return target
    return None


def bump_version(current_ver: str, level: str) -> str:
    match = SEMVER_REGEX.match(current_ver)
    if not match:
        raise ValueError(f"Version '{current_ver}' does not match strict SemVer format ^(\\d+)\\.(\\d+)\\.(\\d+)$")

    major, minor, patch = map(int, match.groups())

    # Milestone Production Clause: If current version is < 1.0.0 (beta surpassed),
    # any new bump establishes the base version at minimum >= 1.0.0
    if major < 1:
        if level in ["patch", "minor", "major"]:
            return "1.0.0"

    if level == "patch":
        patch += 1
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Unsupported bump level '{level}'. Must be 'patch', 'minor', or 'major'.")

    return f"{major}.{minor}.{patch}"


def execute_bump(project_root: Path, level: str, reason: str) -> Dict[str, Any]:
    pkg_path = find_package_json(project_root)
    if not pkg_path:
        return {
            "status": "error",
            "message": f"package.json not found in root '{project_root}'"
        }

    try:
        with open(pkg_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to parse package.json: {exc}"
        }

    if "version" not in data or not isinstance(data["version"], str):
        return {
            "status": "error",
            "message": "Missing or invalid 'version' field in package.json"
        }

    current_version = data["version"].strip()

    try:
        new_version = bump_version(current_version, level)
    except ValueError as exc:
        return {
            "status": "error",
            "message": str(exc)
        }

    data["version"] = new_version

    # Write back preserving 2 spaces indentation and trailing newline
    try:
        with open(pkg_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to write updated package.json: {exc}"
        }

    return {
        "status": "ok",
        "previous_version": current_version,
        "new_version": new_version,
        "level": level,
        "reason": reason or "Semantic version bump applied by semver-governor"
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic SemVer Governor")
    parser.add_argument("--diff-stat", action="store_true", help="Inspect git diff --stat and return compact summary")
    parser.add_argument("--bump", type=str, choices=["patch", "minor", "major"], help="Semantic increment level")
    parser.add_argument("--reason", type=str, default="", help="Brief justification for version bump")
    parser.add_argument("--project-root", type=str, default=".", help="Root directory containing package.json")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.diff_stat:
        res = inspect_diff_stat(project_root)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.bump:
        res = execute_bump(project_root, args.bump, args.reason)
        if res.get("status") == "error":
            print(json.dumps(res, indent=2), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    parser.print_help(sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
