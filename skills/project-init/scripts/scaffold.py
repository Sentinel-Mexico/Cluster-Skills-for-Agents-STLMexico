#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Deterministic Project Scaffolding Engine
Skill: project-init
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, Any, Tuple, Optional, List

LOCKFILE_NAME = ".sentinel-init.lock"

# Whitelist of allowed entries in a new/fresh GitHub or Agent repository
WHITELIST_EXACT = {
    ".git",
    ".gitignore",
    ".gitattributes",
    ".agent",
    ".agents",
    ".github",
    ".ds_store",
    "thumbs.db",
}

WHITELIST_STEMS = {
    "readme",
    "license",
    "licence",
    "copying",
}

DEV_BRANCH_CANDIDATES = ["dev", "developer", "devel", "development"]


def is_whitelisted(entry_name: str) -> bool:
    """Checks if an entry belongs to the initial bootstrap whitelist."""
    name_lower = entry_name.lower()
    if name_lower in WHITELIST_EXACT:
        return True
    p = Path(name_lower)
    if p.stem in WHITELIST_STEMS:
        return True
    return False


def evaluate_existing_project_guard(target_dir: Path) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Evaluates whether the directory is clean for initialization.
    1. Checks if .sentinel-init.lock exists -> abort with already_initialized.
    2. Evaluates non-whitelisted files/directories. If any exist -> abort with existing_codebase.
    Returns: (can_initialize, reason, message)
    """
    if not target_dir.exists():
        return True, None, None

    lockfile_path = target_dir / LOCKFILE_NAME
    if lockfile_path.is_file():
        return (
            False,
            "already_initialized",
            "El proyecto ya fue inicializado previamente con project-init (lockfile detectado).",
        )

    unexpected_entries: List[str] = []
    for item in target_dir.iterdir():
        if is_whitelisted(item.name):
            continue
        unexpected_entries.append(item.name)

    if unexpected_entries:
        items_preview = ", ".join(sorted(unexpected_entries)[:5])
        suffix = "..." if len(unexpected_entries) > 5 else ""
        return (
            False,
            "existing_codebase",
            f"Se detectó código o dependencias existentes en el repositorio ({items_preview}{suffix}). project-init solo debe ejecutarse en repositorios nuevos.",
        )

    return True, None, None


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

    # In case of an empty repository with no commits yet:
    run_git_cmd(["git", "symbolic-ref", "HEAD", "refs/heads/dev"], target_dir)
    return True, "dev"


def scaffold_project(target_dir: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
    project_name = manifest.get("project_name", target_dir.name or "sentinel-project")
    is_monorepo = bool(manifest.get("is_monorepo", False))
    environments = manifest.get("environments", ["app"])
    locales = manifest.get("locales", ["en", "es"])
    include_ci = bool(manifest.get("include_ci", True))

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Root readme.md (preserve if already exists)
    readme_path = target_dir / "readme.md"
    if not readme_path.exists() and not (target_dir / "README.md").exists():
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
        readme_path.write_text(readme_content, encoding="utf-8")

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

    # 4. .gitignore with protected lockfile entry
    gitignore_path = target_dir / ".gitignore"
    if gitignore_path.exists():
        current_gitignore = gitignore_path.read_text(encoding="utf-8")
        if LOCKFILE_NAME not in current_gitignore:
            updated_gitignore = (
                current_gitignore.rstrip()
                + f"\n\n# Sentinel Init Lockfile\n{LOCKFILE_NAME}\n"
            )
            gitignore_path.write_text(updated_gitignore, encoding="utf-8")
    else:
        gitignore_content = f"""# Dependencies
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

# Sentinel Init Lockfile
{LOCKFILE_NAME}

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
        gitignore_path.write_text(gitignore_content, encoding="utf-8")

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

    # 8. Run-Once Lockfile
    lock_data = {
        "initialized_at": datetime.now(timezone.utc).isoformat(),
        "project_name": project_name,
        "architecture": "monorepo" if is_monorepo else "polyrepo",
        "is_monorepo": is_monorepo,
        "environments": created_environments,
        "locales": locales,
        "include_ci": include_ci,
        "generator": "project-init",
        "version": "1.2.0",
    }
    (target_dir / LOCKFILE_NAME).write_text(
        json.dumps(lock_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    return {
        "status": "success",
        "project_name": project_name,
        "is_monorepo": is_monorepo,
        "environments": created_environments,
        "locales": locales,
        "include_ci": include_ci,
        "lockfile": str((target_dir / LOCKFILE_NAME).resolve()),
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

    # Rule 1: Immediate abort guard (evaluated in all modes)
    can_init, reason, msg = evaluate_existing_project_guard(target_dir)
    if not can_init:
        result = {
            "can_initialize": False,
            "reason": reason,
            "message": msg,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    # If --check-git is passed
    if args.check_git:
        success, branch = manage_git_branch(target_dir)
        if not success:
            result = {"can_initialize": False, "reason": "git_error", "message": branch}
            print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(1)
        result = {"can_initialize": True, "active_branch": branch}
        print(json.dumps(result, indent=2, ensure_ascii=False))
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
        print(json.dumps({"can_initialize": True, "active_branch": branch}, indent=2, ensure_ascii=False))
        sys.exit(0)

    # Ensure dev branch is ready before scaffolding
    _, branch = manage_git_branch(target_dir)

    result = scaffold_project(target_dir, manifest_data)
    result["active_branch"] = branch
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
