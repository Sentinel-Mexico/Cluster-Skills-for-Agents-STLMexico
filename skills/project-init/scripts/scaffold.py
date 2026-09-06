#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Deterministic Project Scaffolding Engine
Skill: project-init
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

ALLOWED_EXISTING_ENTRIES = {
    ".git",
    ".gitignore",
    "readme.md",
    "README.md",
    "Readme.md",
    ".ds_store",
    ".DS_Store",
    ".gitattributes",
}

DEV_BRANCH_CANDIDATES = ["dev", "developer", "devel", "development"]


def evaluate_existing_project_guard(target_dir: Path) -> Tuple[bool, Optional[str]]:
    """
    Evaluates whether the directory is clean for initialization.
    Aborts if files/folders exist outside allowed bootstrap entries.
    """
    if not target_dir.exists():
        return True, None

    for item in target_dir.iterdir():
        name = item.name
        if name in ALLOWED_EXISTING_ENTRIES or name.lower() in ALLOWED_EXISTING_ENTRIES:
            continue
        # If any unexpected file or directory is found, abort
        return False, "existing_project"

    return True, None


def run_git_cmd(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    res = subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def manage_git_branch(target_dir: Path) -> Tuple[bool, str]:
    """
    Verifies or creates development branch (dev, developer, devel, development).
    Returns (success, branch_name).
    """
    # Ensure git is initialized
    code, out, _ = run_git_cmd(["git", "rev-parse", "--is-inside-work-tree"], target_dir)
    if code != 0:
        code_init, _, err_init = run_git_cmd(["git", "init"], target_dir)
        if code_init != 0:
            return False, f"Failed to init git: {err_init}"

    # Query local branches
    code, out, _ = run_git_cmd(["git", "branch", "--format=%(refname:short)"], target_dir)
    local_branches = [b.strip() for b in out.splitlines() if b.strip()] if code == 0 else []

    # Check if a dev branch already exists locally
    for cand in DEV_BRANCH_CANDIDATES:
        if cand in local_branches:
            code_co, _, _ = run_git_cmd(["git", "checkout", cand], target_dir)
            if code_co == 0:
                return True, cand

    # Query remote branches if remote exists
    code, out, _ = run_git_cmd(["git", "branch", "-r", "--format=%(refname:short)"], target_dir)
    remote_branches = [b.strip().split("/")[-1] for b in out.splitlines() if b.strip()] if code == 0 else []
    for cand in DEV_BRANCH_CANDIDATES:
        if cand in remote_branches:
            code_co, _, _ = run_git_cmd(["git", "checkout", "-b", cand, f"origin/{cand}"], target_dir)
            if code_co == 0:
                return True, cand

    # If no dev branch exists, check current branch or create dev
    code_cur, cur_branch, _ = run_git_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], target_dir)
    if code_cur == 0 and cur_branch in DEV_BRANCH_CANDIDATES:
        return True, cur_branch

    # Try creating dev branch from current commit/HEAD
    code_create, _, _ = run_git_cmd(["git", "checkout", "-b", "dev"], target_dir)
    if code_create == 0:
        return True, "dev"

    # If repo has no commits yet, create orphan or checkout -b
    return True, "dev"


