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

import github_actions_utils


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
    
    # Validate PR number for pull_request events
    if args.event_name == "pull_request" and not args.pr_number:
        parser.error("--pr-number is required for pull_request events")
    
    return args


def load_image(image_tar: str) -> None:
    """
    Load Docker image from tar archive.
    
    Args:
        image_tar: Path to tar archive
        
    Raises:
        SystemExit: If loading fails
    """
    github_actions_utils.log_info(f"Loading image from {image_tar}")
    try:
        result = subprocess.run(
            ["docker", "load", "-i", image_tar],
            check=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        github_actions_utils.log_info(f"Successfully loaded image from {image_tar}")
        if result.stdout:
            github_actions_utils.log_info(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        github_actions_utils.github_action_log("error", f"Failed to load image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_actions_utils.github_action_log("error", "Image load timed out after 300 seconds")
        sys.exit(1)


def docker_tag(source: str, target: str) -> None:
    """
    Tag a Docker image.
    
    Args:
        source: Source image
        target: Target image
        
    Raises:
        SystemExit: If tagging fails
    """
    github_actions_utils.log_info(f"Tagging {source} as {target}")
    try:
        subprocess.run(
            ["docker", "tag", source, target],
            check=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        github_actions_utils.log_info(f"Successfully tagged as {target}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        github_actions_utils.github_action_log("error", f"Failed to tag image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_actions_utils.github_action_log("error", "Image tagging timed out after 60 seconds")
        sys.exit(1)


def docker_push(image: str) -> str:
    """
    Push a Docker image and extract its digest.
    
    Args:
        image: Image to push
        
    Returns:
        Image digest
        
    Raises:
        SystemExit: If push fails or digest cannot be extracted
    """
    github_actions_utils.log_info(f"Pushing {image}")
    try:
        result = subprocess.run(
            ["docker", "push", image],
            check=True,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        # Extract digest from output
        output = result.stdout + result.stderr
        digest_match = re.search(r"digest:\s+(sha256:[a-f0-9]{64})", output)
        
        if not digest_match:
            github_actions_utils.github_action_log("error", "Could not extract digest from docker push output")
            github_actions_utils.log_info(f"Docker push output:\n{output}")
            sys.exit(1)
        
        digest = digest_match.group(1)
        github_actions_utils.log_info(f"Successfully pushed {image}")
        github_actions_utils.log_info(f"Digest: {digest}")
        return digest
        
    except subprocess.CalledProcessError as e:
        error_msg = str(e.stderr) if e.stderr is not None else str(e)
        github_actions_utils.github_action_log("error", f"Failed to push image: {error_msg}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_actions_utils.github_action_log("error", "Image push timed out after 600 seconds")
        sys.exit(1)


def main() -> None:
    """Main function."""
    args = parse_args()
    
    # Load the image from tar
    load_image(args.image_tar)
    
    # Prepare tag names
    registry = f"ghcr.io/{args.repository}"
    
    if args.event_name == "pull_request":
        # For PRs: push with pr-{number} tag only
        pr_tag = f"{registry}:pr-{args.pr_number}"
        
        docker_tag("candidate_image:latest", pr_tag)
        digest = docker_push(pr_tag)
        github_actions_utils.set_github_output("digest", digest)
        github_actions_utils.set_github_output("tag", pr_tag)
        
    else:
        # On main: push with both SHA and latest tags
        sha_tag = f"{registry}:{args.sha}"
        latest_tag = f"{registry}:latest"
        
        # Tag and push SHA version first
        docker_tag("candidate_image:latest", sha_tag)
        digest = docker_push(sha_tag)
        github_actions_utils.set_github_output("digest", digest)
        
        # Push the latest tag (same image, so same digest)
        docker_tag("candidate_image:latest", latest_tag)
        docker_push(latest_tag)
        github_actions_utils.set_github_output("tag", latest_tag)
    
    github_actions_utils.log_info("Image push completed successfully")


if __name__ == "__main__":
    main()
