#!/usr/bin/env python3
"""
Unit tests for push_image.py script.

These tests verify core functionality without requiring Docker or actual image operations.
"""

import re
import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
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


class TestMainFunctionTagging(unittest.TestCase):
    """Test main function tagging logic with different event types."""
    
    @patch('push_image.docker_push')
    @patch('push_image.docker_tag')
    @patch('push_image.load_image')
    @patch('push_image.set_github_output')
    def test_pr_event_uses_pr_tag(self, mock_output, mock_load, mock_tag, mock_push):
        """Test that PR events use pr-<number> tag."""
        from unittest.mock import MagicMock
        mock_push.return_value = "sha256:abc123"
        
        test_args = [
            "push_image.py",
            "--event-name", "pull_request",
            "--repository", "owner/repo",
            "--sha", "abc123",
            "--pr-number", "42",
            "--image-tar", "/path/to/image.tar"
        ]
        
        with patch('sys.argv', test_args):
            push_image.main()
        
        # Verify PR tag was used
        mock_tag.assert_called_once_with("candidate_image:latest", "ghcr.io/owner/repo:pr-42")
        mock_push.assert_called_once_with("ghcr.io/owner/repo:pr-42")
        
        # Verify outputs were set correctly
        output_calls = [call[0] for call in mock_output.call_args_list]
        self.assertIn(('digest', 'sha256:abc123'), output_calls)
        self.assertIn(('tag', 'ghcr.io/owner/repo:pr-42'), output_calls)
    
    @patch('push_image.docker_push')
    @patch('push_image.docker_tag')
    @patch('push_image.load_image')
    @patch('push_image.set_github_output')
    def test_main_event_uses_sha_and_latest_tags(self, mock_output, mock_load, mock_tag, mock_push):
        """Test that main branch push uses SHA and latest tags."""
        from unittest.mock import MagicMock
        mock_push.return_value = "sha256:def456"
        
        test_args = [
            "push_image.py",
            "--event-name", "push",
            "--repository", "owner/repo",
            "--sha", "abc123def",
            "--image-tar", "/path/to/image.tar"
        ]
        
        with patch('sys.argv', test_args):
            push_image.main()
        
        # Verify both SHA and latest tags were used
        tag_calls = [call[0] for call in mock_tag.call_args_list]
        self.assertIn(("candidate_image:latest", "ghcr.io/owner/repo:abc123def"), tag_calls)
        self.assertIn(("candidate_image:latest", "ghcr.io/owner/repo:latest"), tag_calls)
        
        # Verify both tags were pushed
        push_calls = [call[0][0] for call in mock_push.call_args_list]
        self.assertIn("ghcr.io/owner/repo:abc123def", push_calls)
        self.assertIn("ghcr.io/owner/repo:latest", push_calls)
        
        # Verify outputs were set
        output_calls = [call[0] for call in mock_output.call_args_list]
        self.assertIn(('digest', 'sha256:def456'), output_calls)
        self.assertIn(('tag', 'ghcr.io/owner/repo:latest'), output_calls)


if __name__ == '__main__':
    unittest.main()
