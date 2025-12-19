#!/usr/bin/env python3
"""
Shared utilities for GitHub Actions workflow scripts.

This module provides common functionality used across multiple workflow scripts,
including logging and output handling for GitHub Actions.
"""

import sys


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
