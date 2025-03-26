import subprocess
import sys
import os
import shutil
from dotenv import load_dotenv
from datetime import datetime
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    stream=sys.stdout
)
# --- End Logging Setup ---

load_dotenv()
logging.info("Loaded environment variables from .env file if present.")


# Updated run_command function with timeout
def run_command(command, input_data=None, timeout_seconds=120, env=None): # Added env parameter
    """Run a shell command, optionally passing data to stdin, log details, handle timeout, and return output."""
    try:
        run_args = {
            "check": True,
            "capture_output": True,
            "text": True,
            "encoding": 'utf-8',
            "timeout": timeout_seconds, # Pass timeout to subprocess.run
        }

        if input_data is not None:
            run_args["input"] = input_data
            logging.debug("Input data provided to subprocess stdin (length: %d)", len(input_data))
        else:
            logging.debug("No input data provided to subprocess stdin.")

        logging.info("Running command: %s (Timeout: %ds)", ' '.join(command), timeout_seconds)

        result = subprocess.run(command, **run_args)

        logging.debug("Command stdout:\n%s", result.stdout)
        if result.stderr:
            logging.debug("Command stderr:\n%s", result.stderr)

        logging.info("Command finished successfully.")
        return result.stdout
    except subprocess.TimeoutExpired as err:
        logging.error("Command timed out after %d seconds: %s", err.timeout, ' '.join(err.cmd))
        logging.error("Timeout stdout (partial):\n%s", err.stdout)
        logging.error("Timeout stderr (partial):\n%s", err.stderr)
        sys.exit(1) # Exit after timeout
    except subprocess.CalledProcessError as err:
        logging.error("Command failed with exit code %d: %s", err.returncode, ' '.join(err.cmd))
        logging.error("Failed command stdout:\n%s", err.stdout)
        logging.error("Failed command stderr:\n%s", err.stderr)
        sys.exit(err.returncode)
    except FileNotFoundError:
        logging.error("Command not found: %s", command[0])
        logging.error("Ensure the path to the executable is correct and it has execute permissions.")
        sys.exit(1)


def main():
    logging.info("Script execution started.")

    dev_org_id = os.getenv("DEV_ORG_ID")
    dev_api_key = os.getenv("DEV_API_KEY")

    if not dev_org_id:
        logging.error("DEV_ORG_ID not found.")
        sys.exit(1)
    else:
        logging.debug("DEV_ORG_ID loaded.")

    if not dev_api_key:
        logging.error("DEV_API_KEY not found.")
        sys.exit(1)
    else:
        # Avoid logging the actual key even in debug for security
        logging.debug("DEV_API_KEY loaded.")

    cli_cmd_path = os.path.join("node_modules", ".bin", "coveo")
    logging.debug("Using CLI path: %s", cli_cmd_path)

    # Verify the CLI command exists and is executable (remains the same)
    if not os.path.isfile(cli_cmd_path) or not os.access(cli_cmd_path, os.X_OK):
        cli_cmd_path_win = cli_cmd_path + '.cmd'
        if os.path.isfile(cli_cmd_path_win) and os.access(cli_cmd_path_win, os.X_OK):
            cli_cmd_path = cli_cmd_path_win
            logging.debug("Using Windows CLI path: %s", cli_cmd_path)
        else:
            logging.error("Coveo CLI not found or not executable at '%s' (and not found with .cmd extension).", cli_cmd_path)
            sys.exit(1)

    resources_path = "resources"
    if os.path.exists(resources_path):
        logging.info("Deleting existing '%s' folder.", resources_path)
        try:
            shutil.rmtree(resources_path)
            logging.info("Successfully deleted '%s'.", resources_path)
        except OSError as e:
            logging.error("Error deleting folder '%s': %s", resources_path, e)
            sys.exit(1)
    else:
        logging.info("'%s' folder does not exist.", resources_path)

    # --- MODIFIED AUTHENTICATION ---
    # Option 1: Use auth:login command with flags (Recommended)
    auth_cmd = [
        cli_cmd_path,
        "auth:token",
        "--stdin"
    ]
    logging.info("=== Authenticating to Dev Environment using auth:login ===")
    auth_timeout = 60
    try:
        # No need for input_data here
        run_command(auth_cmd, timeout_seconds=auth_timeout, input_data=dev_api_key)
        logging.info("=== Authentication command finished ===")
    except SystemExit as e:
        logging.error("Authentication failed or timed out after %d seconds.", auth_timeout)
        sys.exit(e.code)

    # Option 2: Rely on Environment Variables (Alternative)
    # Set environment variables for the subprocess
    # coveo_env = os.environ.copy()
    # coveo_env["COVEO_ORG_ID"] = dev_org_id
    # coveo_env["COVEO_ACCESS_TOKEN"] = dev_api_key
    # logging.info("=== Assuming authentication via COVEO_ORG_ID and COVEO_ACCESS_TOKEN environment variables ===")
    # You might not need an explicit auth command if using env vars,
    # the subsequent commands might pick them up automatically.
    # Test if `org:resources:pull` works directly after setting env vars.
    # --- END MODIFIED AUTHENTICATION ---


    # 2. Pull the configuration snapshot (remains mostly the same)
    #    Make sure the org ID is correctly passed if not using env vars for auth.
    #    If using Env Vars (Option 2 above), you might not need -o flag here.
    pull_cmd = [
        cli_cmd_path,
        "org:resources:pull",
        "-o", dev_org_id # Keep this unless relying purely on COVEO_ORG_ID env var
    ]
    logging.info("=== Pulling configuration from Dev ===")
    # If using Env Vars (Option 2), pass the modified environment:
    # run_command(pull_cmd, env=coveo_env)
    # If using auth:login (Option 1), the session should be active, no env needed here:
    run_command(pull_cmd)
    logging.info("=== Pull command finished ===")

    logging.info("Script finished successfully.")


if __name__ == "__main__":
    main()