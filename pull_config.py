"""This module pulls configuration snapshots from a Dev environment using the
Coveo CLI and commits them to a Git repository.
It first authenticates with the Dev environment.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def run_command(command):
    """Run a shell command and print its output."""
    try:
        # Ensure the command is only modified once
        if not command[0].startswith("node_modules"):
            command[0] = os.path.join("node_modules", ".bin", command[0])
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

    # 1. Authenticate to the Dev environment
    auth_cmd = [cli_cmd, "auth:token", "-t", dev_api_key]
    print("=== Authenticating to Dev Environment ===")
    run_command(auth_cmd)

    # 2. Pull the configuration snapshot from the Dev environment
    pull_cmd = [cli_cmd, "org:resources:pull"]
    print("=== Pulling configuration from Dev ===")
    run_command(pull_cmd)

    # At this point, the snapshot is saved (typically in a `resources/` folder)
    # Now add and commit these changes to Git
    print("=== Committing configuration snapshot to Git ===")
    run_command(["git", "add", "resources/"])
    # Check if there are changes to commit


if __name__ == "__main__":
    main()
