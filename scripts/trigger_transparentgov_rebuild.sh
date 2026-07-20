#!/usr/bin/env bash
set -euo pipefail

usage() {
  command_name="$(basename "$0")"
  echo "Usage: $command_name FULL_WIKI_COMMIT_SHA [--execute]" >&2
  echo "Without --execute, the script performs read-only preflight checks." >&2
}

if (( $# < 1 || $# > 2 )); then
  usage
  exit 2
fi

wiki_commit="$1"
execute=false
if (( $# == 2 )); then
  if [[ "$2" != "--execute" ]]; then
    usage
    exit 2
  fi
  execute=true
fi

if [[ ! "$wiki_commit" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: provide the full lowercase 40-character wiki commit SHA." >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git fetch --quiet origin main
git cat-file -e "${wiki_commit}^{commit}"
if ! git merge-base --is-ancestor "$wiki_commit" origin/main; then
  echo "ERROR: wiki commit $wiki_commit is not reachable from origin/main." >&2
  exit 1
fi

parent_repo="abinashkarki/TransparentGov"
parent_branch="main"
parent_commit="$(gh api "repos/${parent_repo}/commits/${parent_branch}" --jq .sha)"
parent_tree="$(gh api "repos/${parent_repo}/git/commits/${parent_commit}" --jq .tree.sha)"

echo "Preflight passed. Wiki commit: $wiki_commit"
echo "TransparentGov parent: $parent_commit"
echo "Required Coolify build argument: NEPAL_ENERGY_REF=$wiki_commit"

if [[ "$execute" != true ]]; then
  echo "No remote state changed. After pinning Coolify, run:"
  echo "CONFIRM_COOLIFY_REF=$wiki_commit $0 $wiki_commit --execute"
  exit 0
fi

if [[ "${CONFIRM_COOLIFY_REF:-}" != "$wiki_commit" ]]; then
  echo "ERROR: set CONFIRM_COOLIFY_REF=$wiki_commit after confirming the Coolify build argument." >&2
  exit 1
fi

trigger_message="deploy: rebuild with Nepal Energy ${wiki_commit}"
trigger_commit="$(
  gh api --method POST "repos/${parent_repo}/git/commits" \
    -f message="$trigger_message" \
    -f tree="$parent_tree" \
    -F "parents[]=$parent_commit" \
    --jq .sha
)"

gh api --method PATCH "repos/${parent_repo}/git/refs/heads/${parent_branch}" \
  -f sha="$trigger_commit" \
  -F force=false \
  --silent

echo "Created TransparentGov trigger commit $trigger_commit"
echo "Coolify should now build the pinned wiki commit instead of reusing the parent image."
