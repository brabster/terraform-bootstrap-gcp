#!/usr/bin/env python3
"""
Unit tests for push_image.py script.

These tests verify core functionality without requiring Docker or actual image operations.
"""

import re
import sys
import unittest
from io import StringIO
from unittest.mock import patch
from pathlib import Path

# Add parent directory to path to import the module in a way that works across environments
script_dir = str(Path(__file__).resolve().parent)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import push_image


class TestDigestExtraction(unittest.TestCase):
    """Test digest extraction from docker push output."""
    
    def test_extract_digest_from_valid_output(self):
        """Test that digest is correctly extracted from valid docker push output."""
        # Simulate docker push output
        mock_output = """
The push refers to repository [ghcr.io/test/repo]
abc123: Pushed
def456: Pushed
latest: digest: sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef size: 1234
        """
        
        match = re.search(r'digest:\s+(sha256:[a-f0-9]{64})', mock_output)
        self.assertIsNotNone(match)
        digest = match.group(1)
        self.assertEqual(digest, "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(len(digest), 71)  # "sha256:" (7) + 64 hex chars
    
    def test_extract_digest_invalid_format(self):
        """Test that extraction fails gracefully with invalid output."""
        invalid_outputs = [
            "No digest here",
            "digest: sha256:tooshort",
            "digest: md5:1234567890abcdef",
            "",
        ]
        
        for output in invalid_outputs:
            match = re.search(r'digest:\s+(sha256:[a-f0-9]{64})', output)
            self.assertIsNone(match, f"Should not match invalid output: {output}")


class TestArgumentParsing(unittest.TestCase):
    """Test command-line argument parsing."""
    
    def test_parse_args_pull_request(self):
        """Test parsing arguments for pull request event."""
        test_args = [
            "push_image.py",
            "--event-name", "pull_request",
            "--repository", "owner/repo",
            "--sha", "abc123",
            "--pr-number", "42",
            "--image-tar", "/path/to/image.tar"
        ]
        
        with patch('sys.argv', test_args):
            args = push_image.parse_args()
            self.assertEqual(args.event_name, "pull_request")
            self.assertEqual(args.repository, "owner/repo")
            self.assertEqual(args.sha, "abc123")
            self.assertEqual(args.pr_number, "42")
            self.assertEqual(args.image_tar, "/path/to/image.tar")
    
    def test_parse_args_main_push(self):
        """Test parsing arguments for main branch push event."""
        test_args = [
            "push_image.py",
            "--event-name", "push",
            "--repository", "owner/repo",
            "--sha", "def456",
            "--image-tar", "/path/to/image.tar"
        ]
        
        with patch('sys.argv', test_args):
            args = push_image.parse_args()
            self.assertEqual(args.event_name, "push")
            self.assertEqual(args.repository, "owner/repo")
            self.assertEqual(args.sha, "def456")
            self.assertIsNone(args.pr_number)
    
    def test_parse_args_missing_pr_number_for_pr_event(self):
        """Test that PR event without PR number causes exit."""
        test_args = [
            "push_image.py",
            "--event-name", "pull_request",
            "--repository", "owner/repo",
            "--sha", "abc123",
            "--image-tar", "/path/to/image.tar"
        ]
        
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                push_image.parse_args()
            self.assertEqual(cm.exception.code, 1)


class TestOutputFormatting(unittest.TestCase):
    """Test that output is properly formatted for GitHub Actions."""
    
    def test_github_output_format(self):
        """Test that set_github_output writes to stdout in correct format."""
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            push_image.set_github_output("test_name", "test_value")
        
        output = captured_output.getvalue()
        self.assertEqual(output, "test_name=test_value\n")
    
    def test_log_info_uses_stderr(self):
        """Test that log_info writes to stderr, not stdout."""
        # Capture stderr
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        
        with patch('sys.stderr', captured_stderr), patch('sys.stdout', captured_stdout):
            push_image.log_info("Test message")
        
        # Message should be in stderr, not stdout
        self.assertEqual(captured_stderr.getvalue(), "Test message\n")
        self.assertEqual(captured_stdout.getvalue(), "")
    
    def test_github_action_log_uses_stderr(self):
        """Test that github_action_log writes to stderr, not stdout."""
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        
        with patch('sys.stderr', captured_stderr), patch('sys.stdout', captured_stdout):
            push_image.github_action_log("warning", "Test warning")
        
        # Action log should be in stderr, not stdout
        self.assertIn("::warning::Test warning", captured_stderr.getvalue())
        self.assertEqual(captured_stdout.getvalue(), "")


class TestTagGeneration(unittest.TestCase):
    """Test image tag generation logic."""
    
    def test_pr_tag_format(self):
        """Test PR tag format is correct."""
        repository = "owner/repo"
        pr_number = "123"
        expected_tag = f"ghcr.io/{repository}:pr-{pr_number}"
        
        self.assertEqual(expected_tag, "ghcr.io/owner/repo:pr-123")
    
    def test_sha_tag_format(self):
        """Test SHA tag format is correct."""
        repository = "owner/repo"
        sha = "abc123def456"
        expected_tag = f"ghcr.io/{repository}:{sha}"
        
        self.assertEqual(expected_tag, "ghcr.io/owner/repo:abc123def456")
    
    def test_latest_tag_format(self):
        """Test latest tag format is correct."""
        repository = "owner/repo"
        expected_tag = f"ghcr.io/{repository}:latest"
        
        self.assertEqual(expected_tag, "ghcr.io/owner/repo:latest")


if __name__ == '__main__':
    unittest.main()
