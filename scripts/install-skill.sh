#!/usr/bin/env bash
# ==============================================================================
# Sentinel Mexico · Deterministic Multi-Platform Agent Skills Installer
# Standard: agentskills.io
# Inspired by: vercel-labs/skills & skillinstaller
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

# Providers Matrix: slug -> "project_rel_path|user_rel_path"
# Paths without leading ~ or / are evaluated relative to project root or $HOME.
declare -A MATRIX=(
  ["universal"]=".agents/skills|.config/agents/skills"
  ["adal"]=".adal/skills|.adal/skills"
  ["amp"]=".agents/skills|.config/agents/skills"
  ["antigravity"]=".agent/skills|.gemini/antigravity/skills"
  ["augment"]=".augment/skills|.augment/skills"
  ["claude-code"]=".claude/skills|.claude/skills"
  ["cline"]=".agents/skills|.agents/skills"
  ["codebuddy"]=".codebuddy/skills|.codebuddy/skills"
  ["codex"]=".agents/skills|.codex/skills"
  ["command-code"]=".commandcode/skills|.commandcode/skills"
  ["continue"]=".continue/skills|.continue/skills"
  ["cortex"]=".cortex/skills|.snowflake/cortex/skills"
  ["crush"]=".crush/skills|.config/crush/skills"
  ["cursor"]=".agents/skills|.cursor/skills"
  ["droid"]=".factory/skills|.factory/skills"
  ["gemini-cli"]=".agents/skills|.gemini/skills"
  ["github-copilot"]=".agents/skills|.copilot/skills"
  ["goose"]=".goose/skills|.config/goose/skills"
  ["iflow-cli"]=".iflow/skills|.iflow/skills"
  ["junie"]=".junie/skills|.junie/skills"
  ["kilo"]=".kilocode/skills|.kilocode/skills"
  ["kimi-cli"]=".agents/skills|.config/agents/skills"
  ["kiro-cli"]=".kiro/skills|.kiro/skills"
  ["kode"]=".kode/skills|.kode/skills"
  ["mcpjam"]=".mcpjam/skills|.mcpjam/skills"
  ["mistral-vibe"]=".vibe/skills|.vibe/skills"
  ["mux"]=".mux/skills|.mux/skills"
  ["neovate"]=".neovate/skills|.neovate/skills"
  ["openclaw"]="skills|.openclaw/skills"
  ["opencode"]=".agents/skills|.config/opencode/skills"
  ["openhands"]=".openhands/skills|.openhands/skills"
  ["pi"]=".pi/skills|.pi/agent/skills"
  ["pochi"]=".pochi/skills|.pochi/skills"
  ["qoder"]=".qoder/skills|.qoder/skills"
  ["qwen-code"]=".qwen/skills|.qwen/skills"
  ["replit"]=".agents/skills|.config/agents/skills"
  ["roo"]=".roo/skills|.roo/skills"
  ["trae"]=".trae/skills|.trae/skills"
  ["trae-cn"]=".trae/skills|.trae-cn/skills"
  ["windsurf"]=".windsurf/skills|.codeium/windsurf/skills"
  ["zencoder"]=".zencoder/skills|.zencoder/skills"
)

# Defaults
SKILLS_ARG=()
PROVIDERS_ARG="universal"
SCOPE="project"
METHOD="symlink"
PROJECT_ROOT="$(pwd)"
FORCE=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --skill <name|all>        Skill name to install, or 'all'. Can be specified multiple times.
  --providers <slugs|all>   Comma-separated provider slugs (e.g. 'antigravity,claude-code') or 'all' (default: 'universal')
  --scope <project|user|both> Installation scope: 'project', 'user', or 'both' (default: 'project')
  --method <symlink|copy>   Deployment method: 'symlink' or 'copy' (default: 'symlink')
  --target-dir <path>       Target workspace/project directory (default: current working directory)
  --force                   Overwrite existing destination files or symlinks
  -h, --help                Show this help message
EOF
}

