#!/usr/bin/env python3
"""
Unit tests for github_actions_utils.py module.

These tests verify the shared GitHub Actions utilities work correctly.
"""

import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path
from urllib.request import Request

# Add parent directory to path to import the module in a way that works across environments
script_dir = str(Path(__file__).resolve().parent)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import github_actions_utils


class TestGitHubActionsLogging(unittest.TestCase):
    """Test GitHub Actions logging functions."""
    
    def test_github_action_log_writes_to_stderr(self):
        """Test that github_action_log writes to stderr in correct format."""
        captured_stderr = StringIO()
        
        with patch('sys.stderr', captured_stderr):
            github_actions_utils.github_action_log('error', 'Test error message')
        
        output = captured_stderr.getvalue()
        self.assertEqual(output, '::error::Test error message\n')
    
    def test_log_info_writes_to_stderr(self):
        """Test that log_info writes to stderr."""
        captured_stderr = StringIO()
        
        with patch('sys.stderr', captured_stderr):
            github_actions_utils.log_info('Test info message')
        
        output = captured_stderr.getvalue()
        self.assertEqual(output, 'Test info message\n')
    
    def test_set_github_output_writes_to_stdout(self):
        """Test that set_github_output writes to stdout in correct format."""
        captured_stdout = StringIO()
        
        with patch('sys.stdout', captured_stdout):
            github_actions_utils.set_github_output('myvar', 'myvalue')
        
        output = captured_stdout.getvalue()
        self.assertEqual(output, 'myvar=myvalue\n')
    
    def test_multiple_log_levels(self):
        """Test different log levels produce correct output."""
        levels_and_messages = [
            ('error', 'An error occurred'),
            ('warning', 'A warning'),
            ('notice', 'A notice'),
            ('debug', 'Debug info')
        ]
        
        for level, message in levels_and_messages:
            with self.subTest(level=level):
                captured_stderr = StringIO()
                
                with patch('sys.stderr', captured_stderr):
                    github_actions_utils.github_action_log(level, message)
                
                output = captured_stderr.getvalue()
                self.assertEqual(output, f'::{level}::{message}\n')


class TestGitHubAPIHeaders(unittest.TestCase):
    """Test GitHub API header utilities."""
    
    def test_add_github_api_headers(self):
        """Test that add_github_api_headers adds all required headers."""
        # Create a mock Request object
        req = Request('https://api.github.com/test')
        test_token = 'test_token_12345'
        
        # Add headers
        github_actions_utils.add_github_api_headers(req, test_token)
        
        # Verify all three headers were added correctly
        self.assertEqual(
            req.get_header('Accept'),
            'application/vnd.github+json',
            'Accept header should be set to GitHub API JSON format'
        )
        self.assertEqual(
            req.get_header('Authorization'),
            f'Bearer {test_token}',
            'Authorization header should use Bearer token format'
        )
        self.assertEqual(
            req.get_header('X-github-api-version'),
            '2022-11-28',
            'X-GitHub-Api-Version header should be set to 2022-11-28'
        )


if __name__ == "__main__":
    unittest.main()
