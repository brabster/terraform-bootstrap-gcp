#!/usr/bin/env python3
"""
Deletes a PR-specific Docker image from GitHub Container Registry.

This script uses the GitHub Packages API to identify and delete a specific
image tag associated with a pull request. It is designed to clean up temporary
PR images when the pull request is closed or merged.

Exit codes:
    0: Success (image deleted or not found)
    1: Error (API failure, authentication failure, validation failure, etc.)
"""

import argparse
import json
import sys
from typing import Optional, Any, Dict, List
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

import github_actions_utils


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Delete PR-specific Docker images from GitHub Container Registry"
    )
    parser.add_argument(
        "--pr-number",
        required=True,
        help="Pull request number"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="Repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="Repository owner"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="GitHub token with packages:write permission"
    )
    
    return parser.parse_args()


def get_package_versions(
    owner: str, package_name: str, token: str
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch all versions of a package from GitHub Container Registry.
    
    Args:
        owner: Repository owner
        package_name: Package name (repository name in lowercase)
        token: GitHub token
        
    Returns:
        List of package versions or None if not found
    """
    url = f"https://api.github.com/users/{owner}/packages/container/{package_name}/versions"
    
    req = urllib_request.Request(url)
    github_actions_utils.add_github_api_headers(req, token)
    
    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            data = response.read().decode()
            from typing import cast
            result = json.loads(data)
            return cast(List[Dict[str, Any]], result)
    except HTTPError as e:
        if e.code == 404:
            github_actions_utils.github_action_log(
                "warning",
                f"Package not found (HTTP {e.code}). The PR image may not exist."
            )
            return None
        github_actions_utils.github_action_log(
            "warning",
            f"Failed to fetch package versions (HTTP {e.code}). "
            "The PR image may not exist or may have already been deleted."
        )
        return None
    except URLError as e:
        github_actions_utils.github_action_log("error", f"Network error fetching package versions: {e}")
        return None


def find_version_id_by_tag(versions: List[Dict[str, Any]], tag: str) -> Optional[int]:
    """
    Find the version ID for a specific tag.
    
    Args:
        versions: List of package versions from GitHub API
        tag: Tag to search for
        
    Returns:
        Version ID if found, None otherwise
    """
    for version in versions:
        tags = version.get("metadata", {}).get("container", {}).get("tags", [])
        if tag in tags:
            vid = version.get("id")
            if vid is not None:
                return int(vid)
    return None


def delete_package_version(
    owner: str, package_name: str, version_id: int, token: str
) -> bool:
    """
    Delete a specific package version.
    
    Args:
        owner: Repository owner
        package_name: Package name
        version_id: Version ID to delete
        token: GitHub token
        
    Returns:
        True if deletion successful, False otherwise
    """
    url = f"https://api.github.com/users/{owner}/packages/container/{package_name}/versions/{version_id}"
    
    req = urllib_request.Request(url, method="DELETE")
    github_actions_utils.add_github_api_headers(req, token)
    
    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            if response.status == 204:
                return True
            github_actions_utils.github_action_log(
                "error",
                f"Unexpected response code {response.status} when deleting version"
            )
            return False
    except HTTPError as e:
        github_actions_utils.github_action_log(
            "error",
            f"Failed to delete package version (HTTP {e.code}): {e.read().decode()}"
        )
        return False
    except URLError as e:
        github_actions_utils.github_action_log("error", f"Network error deleting package version: {e}")
        return False


def main() -> None:
    """Main entry point for the cleanup script."""
    # Parse command line arguments
    args = parse_args()
    
    pr_number = args.pr_number
    repository = args.repository
    owner = args.owner
    token = args.token
    
    # Extract package name from repository
    package_name = repository.split("/")[-1].lower()
    tag = f"pr-{pr_number}"
    image_name = f"ghcr.io/{repository}"
    
    github_actions_utils.log_info(f"Attempting to delete image tag: {image_name}:{tag}")
    github_actions_utils.log_info(f"Looking for package: {package_name} with tag: {tag}")
    
    # Fetch package versions
    versions = get_package_versions(owner, package_name, token)
    if versions is None:
        github_actions_utils.log_info(
            f"No image found with tag: {tag} "
            "(this is expected if the PR was closed before the image was published)"
        )
        sys.exit(0)
    
    # Find version ID for the PR tag
    version_id = find_version_id_by_tag(versions, tag)
    if version_id is None:
        github_actions_utils.log_info(
            f"No image found with tag: {tag} "
            "(this is expected if the PR was closed before the image was published)"
        )
        sys.exit(0)
    
    github_actions_utils.log_info(f"Found version ID: {version_id} for tag {tag}")
    
    # Delete the package version
    if delete_package_version(owner, package_name, version_id, token):
        github_actions_utils.log_info(f"Successfully deleted image tag: {tag}")
        sys.exit(0)
    else:
        github_actions_utils.github_action_log("error", f"Failed to delete image tag {tag}")
        sys.exit(1)


if __name__ == "__main__":
    main()