# Parse Arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)
      if [[ -z "${2:-}" ]]; then echo "Error: --skill requires an argument" >&2; exit 1; fi
      SKILLS_ARG+=("$2")
      shift 2
      ;;
    --providers)
      if [[ -z "${2:-}" ]]; then echo "Error: --providers requires an argument" >&2; exit 1; fi
      PROVIDERS_ARG="$2"
      shift 2
      ;;
    --scope)
      if [[ -z "${2:-}" ]]; then echo "Error: --scope requires an argument" >&2; exit 1; fi
      SCOPE="$2"
      shift 2
      ;;
    --method)
      if [[ -z "${2:-}" ]]; then echo "Error: --method requires an argument" >&2; exit 1; fi
      METHOD="$2"
      shift 2
      ;;
    --target-dir)
      if [[ -z "${2:-}" ]]; then echo "Error: --target-dir requires an argument" >&2; exit 1; fi
      PROJECT_ROOT="$(cd "$2" && pwd)"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ${#SKILLS_ARG[@]} -eq 0 ]]; then
  echo "Error: No skills specified. Use --skill <name|all>" >&2
  usage
  exit 1
fi

# Resolve Skills List
RESOLVED_SKILLS=()
if [[ " ${SKILLS_ARG[*]} " =~ [[:space:]]all[[:space:]] ]]; then
  if [[ -d "$SKILLS_DIR" ]]; then
    while IFS= read -r -d '' dir; do
      RESOLVED_SKILLS+=("$(basename "$dir")")
    done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -print0)
  fi
  if [[ ${#RESOLVED_SKILLS[@]} -eq 0 ]]; then
    echo "Notice: No skills currently exist in $SKILLS_DIR."
  fi
else
  for s in "${SKILLS_ARG[@]}"; do
    IFS=',' read -ra SPLIT <<< "$s"
    for item in "${SPLIT[@]}"; do
      RESOLVED_SKILLS+=("$item")
    done
  done
fi

# Resolve Providers List
RESOLVED_PROVIDERS=()
if [[ "$PROVIDERS_ARG" == "all" ]]; then
  for p in "${!MATRIX[@]}"; do
    RESOLVED_PROVIDERS+=("$p")
  done
else
  IFS=',' read -ra ADAPTERS <<< "$PROVIDERS_ARG"
  for p in "${ADAPTERS[@]}"; do
    p="$(echo "$p" | xargs)"
    if [[ -n "${MATRIX[$p]:-}" ]]; then
      RESOLVED_PROVIDERS+=("$p")
    else
      echo "Warning: Provider slug '$p' not found in matrix. Skipping." >&2
    fi
  done
fi

if [[ ${#RESOLVED_PROVIDERS[@]} -eq 0 ]]; then
  echo "Error: No valid providers selected." >&2
  exit 1
fi

echo "======================================================================"
echo " Sentinel Mexico · Agent Skills Installer"
echo " Standard: agentskills.io | Mode: $METHOD | Scope: $SCOPE"
echo "======================================================================"
echo "Target Project Root: $PROJECT_ROOT"
echo "User Home:           $HOME"
echo "Skills to install:   ${RESOLVED_SKILLS[*]:-(none)}"
echo "Target Providers:    ${RESOLVED_PROVIDERS[*]}"
echo "----------------------------------------------------------------------"

# Deduplication Set to avoid redundant installs in same path
declare -A PROCESSED_PATHS

install_single_target() {
  local skill_name="$1"
  local src_path="$SKILLS_DIR/$skill_name"
  local dest_path="$2"
  local provider="$3"
  local target_scope="$4"

  if [[ -n "${PROCESSED_PATHS["$dest_path"]:-}" ]]; then
    echo "  [Deduplicated] $provider ($target_scope) shares $dest_path"
    return 0
  fi
  PROCESSED_PATHS["$dest_path"]=1

  if [[ ! -d "$src_path" ]]; then
    echo "  [Error] Source skill directory not found: $src_path" >&2
    return 1
  fi

  local parent_dir
  parent_dir="$(dirname "$dest_path")"
  mkdir -p "$parent_dir"

  if [[ -e "$dest_path" || -L "$dest_path" ]]; then
    if [[ "$FORCE" == true ]]; then
      rm -rf "$dest_path"
    else
      echo "  [Skipped] Destination already exists: $dest_path (use --force to overwrite)"
      return 0
    fi
  fi

  if [[ "$METHOD" == "symlink" ]]; then
    ln -s "$src_path" "$dest_path"
    echo "  [Symlink] $skill_name -> $dest_path"
  else
    cp -R "$src_path" "$dest_path"
    echo "  [Copy]    $skill_name -> $dest_path"
  fi
}

for skill in "${RESOLVED_SKILLS[@]}"; do
  echo "Deploying skill: $skill"
  for provider in "${RESOLVED_PROVIDERS[@]}"; do
    raw_paths="${MATRIX[$provider]}"
    proj_rel="${raw_paths%%|*}"
    user_rel="${raw_paths##*|}"

    if [[ "$SCOPE" == "project" || "$SCOPE" == "both" ]]; then
      dest_proj="$PROJECT_ROOT/$proj_rel/$skill"
      install_single_target "$skill" "$dest_proj" "$provider" "project"
    fi

    if [[ "$SCOPE" == "user" || "$SCOPE" == "both" ]]; then
      dest_user="$HOME/$user_rel/$skill"
      install_single_target "$skill" "$dest_user" "$provider" "user"
    fi
  done
done

echo "======================================================================"
echo "Installation process complete."
echo "======================================================================"
