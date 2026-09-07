#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel Mexico · Deterministic i18n Manager & Parity Governor
Skill: i18n-governor
Standard: agentskills.io (Code-as-Skill)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

CANDIDATE_DIR_NAMES = {
    "locale",
    "locales",
    "languages",
    "lang",
    "i18n",
    "translations",
    "messages",
}

IGNORED_DIRS = {
    "node_modules",
    ".git",
    "dist",
    ".next",
    "build",
    "coverage",
    "__pycache__",
    ".turbo",
    ".agent",
    ".agents",
    ".venv",
    "env",
    "out",
}

CANONICAL_ENGLISH_NAMES = [
    "en.json",
    "en-US.json",
    "en-us.json",
    "en_US.json",
    "en_us.json",
    "en-GB.json",
    "en_gb.json",
]


def flatten_json(data: Any, prefix: str = "") -> Dict[str, str]:
    items: Dict[str, str] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{prefix}.{k}" if prefix else str(k)
            items.update(flatten_json(v, new_key))
    elif isinstance(data, list):
        for idx, val in enumerate(data):
            new_key = f"{prefix}[{idx}]"
            items.update(flatten_json(val, new_key))
    else:
        items[prefix] = "" if data is None else str(data)
    return items


def unflatten_json(flat_dict: Dict[str, Any]) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    for composite_key, value in flat_dict.items():
        keys = composite_key.split(".")
        curr = root
        for i, k in enumerate(keys[:-1]):
            if k not in curr or not isinstance(curr[k], dict):
                curr[k] = {}
            curr = curr[k]
        curr[keys[-1]] = value
    return root


def discover_domains(project_root: Path) -> Dict[str, Path]:
    domains: Dict[str, Path] = {}
    for root, dirs, _ in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        for d in dirs:
            if d.lower() in CANDIDATE_DIR_NAMES:
                full_path = Path(root) / d
                rel_path = full_path.relative_to(project_root)
                parts = rel_path.parts
                if len(parts) > 1:
                    workspace = parts[0]
                    dir_tag = "/".join(parts[1:])
                    domain_id = f"{workspace}::{dir_tag}"
                else:
                    domain_id = f"root::{rel_path}"
                domains[domain_id] = full_path
    return domains


def get_canonical_file(domain_path: Path) -> Optional[Path]:
    json_files = list(domain_path.glob("*.json"))
    if not json_files:
        return None

    # Priority 1: standard English names
    for eng_name in CANONICAL_ENGLISH_NAMES:
        for jf in json_files:
            if jf.name.lower() == eng_name.lower():
                return jf

    # Priority 2: file with highest key count
    best_file = None
    max_keys = -1
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                flat = flatten_json(data)
                if len(flat) > max_keys:
                    max_keys = len(flat)
                    best_file = jf
        except Exception:
            continue
    return best_file


def audit_parity(project_root: Path) -> Tuple[int, Dict[str, Any]]:
    domains = discover_domains(project_root)
    if not domains:
        return 0, {
            "status": "synced",
            "message": "No i18n candidate directories detected in project.",
            "domains": {}
        }

    overall_missing = 0
    domains_report: Dict[str, Any] = {}

    for domain_id, domain_path in sorted(domains.items()):
        canonical_file = get_canonical_file(domain_path)
        if not canonical_file:
            domains_report[domain_id] = {
                "status": "empty",
                "message": "No valid JSON translation dictionaries in directory",
                "path": str(domain_path.relative_to(project_root))
            }
            continue

        try:
            with open(canonical_file, "r", encoding="utf-8") as fh:
                canonical_data = json.load(fh)
            canonical_flat = flatten_json(canonical_data)
        except Exception as exc:
            domains_report[domain_id] = {
                "status": "error",
                "message": f"Failed reading canonical {canonical_file.name}: {exc}"
            }
            continue

        domain_entry: Dict[str, Any] = {
            "path": str(domain_path.relative_to(project_root)),
            "canonical": canonical_file.name,
            "canonical_keys": len(canonical_flat),
            "targets": {}
        }

        all_json = sorted(list(domain_path.glob("*.json")))
        for tf in all_json:
            if tf == canonical_file:
                continue

            try:
                with open(tf, "r", encoding="utf-8") as fh:
                    target_data = json.load(fh)
                target_flat = flatten_json(target_data)
            except Exception as exc:
                domain_entry["targets"][tf.name] = {
                    "status": "error",
                    "message": f"Failed parsing JSON: {exc}"
                }
                overall_missing += 1
                continue

            missing_keys = []
            for k in canonical_flat:
                if k not in target_flat or str(target_flat[k]).strip() == "":
                    missing_keys.append(k)

            if missing_keys:
                domain_entry["targets"][tf.name] = {
                    "status": "missing_keys",
                    "missing_count": len(missing_keys),
                    "missing_keys": missing_keys
                }
                overall_missing += len(missing_keys)
            else:
                domain_entry["targets"][tf.name] = {
                    "status": "synced",
                    "keys_count": len(target_flat)
                }

        domains_report[domain_id] = domain_entry

    if overall_missing > 0:
        return 1, {
            "status": "missing_keys",
            "total_missing_keys": overall_missing,
            "domains": domains_report
        }

    return 0, {
        "status": "synced",
        "total_missing_keys": 0,
        "domains": domains_report
    }


