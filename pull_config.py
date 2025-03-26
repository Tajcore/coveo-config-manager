"""This module pulls configuration snapshots from a Dev environment using the
Coveo CLI and commits them to a Git repository.
It first authenticates with the Dev environment.
"""

import subprocess
import sys
import os
import shutil
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def run_command(command):
    """Run a shell command and print its output."""
    try:

        print("Running command:", " ".join(command))
        result = subprocess.run(" ".join(command), shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as err:
        print("Command failed:", err.stderr)
        sys.exit(err.returncode)


def main():
    """
    Main function to authenticate with the Dev environment, pull configuration
    snapshots, and commit them to a Git repository.
    """
    # Load Dev environment credentials
    dev_org_id = os.getenv("DEV_ORG_ID")
    dev_api_key = os.getenv("DEV_API_KEY")
    if not all([dev_org_id, dev_api_key]):
        print("Please set DEV_ORG_ID and DEV_API_KEY in your .env file.")
        sys.exit(1)

    # Directly use the Coveo CLI from node_modules/.bin
    cli_cmd = os.path.join("node_modules", ".bin", "coveo") 
    
    # Delete Resources folder
    if os.path.exists("resources"):
        print("Deleting resources folder to ensure a clean pull")
        shutil.rmtree("resources")

    # 1. Authenticate to the Dev environment
    auth_cmd = [cli_cmd, "auth:token", "-t", dev_api_key]
    print("=== Authenticating to Dev Environment ===")
    run_command(auth_cmd)

    # 2. Pull the configuration snapshot from the Dev environment
    pull_cmd = [cli_cmd, "org:resources:pull"]
    print("=== Pulling configuration from Dev ===")
    run_command(pull_cmd)


if __name__ == "__main__":
    main()
