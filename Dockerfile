# Base image with Node.js
FROM node:18-slim

# Install Python 3, pip, and git (git might be needed for some npm/pip installs)
# Running as root for installations
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Switch back to the non-root node user provided by the base image
USER node

WORKDIR /app

# Copy dependency files first for caching
# Use --chown=node:node to ensure the non-root user owns the files
COPY --chown=node:node package.json ./
COPY --chown=node:node package-lock.json ./
COPY --chown=node:node requirements.txt ./

# Copy the rest of the application code (respects .dockerignore if present)
# This includes push_config.py, pull_config.py, resources/, etc.
COPY --chown=node:node . .