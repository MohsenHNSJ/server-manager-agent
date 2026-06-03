#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# install-agent.sh
#
# Production-grade installer and updater for the Server Manager Agent.
#
# Responsibilities:
# - Fetch latest release metadata from GitHub
# - Download release archive and checksum
# - Verify archive integrity using SHA256
# - Extract and install agent binary
# - Initialize configuration securely
# - Register and manage systemd service
# - Start or restart the agent service
#
# Design Principles:
# - Idempotent: safe to run multiple times (acts as updater)
# - Secure: validates checksum before execution
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

# -----------------------------------------------------------------------------
# Logging Utilities
#
# Provides consistent, timestamped logs for observability.
# -----------------------------------------------------------------------------
log() {
	printf "\n[%s] [INFO] %s\n" "$(date +'%Y-%m-%d %H:%M:%S')" "$1"
}
error() {
	printf "\n[%s] [ERROR] %s\n" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" >&2
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
# - Corresponding SHA256 file
#
# Notes:
# - Uses basic parsing (grep) to avoid external dependencies like jq
# -----------------------------------------------------------------------------
fetch_latest_release() {
	log "Fetching latest release metadata..."

	RELEASE_JSON=$(curl -sSL "https://api.github.com/repos/${GITHUB_REPO}/releases/latest")

	LATEST_TAG=$(echo "${RELEASE_JSON}" | grep -Po '"tag_name": "\K.*?(?=")')
	TAR_URL=$(echo "${RELEASE_JSON}" | grep -Po '"browser_download_url": "\K.*?\.tar\.gz(?=")')
	SHA_URL="${TAR_URL%.tar.gz}.sha256"

	log "Resolved version: ${LATEST_TAG}"
}

# -----------------------------------------------------------------------------
# download_release
#
# Downloads:
# - Release archive (.tar.gz)
# - SHA256 checksum file
#
# Uses temporary working directory under /tmp.
# -----------------------------------------------------------------------------

download_release() {
	TMP_DIR="/tmp/${AGENT_NAME}"
	mkdir -p "${TMP_DIR}"

	log "Downloading release archive..."
	curl -sSL "${TAR_URL}" -o "${TMP_DIR}/${AGENT_NAME}.tar.gz"

	log "Downloading checksum file..."
	curl -sSL "${SHA_URL}" -o "${TMP_DIR}/${AGENT_NAME}.sha256"
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
# verify_checksum
#
# Validates integrity of downloaded archive using SHA256.
#
# Security Critical:
# - Prevents execution of tampered or corrupted binaries
# -----------------------------------------------------------------------------
verify_checksum() {
	log "Verifying SHA256 checksum..."

	cd "${TMP_DIR}"
	sha256sum -c "${AGENT_NAME}.sha256" || error "Checksum verification failed"

	log "Checksum validation passed"
}

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
	tar -xzf "${TMP_DIR}/${AGENT_NAME}.tar.gz" -C "${INSTALL_DIR}"
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
	verify_checksum
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
