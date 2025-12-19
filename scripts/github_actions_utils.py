#!/usr/bin/env python3
"""
Shared utilities for GitHub Actions workflow scripts.

This module provides common functionality used across multiple workflow scripts,
including logging, output variable setting, and GitHub Actions workflow commands.
"""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from urllib.request import Request


def github_action_log(level: str, message: str) -> None:
    """
    Output GitHub Actions workflow command to stderr.
    
    This function writes workflow commands in the format GitHub Actions expects.
    The output goes to stderr to avoid interfering with stdout-based outputs.
    
    Args:
        level: Log level (e.g., 'error', 'warning', 'notice', 'debug')
        message: Log message to output
        
    Example:
        >>> github_action_log('error', 'Something went wrong')
        ::error::Something went wrong
    """
    print(f"::{level}::{message}", file=sys.stderr)


def log_info(message: str) -> None:
    """
    Log informational message to stderr.
    
    This ensures log messages don't interfere with GitHub Actions outputs
    that are written to stdout.
    
    Args:
        message: Informational message to log
        
    Example:
        >>> log_info('Processing file...')
        Processing file...
    """
    print(message, file=sys.stderr)


def set_github_output(name: str, value: str) -> None:
    """
    Set GitHub Actions output variable by writing to stdout.
    
    GitHub Actions reads stdout to capture output variables in the format:
    name=value
    
    Args:
        name: Output variable name
        value: Output variable value
        
    Example:
        >>> set_github_output('digest', 'sha256:abc123')
        digest=sha256:abc123
    """
    print(f"{name}={value}")


def add_github_api_headers(req: "Request", token: str) -> None:
    """
    Add standard GitHub API headers to an HTTP request.
    
    Adds the Accept, Authorization, and X-GitHub-Api-Version headers
    required for GitHub API v3 requests.
    
    Args:
        req: urllib Request object to add headers to
        token: GitHub API token for authentication
        
    Example:
        >>> from urllib.request import Request
        >>> req = Request('https://api.github.com/...')
        >>> add_github_api_headers(req, 'gh_token_123')
    """
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
