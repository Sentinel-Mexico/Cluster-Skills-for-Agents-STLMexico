#!/usr/bin/env python3
"""
Sentinel Mexico · Cluster Sync Engine (Fleet Auditor & Batch Synchronizer)
Standard: agentskills.io
Audits installed agent skills across workspaces and user environments against the
official remote catalog on GitHub and executes batch synchronization.
Zero external dependencies (Python 3 standard library only).
"""

import os
import sys
import json
import re
import time
import argparse
import subprocess
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

DEFAULT_REPO = "Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
REMOTE_BASE_URL = f"https://raw.githubusercontent.com/{DEFAULT_REPO}/main"
CACHE_TTL = 86400  # 24 hours

KNOWN_PROJECT_PATHS = [
    ".agents/skills",
    ".agent/skills",
    ".claude/skills",
    ".cursor/skills",
    ".codex/skills",
    ".adal/skills",
    ".augment/skills",
    ".codebuddy/skills",
    ".commandcode/skills",
    ".continue/skills",
    ".cortex/skills",
    ".crush/skills",
    ".factory/skills",
    ".goose/skills",
    ".iflow/skills",
    ".junie/skills",
    ".kilocode/skills",
    ".kiro/skills",
    ".kode/skills",
    ".mcpjam/skills",
    ".vibe/skills",
    ".mux/skills",
    ".neovate/skills",
    ".openclaw/skills",
    ".openhands/skills",
    ".pi/skills",
    ".pochi/skills",
    ".qoder/skills",
    ".qwen/skills",
    ".roo/skills",
    ".trae/skills",
    ".windsurf/skills",
    ".zencoder/skills",
    "skills",
]

KNOWN_USER_PATHS = [
    ".config/agents/skills",
    ".gemini/antigravity/skills",
    ".claude/skills",
    ".cursor/skills",
    ".agents/skills",
    ".codex/skills",
    ".adal/skills",
    ".augment/skills",
    ".continue/skills",
    ".factory/skills",
    ".goose/skills",
    ".kiro/skills",
    ".roo/skills",
    ".windsurf/skills",
]


def parse_semver(v_str: str):
    """Parse version string into tuple of integers."""
    if not v_str:
        return (0, 0, 0)
    nums = re.findall(r"\d+", v_str)
    return tuple(int(x) for x in nums) if nums else (0, 0, 0)


def extract_metadata(skill_md_path: str) -> Dict[str, str]:
    """Parse SKILL.md frontmatter for name, version, author, origin, and repo."""
    meta = {
        "name": "",
        "version": "0.0.0",
        "author": "",
        "origin": "",
        "repository": "",
        "path": skill_md_path,
    }
    if not os.path.isfile(skill_md_path):
        return meta

    try:
        with open(skill_md_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(4096)

        name_m = re.search(r"^name:\s*([^\s\n\r]+)", content, re.MULTILINE)
        if name_m:
            meta["name"] = name_m.group(1).strip("'\"")

        ver_m = re.search(r"^\s*version:\s*[\"']?([0-9A-Za-z\.\-\+]+)[\"']?", content, re.MULTILINE)
        if ver_m:
            meta["version"] = ver_m.group(1).strip()

        author_m = re.search(r"^\s*author:\s*[\"']?([^\"'\n\r]+)[\"']?", content, re.MULTILINE)
        if author_m:
            meta["author"] = author_m.group(1).strip()

        origin_m = re.search(r"^\s*skill-origin:\s*[\"']?([^\"'\n\r]+)[\"']?", content, re.MULTILINE)
        if origin_m:
            meta["origin"] = origin_m.group(1).strip()

        repo_m = re.search(r"^\s*repository:\s*[\"']?([^\"'\n\r]+)[\"']?", content, re.MULTILINE)
        if repo_m:
            meta["repository"] = repo_m.group(1).strip()
    except Exception:
        pass

    return meta


def fetch_remote_version(skill_name: str, origin: str = "") -> Optional[str]:
    """Fetch the latest metadata.version for a skill from GitHub main branch."""
    path_suffix = origin if origin else f"skills/{skill_name}"
    url = f"{REMOTE_BASE_URL}/{path_suffix}/SKILL.md"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Sentinel-Mexico-Cluster-Sync/1.0",
                "Accept": "text/plain",
            },
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            if resp.status == 200:
                body = resp.read(4096).decode("utf-8", errors="replace")
                ver_m = re.search(r"^\s*version:\s*[\"']?([0-9A-Za-z\.\-\+]+)[\"']?", body, re.MULTILINE)
                if ver_m:
                    return ver_m.group(1).strip()
    except Exception:
        pass
    return None


