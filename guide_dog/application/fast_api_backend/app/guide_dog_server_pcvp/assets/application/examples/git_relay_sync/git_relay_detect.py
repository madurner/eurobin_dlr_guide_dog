#!/usr/bin/env python3
"""
git_relay_detect.py — Git-based image relay with guide dog detection.

This script extends git_relay_sync.py to integrate with the guide dog backend API.
It monitors a git repository for new images, sends them for detection, and pushes
the results (overlay images with bounding boxes and pose data) back to the repository.

Model
-----
  --local   Your working folder (originals)
  --repo    A clone of the private repo, used as transport

Usage
-----
1. Create or use a private git repo for relay
2. Clone it to --repo
3. Install dependencies: pip install -r requirements.txt
4. Place images and intrinsic.json directly in the repo directory
5. Run the script:
   python git_relay_detect.py --local ./pipeline_io --repo ./relay-repo --watch 30

Image Expectations
------------------
Images should be placed directly in the repo directory (no subfolder required).
Supported formats: .png, .jpg, .jpeg, .npy

Intrinsic file
--------------
Camera intrinsic should be stored as JSON directly in the repo directory.
The format should be an array: [focal_length_x, focal_length_y, principal_point_x, principal_point_y]

Results
-------
Results are saved directly to the repo directory:
  - overlay_image.png: Result image with overlays (as PNG)
  - poses.json: Detection poses as JSON

API Configuration
-----------------
The backend API URL can be configured via --api-url and --api-key.

Dependencies
------------
- requests >= 2.31.0
- numpy >= 1.24.0

Based on git_relay_sync.py by DLR RMC.
"""

import argparse
import base64
import codecs
import io
import json
import os
import string
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List

import cv2
import numpy as np
import requests

# Import functions from git_relay_sync.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from git_relay_sync import (
    DEFAULT_EXCLUDES,
    _head,
    _same_dir,
    commit_all,
    copy_atomic,
    ensure_repo,
    excluded,
    git,
    pull_rebase,
    push_retry,
    same,
    scan,
    squash_history,
)

API_DEFAULT_URL = "http://localhost:8000"
API_DEFAULT_KEY = "my_secret_key"

# Guide dog server assets directory (relative to local dir)
DEFAULT_INPUT_IMG_NAME = "input_image.png"
DEFAULT_INTR_NAME = "intrinsic.json"
DEFAULT_POSES_NAME = "poses.json"
DEFAULT_OVERLAY_NAME = "overlay_image.png"


# --------------------------------------------------------------------------- #
# API operations
# --------------------------------------------------------------------------- #
def load_intrinsics(intr_path: Path) -> list:
    """Load camera intrinsics from JSON file.

    Format: [focal_length_x, focal_length_y, principal_point_x, principal_point_y]
    """
    if not intr_path.exists():
        raise FileNotFoundError(f"Intrinsic file not found: {intr_path}")
    with codecs.open(str(intr_path), "r", encoding="utf-8") as f:
        intr_data = json.load(f)

    # Handle both array format [fx, fy, cx, cy] and dict format
    if isinstance(intr_data, list):
        return intr_data
    elif isinstance(intr_data, dict):
        # Convert dict to array format
        return [
            intr_data.get("focal_length_x", intr_data.get("fx", 0)),
            intr_data.get("focal_length_y", intr_data.get("fy", 0)),
            intr_data.get("principal_point_x", intr_data.get("cx", 0)),
            intr_data.get("principal_point_y", intr_data.get("cy", 0)),
        ]
    raise ValueError(f"Unexpected intrinsic format: {type(intr_data)}")


def save_poses(poses: list, poses_path: Path):
    """Save detection poses as JSON.

    Format: {class_name: {instance_id: [pose_array]}}
    """
    os.makedirs(os.path.dirname(poses_path), exist_ok=True)
    # Convert poses to the expected format
    # poses format: [[class_name, instance_id, pose_matrix], ...]
    pose_dict = {}
    for pose in poses:
        class_name = pose[0]
        instance_id = str(pose[1])
        pose_matrix = pose[2].flatten().tolist() if hasattr(pose[2], "flatten") else list(pose[2])

        if class_name not in pose_dict:
            pose_dict[class_name] = {}
        pose_dict[class_name][instance_id] = pose_matrix

    with codecs.open(str(poses_path), "w", encoding="utf-8") as f:
        json.dump(pose_dict, f, separators=(",", ":"), sort_keys=True, indent=4)


def save_overlay(overlay_image: np.ndarray, overlay_path: Path):
    """Save overlay image as PNG."""
    os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
    # Convert RGB to BGR for cv2
    bgr_image = cv2.cvtColor(overlay_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(overlay_path), bgr_image)


