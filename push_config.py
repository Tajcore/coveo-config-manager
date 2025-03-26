import subprocess
import sys
import os
from dotenv import load_dotenv
import threading
import io

load_dotenv()

def run_command_interactive(command, input_str=None):
    """Run a command and print output in real-time."""
    try:
        print("Running command:", " ".join(command))
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE if input_str else None,
        )

        def read_output(pipe, is_stdout):
            """Read and print output from a pipe."""
            try:
                while True:
                    line_bytes = pipe.readline()
                    if not line_bytes:
                        break
                    line = line_bytes.decode('utf-8', errors='replace')
                    print(line, end="")
            except ValueError as e:
                print(f"Error reading output: {e}")

        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, True))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, False))

        stdout_thread.start()
        stderr_thread.start()

        if input_str:
            process.stdin.write(input_str.encode('utf-8')) # encode the string.
            process.stdin.flush()
            process.stdin.close()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()

        if process.returncode != 0:
            print(f"Command failed with return code: {process.returncode}")
            sys.exit(process.returncode)

    except FileNotFoundError:
        print(f"Command not found: {' '.join(command)}")
        sys.exit(1)

def main():
    """Main function to push configuration snapshots to a target environment."""
    target_org_id = os.getenv("TARGET_ORG_ID")
    target_api_key = os.getenv("TARGET_API_KEY")
    if not all([target_org_id, target_api_key]):
        print("Please set TARGET_ORG_ID and TARGET_API_KEY in your .env file.")
        sys.exit(1)

    cli_cmd = os.path.join("coveo")

    auth_cmd = [cli_cmd, "auth:token", "-t", target_api_key]
    print("=== Authenticating to target environment ===")
    run_command_interactive(auth_cmd)

    push_cmd = [cli_cmd, "org:resources:push"]
    print("=== Pushing configuration to target environment ===")
    run_command_interactive(push_cmd, input_str="y\n")

if __name__ == "__main__":
    main()