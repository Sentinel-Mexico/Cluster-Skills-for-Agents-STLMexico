#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Deterministic Git Push & Changelog Governor
Skill: git-push-governor
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List


def run_git_cmd(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    res = subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def discover_git_state(cwd: Path) -> Dict[str, Any]:
    """
    Inspects working tree status, local branches, current branch,
    and unpushed commits without loading file contents.
    """
    # 1. Uncommitted changes
    code_stat, out_stat, _ = run_git_cmd(["git", "status", "--porcelain"], cwd)
    has_uncommitted = bool(out_stat.strip()) if code_stat == 0 else False

    # 2. Local branches
    code_br, out_br, _ = run_git_cmd(["git", "branch", "--format=%(refname:short)"], cwd)
    branches = [b.strip() for b in out_br.splitlines() if b.strip()] if code_br == 0 else []

    # 3. Current branch
    code_cur, out_cur, _ = run_git_cmd(["git", "branch", "--show-current"], cwd)
    current_branch = out_cur.strip() if code_cur == 0 and out_cur.strip() else "HEAD"

    # 4. Unpushed commits
    unpushed_commits = 0
    code_log, out_log, _ = run_git_cmd(["git", "log", "@{u}..HEAD", "--oneline"], cwd)
    if code_log == 0:
        unpushed_commits = len([line for line in out_log.splitlines() if line.strip()])
    else:
        # Fallback if upstream tracking is not configured directly
        code_rev, _, _ = run_git_cmd(["git", "rev-parse", f"origin/{current_branch}"], cwd)
        if code_rev == 0:
            code_fb, out_fb, _ = run_git_cmd(["git", "log", f"origin/{current_branch}..HEAD", "--oneline"], cwd)
            if code_fb == 0:
                unpushed_commits = len([line for line in out_fb.splitlines() if line.strip()])
        else:
            # New local branch with unpushed commits
            code_all, out_all, _ = run_git_cmd(["git", "log", "-n", "10", "--oneline"], cwd)
            if code_all == 0 and out_all.strip():
                unpushed_commits = len([line for line in out_all.splitlines() if line.strip()])

    return {
        "has_uncommitted": has_uncommitted,
        "unpushed_commits": unpushed_commits,
        "current_branch": current_branch,
        "branches": branches
    }


def resolve_version(project_root: Path) -> str:
    """
    Extracts version from package.json, version.txt, or defaults to 1.0.0.
    """
    pkg_path = project_root / "package.json"
    if pkg_path.exists() and pkg_path.is_file():
        try:
            with open(pkg_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "version" in data and isinstance(data["version"], str):
                    return data["version"].strip()
        except Exception:
            pass

    ver_path = project_root / "version.txt"
    if ver_path.exists() and ver_path.is_file():
        try:
            ver_str = ver_path.read_text(encoding="utf-8").strip()
            if ver_str:
                return ver_str
        except Exception:
            pass

    return "1.0.0"


def format_changelog_entry(version: str, reason: str, cwd: Path, is_production: bool = False) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    code_log, out_log, _ = run_git_cmd(["git", "log", "-n5", "--pretty=format:- %s (%h)"], cwd)
    commit_lines = [line.strip() for line in out_log.splitlines() if line.strip()] if code_log == 0 else []

    section_header = "### Releases & Features" if is_production else "### Active Iteration & Deliverables"
    reason_line = f"- **Summary:** {reason}" if reason else "- **Summary:** Standard development synchronization"

    lines = [
        f"## [{version}] - {today}",
        "",
        section_header,
        reason_line,
    ]

    if commit_lines:
        lines.append("### Recent Commits")
        lines.extend(commit_lines)

    lines.append("")
    return "\n".join(lines)


def inject_entry_into_file(file_path: Path, entry: str, fallback_header: str) -> None:
    if not file_path.exists():
        content = f"{fallback_header}\n\n{entry}\n"
        file_path.write_text(content, encoding="utf-8")
        return

    content = file_path.read_text(encoding="utf-8")

    # If file already contains the exact version header for today, avoid duplicate insertion
    first_line = entry.strip().splitlines()[0]
    if first_line in content:
        return

    # Check for ## [Unreleased]
    unreleased_idx = content.find("## [Unreleased]")
    if unreleased_idx != -1:
        # Insert after ## [Unreleased] block line
        insert_pos = content.find("\n", unreleased_idx)
        if insert_pos != -1:
            new_content = content[:insert_pos+1] + "\n" + entry + "\n" + content[insert_pos+1:].lstrip()
            file_path.write_text(new_content, encoding="utf-8")
            return

    # Look for first version heading ## [
    heading_match = re.search(r"^##\s+\[", content, re.MULTILINE)
    if heading_match:
        insert_pos = heading_match.start()
        new_content = content[:insert_pos] + entry + "\n" + content[insert_pos:]
        file_path.write_text(new_content, encoding="utf-8")
        return

    # Append if no version headings found
    new_content = content.rstrip() + "\n\n" + entry + "\n"
    file_path.write_text(new_content, encoding="utf-8")


def sync_changelog(project_root: Path, target: str, reason: str) -> Dict[str, Any]:
    version = resolve_version(project_root)
    updated_files = []

    if target in ["dev", "both"]:
        dev_file = project_root / "changelog-dev.md"
        entry_dev = format_changelog_entry(version, reason, project_root, is_production=False)
        fallback_dev = "# Changelog (Development)\n\nAll active iterations and sprint tasks are tracked here."
        inject_entry_into_file(dev_file, entry_dev, fallback_dev)
        updated_files.append(str(dev_file.name))

    if target in ["main", "both"]:
        prod_file = project_root / "changelog.md"
        entry_prod = format_changelog_entry(version, reason, project_root, is_production=True)
        fallback_prod = "# Changelog\n\nAll notable changes to this project will be documented in this file."
        inject_entry_into_file(prod_file, entry_prod, fallback_prod)
        updated_files.append(str(prod_file.name))

    return {
        "status": "ok",
        "target": target,
        "version_recorded": version,
        "updated_files": updated_files
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic Git Push and Changelog Governor")
    parser.add_argument("--discover", action="store_true", help="Discover working tree, branches, and unpushed commits")
    parser.add_argument("--sync-changelog", type=str, choices=["dev", "main", "both"], help="Synchronize changelogs")
    parser.add_argument("--reason", type=str, default="", help="Summary reason for the changelog entry")
    parser.add_argument("--project-root", type=str, default=".", help="Root directory of the repository")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.discover:
        res = discover_git_state(project_root)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.sync_changelog:
        res = sync_changelog(project_root, args.sync_changelog, args.reason)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    parser.print_help(sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
