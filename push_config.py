import subprocess
import sys
import os
import shutil # Keep shutil in case needed later, though not used currently
from dotenv import load_dotenv
from datetime import datetime
import logging

# --- Logging Setup ---
# Copied directly from pull_config.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    stream=sys.stdout
)
# --- End Logging Setup ---

load_dotenv()
logging.info("Loaded environment variables from .env file if present.")


# Updated run_command function with timeout
# Copied directly from pull_config.py
def run_command(command, input_data=None, timeout_seconds=120, env=None):
    """Run a shell command, optionally passing data to stdin, log details, handle timeout, and return output."""
    try:
        run_args = {
            "check": True,
            "capture_output": True,
            "text": True,
            "encoding": 'utf-8',
            "timeout": timeout_seconds,
            # Pass specific env or inherit from parent if None
            "env": env or os.environ.copy()
        }

        if input_data is not None:
            run_args["input"] = input_data
            # Avoid logging sensitive input like API keys
            if "auth:token" in command:
                 logging.debug("Input data provided to subprocess stdin (length: %d) for auth", len(input_data))
            else:
                 logging.debug("Input data provided to subprocess stdin: %r", input_data)
        else:
            logging.debug("No input data provided to subprocess stdin.")

        logging.info("Running command: %s (Timeout: %ds)", ' '.join(command), timeout_seconds)

        result = subprocess.run(command, **run_args)

        # Log stdout/stderr only if they contain data
        if result.stdout:
             logging.debug("Command stdout:\n%s", result.stdout.strip())
        if result.stderr:
             logging.debug("Command stderr:\n%s", result.stderr.strip())

        logging.info("Command finished successfully.")
        return result.stdout
    except subprocess.TimeoutExpired as err:
        logging.error("Command timed out after %d seconds: %s", err.timeout, ' '.join(err.cmd))
        # Try to log partial output if available
        if err.stdout:
             logging.error("Timeout stdout (partial):\n%s", err.stdout.strip())
        if err.stderr:
             logging.error("Timeout stderr (partial):\n%s", err.stderr.strip())
        sys.exit(1) # Exit after timeout
    except subprocess.CalledProcessError as err:
        logging.error("Command failed with exit code %d: %s", err.returncode, ' '.join(err.cmd))
        # Log full output on error for easier debugging
        if err.stdout:
            logging.error("Failed command stdout:\n%s", err.stdout.strip())
        if err.stderr:
            logging.error("Failed command stderr:\n%s", err.stderr.strip())
        sys.exit(err.returncode)
    except FileNotFoundError:
        logging.error("Command not found: %s", command[0])
        logging.error("Ensure the path to the executable is correct and it has execute permissions.")
        sys.exit(1)
    except Exception as e: # Catch other potential errors
        logging.error("An unexpected error occurred: %s", e)
        sys.exit(1)


def main():
    """Main function to push configuration snapshots to a target environment."""
    logging.info("Push script execution started.")

    target_org_id = os.getenv("TARGET_ORG_ID")
    target_api_key = os.getenv("TARGET_API_KEY")

    # Add checks similar to pull_config.py
    if not target_org_id:
        logging.error("TARGET_ORG_ID not found in environment variables.")
        sys.exit(1)
    else:
        logging.debug("TARGET_ORG_ID loaded.")

    if not target_api_key:
        logging.error("TARGET_API_KEY not found in environment variables.")
        sys.exit(1)
    else:
        # Avoid logging the actual key even in debug for security
        logging.debug("TARGET_API_KEY loaded.")

    # Use CLI path finding logic from pull_config.py
    cli_cmd_path = os.path.join("node_modules", ".bin", "coveo")
    logging.debug("Using base CLI path: %s", cli_cmd_path)

    if not os.path.isfile(cli_cmd_path) or not os.access(cli_cmd_path, os.X_OK):
        cli_cmd_path_win = cli_cmd_path + '.cmd'
        if os.path.isfile(cli_cmd_path_win) and os.access(cli_cmd_path_win, os.X_OK):
            cli_cmd_path = cli_cmd_path_win
            logging.debug("Using Windows CLI path: %s", cli_cmd_path)
        else:
            # Try finding coveo in PATH as a last resort (like original push.py implicitly did)
            logging.warning("Coveo CLI not found at '%s' (or .cmd). Checking PATH.", os.path.join("node_modules", ".bin", "coveo"))
            cli_cmd_path_from_path = shutil.which("coveo")
            if cli_cmd_path_from_path:
                 cli_cmd_path = cli_cmd_path_from_path
                 logging.info("Using CLI from PATH: %s", cli_cmd_path)
            else:
                 logging.error("Coveo CLI not found in node_modules/.bin or system PATH.")
                 sys.exit(1)


    # 1. Authenticate to the Target environment using token via stdin
    #    Using the same method as the working pull_config.py
    auth_cmd = [
        cli_cmd_path,
        "auth:token",
        "--stdin" # Explicitly tell CLI to read from stdin
    ]
    logging.info("=== Authenticating to Target Environment ===")
    auth_timeout = 60
    try:
        # Pass the API key PLUS A NEWLINE character as input_data
        # The newline simulates pressing Enter after pasting the token
        run_command(auth_cmd, input_data=target_api_key + '\n', timeout_seconds=auth_timeout)
        logging.info("=== Authentication command finished successfully ===")
    except SystemExit as e:
        # run_command already logs the error and exits, but we add context
        logging.error("Authentication step failed.")
        sys.exit(e.code) # Re-exit with the same code


    # 2. Push the configuration snapshot to the Target environment
    #    Requires confirmation ('y' + newline) via stdin
    push_cmd = [
        cli_cmd_path,
        "org:resources:push",
    ]
    logging.info("=== Pushing configuration to Target ===")
    push_timeout = 300 # Allow more time for push operation
    try:
        # Provide 'y' followed by newline to confirm the push
        run_command(push_cmd, input_data="y\n", timeout_seconds=push_timeout)
        logging.info("=== Push command finished successfully ===")
    except SystemExit as e:
        logging.error("Push step failed.")
        sys.exit(e.code)

    logging.info("Push script finished successfully.")


if __name__ == "__main__":
    main()