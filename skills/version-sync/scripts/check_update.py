#!/usr/bin/env python3
"""
Sentinel Mexico · Skill Update Check Gate (Deterministic Engine)
Standard: agentskills.io
Zero external dependencies (Python 3 standard library only).
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error

CACHE_TTL_SECONDS = 86400  # 24 hours
DEFAULT_REPO = "Sentinel-Mexico/Cluster-Skills-for-Agents-STLMexico"
HTTP_TIMEOUT_SECONDS = 2.0


def parse_semver(v_str: str):
    """Extract integer tuple for semver comparison e.g. '1.2.3' -> (1, 2, 3)."""
    if not v_str:
        return (0, 0, 0)
    nums = re.findall(r"\d+", v_str)
    return tuple(int(x) for x in nums) if nums else (0, 0, 0)


def extract_skill_metadata(skill_md_path: str):
    """Extract name, version, and skill-origin from local SKILL.md frontmatter."""
    metadata = {
        "name": "",
        "version": "1.0.0",
        "origin": "",
        "repository": DEFAULT_REPO,
    }
    if not os.path.isfile(skill_md_path):
        return metadata

    try:
        with open(skill_md_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(4096)  # Frontmatter is at top

        # Extract name
        name_m = re.search(r"^name:\s*([^\s\n\r]+)", content, re.MULTILINE)
        if name_m:
            metadata["name"] = name_m.group(1).strip("'\"")

        # Extract version
        ver_m = re.search(r"^\s*version:\s*[\"']?([0-9A-Za-z\.\-\+]+)[\"']?", content, re.MULTILINE)
        if ver_m:
            metadata["version"] = ver_m.group(1).strip()

        # Extract skill-origin
        origin_m = re.search(r"^\s*skill-origin:\s*[\"']?([^\"'\n\r]+)[\"']?", content, re.MULTILINE)
        if origin_m:
            metadata["origin"] = origin_m.group(1).strip()

        # Extract repository
        repo_m = re.search(r"^\s*repository:\s*[\"']?([^\"'\n\r]+)[\"']?", content, re.MULTILINE)
        if repo_m:
            metadata["repository"] = repo_m.group(1).strip()
    except Exception:
        pass

    return metadata


def save_cache(cache_path: str, assets_dir: str):
    """Persist last_check_timestamp to assets/.update_cache.json."""
    try:
        os.makedirs(assets_dir, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"last_check_timestamp": time.time()}, f, indent=2)
    except Exception:
        pass


def main():
    force_check = "--force" in sys.argv

    # Resolve paths relative to script location: <skill_root>/scripts/check_update.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    skill_name_dir = os.path.basename(skill_dir)

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    assets_dir = os.path.join(skill_dir, "assets")
    cache_path = os.path.join(assets_dir, ".update_cache.json")

    local_meta = extract_skill_metadata(skill_md_path)
    skill_name = local_meta["name"] or skill_name_dir
    local_version = local_meta["version"]
    skill_origin = local_meta["origin"] or f"skills/{skill_name}"

    # 1. 24-hour Cache Check
    if not force_check and os.path.isfile(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            last_ts = float(cache_data.get("last_check_timestamp", 0))
            if (time.time() - last_ts) < CACHE_TTL_SECONDS:
                print(json.dumps({"update_available": False, "cached": True}))
                sys.exit(0)
        except Exception:
            pass

    # 2. Remote check via GitHub Raw
    remote_url = f"https://raw.githubusercontent.com/{DEFAULT_REPO}/main/{skill_origin}/SKILL.md"

    try:
        req = urllib.request.Request(
            remote_url,
            headers={
                "User-Agent": "Sentinel-Mexico-Skill-Updater/1.0",
                "Accept": "text/plain",
            },
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                save_cache(cache_path, assets_dir)
                print(json.dumps({"update_available": False}))
                sys.exit(0)
            remote_raw = response.read(4096).decode("utf-8", errors="replace")

        # Extract remote version
        ver_m = re.search(r"^\s*version:\s*[\"']?([0-9A-Za-z\.\-\+]+)[\"']?", remote_raw, re.MULTILINE)
        if not ver_m:
            save_cache(cache_path, assets_dir)
            print(json.dumps({"update_available": False}))
            sys.exit(0)

        remote_version = ver_m.group(1).strip()

        # Update cache timestamp
        save_cache(cache_path, assets_dir)

        # Compare versions
        if parse_semver(remote_version) > parse_semver(local_version):
            output = {
                "update_available": True,
                "current_version": local_version,
                "latest_version": remote_version,
                "skill_name": skill_name,
                "repo": DEFAULT_REPO,
            }
            print(json.dumps(output, indent=2))
            sys.exit(0)
        else:
            print(json.dumps({"update_available": False}))
            sys.exit(0)

    except Exception:
        # Graceful fallback on network timeout, 404, connection refusal, or DNS failure
        save_cache(cache_path, assets_dir)
        print(json.dumps({"update_available": False}))
        sys.exit(0)


if __name__ == "__main__":
    main()
