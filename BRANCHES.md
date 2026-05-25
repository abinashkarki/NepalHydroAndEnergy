# Branch Discipline — Nepal Energy Wiki

> **Rule: No new branches without explicit owner approval.**

## Active Branches

| Branch | Worktree | Purpose | Lifecycle |
|---|---|---|---|
| `main` | `nepalEnergy/` | Production wiki + mobile UX. Deployed to transparentgov.ai. | Permanent |
| `codex/beta-features` | `nepalEnergy-mobile-ux/` | Experimental sandbox. Merge to `main` when ready. | Permanent |
| `codex/documentary-essay-work` | *(none — checkout when needed)* | Documentary prep docs, video-labs, artifacts. Sheddable after video release. | Temporary |

## Rules

1. **main is sacred.** Only merge finished, validated work. No direct commits for experiments.
2. **beta-features is the playground.** Try things here. When a feature is solid, open a merge to `main`.
3. **documentary-essay-work is disposable.** All documentary-specific files (video-labs/, documentary/, essay drafts) live here. Nothing documentary-specific merges to `main` except verified wiki content updates.
4. **No new branches.** If you need one, ask. The three above cover all current work.
5. **Worktrees are fine** for parallel access, but document them here.

## Worktrees

```
/Users/hi/projects/nepalEnergy              → main
/Users/hi/projects/nepalEnergy-mobile-ux    → codex/beta-features
```

To add a documentary worktree when needed:
```bash
git worktree add ../nepalEnergy-documentary codex/documentary-essay-work
```

## Merge Direction

```
codex/beta-features ──► main
codex/documentary-essay-work ──╳──► main  (wiki updates only, cherry-picked)
```
