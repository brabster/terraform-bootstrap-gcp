#!/usr/bin/env python3

import argparse
import os
import google.auth
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

def main():
    parser = argparse.ArgumentParser(description="Google Cloud Authentication")
    parser.add_argument("--project", help="Google Cloud project ID")
    parser.add_argument("--billing-project", help="Google Cloud billing project ID")
    args = parser.parse_args()

    project_id = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    billing_project_id = args.billing_project or os.environ.get("GOOGLE_BILLING_PROJECT") or project_id

    if not project_id:
        raise ValueError("Google Cloud project ID is not set. Please set the GOOGLE_CLOUD_PROJECT environment variable or use the --project flag.")

    credentials, _ = google.auth.default(
        scopes=["https'://www.googleapis.com/auth/cloud-platform"],
        project_id=project_id,
        quota_project_id=billing_project_id,
    )

    if isinstance(credentials, Credentials) and credentials.valid and credentials.token:
        print("Already authenticated.")
    else:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            project_id=project_id,
            quota_project_id=billing_project_id,
        )

    # Save the credentials to the default path
    google.auth.save_credentials_to_file(credentials, google.auth.default_credentials_path())
    print(f"Successfully authenticated. Credentials saved to {google.auth.default_credentials_path()}")

if __name__ == "__main__":
    main()
