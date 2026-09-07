#!/usr/bin/env python3
"""
==============================================================================
Sentinel Mexico · Deterministic README Engine (readme-generator)
Standard: agentskills.io
Specification: Code-as-Skill README inspection, 5-change cadence, and badge generator
==============================================================================
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Set, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STATE_FILE = os.path.join(SKILL_ROOT, "assets", "readme-state.json")

IGNORED_DIRS = {
    ".git",
    "node_modules",
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


def find_repo_root(start_dir: str = None) -> str:
    current = start_dir or os.getcwd()
    while current != os.path.dirname(current):
        if (
            os.path.exists(os.path.join(current, ".git"))
            or os.path.exists(os.path.join(current, "package.json"))
            or os.path.exists(os.path.join(current, "version.txt"))
        ):
            return current
        current = os.path.dirname(current)
    return os.getcwd()


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        initial = {"last_sync_entries": 0}
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(initial, fh, indent=2)
        return initial
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"last_sync_entries": 0}


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def get_changelog_entries(repo_root: str) -> List[str]:
    candidate_files = [
        "changelog-dev.md",
        "changelog.md",
        "CHANGELOG-DEV.md",
        "CHANGELOG.md",
    ]
    entries: Set[str] = set()
    for fname in candidate_files:
        fpath = os.path.join(repo_root, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                    matches = re.findall(r"^##\s*\[([^\]]+)\]", content, re.MULTILINE)
                    for match in matches:
                        entries.add(match.strip())
            except Exception:
                pass
    return sorted(list(entries))


def check_empty_readme(repo_root: str) -> Tuple[bool, str]:
    for candidate in ["README.md", "readme.md"]:
        fpath = os.path.join(repo_root, candidate)
        if os.path.exists(fpath):
            try:
                size = os.path.getsize(fpath)
                if size == 0:
                    return True, candidate
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    non_empty = [line.strip() for line in fh if line.strip()]
                if len(non_empty) <= 3:
                    return True, candidate
                return False, candidate
            except Exception:
                return True, candidate
    return True, "README.md"


def get_active_version(repo_root: str) -> Tuple[str, str]:
    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "version" in data and str(data["version"]).strip():
                    return str(data["version"]).strip(), "package.json"
        except Exception:
            pass

    ver_path = os.path.join(repo_root, "version.txt")
    if os.path.isfile(ver_path):
        try:
            with open(ver_path, "r", encoding="utf-8") as fh:
                content = fh.read().strip()
                if content:
                    return content, "version.txt"
        except Exception:
            pass

    return "1.0.0", "version.txt"


def get_license_type(repo_root: str) -> str:
    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "license" in data and str(data["license"]).strip():
                    return str(data["license"]).strip()
        except Exception:
            pass

    lic_path = os.path.join(repo_root, "LICENSE")
    if os.path.isfile(lic_path):
        try:
            with open(lic_path, "r", encoding="utf-8", errors="ignore") as fh:
                head = fh.read(1024)
                if "Apache" in head:
                    return "Apache-2.0"
                if "MIT" in head:
                    return "MIT"
                if "GNU" in head or "GPL" in head:
                    return "GPL-3.0"
        except Exception:
            pass

    return "Apache-2.0"


def generate_badges(repo_root: str, version: str, version_file: str, license_str: str) -> List[str]:
    badges = []

    # 1. Version Badge
    ver_clean = re.sub(r"[^a-zA-Z0-9._-]", "", version)
    badges.append(
        f"[![Version](https://img.shields.io/badge/version-{ver_clean}-blue?style=for-the-badge)]({version_file})"
    )

    # 2. License Badge (Shields requires hyphens escaped as double hyphen)
    lic_badge_val = license_str.replace("-", "--")
    badges.append(
        f"[![License](https://img.shields.io/badge/License-{lic_badge_val}-red?style=for-the-badge)](LICENSE)"
    )

    # 3. Standard Specification Badge
    badges.append(
        "[![Standard](https://img.shields.io/badge/Standard-agentskills.io-black?style=for-the-badge)](https://agentskills.io)"
    )

    # 4. Runtimes & Ecosystem Badges
    has_node = False
    has_python = False
    has_bash = False
    has_electron = False
    has_ts = False

    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(pkg_path):
        has_node = True
        try:
            with open(pkg_path, "r", encoding="utf-8") as fh:
                content = fh.read()
                if "electron" in content.lower():
                    has_electron = True
                if "typescript" in content.lower():
                    has_ts = True
        except Exception:
            pass

    if os.path.exists(os.path.join(repo_root, "tsconfig.json")):
        has_ts = True

    # Check for python files or configs
    for candidate in ["pyproject.toml", "requirements.txt", "setup.py"]:
        if os.path.exists(os.path.join(repo_root, candidate)):
            has_python = True
            break

    if not has_python:
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            if any(f.endswith(".py") for f in files):
                has_python = True
                break

    # Check for shell scripts
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        if any(f.endswith(".sh") for f in files):
            has_bash = True
            break

    if has_node:
        badges.append(
            "[![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org)"
        )
    if has_ts:
        badges.append(
            "[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)"
        )
    if has_electron:
        badges.append(
            "[![Electron](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://electronjs.org)"
        )
    if has_python:
        badges.append(
            "[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)"
        )
    if has_bash:
        badges.append(
            "[![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)"
        )

    return badges


def build_sanitized_tree(repo_root: str, max_depth: int = 2) -> str:
    tree_lines = ["."]

    def walk(current_dir: str, prefix: str, current_depth: int):
        if current_depth > max_depth:
            return

        try:
            entries = sorted(os.listdir(current_dir))
        except OSError:
            return

        filtered_entries = []
        for e in entries:
            if e.startswith("."):
                continue
            if e in IGNORED_DIRS:
                continue
            filtered_entries.append(e)

        dirs_list = [e for e in filtered_entries if os.path.isdir(os.path.join(current_dir, e))]
        files_list = [e for e in filtered_entries if not os.path.isdir(os.path.join(current_dir, e))]
        sorted_all = dirs_list + files_list

        count = len(sorted_all)
        for i, item in enumerate(sorted_all):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            child_path = os.path.join(current_dir, item)
            is_dir = os.path.isdir(child_path)
            display_name = f"{item}/" if is_dir else item

            tree_lines.append(f"{prefix}{connector}{display_name}")

            if is_dir and current_depth < max_depth:
                next_prefix = prefix + ("    " if is_last else "│   ")
                walk(child_path, next_prefix, current_depth + 1)

    walk(repo_root, "", 1)
    return "\n".join(tree_lines)


def run_inspect(repo_root: str, force: bool = False) -> Dict[str, Any]:
    state = load_state()
    last_sync = state.get("last_sync_entries", 0)

    changelog_entries = get_changelog_entries(repo_root)
    total_entries = len(changelog_entries)
    delta = max(0, total_entries - last_sync)

    is_empty_readme, readme_filename = check_empty_readme(repo_root)
    version, version_file = get_active_version(repo_root)
    license_str = get_license_type(repo_root)

    repo_name = os.path.basename(os.path.abspath(repo_root))
    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "name" in data and str(data["name"]).strip():
                    repo_name = str(data["name"]).strip()
        except Exception:
            pass

    badges = generate_badges(repo_root, version, version_file, license_str)
    sanitized_tree = build_sanitized_tree(repo_root, max_depth=2)

    if is_empty_readme:
        can_generate = True
        reason = "empty_readme"
    elif force:
        can_generate = True
        reason = "user_forced"
    elif delta >= 5:
        can_generate = True
        reason = "changelog_delta_5"
    else:
        can_generate = False
        reason = "delta_below_threshold"

    return {
        "can_generate": can_generate,
        "reason": reason,
        "unreflected_changes": delta,
        "total_entries": total_entries,
        "last_sync_entries": last_sync,
        "target_readme": readme_filename,
        "metadata": {
            "name": repo_name,
            "version": version,
            "version_file": version_file,
            "license": license_str,
            "badges": badges,
        },
        "sanitized_tree": sanitized_tree,
    }


def run_reset_counter(repo_root: str) -> Dict[str, Any]:
    changelog_entries = get_changelog_entries(repo_root)
    total_entries = len(changelog_entries)

    state = {"last_sync_entries": total_entries}
    save_state(state)

    return {
        "status": "counter_reset",
        "last_sync_entries": total_entries,
        "unreflected_changes": 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic README inspection, badge generation, and cadence engine."
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Inspect changelog delta, empty status, and generate metadata/badges.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force README generation even if delta is less than 5.",
    )
    parser.add_argument(
        "--reset-counter",
        action="store_true",
        help="Reset unreflected changes counter to current changelog entries.",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Root path of the target repository.",
    )

    args = parser.parse_args()

    repo_root = args.repo_root or find_repo_root()

    if args.reset_counter:
        result = run_reset_counter(repo_root)
        print(json.dumps(result, indent=2))
        return

    # Default to inspect mode
    result = run_inspect(repo_root, force=args.force)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