def find_domain_by_query(domains: Dict[str, Path], query: str) -> Optional[Tuple[str, Path]]:
    q_norm = query.strip().lower()
    for d_id, path in domains.items():
        if d_id.lower() == q_norm:
            return d_id, path
        if d_id.lower().startswith(f"{q_norm}::"):
            return d_id, path
        if q_norm in str(path).lower():
            return d_id, path
    return None


def extract_diff(project_root: Path, env_query: str, target_lang: str) -> Dict[str, Any]:
    domains = discover_domains(project_root)
    match = find_domain_by_query(domains, env_query)
    if not match:
        return {
            "status": "error",
            "message": f"Domain environment '{env_query}' not found. Discovered: {list(domains.keys())}"
        }

    domain_id, domain_path = match
    canonical_file = get_canonical_file(domain_path)
    if not canonical_file:
        return {
            "status": "error",
            "message": f"No canonical dictionary found in domain '{domain_id}'"
        }

    with open(canonical_file, "r", encoding="utf-8") as fh:
        canonical_flat = flatten_json(json.load(fh))

    lang_ext = target_lang if target_lang.endswith(".json") else f"{target_lang}.json"
    target_path = domain_path / lang_ext

    target_flat: Dict[str, str] = {}
    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as fh:
                target_flat = flatten_json(json.load(fh))
        except Exception:
            target_flat = {}

    diff: Dict[str, str] = {}
    for k, v in canonical_flat.items():
        if k not in target_flat or str(target_flat[k]).strip() == "":
            diff[k] = v

    return {
        "status": "ok",
        "domain": domain_id,
        "target": target_lang,
        "target_file": str(target_path.relative_to(project_root)),
        "canonical_file": canonical_file.name,
        "missing_count": len(diff),
        "diff": diff
    }


def apply_patch(project_root: Path, env_query: str, target_lang: str, patch_dict: Dict[str, Any]) -> Dict[str, Any]:
    domains = discover_domains(project_root)
    match = find_domain_by_query(domains, env_query)
    if not match:
        return {
            "status": "error",
            "message": f"Domain environment '{env_query}' not found. Discovered: {list(domains.keys())}"
        }

    domain_id, domain_path = match
    lang_ext = target_lang if target_lang.endswith(".json") else f"{target_lang}.json"
    target_path = domain_path / lang_ext

    existing_flat: Dict[str, Any] = {}
    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as fh:
                existing_flat = flatten_json(json.load(fh))
        except Exception:
            existing_flat = {}

    flat_patch = flatten_json(patch_dict)
    for k, v in flat_patch.items():
        existing_flat[k] = v

    unflattened = unflatten_json(existing_flat)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as fh:
        json.dump(unflattened, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    return {
        "status": "ok",
        "domain": domain_id,
        "target": target_lang,
        "target_file": str(target_path.relative_to(project_root)),
        "keys_injected": len(flat_patch),
        "total_keys": len(existing_flat)
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic i18n Manager & Parity Governor")
    parser.add_argument("--audit", action="store_true", help="Execute complete parity audit across all translation domains")
    parser.add_argument("--get-diff", action="store_true", help="Extract missing keys diff for a specific environment and target")
    parser.add_argument("--apply-patch", type=str, help="JSON string containing missing key translations to inject")
    parser.add_argument("--patch-file", type=str, help="Path to JSON file containing patch dictionary")
    parser.add_argument("--env", type=str, help="Domain environment identifier (e.g. 'frontend', 'backend::locale')")
    parser.add_argument("--target", type=str, help="Target language code (e.g. 'es', 'fr', 'pt-BR')")
    parser.add_argument("--project-root", type=str, default=".", help="Root of project workspace")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.audit:
        code, res = audit_parity(project_root)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(code)

    if args.get_diff:
        if not args.env or not args.target:
            print(json.dumps({"status": "error", "message": "--get-diff requires both --env and --target"}), file=sys.stderr)
            sys.exit(1)
        res = extract_diff(project_root, args.env, args.target)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("status") == "ok" else 1)

    if args.apply_patch or args.patch_file:
        if not args.env or not args.target:
            print(json.dumps({"status": "error", "message": "Applying patch requires both --env and --target"}), file=sys.stderr)
            sys.exit(1)

        patch_dict = {}
        if args.apply_patch:
            try:
                patch_dict = json.loads(args.apply_patch)
            except Exception as exc:
                print(json.dumps({"status": "error", "message": f"Invalid JSON in --apply-patch: {exc}"}), file=sys.stderr)
                sys.exit(1)
        elif args.patch_file:
            try:
                with open(args.patch_file, "r", encoding="utf-8") as fh:
                    patch_dict = json.load(fh)
            except Exception as exc:
                print(json.dumps({"status": "error", "message": f"Cannot read patch-file: {exc}"}), file=sys.stderr)
                sys.exit(1)

        res = apply_patch(project_root, args.env, args.target, patch_dict)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res.get("status") == "ok" else 1)

    parser.print_help(sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
