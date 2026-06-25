# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:66af9ee0a89e76f83b5c54a0cfdc19966ec8e443e294707f8f9b45f465b42cf1
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
