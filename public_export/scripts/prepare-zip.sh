#!/usr/bin/env bash
# Prepare distribution zip package for OsintNeoAi
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ZIP_TARGET="${DIST_DIR}/OsintNeoAi_${TIMESTAMP}.zip"
ZIP_LATEST="${DIST_DIR}/OsintNeoAi_latest.zip"

echo "=========================================="
echo " Packaging OsintNeoAi Deployment Archive  "
echo "=========================================="
echo "Project Root : ${PROJECT_ROOT}"
echo "Output Target: ${ZIP_TARGET}"

mkdir -p "${DIST_DIR}"

if command -v zip &>/dev/null; then
    cd "${PROJECT_ROOT}"
    zip -r "${ZIP_TARGET}" manifest.json package.json README.md scripts/ \
      -x "scripts/__pycache__/*" -x "*.pyc" -x "*.log"
    cp -f "${ZIP_TARGET}" "${ZIP_LATEST}"
elif command -v powershell.exe &>/dev/null; then
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${SCRIPT_DIR}/prepare-zip.ps1"
    exit 0
else
    echo "[-] Neither zip nor powershell.exe was found."
    exit 1
fi

echo "[+] Archive created successfully:"
echo "    - ${ZIP_TARGET}"
echo "    - ${ZIP_LATEST}"
echo "=========================================="
