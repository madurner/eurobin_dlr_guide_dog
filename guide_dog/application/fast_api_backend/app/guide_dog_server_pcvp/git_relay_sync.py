#!/usr/bin/env python3
"""
git_relay_sync.py — Use a private GitHub repo as a two-way file relay between
two machines.

Model
-----
  --local   your real working folder (originals)
  --repo    a clone of the private repo, used purely as transport. Files are
            stored verbatim here; commit/push/pull happen here.

Each side runs the script. Push: local files missing/changed in the repo are
copied in, committed, and pushed. Pull: after a rebase pull, repo files
missing/changed locally are copied back out. Comparison is by content hash, so
nothing loops and overwrites propagate.

Auth (the easy part vs Drive)
-----------------------------
Clone over HTTPS with a fine-grained Personal Access Token scoped to this ONE
private repo (Contents: read/write), or use an SSH deploy key. Either is a
static, least-privilege, no-interactive-auth credential. One-time clone:
    git clone https://<USER>:<TOKEN>@github.com/<USER>/<REPO>.git ./relay-repo

Setup
-----
1. Create the private repo, clone it to --repo (see auth note above).
2. Run on each machine:
   python git_relay_sync.py --local ./pipeline_io --repo ./relay-repo --watch 30

History note
------------
Overwriting a file does NOT shrink the repo — git keeps every past version.
Run `--squash-history --yes` occasionally, WHEN BOTH SIDES ARE IDLE, to collapse
history to current state (force-pushes; the other side must then
`git fetch && git reset --hard origin/<branch>`). Never put this in the loop.

Conflicts
---------
If both machines write the SAME path in one cycle, git can't merge binaries; the
pull rebase is aborted that round (safe, no clobber) and retried next cycle. Use
distinct filenames per producer and it never happens.
"""

import argparse
import fnmatch
import hashlib
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXCLUDES = [".git", "__pycache__", "*.pyc", ".gitattributes", "README*", ".gitignore"]


# --------------------------------------------------------------------------- #
# git
# --------------------------------------------------------------------------- #
def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r


def ensure_repo(repo):
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"{repo} is not a git clone. Clone your private repo there first.")


def pull_rebase(repo, branch):
    git(repo, "fetch", "origin", branch, check=False)
    if git(repo, "rev-parse", "--verify", f"origin/{branch}", check=False).returncode != 0:
        return True  # remote branch doesn't exist yet (fresh repo)
    if git(repo, "rev-parse", "--verify", "HEAD", check=False).returncode != 0:
        git(repo, "checkout", "-B", branch, f"origin/{branch}")  # unborn local branch
        return True
    if git(repo, "merge", "--ff-only", f"origin/{branch}", check=False).returncode == 0:
        return True  # no local commits ahead -> fast-forward
    rb = git(repo, "rebase", f"origin/{branch}", check=False)  # replay our commits
    if rb.returncode != 0:
        git(repo, "rebase", "--abort", check=False)
        print("  rebase conflict (binary files can't merge) — aborted; retry next cycle.")
        return False
    return True


def commit_all(repo, dry_run):
    git(repo, "add", "-A")
    if not git(repo, "status", "--porcelain").stdout.strip():
        return False
    if dry_run:
        print("  [dry-run] would commit + push")
        return False
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    git(repo, "commit", "-m", f"relay {stamp}")
    return True


def push_retry(repo, branch, retries):
    for attempt in range(1, retries + 1):
        if git(repo, "push", "origin", f"HEAD:{branch}", check=False).returncode == 0:
            return True
        print(f"  push rejected (attempt {attempt}); pull --rebase and retry")
        if not pull_rebase(repo, branch):
            return False
    print("  push still failing after retries.")
    return False


def squash_history(repo, branch, yes):
    if not yes:
        sys.exit("Refusing to rewrite history without --yes. Run when BOTH sides are idle.\n"
                 "Afterwards the other machine must: git fetch && git reset --hard origin/" + branch)
    print("Squashing history to current state (force-push)...")
    git(repo, "checkout", "--orphan", "__relay_fresh")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "relay snapshot")
    git(repo, "branch", "-D", branch, check=False)
    git(repo, "branch", "-m", branch)
    git(repo, "push", "-f", "origin", f"HEAD:{branch}")
    git(repo, "gc", "--aggressive", "--prune=now", check=False)
    print("Done. Other side: git fetch && git reset --hard origin/" + branch)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def excluded(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def scan(root, excludes):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not excluded(d, excludes)]
        for fn in filenames:
            if excluded(fn, excludes):
                continue
            ap = os.path.join(dirpath, fn)
            rel = os.path.relpath(ap, root).replace(os.sep, "/")
            out[rel] = ap
    return out


