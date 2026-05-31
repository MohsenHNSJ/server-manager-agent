# https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:882b17d068262c7af4300180ead0ee14423d2c03393778c92435b0ca642dea07
# Set up required dependencies for building and installing packages
RUN apt-get update && apt-get install -y \
    # Build tools and utilities
    build-essential \
    curl \
    git \
    \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*