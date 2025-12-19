#!/usr/bin/env python3
"""
Push Docker images with appropriate tags and extract digest.

This script handles conditional image tagging and pushing based on the event type
(pull request or main branch push), and extracts the digest for attestation.

Exit codes:
    0: Success
    1: Error (push failure, digest extraction failure, etc.)
"""

import argparse
import re
import subprocess
import sys

from github_actions_utils import github_action_log, log_info, set_github_output


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Push Docker images with appropriate tags"
    )
    parser.add_argument(
        "--event-name",
        required=True,
        choices=["pull_request", "push", "schedule", "workflow_dispatch"],
        help="GitHub event name"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="Repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--sha",
        required=True,
        help="Git commit SHA"
    )
    parser.add_argument(
        "--pr-number",
        help="Pull request number (required for pull_request events)"
    )
    parser.add_argument(
        "--image-tar",
        required=True,
        help="Path to the image tar file"
    )
    
    args = parser.parse_args()
    
    # Validate PR number is provided for pull_request events
    if args.event_name == "pull_request" and not args.pr_number:
        github_action_log("error", "PR number is required for pull_request events")
        sys.exit(1)
    
    return args


def load_image(tar_path: str) -> None:
    """
    Load Docker image from tar file.
    
    Args:
        tar_path: Path to the tar file
        
    Raises:
        SystemExit: If loading fails
    """
    try:
        subprocess.run(
            ["docker", "load", "-i", tar_path],
            check=True,
            capture_output=True,
            timeout=300
        )
        log_info(f"Successfully loaded image from {tar_path}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        github_action_log("error", f"Failed to load image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_action_log("error", "Image load timed out")
        sys.exit(1)


def docker_tag(source: str, target: str) -> None:
    """
    Tag a Docker image.
    
    Args:
        source: Source image name
        target: Target image name
        
    Raises:
        SystemExit: If tagging fails
    """
    try:
        subprocess.run(
            ["docker", "tag", source, target],
            check=True,
            capture_output=True,
            timeout=30
        )
        log_info(f"Tagged {source} as {target}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        github_action_log("error", f"Failed to tag image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_action_log("error", "Image tagging timed out")
        sys.exit(1)


def docker_push(image: str) -> str:
    """
    Push a Docker image and extract its digest.
    
    Args:
        image: Image name to push
        
    Returns:
        Image digest (sha256:...)
        
    Raises:
        SystemExit: If push fails or digest cannot be extracted
    """
    try:
        result = subprocess.run(
            ["docker", "push", image],
            check=True,
            capture_output=True,
            timeout=600,
            text=True
        )
        output = result.stdout + result.stderr
        log_info(f"Successfully pushed {image}")
        
        # Extract digest from output (format: "digest: sha256:... size: ...")
        match = re.search(r'digest:\s+(sha256:[a-f0-9]{64})', output)
        if not match:
            github_action_log("error", "Failed to extract digest from docker push output")
            github_action_log("error", f"Push output was: {output}")
            sys.exit(1)
        
        digest = match.group(1)
        log_info(f"Extracted digest: {digest}")
        return digest
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        github_action_log("error", f"Failed to push image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_action_log("error", "Image push timed out")
        sys.exit(1)


def main() -> None:
    """Main entry point for the push script."""
    args = parse_args()
    
    # Load the image
    load_image(args.image_tar)
    
    # Prepare tag names
    registry = f"ghcr.io/{args.repository}"
    
    if args.event_name == "pull_request":
        # On PR: push only with PR-specific tag
        pr_tag = f"{registry}:pr-{args.pr_number}"
        docker_tag("candidate_image:latest", pr_tag)
        digest = docker_push(pr_tag)
        set_github_output("digest", digest)
        set_github_output("tag", pr_tag)
    else:
        # On main: push with both SHA and latest tags
        sha_tag = f"{registry}:{args.sha}"
        latest_tag = f"{registry}:latest"
        
        # Tag and push SHA version first
        docker_tag("candidate_image:latest", sha_tag)
        digest = docker_push(sha_tag)
        set_github_output("digest", digest)
        
        # Push the latest tag (same image, so same digest)
        docker_tag("candidate_image:latest", latest_tag)
        docker_push(latest_tag)
        set_github_output("tag", latest_tag)


if __name__ == "__main__":
    main()
