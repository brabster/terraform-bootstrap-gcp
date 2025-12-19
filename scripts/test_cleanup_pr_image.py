#!/usr/bin/env python3
"""
Unit tests for cleanup_pr_image.py script.

These tests verify core functionality without requiring actual API calls or authentication.
"""

import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import json

# Add parent directory to path to import the module in a way that works across environments
script_dir = str(Path(__file__).resolve().parent)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import cleanup_pr_image


class TestArgumentParsing(unittest.TestCase):
    """Test command-line argument parsing."""
    
    def test_parse_args_with_all_required(self):
        """Test parsing arguments with all required parameters."""
        test_args = [
            "cleanup_pr_image.py",
            "--pr-number", "42",
            "--repository", "owner/repo",
            "--owner", "owner",
            "--token", "ghp_test123",
            "--actor", "testuser"
        ]
        
        with patch('sys.argv', test_args):
            args = cleanup_pr_image.parse_args()
        
        self.assertEqual(args.pr_number, "42")
        self.assertEqual(args.repository, "owner/repo")
        self.assertEqual(args.owner, "owner")
        self.assertEqual(args.token, "ghp_test123")
        self.assertEqual(args.actor, "testuser")


class TestVersionIdLookup(unittest.TestCase):
    """Test version ID lookup from package versions."""
    
    def test_find_version_id_by_tag_found(self):
        """Test finding version ID when tag exists."""
        versions = [
            {
                "id": 123,
                "metadata": {
                    "container": {
                        "tags": ["latest", "v1.0"]
                    }
                }
            },
            {
                "id": 456,
                "metadata": {
                    "container": {
                        "tags": ["pr-42", "test"]
                    }
                }
            }
        ]
        
        version_id = cleanup_pr_image.find_version_id_by_tag(versions, "pr-42")
        self.assertEqual(version_id, 456)
    
    def test_find_version_id_by_tag_not_found(self):
        """Test finding version ID when tag doesn't exist."""
        versions = [
            {
                "id": 123,
                "metadata": {
                    "container": {
                        "tags": ["latest", "v1.0"]
                    }
                }
            }
        ]
        
        version_id = cleanup_pr_image.find_version_id_by_tag(versions, "pr-99")
        self.assertIsNone(version_id)
    
    def test_find_version_id_with_missing_metadata(self):
        """Test finding version ID when metadata is missing."""
        versions = [
            {"id": 123},  # No metadata
            {
                "id": 456,
                "metadata": {}  # Empty metadata
            }
        ]
        
        version_id = cleanup_pr_image.find_version_id_by_tag(versions, "pr-42")
        self.assertIsNone(version_id)


class TestGetPackageVersions(unittest.TestCase):
    """Test fetching package versions from GitHub API."""
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_get_package_versions_success(self, mock_urlopen):
        """Test successful package versions fetch."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([
            {"id": 123, "metadata": {"container": {"tags": ["latest"]}}}
        ]).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        versions = cleanup_pr_image.get_package_versions("owner", "repo", "token123")
        
        self.assertIsNotNone(versions)
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["id"], 123)
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_get_package_versions_not_found(self, mock_urlopen):
        """Test package versions fetch when package doesn't exist."""
        from urllib.error import HTTPError
        
        mock_urlopen.side_effect = HTTPError(
            "url", 404, "Not Found", {}, None
        )
        
        versions = cleanup_pr_image.get_package_versions("owner", "repo", "token123")
        
        self.assertIsNone(versions)
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_get_package_versions_other_http_error(self, mock_urlopen):
        """Test package versions fetch with other HTTP errors."""
        from urllib.error import HTTPError
        
        mock_urlopen.side_effect = HTTPError(
            "url", 500, "Internal Server Error", {}, None
        )
        
        versions = cleanup_pr_image.get_package_versions("owner", "repo", "token123")
        
        self.assertIsNone(versions)


