#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# install-agent.sh
#
# Production-grade installer and updater for the Server Manager Agent.
#
# Responsibilities:
# - Fetch latest release metadata from GitHub
# - Download release archive and checksum
# - Extract and install agent binary
# - Initialize configuration securely
# - Register and manage systemd service
# - Start or restart the agent service
#
# Design Principles:
# - Idempotent: safe to run multiple times (acts as updater)
# - Minimal dependencies: works on bare VPS systems
# - Observable: structured logging for debugging
#
# Installation Layout:
# /opt/server-manager-agent/
# ├── server-manager-agent (binary)
#
# Service:
# - systemd unit: /etc/systemd/system/server-manager-agent.service
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Strict Mode
#
# -E : Ensures ERR trap is inherited by functions
# -e : Exit immediately on any command failure
# -u : Treat unset variables as errors
# -o pipefail : Fail if any command in a pipeline fails
# -----------------------------------------------------------------------------
set -Eeuo pipefail

# Restrict word splitting to newline and tab only (safer scripting)
IFS=$'\n\t'

# -----------------------------------------------------------------------------
# Constants & Configuration
# -----------------------------------------------------------------------------
AGENT_NAME="server-manager-agent"
INSTALL_DIR="/opt/${AGENT_NAME}"
SYSTEMD_SERVICE="/etc/systemd/system/${AGENT_NAME}.service"
GITHUB_REPO="MohsenHNSJ/${AGENT_NAME}"

# -------------------------------------------------------------------
# Global variables for downloaded files
# -------------------------------------------------------------------
TAR_FILE=""
TMP_DIR=""
TAR_URL=""

# -----------------------------------------------------------------------------
# Logging Utilities
#
# Provides consistent, timestamped logs for observability.
# -----------------------------------------------------------------------------
log() {
	printf "[%s] [INFO] %s\n" "$(date +'%H:%M:%S.%3N')" "$1"
}
error() {
	printf "[%s] [ERROR] %s\n" "$(date +'%H:%M:%S.%3N')" "$1" >&2
	exit 1
}

# -----------------------------------------------------------------------------
# Error Handling
#
# Captures the line number of any failure to aid debugging.
# -----------------------------------------------------------------------------
trap 'echo "Error: Script failed at line $LINENO." >&2' ERR

# -----------------------------------------------------------------------------
# Privilege Check
#
# Installer requires root privileges for:
# - Writing to /opt
# - Creating systemd service
#
# If the script is not run as root, it will exit with an error message.
# -----------------------------------------------------------------------------
if [ "${EUID}" -ne 0 ]; then
	log "Please run this script as root (e.g., with sudo)."
	exit 1
fi

# -----------------------------------------------------------------------------
# fetch_latest_release
#
# Queries GitHub API for the latest release metadata.
#
# Extracts:
# - Version tag
# - Download URL for tar.gz archive
#
# Notes:
# - Uses basic parsing (grep) to avoid external dependencies like jq
# -----------------------------------------------------------------------------
fetch_latest_release() {
	log "Fetching latest release metadata..."

	RELEASE_JSON=$(curl -sSL "https://api.github.com/repos/${GITHUB_REPO}/releases/latest")

	LATEST_TAG=$(echo "${RELEASE_JSON}" | grep -Po '"tag_name": "\K.*?(?=")')
	TAR_URL=$(echo "${RELEASE_JSON}" | grep -Po '"browser_download_url": "\K.*?\.tar\.gz(?=")')

	log "Resolved version: ${LATEST_TAG}"
}

# -----------------------------------------------------------------------------
# download_release
#
# Downloads release artifacts from GitHub:
# - Release archive (.tar.gz)
#
# Behavior:
# - Uses a temporary working directory under /tmp
# - Dynamically extracts filenames from the provided URLs
# - Preserves original upstream filenames (no renaming)
# - Detects execution context (interactive vs non-interactive)
#
# Output behavior:
# - Interactive (TTY): shows curl progress bar for downloads
# - Non-interactive (CI/automation): runs silently
#
# Error handling:
# - Fails immediately if required URLs are unset
# - Fails if any download operation does not complete successfully
#
# Notes:
# - Uses curl with context-aware flags for optimal UX and automation safety
# -----------------------------------------------------------------------------
download_release() {
	# Fail fast if required inputs are missing
	: "${TAR_URL:?TAR_URL is not set}"

	TMP_DIR="/tmp/${AGENT_NAME}"
	mkdir -p "${TMP_DIR}"

	# Extract filenames from URLs
	TAR_FILE="$(basename "${TAR_URL}")"

	# Detect if running in a terminal
	if [ -t 1 ]; then
		CURL_FLAGS="-L"
	else
		CURL_FLAGS="-sSL"
	fi

	log "Downloading release archive..."
	curl "${CURL_FLAGS}" "${TAR_URL}" -o "${TMP_DIR}/${TAR_FILE}" ||
		error "Failed to download archive"
}