def send_to_api(image_path: Path, intr_path: Path, api_url: str, api_key: str) -> Optional[tuple[np.ndarray, list]]:
    """
    Send image and intrinsics to the guide dog API.

    Returns: (overlay_image, poses) or None if failed
    """
    try:
        # Load image - handle both .png and .npy formats
        if image_path.suffix == ".npy":
            image_data = np.load(image_path, allow_pickle=True)
        else:
            # Load as image and convert to RGB numpy array
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                raise ValueError(f"Failed to load image: {image_path}")
            image_data = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Load intrinsics
        intr = load_intrinsics(intr_path)

        # Prepare API request
        headers = {
            "x-api-key": api_key,
        }

        # Build camera data
        camera_data = {
            "camera_name": "git_relay_camera",
            "intrinsics": {
                "principal_point_x": int(intr[2]),  # cx
                "principal_point_y": int(intr[3]),  # cy
                "focal_length_x": float(intr[0]),  # fx
                "focal_length_y": float(intr[1]),  # fy
                "image_width": int(image_data.shape[1]),
                "image_height": int(image_data.shape[0]),
            },
        }

        # First, set the camera
        resp = requests.post(f"{api_url}/camera", json=camera_data, headers=headers)
        resp.raise_for_status()

        # Now upload image as multipart/form-data
        # The backend expects numpy arrays saved as bytes
        np_bytes = io.BytesIO()
        np.save(np_bytes, image_data, allow_pickle=True)
        np_bytes.seek(0)

        files = {"file": ("image.npy", np_bytes.getvalue(), "application/octet-stream")}
        resp = requests.post(f"{api_url}/image", files=files, headers=headers)
        resp.raise_for_status()

        # Start pipeline
        resp = requests.post(f"{api_url}/pipeline", headers=headers)
        resp.raise_for_status()

        # Run detection
        resp = requests.get(f"{api_url}/detection", headers=headers)
        resp.raise_for_status()

        result = resp.json()

        # Decode result image from base64
        image_bytes = base64.b64decode(result["image_base64"])

        # Convert back to numpy array
        np_bytes = io.BytesIO(image_bytes)
        overlay_image = np.load(np_bytes, allow_pickle=True)

        poses = []
        for detection in result.get("result", []):
            pose_matrix = np.array(detection["pose_6dof"]).reshape(4, 4)
            poses.append([detection["class_name"], detection["instance_id"], pose_matrix])

        return overlay_image, poses

    except Exception as e:
        print(f"  Error calling API: {e}")
        return None


# --------------------------------------------------------------------------- #
# Sync with detection processing
# --------------------------------------------------------------------------- #
def process_detection(parent_dir: Path, local_dir: Path, repo_dir: Path, branch: str, api_url: str, api_key: str, dry_run: bool) -> bool:
    """
    Process the current image in local_dir directly via API.
    Returns True if processing was successful.
    """
    processed = False

    # Define paths directly in local directory (no assets/ subfolder)
    intr_path = local_dir / parent_dir / DEFAULT_INTR_NAME
    image_path = local_dir / parent_dir / DEFAULT_INPUT_IMG_NAME

    if not intr_path.exists():
        print(f"  Warning: No intrinsic file at {intr_path}, skipping")
        return processed

    if not image_path.exists():
        print(f"  Warning: No input image found at {image_path}, skipping")
        return processed

    print(f"  Processing: {image_path.name}")

    # Call API
    if dry_run:
        print(f"    [dry-run] Would call API for {image_path.name}")
        return True

    result = send_to_api(image_path, intr_path, api_url, api_key)
    if result is None:
        print(f"    Failed to process {image_path.name}")
        return processed

    overlay_image, poses = result

    # Save paths directly in local directory
    overlay_path = local_dir / parent_dir / DEFAULT_OVERLAY_NAME
    poses_path = local_dir / parent_dir / DEFAULT_POSES_NAME

    # Save results to local directory
    save_overlay(overlay_image, overlay_path)
    save_poses(poses, poses_path)

    print(f"    Saved: {overlay_path.name}, {poses_path.name}")

    # Copy to repo if not in same directory
    if not _same_dir(str(local_dir), str(repo_dir)):
        # Copy result files to repo (directly, no assets/ subfolder)
        repo_overlay = repo_dir / DEFAULT_OVERLAY_NAME
        repo_poses = repo_dir / DEFAULT_POSES_NAME
        repo_intr = repo_dir / DEFAULT_INTR_NAME

        copy_atomic(str(overlay_path), str(repo_overlay))
        copy_atomic(str(poses_path), str(repo_poses))
        copy_atomic(str(intr_path), str(repo_intr))

    processed = True
    return processed


