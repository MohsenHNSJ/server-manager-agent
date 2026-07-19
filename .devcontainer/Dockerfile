# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:1c3a6304ca90d6843915738d1adfbc4db1a660a65fa96948b88048357cc3811a
# Set up required dependencies for building and installing packages
RUN apt-get update && apt-get --no-install-recommends install -y \
    # Build tools and utilities
    build-essential \
    curl \
    git \
    \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
