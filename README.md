# Coveo Config Manager POC

This project demonstrates a Git-based promotion approach for managing Coveo configuration. It separates concerns into two main steps:

1. **Pulling from Dev:**  
   A Python script (`pull_config.py`) uses the Coveo CLI to pull a configuration snapshot from your Dev environment and commits it into your Git repository as the "source of truth."

2. **Pushing to Target:**  
   Another Python script (`push_config.py`) pushes the configuration snapshot from the repository to your target environment (QA or Prod). This script can be integrated into a CI/CD pipeline triggered by a branch merge, tag, or manual approval.

## Prerequisites

- [Node.js and npm](https://nodejs.org/en/) installed.
- Python 3.6+ installed.
- The Coveo CLI installed as a local dependency (via npm).

## Setup

1. **Clone the Repository:**
   ```bash
   git clone <repo-url>
   cd coveo-config-manager
