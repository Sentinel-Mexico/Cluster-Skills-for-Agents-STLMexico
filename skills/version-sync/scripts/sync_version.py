#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Universal Version Synchronizer
Skill: version-sync
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, Set

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
    ".venv",
    "env",
    "out",
}

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB size ceiling to prevent memory issues

DEDICATED_VERSION_FILENAMES = {
    "version.txt",
    "VERSION",
    ".version",
    "version",
}

# Contextual regex patterns matching versions across diverse languages and formats
PATTERNS = [
    # 1. JSON, TOML, YAML, INI, Properties, Env manifests
    re.compile(r'(?P<prefix>["\']?(?:[a-zA-Z0-9_]*version[a-zA-Z0-9_]*)["\']?\s*[:=]\s*["\']?)(?P<ver>\d+\.\d+\.\d+)(?P<suffix>["\']?)', re.IGNORECASE),
    re.compile(r'(?P<prefix><version>)(?P<ver>\d+\.\d+\.\d+)(?P<suffix><\/version>)', re.IGNORECASE),

    # 2. Source code constants (TS, JS, Python, Go, Rust, PHP, Java, C, C++, etc.)
    re.compile(r'(?P<prefix>(?:const|let|var|val|export const|export let|final|pub const|public static final String)?\s*(?:[a-zA-Z0-9_]*version[a-zA-Z0-9_]*|__version__)\s*(?::\s*[^=]+)?[:=]\s*["\'])(?P<ver>\d+\.\d+\.\d+)(?P<suffix>["\'])', re.IGNORECASE),

    # 3. Badges in Markdown, RST, and Documentation
    re.compile(r'(?P<prefix>version-)(?P<ver>\d+\.\d+\.\d+)(?P<suffix>-(?:blue|green|red|purple|orange|yellow|brightgreen|informational)\.svg)'),
    re.compile(r'(?P<prefix>\[!\[Version\]\(https://img\.shields\.io/badge/version-)(?P<ver>\d+\.\d+\.\d+)(?P<suffix>-blue\.svg\))'),

    # 4. UI / Frontend templates (HTML, JSX, TSX, Vue, Svelte, Astro, Blade, etc.)
    re.compile(r'(?P<prefix><(?:span|div|p|small|footer|h\d|b|strong)[^>]*>\s*(?:[vV]|Version[:\s]*|v\.\s*)?)(?P<ver>\d+\.\d+\.\d+)(?P<suffix>\s*<\/(?:span|div|p|small|footer|h\d|b|strong)>)'),
    re.compile(r'(?P<prefix>(?:App|Version|Release|v)\s+v?)(?P<ver>\d+\.\d+\.\d+)(?P<suffix>(?:<\/|[^\d\.]|$))'),
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


def get_ground_truth_version(project_root: Path) -> str:
    """
    Extracts canonical version from package.json, version.txt, or default 1.0.0.
    """
    pkg_file = project_root / "package.json"
    if pkg_file.exists() and pkg_file.is_file():
        try:
            with open(pkg_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "version" in data and isinstance(data["version"], str):
                    ver = data["version"].strip()
                    if re.match(r"^\d+\.\d+\.\d+$", ver):
                        return ver
        except Exception:
            pass

    ver_file = project_root / "version.txt"
    if ver_file.exists() and ver_file.is_file():
        try:
            ver = ver_file.read_text(encoding="utf-8").strip()
            if re.match(r"^\d+\.\d+\.\d+$", ver):
                return ver
        except Exception:
            pass

    return "1.0.0"


def find_manifest_file(project_root: Path, custom_path: Optional[str] = None) -> Path:
    if custom_path:
        return Path(custom_path).resolve()
    # Canonical location inside skills/version-sync/assets/version-manifest.json
    internal_manifest = Path(__file__).resolve().parent.parent / "assets" / "version-manifest.json"
    if internal_manifest.parent.exists():
        return internal_manifest
    return project_root / "assets" / "version-manifest.json"


def scan_project_files(project_root: Path) -> List[Path]:
    candidates = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for f in files:
            fp = Path(root) / f
            if fp.name == "version-manifest.json":
                continue
            if is_binary_or_oversized(fp):
                continue
            candidates.append(fp)
    return candidates


def discover_occurrences(project_root: Path, manifest_path: Path) -> Dict[str, Any]:
    target_version = get_ground_truth_version(project_root)
    candidates = scan_project_files(project_root)
    discovered_files: Set[str] = set()

    for fp in candidates:
        rel_str = str(fp.relative_to(project_root))
        # Protect historical changelogs from indiscriminate replacement
        if rel_str in ["changelog.md", "changelog-dev.md"]:
            continue

        # Dedicated version files
        if fp.name in DEDICATED_VERSION_FILENAMES:
            discovered_files.add(rel_str)
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        matched = False
        for pat in PATTERNS:
            if pat.search(content):
                matched = True
                break

        if matched:
            discovered_files.add(rel_str)

    tracked_list = sorted(list(discovered_files))

    manifest_data = {
        "ground_truth_version": target_version,
        "tracked_files_count": len(tracked_list),
        "tracked_files": tracked_list
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest_data, fh, indent=2)
        fh.write("\n")

    return {
        "status": "discovered",
        "count": len(tracked_list),
        "files": tracked_list
    }


def sync_occurrences(project_root: Path, manifest_path: Path, new_version_arg: Optional[str] = None) -> Dict[str, Any]:
    target_version = new_version_arg.strip() if new_version_arg else get_ground_truth_version(project_root)
    if not re.match(r"^\d+\.\d+\.\d+$", target_version):
        return {
            "status": "error",
            "message": f"Target version '{target_version}' must match strict SemVer format ^\\d+\\.\\d+\\.\\d+$"
        }

    # Step 1: Execute dynamic discovery pass first to index any newly added files
    discover_occurrences(project_root, manifest_path)

    # Step 2: Load discovered manifest
    tracked_files: Set[str] = set()
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "tracked_files" in data and isinstance(data["tracked_files"], list):
                    tracked_files.update(data["tracked_files"])
        except Exception:
            pass

    updated_paths: List[str] = []

    for rel_path in sorted(list(tracked_files)):
        fp = project_root / rel_path
        if not fp.exists() or not fp.is_file():
            continue

        try:
            old_content = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        new_content = old_content

        # Dedicated version files (version.txt, VERSION, .version)
        if fp.name in DEDICATED_VERSION_FILENAMES:
            new_content = f"{target_version}\n"
        else:
            for pat in PATTERNS:
                def replace_ver(m):
                    prefix = m.group("prefix")
                    suffix = m.group("suffix")
                    return f"{prefix}{target_version}{suffix}"
                new_content = pat.sub(replace_ver, new_content)

        if new_content != old_content:
            fp.write_text(new_content, encoding="utf-8")
            updated_paths.append(rel_path)

    # Re-sync package.json if present
    pkg_file = project_root / "package.json"
    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8") as fh:
                pkg_data = json.load(fh)
            if pkg_data.get("version") != target_version:
                pkg_data["version"] = target_version
                with open(pkg_file, "w", encoding="utf-8") as fh:
                    json.dump(pkg_data, fh, indent=2)
                    fh.write("\n")
                if "package.json" not in updated_paths:
                    updated_paths.append("package.json")
        except Exception:
            pass

    # Update manifest file with final state
    manifest_data = {
        "ground_truth_version": target_version,
        "tracked_files_count": len(tracked_files),
        "tracked_files": sorted(list(tracked_files))
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest_data, fh, indent=2)
        fh.write("\n")

    return {
        "status": "synced",
        "target_version": target_version,
        "files_updated": len(updated_paths),
        "updated_paths": updated_paths
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic Universal Version Synchronizer")
    parser.add_argument("--discover", action="store_true", help="Recursively scan project and register version occurrences")
    parser.add_argument("--sync", action="store_true", help="Atomically synchronize version across all tracked occurrences")
    parser.add_argument("--new-version", type=str, help="Explicit target version (defaults to package.json / version.txt)")
    parser.add_argument("--manifest-file", type=str, help="Path to version-manifest.json")
    parser.add_argument("--project-root", type=str, default=".", help="Root directory of the project")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    manifest_path = find_manifest_file(project_root, args.manifest_file)

    if args.discover:
        res = discover_occurrences(project_root, manifest_path)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.sync:
        res = sync_occurrences(project_root, manifest_path, args.new_version)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res.get("status") == "synced" else 1)

    parser.print_help(sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
