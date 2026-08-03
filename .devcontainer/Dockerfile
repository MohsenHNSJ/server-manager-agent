# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:f04a1e9c29e371436d6086908eed22ac0ba087bae0f8edb826838283cf3d1726
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