def sync_with_detection(  # noqa: C901
    repo: str,
    local: str,
    branch: str,
    excludes: list,
    push: bool,
    pull: bool,
    retries: int,
    api_url: str,
    api_key: str,
    dry_run: bool,
) -> int:
    """
    Pull, process images via API, then push. Returns count of processed images.
    Extends base sync_once with API detection integration.
    """
    in_repo = _same_dir(local, repo)
    pulled = []

    if pull:
        before = _head(repo)
        if not pull_rebase(repo, branch):
            return 0
        if in_repo:
            # No copy step (local IS the repo) — report what git brought in.
            after = _head(repo)
            if before != after:
                if before is None:
                    names = git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines()
                else:
                    names = git(repo, "diff", "--name-only", "--diff-filter=ACMR", before, after).stdout.splitlines()
                pulled = [n for n in names if n and not excluded(os.path.basename(n), excludes)]
                for rel in pulled:
                    # Skip result files from being "pulled" as new images
                    if rel.startswith("results/"):
                        continue
                    print(f"down  {rel}")
        else:
            for rel, rp in sorted(scan(repo, excludes).items()):
                lp = os.path.join(local, rel)
                if same(lp, rp):
                    continue
                # Skip result files
                if rel.startswith("results/") or rel.startswith("assets/"):
                    continue
                print(f"{'[dry-run] ' if dry_run else ''}down  {rel}")
                if not dry_run:
                    copy_atomic(rp, lp)
                pulled.append(rel)

    # Process images via API only if image or intrinsic has changed
    local_path = Path(local)
    processed_count = 0
    needs_processing = False
    for file in pulled:
        if DEFAULT_INPUT_IMG_NAME in file:
            needs_processing = True
            continue
        if DEFAULT_INTR_NAME in file:
            needs_processing = True
            continue

    if not needs_processing:
        print("  No image/intrinsic changes, skipping API call")
    else:
        if process_detection(Path(pulled[0]).parent, Path(local), Path(repo), branch, api_url, api_key, dry_run):
            processed_count = 1
    print(f"  Processed {processed_count} image(s)")

    if push:
        if in_repo:
            # local IS the repo: stage everything not ignored by .gitignore.
            if not dry_run:
                git(repo, "add", "-A")
            staged = git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
            if dry_run:
                staged = [ln[3:] for ln in git(repo, "status", "--porcelain").stdout.splitlines()]
            for rel in staged:
                if rel:
                    print(f"{'[dry-run] ' if dry_run else ''}up    {rel}")
            if not dry_run and staged:
                stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
                git(repo, "commit", "-m", f"relay detection results {stamp}")
                push_retry(repo, branch, retries)
        else:
            # Scan local directory for changes to push
            local_exclude = [*excludes, "*.part"]
            for rel, lp in sorted(scan(local, local_exclude).items()):
                rp = os.path.join(repo, rel)
                if same(lp, rp):
                    continue
                print(f"{'[dry-run] ' if dry_run else ''}up    {rel}")
                if not dry_run:
                    copy_atomic(lp, rp)
            if commit_all(repo, dry_run):
                push_retry(repo, branch, retries)

    print("done.")
    return processed_count


def main():
    p = argparse.ArgumentParser(description="GitHub private repo as a two-way file relay with guide dog detection.")
    p.add_argument("--local", required=True, help="Your working folder (originals).")
    p.add_argument("--repo", required=True, help="Clone of the private relay repo (transport).")
    p.add_argument("--branch", default="main")
    p.add_argument("--exclude", default=",".join(DEFAULT_EXCLUDES))
    p.add_argument("--push-only", action="store_true")
    p.add_argument("--pull-only", action="store_true")
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--watch", type=int, default=0, help="Seconds between syncs (0 = once).")
    p.add_argument("--api-url", default=API_DEFAULT_URL, help=f"Backend API URL (default: {API_DEFAULT_URL})")
    p.add_argument("--api-key", default=API_DEFAULT_KEY, help=f"Backend API key (default: {API_DEFAULT_KEY})")
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
            processed_count = sync_with_detection(
                repo, local, args.branch, excludes, push, pull, args.retries, args.api_url, args.api_key, args.dry_run
            )
            if processed_count > 0:
                print(f"Processed {processed_count} file(s)")
        except RuntimeError as e:
            print(f"error: {e}")
        if args.watch <= 0:
            break
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
