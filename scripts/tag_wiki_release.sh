#!/usr/bin/env bash
set -euo pipefail

usage() {
  command_name="$(basename "$0")"
  echo "Usage: $command_name VERSION FULL_COMMIT_SHA [--create] [--push]" >&2
  echo "Example: $command_name 1.1.0 0123456789abcdef0123456789abcdef01234567 --create --push" >&2
}

if (( $# < 2 || $# > 4 )); then
  usage
  exit 2
fi

release_version="$1"
release_commit="$2"
shift 2

create_tag=false
push_tag=false
for option in "$@"; do
  case "$option" in
    --create) create_tag=true ;;
    --push) create_tag=true; push_tag=true ;;
    *) usage; exit 2 ;;
  esac
done

if [[ ! "$release_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "ERROR: VERSION must be semantic version syntax without a leading v." >&2
  exit 2
fi
if [[ ! "$release_commit" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: FULL_COMMIT_SHA must be a full lowercase 40-character SHA." >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

git fetch --quiet origin main --tags
git cat-file -e "${release_commit}^{commit}"
if ! git merge-base --is-ancestor "$release_commit" origin/main; then
  echo "ERROR: $release_commit is not reachable from origin/main." >&2
  exit 1
fi

release_tag="wiki-v${release_version}"
remote_tag_sha="$(git ls-remote --tags origin "refs/tags/${release_tag}^{}" | awk '{print $1}')"
if [[ -z "$remote_tag_sha" ]]; then
  remote_tag_sha="$(git ls-remote --tags origin "refs/tags/${release_tag}" | awk '{print $1}')"
fi
if [[ -n "$remote_tag_sha" ]]; then
  echo "ERROR: remote tag $release_tag already exists; release tags must never be moved." >&2
  exit 1
fi

if [[ "$create_tag" != true ]]; then
  echo "Dry run passed: $release_tag can be created at $release_commit"
  echo "Create locally: $0 $release_version $release_commit --create"
  echo "Create and push: $0 $release_version $release_commit --push"
  exit 0
fi

if git show-ref --verify --quiet "refs/tags/$release_tag"; then
  local_tag_sha="$(git rev-list -n 1 "$release_tag")"
  if [[ "$local_tag_sha" != "$release_commit" ]]; then
    echo "ERROR: local tag $release_tag points to $local_tag_sha, not $release_commit." >&2
    exit 1
  fi
else
  git tag -a "$release_tag" "$release_commit" -m "Nepal Energy Wiki v${release_version}"
  echo "Created annotated tag $release_tag at $release_commit"
fi

if [[ "$push_tag" == true ]]; then
  git push origin "refs/tags/$release_tag"
  echo "Pushed $release_tag to origin"
else
  echo "Tag is local only. Push with: git push origin refs/tags/$release_tag"
fi