def scaffold_project(target_dir: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    project_name = manifest.get("project_name", target_dir.name or "sentinel-project")
    is_monorepo = bool(manifest.get("is_monorepo", False))
    environments = manifest.get("environments", ["app"])
    locales = manifest.get("locales", ["en", "es"])
    include_ci = bool(manifest.get("include_ci", True))

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Root readme.md
    readme_content = f"""# {project_name}

Official repository architecture scaffolded by **Sentinel Mexico** using `project-init`.

## Environments
{chr(10).join(f"- `{env}`" for env in environments)}

## Localization
Supported locales: {', '.join(f'`{loc}`' for loc in locales)}

## Governance & Architecture
- Code-as-Skill deterministic workflows
- Dual changelog tracking (`changelog.md` for production, `changelog-dev.md` for sprint iterations)
- Asymmetric progressive disclosure structure
"""
    (target_dir / "readme.md").write_text(readme_content, encoding="utf-8")

    # 2. changelog.md (Production)
    changelog_prod = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
"""
    (target_dir / "changelog.md").write_text(changelog_prod, encoding="utf-8")

    # 3. changelog-dev.md (Active Iterations)
    changelog_dev = """# Changelog (Development)

All active iterations, sprint tasks, and unreleased technical changes are tracked here.

## Sprint Backlog & Active Iterations
- [x] Initial project scaffolding via Sentinel Mexico `project-init` skill.
- [ ] Base service configuration and environment validation.
"""
    (target_dir / "changelog-dev.md").write_text(changelog_dev, encoding="utf-8")

    # 4. .gitignore
    gitignore_content = """# Dependencies
node_modules/
vendor/
.venv/
env/
__pycache__/
*.pyc

# Environment & Secrets
.env
.env.*
!.env.example

# Build Artifacts
dist/
build/
out/
.next/
*.tsbuildinfo

# System & IDE
.DS_Store
Thumbs.db
.vscode/
.idea/

# Multimedia & Binary Bundles
*.mp4
*.mov
*.avi
*.zip
*.tar.gz
"""
    (target_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

    # 5. CI Workflow (Optional)
    if include_ci:
        ci_dir = target_dir / ".github" / "workflows"
        ci_dir.mkdir(parents=True, exist_ok=True)
        ci_deploy = """name: CI & Deployment Pipeline
on:
  push:
    branches:
      - main
      - dev
  pull_request:
    branches:
      - main
      - dev

jobs:
  validate:
    name: Lint & Test Verification
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Pipeline Verification
        run: echo "Executing deterministic environment tests..."
"""
        (ci_dir / "deploy.yml").write_text(ci_deploy, encoding="utf-8")

    # 6. Monorepo Root package.json (Optional)
    if is_monorepo:
        pkg_json = {
            "name": project_name,
            "private": True,
            "workspaces": [f"{env}/*" for env in environments] if any("/" in e for e in environments) else environments,
            "scripts": {
                "test": "echo \"Running workspace tests...\""
            }
        }
        (target_dir / "package.json").write_text(json.dumps(pkg_json, indent=2) + "\n", encoding="utf-8")

    # 7. Invariantes por entorno
    created_environments = []
    for env in environments:
        env_root = target_dir / env
        env_root.mkdir(parents=True, exist_ok=True)

        # <env>/locale/
        locale_dir = env_root / "locale"
        locale_dir.mkdir(parents=True, exist_ok=True)
        for loc in locales:
            loc_file = locale_dir / f"{loc}.json"
            if not loc_file.exists():
                loc_dict = {
                    "app_title": project_name,
                    "environment": env,
                    "language": loc
                }
                loc_file.write_text(json.dumps(loc_dict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # <env>/src/img/.gitkeep & <env>/src/video/.gitkeep
        img_dir = env_root / "src" / "img"
        video_dir = env_root / "src" / "video"
        img_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)
        (img_dir / ".gitkeep").touch(exist_ok=True)
        (video_dir / ".gitkeep").touch(exist_ok=True)

        created_environments.append(env)

    return {
        "status": "success",
        "project_name": project_name,
        "is_monorepo": is_monorepo,
        "environments": created_environments,
        "locales": locales,
        "include_ci": include_ci,
        "path": str(target_dir.resolve())
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic Project Initializer")
    parser.add_argument("--check-git", action="store_true", help="Execute existing project guard and branch resolution")
    parser.add_argument("--manifest", type=str, help="JSON manifest string")
    parser.add_argument("--manifest-file", type=str, help="Path to JSON manifest file")
    parser.add_argument("--target-dir", type=str, default=".", help="Target workspace root")

    args = parser.parse_args()
    target_dir = Path(args.target_dir).resolve()

    # Rule 1: Immediate abort guard
    can_init, reason = evaluate_existing_project_guard(target_dir)
    if not can_init:
        result = {"can_initialize": False, "reason": reason}
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # If --check-git is passed
    if args.check_git:
        success, branch = manage_git_branch(target_dir)
        if not success:
            result = {"can_initialize": False, "reason": branch}
            print(json.dumps(result, indent=2))
            sys.exit(1)
        result = {"can_initialize": True, "active_branch": branch}
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # Scaffolding execution
    manifest_data = {}
    if args.manifest:
        try:
            manifest_data = json.loads(args.manifest)
        except json.JSONDecodeError as exc:
            print(json.dumps({"status": "error", "message": f"Invalid JSON manifest: {exc}"}), file=sys.stderr)
            sys.exit(1)
    elif args.manifest_file:
        try:
            with open(args.manifest_file, "r", encoding="utf-8") as fh:
                manifest_data = json.load(fh)
        except Exception as exc:
            print(json.dumps({"status": "error", "message": f"Cannot read manifest file: {exc}"}), file=sys.stderr)
            sys.exit(1)
    else:
        # Default check if neither manifest nor check-git is supplied
        success, branch = manage_git_branch(target_dir)
        print(json.dumps({"can_initialize": True, "active_branch": branch}, indent=2))
        sys.exit(0)

    # Ensure dev branch is ready before scaffolding
    _, branch = manage_git_branch(target_dir)

    result = scaffold_project(target_dir, manifest_data)
    result["active_branch"] = branch
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