def copy_atomic(src, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    tmp = dst + ".part"
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)


def same(a, b):
    return os.path.exists(a) and os.path.exists(b) and md5(a) == md5(b)


def _same_dir(a, b):
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _head(repo):
    r = git(repo, "rev-parse", "--verify", "HEAD", check=False)
    return r.stdout.strip() if r.returncode == 0 else None


# --------------------------------------------------------------------------- #
# sync
# --------------------------------------------------------------------------- #
def sync_once(repo, local, branch, excludes, push, pull, retries, dry_run):
    """Pull then push. Returns the list of file paths pulled this cycle."""
    in_repo = _same_dir(local, repo)
    pulled = []

    if pull:
        before = _head(repo)
        if not pull_rebase(repo, branch):
            return pulled
        if in_repo:
            # No copy step (local IS the repo) — report what git brought in.
            after = _head(repo)
            if before != after:
                if before is None:
                    names = git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines()
                else:
                    names = git(repo, "diff", "--name-only", "--diff-filter=ACMR",
                                before, after).stdout.splitlines()
                pulled = [n for n in names if n and not excluded(os.path.basename(n), excludes)]
                for rel in pulled:
                    print(f"down  {rel}")
        else:
            for rel, rp in sorted(scan(repo, excludes).items()):
                lp = os.path.join(local, rel)
                if same(lp, rp):
                    continue
                print(f"{'[dry-run] ' if dry_run else ''}down  {rel}")
                if not dry_run:
                    copy_atomic(rp, lp)
                pulled.append(rel)

    if push:
        if in_repo:
            # local IS the repo: stage everything not ignored by .gitignore.

            assets = Path(repo)

            files = [
                *assets.rglob("input_image.png"),
                *assets.rglob("intrinsic.json"),
            ]

            if not dry_run:
                #git(repo, "add", "-A")
                if files:
                    git(repo, "add", "--", *(str(path.relative_to(assets)) for path in files))

            staged = git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
            if dry_run:  # show would-be changes without staging
                staged = [ln[3:] for ln in git(repo, "status", "--porcelain").stdout.splitlines()]
            for rel in staged:
                if rel:
                    print(f"{'[dry-run] ' if dry_run else ''}up    {rel}")
            if not dry_run and staged:
                stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
                git(repo, "commit", "-m", f"relay {stamp}")
                push_retry(repo, branch, retries)
        else:
            for rel, lp in sorted(scan(local, excludes).items()):
                rp = os.path.join(repo, rel)
                if same(lp, rp):
                    continue
                print(f"{'[dry-run] ' if dry_run else ''}up    {rel}")
                if not dry_run:
                    copy_atomic(lp, rp)
            if commit_all(repo, dry_run):
                push_retry(repo, branch, retries)

    print("done.")
    return pulled


def main():
    p = argparse.ArgumentParser(description="GitHub private repo as a two-way file relay.")
    p.add_argument("--local", required=True, help="Your working folder (originals).")
    p.add_argument("--repo", required=True, help="Clone of the private relay repo (transport).")
    p.add_argument("--branch", default="main")
    p.add_argument("--exclude", default=",".join(DEFAULT_EXCLUDES))
    p.add_argument("--push-only", action="store_true")
    p.add_argument("--pull-only", action="store_true")
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--watch", type=int, default=0, help="Seconds between syncs (0 = once).")
    p.add_argument("--squash-history", action="store_true", help="Collapse history; run when both sides idle.")
    p.add_argument("--yes", action="store_true", help="Confirm the destructive history squash.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    repo = os.path.abspath(args.repo)
    local = os.path.abspath(args.local)
    ensure_repo(repo)
    os.makedirs(local, exist_ok=True)

    if args.squash_history:
        squash_history(repo, args.branch, args.yes)
        return

    if args.push_only and args.pull_only:
        sys.exit("Choose at most one of --push-only / --pull-only.")
    push = not args.pull_only
    pull = not args.push_only
    excludes = [e.strip() for e in args.exclude.split(",") if e.strip()]

    while True:
        stamp = datetime.now(timezone.utc).astimezone().strftime("%H:%M:%S")
        print(f"--- relay @ {stamp} ---")
        try:
            pulled = sync_once(repo, local, args.branch, excludes, push, pull, args.retries, args.dry_run)
            if pulled:
                print(f"pulled {len(pulled)} file(s): {pulled}")
        except RuntimeError as e:
            print(f"error: {e}")
        if args.watch <= 0:
            break
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
