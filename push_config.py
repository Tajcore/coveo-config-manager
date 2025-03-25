"""This module pushes configuration snapshots to a target environment
using the Coveo CLI."""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()


def run_command(command):
    """Run a shell command and print its output."""
    print("Running command:", " ".join(command))
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as err:
        print("Command failed:", err.stderr)
        sys.exit(err.returncode)


def main():
    """Main function to push configuration snapshots to a target environment."""
    # Load target environment credentials
    target_org_id = os.getenv("TARGET_ORG_ID")
    target_api_key = os.getenv("TARGET_API_KEY")
    if not all([target_org_id, target_api_key]):
        print("Please set TARGET_ORG_ID and TARGET_API_KEY in your .env file.")
        sys.exit(1)

    # Use npx to run the locally installed Coveo CLI
    cli_cmd = "npx coveo"

    # Optionally: Preview differences before pushing (this can be commented out if not needed)
    preview_cmd = cli_cmd.split() + [
        "org:resources:preview",
        "--org", target_org_id,
        "--api-key", target_api_key
    ]
    print("=== Previewing configuration differences for target environment ===")
    run_command(preview_cmd)

    # Push the configuration snapshot to the target environment
    push_cmd = cli_cmd.split() + [
        "org:resources:push",
        "--org", target_org_id,
        "--api-key", target_api_key
    ]
    print("=== Pushing configuration to target environment ===")
    run_command(push_cmd)


if __name__ == "__main__":
    main()