def discover_skills(scan_roots: List[str]) -> List[Dict[str, Any]]:
    """Scan candidate directories for installed skills matching Sentinel Mexico."""
    discovered = []
    seen_paths = set()

    for root_dir in scan_roots:
        if not os.path.isdir(root_dir):
            continue

        # Look for subdirectories containing SKILL.md
        try:
            for item in sorted(os.listdir(root_dir)):
                candidate_dir = os.path.join(root_dir, item)
                if not os.path.isdir(candidate_dir):
                    continue

                skill_md = os.path.join(candidate_dir, "SKILL.md")
                if os.path.isfile(skill_md):
                    norm_path = os.path.abspath(candidate_dir)
                    if norm_path in seen_paths:
                        continue
                    seen_paths.add(norm_path)

                    meta = extract_metadata(skill_md)
                    # Use directory name as fallback if name is empty
                    if not meta["name"]:
                        meta["name"] = os.path.basename(candidate_dir)

                    # Only filter skills affiliated with Sentinel Mexico or cluster catalog
                    is_sentinel = (
                        "Sentinel Mexico" in meta["author"]
                        or "Cluster-Skills-for-Agents-STLMexico" in meta["repository"]
                        or meta["origin"].startswith("skills/")
                    )
                    if is_sentinel or not meta["author"]:
                        discovered.append({
                            "name": meta["name"],
                            "version": meta["version"],
                            "author": meta["author"] or "Sentinel Mexico",
                            "origin": meta["origin"],
                            "dir_path": candidate_dir,
                            "skill_md": skill_md,
                            "is_symlink": os.path.islink(candidate_dir),
                        })
        except Exception:
            continue

    return discovered