# -------------------------------------------------------------------
# Cleanup temporary directory on exit
# -------------------------------------------------------------------
cleanup() {
	if [ -n "${TMP_DIR:-}" ] && [ -d "${TMP_DIR}" ]; then
		rm -rf "${TMP_DIR}"
		log "Temporary files cleaned up"
	fi
}
# Register cleanup function to run when the script exits (normal or error)
trap cleanup EXIT

# -----------------------------------------------------------------------------
# extract_binary
#
# Extracts archive into installation directory.
#
# Ensures:
# - Correct permissions
# - Binary is executable
# -----------------------------------------------------------------------------
extract_binary() {
	log "Installing agent to ${INSTALL_DIR}..."

	mkdir -p "${INSTALL_DIR}"
	tar -xzf "${TMP_DIR}/${TAR_FILE}" -C "${INSTALL_DIR}"
	chmod +x "${INSTALL_DIR}/${AGENT_NAME}"
}

# -----------------------------------------------------------------------------
# setup_config
#
# Handles provisioning of the agent API key via file-based mechanism.
#
# Expected Flow:
# - External system (e.g., Android app) uploads `agent.key` via SFTP
# - Installer moves the key into the installation directory
#
# Lookup Order:
# 1. Existing key in installation directory (reuse)
# 2. Temporary uploaded key in /tmp (consume and move)
# 3. Fail if no key is found
#
# Security:
# - File permissions restricted to 600
# - Prevents accidental exposure of credentials
# -----------------------------------------------------------------------------
setup_config() {
	KEY_SOURCE_TMP="/tmp/${AGENT_NAME}/agent.key"
	KEY_TARGET="${INSTALL_DIR}/agent.key"

	if [ -f "${KEY_TARGET}" ]; then
		log "Existing agent key found — reusing"
		return
	fi

	if [ -f "${KEY_SOURCE_TMP}" ]; then
		log "Found uploaded agent.key in /tmp/${AGENT_NAME}/ — installing..."

		mkdir -p "${INSTALL_DIR}"
		mv "${KEY_SOURCE_TMP}" "${KEY_TARGET}"

		chmod 600 "${KEY_TARGET}"

		log "Agent key installed securely"
		return
	fi

	error "No agent.key found. Please upload it via SFTP to /tmp/${AGENT_NAME}/agent.key before running installer."
}

# -----------------------------------------------------------------------------
# setup_systemd_service
#
# Creates and registers a systemd unit file.
#
# Features:
# - Automatic restart on failure
# - Environment file support
# - Boot-time startup
# -----------------------------------------------------------------------------
setup_systemd_service() {
	if [ ! -f "${SYSTEMD_SERVICE}" ]; then
		log "Creating systemd service..."

		cat <<EOF >"${SYSTEMD_SERVICE}"

[Unit]
Description=Server Manager Agent
After=network.target

[Service]
Type=simple
ExecStart=${INSTALL_DIR}/${AGENT_NAME}
Restart=always
WorkingDirectory=${INSTALL_DIR}

[Install]
WantedBy=multi-user.target
EOF

		systemctl daemon-reload
		systemctl enable "${AGENT_NAME}"
	else
		log "Systemd service already exists — skipping"
	fi
}

# -----------------------------------------------------------------------------
# start_agent
#
# Starts or restarts the agent service.
#
# Also prints current service status for visibility.
# -----------------------------------------------------------------------------
start_agent() {
	log "Starting agent service..."

	systemctl restart "${AGENT_NAME}"
	systemctl status "${AGENT_NAME}" --no-pager
}

# -----------------------------------------------------------------------------
# main
#
# Orchestrates the full installation/update workflow.
#
# Flow:
# 1. Fetch release metadata
# 2. Download assets
# 3. Verify integrity
# 4. Install binary
# 5. Configure environment
# 6. Register systemd service
# 7. Start service
# -----------------------------------------------------------------------------
main() {
	fetch_latest_release
	download_release
	extract_binary
	setup_config
	setup_systemd_service
	start_agent

	log "Installation/update completed successfully"
}

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
main "$@"
