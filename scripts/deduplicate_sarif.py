#!/usr/bin/env python3
# Maintained by: brabster (project owner)
"""
Deduplicate SARIF vulnerability results from osv-scanner.

This script processes SARIF output from osv-scanner to remove duplicate vulnerability
entries by generating stable fingerprints based on ruleId and affected package information.
GitHub Code Scanning uses fingerprints to deduplicate alerts, but osv-scanner doesn't
generate them, leading to duplicate alerts in the security tab.
"""

import argparse
import hashlib
import json
import re
import sys


def extract_package_info(message_text):
    """
    Extract package name and version from the vulnerability message.
    
    Example message: "Package 'gnupg2@2.4.4-2ubuntu17.3' is vulnerable to 'UBUNTU-CVE-2022-3219'."
    Returns: ('gnupg2', '2.4.4-2ubuntu17.3')
    """
    # Match pattern: Package 'name@version' is vulnerable to...
    match = re.search(r"Package '([^@]+)@([^']+)'", message_text)
    if match:
        return match.group(1), match.group(2)
    return None, None


def generate_fingerprint(rule_id, package_name, package_version, location_uri):
    """
    Generate a stable fingerprint for a vulnerability.
    
    The fingerprint is created by hashing the combination of:
    - ruleId (CVE identifier)
    - package name
    - package version
    - location URI (to differentiate same package in different locations)
    """
    components = [rule_id, package_name or "", package_version or "", location_uri or ""]
    fingerprint_input = "|".join(components)
    return hashlib.sha256(fingerprint_input.encode()).hexdigest()


def deduplicate_sarif(input_path, output_path):
    """
    Deduplicate SARIF results by adding fingerprints and removing duplicates.
    """
    with open(input_path, "r") as f:
        sarif = json.load(f)
    
    if "runs" not in sarif or len(sarif["runs"]) == 0:
        print("No runs found in SARIF file", file=sys.stderr)
        sys.exit(1)
    
    run = sarif["runs"][0]
    original_count = len(run.get("results", []))
    
    # Track unique results by fingerprint
    unique_results = {}
    
    for result in run.get("results", []):
        rule_id = result.get("ruleId", "")
        message_text = result.get("message", {}).get("text", "")
        
        # Extract package info from message
        package_name, package_version = extract_package_info(message_text)
        
        # Get location URI
        location_uri = ""
        locations = result.get("locations", [])
        if locations:
            physical_location = locations[0].get("physicalLocation", {})
            artifact_location = physical_location.get("artifactLocation", {})
            location_uri = artifact_location.get("uri", "")
        
        # Generate fingerprint
        fingerprint = generate_fingerprint(rule_id, package_name, package_version, location_uri)
        
        # Add fingerprint to result
        if "partialFingerprints" not in result:
            result["partialFingerprints"] = {}
        result["partialFingerprints"]["primaryLocationLineHash"] = fingerprint
        
        # Keep only the first occurrence of each unique fingerprint
        if fingerprint not in unique_results:
            unique_results[fingerprint] = result
    
    # Replace results with deduplicated list
    run["results"] = list(unique_results.values())
    deduplicated_count = len(run["results"])
    
    # Write deduplicated SARIF
    with open(output_path, "w") as f:
        json.dump(sarif, f, indent=2)
    
    print(f"Deduplicated SARIF: {original_count} results -> {deduplicated_count} unique results")
    print(f"Removed {original_count - deduplicated_count} duplicate entries")


def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate SARIF vulnerability results from osv-scanner"
    )
    parser.add_argument("input", help="Input SARIF file")
    parser.add_argument("output", help="Output SARIF file")
    
    args = parser.parse_args()
    
    deduplicate_sarif(args.input, args.output)


if __name__ == "__main__":
    main()