def run_sync_skill(skill_entry: Dict[str, Any]) -> bool:
    """Synchronize an individual skill via git pull or npx skills add."""
    skill_name = skill_entry["name"]
    dir_path = skill_entry["dir_path"]

    print(f"\n[Syncing] '{skill_name}' at {dir_path}...")

    if skill_entry["is_symlink"]:
        print(f"  -> Detected symbolic link. Updating cluster repository via git pull...")
        real_path = os.path.realpath(dir_path)
        cluster_root = os.path.dirname(os.path.dirname(real_path))
        try:
            res = subprocess.run(["git", "-C", cluster_root, "pull"], check=False, capture_output=True, text=True)
            print(f"  {res.stdout.strip()}")
            return res.returncode == 0
        except Exception as e:
            print(f"  ❌ Git pull failed: {e}")
            return False
    else:
        # Standard installation via npx skills or git-based copy
        cmd = ["npx", "-y", "skills", "add", DEFAULT_REPO, "--skill", skill_name, "--force"]
        print(f"  -> Executing: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  ✅ Successfully updated '{skill_name}'")
                return True
            else:
                print(f"  ⚠️ Warning: npx skills output: {res.stderr.strip() or res.stdout.strip()}")
                return False
        except Exception as e:
            print(f"  ❌ Execution failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel Mexico Cluster Sync: Fleet Auditor & Batch Synchronizer"
    )
    parser.add_argument("--scan-path", type=str, help="Custom directory to audit for installed skills")
    parser.add_argument("--user", action="store_true", help="Audit user home directory skills")
    parser.add_argument("--check", action="store_true", help="Perform non-interactive audit check without updating")
    parser.add_argument("--json", action="store_true", help="Output audit results in JSON format")
    parser.add_argument("--sync-all", action="store_true", help="Automatically synchronize all outdated skills in batch")
    parser.add_argument("--force", action="store_true", help="Bypass cached checks and force remote lookup")
    args = parser.parse_args()

    # Determine paths to inspect
    scan_roots = []
    cwd = os.getcwd()

    if args.scan_path:
        scan_roots.append(os.path.abspath(args.scan_path))
    else:
        # Project level paths relative to CWD
        for rel_p in KNOWN_PROJECT_PATHS:
            p = os.path.join(cwd, rel_p)
            if os.path.isdir(p):
                scan_roots.append(p)

        # User level paths relative to HOME if requested or if no project skills found
        home = os.path.expanduser("~")
        if args.user:
            for rel_u in KNOWN_USER_PATHS:
                p = os.path.join(home, rel_u)
                if os.path.isdir(p):
                    scan_roots.append(p)

    skills = discover_skills(scan_roots)

    audit_results = []
    outdated_entries = []

    for sk in skills:
        remote_v = fetch_remote_version(sk["name"], sk.get("origin", ""))
        local_v = sk["version"]

        if remote_v is None:
            status = "UNKNOWN_REMOTE"
            display_status = "⚠️ UNVERIFIED (Offline/Private)"
        elif parse_semver(remote_v) > parse_semver(local_v):
            status = "OUTDATED"
            display_status = "🔄 UPDATE AVAILABLE"
            outdated_entries.append((sk, remote_v))
        else:
            status = "UP_TO_DATE"
            display_status = "✅ SYNCHRONIZED"

        audit_results.append({
            "name": sk["name"],
            "directory": sk["dir_path"],
            "local_version": local_v,
            "remote_version": remote_v or "N/A",
            "status": status,
            "display_status": display_status,
            "is_symlink": sk["is_symlink"],
        })

    # JSON Output
    if args.json:
        print(json.dumps({
            "catalog_repository": DEFAULT_REPO,
            "timestamp": time.time(),
            "scanned_paths": scan_roots,
            "total_discovered": len(skills),
            "outdated_count": len(outdated_entries),
            "skills": audit_results,
        }, indent=2))
        sys.exit(0)

    # CLI Table Output
    print("\n" + "=" * 90)
    print(f" Sentinel Mexico · Agent Skills Catalog Synchronization Audit")
    print(f" Remote Catalog: https://github.com/{DEFAULT_REPO}")
    print("=" * 90)

    if not skills:
        print(" No Sentinel Mexico skills discovered in active workspace paths.")
        print(f" Checked paths ({len(scan_roots)} targets). Use --scan-path <dir> to target a specific folder.")
        print("=" * 90 + "\n")
        sys.exit(0)

    row_fmt = "{:<22} {:<32} {:<11} {:<11} {:<20}"
    print(row_fmt.format("SKILL NAME", "LOCATION", "LOCAL", "REMOTE", "STATUS"))
    print("-" * 90)

    for item in audit_results:
        loc_display = os.path.relpath(item["directory"], cwd)
        if len(loc_display) > 31:
            loc_display = "..." + loc_display[-28:]
        print(row_fmt.format(
            item["name"][:21],
            loc_display,
            item["local_version"],
            item["remote_version"],
            item["display_status"]
        ))

    print("=" * 90)
    print(f" Summary: {len(skills)} skills audited, {len(outdated_entries)} outdated.\n")

    if args.check:
        sys.exit(0)

    # Batch synchronization
    if not outdated_entries:
        print("✅ All discovered skills are up to date with the remote catalog.\n")
        sys.exit(0)

    if args.sync_all:
        print(f"Initiating batch update for {len(outdated_entries)} outdated skills...")
        for sk, rem_ver in outdated_entries:
            run_sync_skill(sk)
        print("\n✅ Batch synchronization completed.\n")
        sys.exit(0)

    # Interactive prompt
    print(f"⚠️ {len(outdated_entries)} skill(s) have new versions available.")
    print("Options:")
    print("  [A] Update all outdated skills in batch")
    print("  [1..N] Update a specific skill from the list")
    print("  [Q] Quit without updating")

    try:
        choice = input("\nSelect an action [A/1..N/Q]: ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.")
        sys.exit(0)

    if choice == "A":
        for sk, rem_ver in outdated_entries:
            run_sync_skill(sk)
        print("\n✅ All outdated skills synchronized successfully.\n")
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(outdated_entries):
            target_skill, _ = outdated_entries[idx]
            run_sync_skill(target_skill)
        else:
            print("Invalid selection.")
    else:
        print("Exiting without making changes.")


if __name__ == "__main__":
    main()
