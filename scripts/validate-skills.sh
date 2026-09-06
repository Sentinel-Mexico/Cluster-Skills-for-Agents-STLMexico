#!/usr/bin/env bash
# ==============================================================================
# Sentinel Mexico · Agent Skills Validation Engine
# Standard: agentskills.io
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Scanning repository for SKILL.md specifications..."
FAILED=0

# Use python to perform deterministic parsing without external dependencies
python3 - <<'PYCHECK'
import os
import re
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "__file__" in globals() else os.getcwd()
targets = []

for root, dirs, files in os.walk(repo_root):
    if ".git" in root:
        continue
    for f in files:
        if f == "SKILL.md":
            targets.append(os.path.join(root, f))

if not targets:
    print("Warning: No SKILL.md files found.")
    sys.exit(0)

has_error = False

for target in targets:
    rel_path = os.path.relpath(target, repo_root)
    dir_name = os.path.basename(os.path.dirname(target))
    
    with open(target, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
        content = "".join(lines)
    
    print(f"\n[Auditing] {rel_path} ({len(lines)} lines)")
    
    # 1. Line count ceiling check (<500 lines)
    if len(lines) > 500:
        print(f"  ❌ ERROR: {rel_path} exceeds 500 lines ceiling ({len(lines)} lines). Move long manuals to references/.")
        has_error = True
    else:
        print(f"  ✓ Line count constraint passed ({len(lines)}/500 lines)")

    # 2. YAML Frontmatter check
    if not content.startswith("---"):
        print(f"  ❌ ERROR: {rel_path} does not start with YAML frontmatter delimiter '---'.")
        has_error = True
        continue
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"  ❌ ERROR: {rel_path} has malformed frontmatter (closing delimiter missing).")
        has_error = True
        continue

    fm_raw = parts[1]
    
    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", fm_raw, re.MULTILINE)
    if not name_match:
        print(f"  ❌ ERROR: {rel_path} is missing required 'name' field.")
        has_error = True
    else:
        skill_name = name_match.group(1).strip().strip("'\"")
        if not re.match(r"^[a-z0-9-]+$", skill_name):
            print(f"  ❌ ERROR: Name '{skill_name}' must be kebab-case (^[a-z0-9-]+$).")
            has_error = True
        elif dir_name != "skill-template" and skill_name != dir_name:
            print(f"  ❌ ERROR: Skill name '{skill_name}' does not match parent directory name '{dir_name}'.")
            has_error = True
        else:
            print(f"  ✓ Name valid: '{skill_name}'")

    # Extract description
    desc_match = re.search(r"^description:\s*(.+)$", fm_raw, re.MULTILINE)
    if not desc_match:
        print(f"  ❌ ERROR: {rel_path} is missing required 'description' field.")
        has_error = True
    else:
        desc = desc_match.group(1).strip().strip("'\"")
        if len(desc) < 1 or len(desc) > 1024:
            print(f"  ❌ ERROR: Description length ({len(desc)}) violates [1, 1024] char limits.")
            has_error = True
        else:
            print(f"  ✓ Description valid ({len(desc)} characters)")

    # Author verification
    if "Sentinel Mexico" not in fm_raw:
        print(f"  ❌ ERROR: {rel_path} must cite 'Sentinel Mexico' in author metadata.")
        has_error = True
    else:
        print(f"  ✓ Author metadata verified")

if has_error:
    sys.exit(1)

print("\n✅ All SKILL.md files successfully validated against agentskills.io standard.")
PYCHECK
