#!/usr/bin/env python3
"""
Unit tests for push_image.py script.

These tests verify core functionality without requiring Docker or actual image operations.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path to import the module in a way that works across environments
script_dir = str(Path(__file__).resolve().parent)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import push_image


class TestDigestExtraction(unittest.TestCase):
    """Test digest extraction from docker push output."""
    
    @patch('push_image.subprocess.run')
    def test_docker_push_extracts_digest_from_valid_output(self, mock_run):
        """Test that docker_push correctly extracts digest from valid output."""
        # Mock subprocess.run to return valid docker push output
        mock_result = MagicMock()
        mock_result.stdout = """
The push refers to repository [ghcr.io/test/repo]
abc123: Pushed
def456: Pushed
latest: digest: sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef size: 1234
        """
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Call the actual docker_push function
        digest = push_image.docker_push("ghcr.io/test/repo:latest")
        
        # Verify the digest was extracted correctly
        self.assertEqual(digest, "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(len(digest), 71)  # "sha256:" (7) + 64 hex chars
    
    @patch('push_image.subprocess.run')
    def test_docker_push_fails_with_invalid_output(self, mock_run):
        """Test that docker_push exits when digest cannot be extracted."""
        # Mock subprocess.run to return invalid output
        mock_result = MagicMock()
        mock_result.stdout = "No digest here"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Should exit with error
        with self.assertRaises(SystemExit) as cm:
            push_image.docker_push("ghcr.io/test/repo:latest")
        self.assertEqual(cm.exception.code, 1)
    
    @patch('push_image.subprocess.run')
    def test_docker_push_handles_calledprocesserror_with_stderr(self, mock_run):
        """Test that docker_push handles CalledProcessError with stderr correctly."""
        import subprocess
        # Mock subprocess.run to raise CalledProcessError with stderr
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'push', 'test'],
            stderr=b"Permission denied"
        )
        
        # Should exit with error
        with self.assertRaises(SystemExit) as cm:
            push_image.docker_push("ghcr.io/test/repo:latest")
        self.assertEqual(cm.exception.code, 1)
    
    @patch('push_image.subprocess.run')
    def test_docker_push_handles_calledprocesserror_without_stderr(self, mock_run):
        """Test that docker_push handles CalledProcessError when stderr is None."""
        import subprocess
        # Mock subprocess.run to raise CalledProcessError with None stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'push', 'test']
        )
        error.stderr = None
        mock_run.side_effect = error
        
        # Should exit with error without AttributeError
        with self.assertRaises(SystemExit) as cm:
            push_image.docker_push("ghcr.io/test/repo:latest")
        self.assertEqual(cm.exception.code, 1)
    
    @patch('push_image.subprocess.run')
    def test_docker_push_handles_timeout(self, mock_run):
        """Test that docker_push handles TimeoutExpired correctly."""
        import subprocess
        # Mock subprocess.run to raise TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['docker', 'push', 'test'],
            timeout=60
        )
        
        # Should exit with error
        with self.assertRaises(SystemExit) as cm:
            push_image.docker_push("ghcr.io/test/repo:latest")
        self.assertEqual(cm.exception.code, 1)
    
    @patch('push_image.subprocess.run')
    def test_load_image_handles_calledprocesserror_without_stderr(self, mock_run):
        """Test that load_image handles CalledProcessError when stderr is None."""
        import subprocess
        # Mock subprocess.run to raise CalledProcessError with None stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'load', '-i', 'test.tar']
        )
        error.stderr = None
        mock_run.side_effect = error
        
        # Should exit with error without AttributeError
        with self.assertRaises(SystemExit) as cm:
            push_image.load_image("test.tar")
        self.assertEqual(cm.exception.code, 1)
    
    @patch('push_image.subprocess.run')
    def test_docker_tag_handles_calledprocesserror_without_stderr(self, mock_run):
        """Test that docker_tag handles CalledProcessError when stderr is None."""
        import subprocess
        # Mock subprocess.run to raise CalledProcessError with None stderr
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['docker', 'tag', 'source', 'target']
        )
        error.stderr = None
        mock_run.side_effect = error
        
        # Should exit with error without AttributeError
        with self.assertRaises(SystemExit) as cm:
            push_image.docker_tag("source", "target")
        self.assertEqual(cm.exception.code, 1)


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



class TestMainFunctionTagging(unittest.TestCase):
    """Test main function tagging logic with different event types."""
    
    @patch('push_image.docker_push')
    @patch('push_image.docker_tag')
    @patch('push_image.load_image')
    @patch('push_image.set_github_output')
    def test_pr_event_uses_pr_tag(self, mock_output, mock_load, mock_tag, mock_push):
        """Test that PR events use pr-<number> tag."""
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