class TestDeletePackageVersion(unittest.TestCase):
    """Test deleting package versions via GitHub API."""
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_delete_package_version_success(self, mock_urlopen):
        """Test successful package version deletion."""
        mock_response = MagicMock()
        mock_response.status = 204
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = cleanup_pr_image.delete_package_version(
            "owner", "repo", 123, "token123"
        )
        
        self.assertTrue(result)
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_delete_package_version_unexpected_status(self, mock_urlopen):
        """Test package version deletion with unexpected status code."""
        mock_response = MagicMock()
        mock_response.status = 200  # Unexpected, should be 204
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = cleanup_pr_image.delete_package_version(
            "owner", "repo", 123, "token123"
        )
        
        self.assertFalse(result)
    
    @patch('cleanup_pr_image.request.urlopen')
    def test_delete_package_version_http_error(self, mock_urlopen):
        """Test package version deletion with HTTP error."""
        from urllib.error import HTTPError
        
        mock_error = HTTPError("url", 403, "Forbidden", {}, None)
        mock_error.read = MagicMock(return_value=b"Access denied")
        mock_urlopen.side_effect = mock_error
        
        result = cleanup_pr_image.delete_package_version(
            "owner", "repo", 123, "token123"
        )
        
        self.assertFalse(result)


class TestMainFunction(unittest.TestCase):
    """Test main function orchestration."""
    
    @patch('cleanup_pr_image.delete_package_version')
    @patch('cleanup_pr_image.find_version_id_by_tag')
    @patch('cleanup_pr_image.get_package_versions')
    @patch('cleanup_pr_image.docker_login')
    def test_main_successful_deletion(self, mock_login, mock_get_versions, 
                                      mock_find_version, mock_delete):
        """Test successful main execution with version found and deleted."""
        # Setup mocks
        mock_get_versions.return_value = [{"id": 123}]
        mock_find_version.return_value = 123
        mock_delete.return_value = True
        
        test_args = [
            "cleanup_pr_image.py",
            "--pr-number", "42",
            "--repository", "owner/repo",
            "--owner", "owner",
            "--token", "token123",
            "--actor", "testuser"
        ]
        
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                cleanup_pr_image.main()
        
        self.assertEqual(cm.exception.code, 0)
        mock_delete.assert_called_once()
    
    @patch('cleanup_pr_image.get_package_versions')
    @patch('cleanup_pr_image.docker_login')
    def test_main_package_not_found(self, mock_login, mock_get_versions):
        """Test main when package doesn't exist."""
        mock_get_versions.return_value = None
        
        test_args = [
            "cleanup_pr_image.py",
            "--pr-number", "42",
            "--repository", "owner/repo",
            "--owner", "owner",
            "--token", "token123",
            "--actor", "testuser"
        ]
        
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                cleanup_pr_image.main()
        
        self.assertEqual(cm.exception.code, 0)  # Expected: exits with success
    
    @patch('cleanup_pr_image.find_version_id_by_tag')
    @patch('cleanup_pr_image.get_package_versions')
    @patch('cleanup_pr_image.docker_login')
    def test_main_version_not_found(self, mock_login, mock_get_versions, mock_find_version):
        """Test main when version with tag doesn't exist."""
        mock_get_versions.return_value = [{"id": 123}]
        mock_find_version.return_value = None
        
        test_args = [
            "cleanup_pr_image.py",
            "--pr-number", "42",
            "--repository", "owner/repo",
            "--owner", "owner",
            "--token", "token123",
            "--actor", "testuser"
        ]
        
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                cleanup_pr_image.main()
        
        self.assertEqual(cm.exception.code, 0)  # Expected: exits with success
    
    @patch('cleanup_pr_image.delete_package_version')
    @patch('cleanup_pr_image.find_version_id_by_tag')
    @patch('cleanup_pr_image.get_package_versions')
    @patch('cleanup_pr_image.docker_login')
    def test_main_deletion_failed(self, mock_login, mock_get_versions,
                                   mock_find_version, mock_delete):
        """Test main when deletion fails."""
        mock_get_versions.return_value = [{"id": 123}]
        mock_find_version.return_value = 123
        mock_delete.return_value = False
        
        test_args = [
            "cleanup_pr_image.py",
            "--pr-number", "42",
            "--repository", "owner/repo",
            "--owner", "owner",
            "--token", "token123",
            "--actor", "testuser"
        ]
        
        with patch('sys.argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                cleanup_pr_image.main()
        
        self.assertEqual(cm.exception.code, 1)  # Expected: exits with error


if __name__ == "__main__":
    unittest.main()
