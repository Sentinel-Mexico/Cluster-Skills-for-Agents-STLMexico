#!/usr/bin/env bash

set -euo pipefail

# Deterministic multi‑platform skill installer
# Usage:
#   ./install-skill.sh --all
#   ./install-skill.sh --skill <skill-name> [--skill <skill-name> ...] [--force]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}") && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

# Platform matrix (project scope | user scope)
declare -A MATRIX=(
  [universal]=".agents/skills/ ~/.config/agents/skills/"
  [antigravity]=".agent/skills/ ~/.gemini/antigravity/skills/"
  [claude-code]=".claude/skills/ ~/.claude/skills/"
  [windsurf]=".windsurf/skills/ ~/.codeium/windsurf/skills/"
  [openclaw]="skills/ ~/.openclaw/skills/"
  [roo]=".roo/skills/ ~/.roo/skills/"
  [continue]=".continue/skills/ ~/.continue/skills/"
  [cortex]=".cortex/skills/ ~/.snowflake/cortex/skills/"
  [droid]=".factory/skills/ ~/.factory/skills/"
  [kiro-cli]=".kiro/skills/ ~/.kiro/skills/"
  [trae]=".trae/skills/ ~/.trae/skills/"
  [trae-cn]=".trae/skills/ ~/.trae-cn/skills/"
  [augment]=".augment/skills/ ~/.augment/skills/"
  [codebuddy]=".codebuddy/skills/ ~/.codebuddy/skills/"
  [command-code]=".commandcode/skills/ ~/.commandcode/skills/"
  [crush]=".crush/skills/ ~/.config/crush/skills/"
  [goose]=".goose/skills/ ~/.config/goose/skills/"
  [iflow-cli]=".iflow/skills/ ~/.iflow/skills/"
  [junie]=".junie/skills/ ~/.junie/skills/"
  [kilo]=".kilocode/skills/ ~/.kilocode/skills/"
  [kode]=".kode/skills/ ~/.kode/skills/"
  [mcpjam]=".mcpjam/skills/ ~/.mcpjam/skills/"
  [mistral-vibe]=".vibe/skills/ ~/.vibe/skills/"
  [mux]=".mux/skills/ ~/.mux/skills/"
  [neovate]=".neovate/skills/ ~/.neovate/skills/"
  [openhands]=".openhands/skills/ ~/.openhands/skills/"
  [pi]=".pi/skills/ ~/.pi/agent/skills/"
  [pochi]=".pochi/skills/ ~/.pochi/skills/"
  [qoder]=".qoder/skills/ ~/.qoder/skills/"
  [qwen-code]=".qwen/skills/ ~/.qwen/skills/"
  [zencoder]=".zencoder/skills/ ~/.zencoder/skills/"
  [adal]=".adal/skills/ ~/.adal/skills/"
)

FORCE=false
SKILL_LIST=()

while (( $# )); do
  case "$1" in
    --all)
      SKILL_LIST=("ALL")
      shift
      ;;
    --skill)
      if [[ -z "${2-}" ]]; then echo "Missing argument for --skill"; exit 1; fi
      SKILL_LIST+=("$2")
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ ${#SKILL_LIST[@]} -eq 0 ]]; then
  echo "No skills specified. Use --all or --skill <name>."
  exit 1
fi

install_skill() {
  local skill_name="$1"
  local skill_path="$SKILLS_DIR/$skill_name"
  if [[ ! -d "$skill_path" ]]; then
    echo "⚠️ Skill directory $skill_path does not exist, skipping."
    return
  fi

  for agent in "${!MATRIX[@]}"; do
    IFS=' ' read -r proj_dir user_dir <<< "${MATRIX[$agent]}"
    for dest_base in "$proj_dir" "$user_dir"; do
      dest_path="$HOME/$dest_base/$skill_name"
      mkdir -p "$(dirname "$dest_path")"
      if [[ -e "$dest_path" && "$FORCE" == false ]]; then
        echo "⏭️ $dest_path exists, use --force to overwrite."
        continue
      fi
      # Use symlink when possible (project scope), copy for user scope as fallback
      if [[ "$dest_base" == "$proj_dir" ]]; then
        ln -sfn "$skill_path" "$dest_path"
        echo "🔗 Linked $skill_name to $dest_path"
      else
        cp -r "$skill_path" "$dest_path"
        echo "📋 Copied $skill_name to $dest_path"
      fi
    done
  done
}

if [[ "${SKILL_LIST[0]}" == "ALL" ]]; then
  for dir in "$SKILLS_DIR"/*/; do
    [[ -d "$dir" ]] || continue
    skill=$(basename "$dir")
    install_skill "$skill"
  done
else
  for skill in "${SKILL_LIST[@]}"; do
    install_skill "$skill"
  done
fi

echo "✅ Installation complete."
