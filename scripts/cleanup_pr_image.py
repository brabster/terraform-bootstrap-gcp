#!/usr/bin/env python3
"""
Deletes a PR-specific Docker image from GitHub Container Registry.

This script uses the GitHub Packages API to identify and delete a specific
image tag associated with a pull request. It is designed to clean up temporary
PR images when the pull request is closed or merged.

Required environment variables:
    PR_NUMBER: The pull request number
    GITHUB_REPOSITORY: The repository in format "owner/repo"
    GITHUB_REPOSITORY_OWNER: The repository owner
    GITHUB_TOKEN: GitHub token with packages:write permission
    GITHUB_ACTOR: GitHub username for authentication

Exit codes:
    0: Success (image deleted or not found)
    1: Error (API failure, authentication failure, validation failure, etc.)
"""

import json
import os
import subprocess
import sys
from typing import Optional
from urllib import request
from urllib.error import HTTPError, URLError


def github_action_log(level: str, message: str) -> None:
    """Output GitHub Actions workflow command."""
    print(f"::{level}::{message}")


def validate_env_vars() -> dict:
    """
    Validate required environment variables are set.
    
    Returns:
        dict: Dictionary of validated environment variables
        
    Raises:
        SystemExit: If any required variable is missing
    """
    required_vars = [
        "PR_NUMBER",
        "GITHUB_REPOSITORY",
        "GITHUB_REPOSITORY_OWNER",
        "GITHUB_TOKEN",
        "GITHUB_ACTOR",
    ]
    
    env_vars = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            env_vars[var] = value
    
    if missing_vars:
        github_action_log(
            "error",
            f"Required environment variables not set: {', '.join(missing_vars)}"
        )
        sys.exit(1)
    
    return env_vars


def docker_login(token: str, actor: str) -> None:
    """
    Authenticate to GitHub Container Registry using Docker.
    
    Args:
        token: GitHub token
        actor: GitHub actor (username)
        
    Raises:
        SystemExit: If authentication fails
    """
    try:
        process = subprocess.run(
            ["docker", "login", "ghcr.io", "-u", actor, "--password-stdin"],
            input=token.encode(),
            capture_output=True,
            check=True,
            timeout=30
        )
        print("Successfully authenticated to GitHub Container Registry")
    except subprocess.CalledProcessError as e:
        github_action_log("error", f"Docker login failed: {e.stderr.decode()}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        github_action_log("error", "Docker login timed out")
        sys.exit(1)


def get_package_versions(
    owner: str, package_name: str, token: str
) -> Optional[list]:
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
    
    req = request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        if e.code == 404:
            github_action_log(
                "warning",
                f"Package not found (HTTP {e.code}). The PR image may not exist."
            )
            return None
        github_action_log(
            "warning",
            f"Failed to fetch package versions (HTTP {e.code}). "
            "The PR image may not exist or may have already been deleted."
        )
        return None
    except URLError as e:
        github_action_log("error", f"Network error fetching package versions: {e}")
        return None


def find_version_id_by_tag(versions: list, tag: str) -> Optional[int]:
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
            return version.get("id")
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
    
    req = request.Request(url, method="DELETE")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    
    try:
        with request.urlopen(req, timeout=30) as response:
            if response.status == 204:
                return True
            github_action_log(
                "error",
                f"Unexpected response code {response.status} when deleting version"
            )
            return False
    except HTTPError as e:
        github_action_log(
            "error",
            f"Failed to delete package version (HTTP {e.code}): {e.read().decode()}"
        )
        return False
    except URLError as e:
        github_action_log("error", f"Network error deleting package version: {e}")
        return False


def main() -> None:
    """Main entry point for the cleanup script."""
    # Validate environment variables
    env = validate_env_vars()
    
    pr_number = env["PR_NUMBER"]
    repository = env["GITHUB_REPOSITORY"]
    owner = env["GITHUB_REPOSITORY_OWNER"]
    token = env["GITHUB_TOKEN"]
    actor = env["GITHUB_ACTOR"]
    
    # Extract package name from repository
    package_name = repository.split("/")[-1].lower()
    tag = f"pr-{pr_number}"
    image_name = f"ghcr.io/{repository}"
    
    print(f"Attempting to delete image tag: {image_name}:{tag}")
    print(f"Looking for package: {package_name} with tag: {tag}")
    
    # Authenticate to registry
    docker_login(token, actor)
    
    # Fetch package versions
    versions = get_package_versions(owner, package_name, token)
    if versions is None:
        print(
            f"No image found with tag: {tag} "
            "(this is expected if the PR was closed before the image was published)"
        )
        sys.exit(0)
    
    # Find version ID for the PR tag
    version_id = find_version_id_by_tag(versions, tag)
    if version_id is None:
        print(
            f"No image found with tag: {tag} "
            "(this is expected if the PR was closed before the image was published)"
        )
        sys.exit(0)
    
    print(f"Found version ID: {version_id} for tag {tag}")
    
    # Delete the package version
    if delete_package_version(owner, package_name, version_id, token):
        print(f"Successfully deleted image tag: {tag}")
        sys.exit(0)
    else:
        github_action_log("error", f"Failed to delete image tag {tag}")
        sys.exit(1)


if __name__ == "__main__":
    main()
