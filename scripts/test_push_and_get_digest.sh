#!/bin/env bash

# Test script for push_and_get_digest.sh
#
# This script tests the push_and_get_digest.sh script using a local Docker registry.
# It verifies that the script correctly:
# 1. Tags and pushes images
# 2. Extracts the digest from push output
# 3. Handles multiple tags
# 4. Validates error conditions
#
# Usage:
#   ./test_push_and_get_digest.sh
#
# Requirements:
#   - Docker must be installed and running
#   - Port 5000 must be available for local registry

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_UNDER_TEST="${SCRIPT_DIR}/push_and_get_digest.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Cleanup function
cleanup() {
    echo "Cleaning up test resources..."
    
    # Stop and remove local registry if running
    if docker ps -a | grep -q test-registry; then
        docker rm -f test-registry >/dev/null 2>&1 || true
    fi
    
    # Remove test images
    docker rmi test-image:v1 >/dev/null 2>&1 || true
    docker rmi localhost:5000/test:tag1 >/dev/null 2>&1 || true
    docker rmi localhost:5000/test:tag2 >/dev/null 2>&1 || true
}

# Setup test environment
setup_test_env() {
    echo "Setting up test environment..."
    
    # Start local Docker registry
    if docker ps | grep -q test-registry; then
        echo "Test registry already running"
    else
        docker run -d -p 5000:5000 --name test-registry registry:2 >/dev/null
        sleep 2
    fi
    
    # Create a minimal test image
    echo "FROM alpine:latest" | docker build -t test-image:v1 -q - >/dev/null
    
    echo "Test environment ready"
}

# Run a test
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "\n${YELLOW}Test ${TESTS_RUN}: ${test_name}${NC}"
    
    if $test_function; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Test: Script exists and is executable
test_script_exists() {
    [[ -f "${SCRIPT_UNDER_TEST}" ]] && [[ -x "${SCRIPT_UNDER_TEST}" ]]
}

# Test: No arguments shows usage and exits with error
test_no_arguments() {
    local output
    output=$("${SCRIPT_UNDER_TEST}" 2>&1 || true)
    if echo "$output" | grep -q "Usage:"; then
        return 0
    else
        return 1
    fi
}

# Test: Single tag push and digest extraction
test_single_tag_push() {
    local digest
    digest=$("${SCRIPT_UNDER_TEST}" test-image:v1 localhost:5000/test:tag1 2>/dev/null)
    
    # Verify digest format (sha256: followed by 64 hex characters)
    if [[ "${digest}" =~ ^sha256:[a-f0-9]{64}$ ]]; then
        echo "  Extracted digest: ${digest}"
        return 0
    else
        echo "  Invalid digest format: ${digest}"
        return 1
    fi
}

# Test: Multiple tags push
test_multiple_tags_push() {
    local digest
    digest=$("${SCRIPT_UNDER_TEST}" test-image:v1 \
        localhost:5000/test:tag1 \
        localhost:5000/test:tag2 2>/dev/null)
    
    # Verify digest format
    if [[ "${digest}" =~ ^sha256:[a-f0-9]{64}$ ]]; then
        # Verify both tags exist in registry
        if docker pull localhost:5000/test:tag1 >/dev/null 2>&1 && \
           docker pull localhost:5000/test:tag2 >/dev/null 2>&1; then
            echo "  Both tags successfully pushed"
            return 0
        else
            echo "  Failed to verify both tags in registry"
            return 1
        fi
    else
        echo "  Invalid digest format: ${digest}"
        return 1
    fi
}

# Test: Invalid local image fails gracefully
test_invalid_image() {
    local output
    output=$("${SCRIPT_UNDER_TEST}" nonexistent-image:latest localhost:5000/test:fail 2>&1 || true)
    if echo "$output" | grep -q "not found"; then
        return 0
    else
        return 1
    fi
}

# Test: Digest format validation
test_digest_format() {
    local digest
    digest=$("${SCRIPT_UNDER_TEST}" test-image:v1 localhost:5000/test:format-test 2>/dev/null)
    
    # Must start with sha256:
    if [[ ! "${digest}" =~ ^sha256: ]]; then
        echo "  Digest doesn't start with 'sha256:'"
        return 1
    fi
    
    # Must be exactly 64 hex characters after sha256:
    local hash_part="${digest#sha256:}"
    if [[ ${#hash_part} -ne 64 ]]; then
        echo "  Hash part is not 64 characters: ${#hash_part}"
        return 1
    fi
    
    # Must contain only lowercase hex characters
    if [[ ! "${hash_part}" =~ ^[a-f0-9]{64}$ ]]; then
        echo "  Hash contains invalid characters"
        return 1
    fi
    
    return 0
}

# Main test execution
main() {
    echo "=================================="
    echo "Testing push_and_get_digest.sh"
    echo "=================================="
    
    # Setup
    trap cleanup EXIT
    cleanup
    setup_test_env
    
    # Run tests
    run_test "Script exists and is executable" test_script_exists
    run_test "No arguments shows usage" test_no_arguments
    run_test "Single tag push and digest extraction" test_single_tag_push
    run_test "Multiple tags push" test_multiple_tags_push
    run_test "Invalid local image fails gracefully" test_invalid_image
    run_test "Digest format validation" test_digest_format
    
    # Summary
    echo ""
    echo "=================================="
    echo "Test Summary"
    echo "=================================="
    echo "Tests run:    ${TESTS_RUN}"
    echo -e "Tests passed: ${GREEN}${TESTS_PASSED}${NC}"
    
    if [[ ${TESTS_FAILED} -gt 0 ]]; then
        echo -e "Tests failed: ${RED}${TESTS_FAILED}${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    fi
}

main "$@"
