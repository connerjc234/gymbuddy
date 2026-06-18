#!/bin/bash
# Build a Windows .exe for GymBuddy using Docker + PyInstaller cross-compilation
# Prerequisites: Docker installed and running
set -e

VERSION="0.2.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/dist/windows"
BUILD_DIR="${PROJECT_DIR}/build/windows"
MEIPASS_FONTS="${PROJECT_DIR}/build/windows/meipass/fonts"

# Image: PyInstaller with Wine + Python 3.11
DOCKER_IMAGE="cdrx/pyinstaller-windows:latest"

echo "=== Building GymBuddy Windows .exe v${VERSION} ==="

# ── 1. Check prerequisites ──
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is required. Install Docker Desktop or use the GitHub Actions workflow."
    echo "       See .github/workflows/build-windows.yml for CI-based builds."
    exit 1
fi

# ── 2. Clean ──
rm -rf "${OUTPUT_DIR}" "${BUILD_DIR}"
mkdir -p "${OUTPUT_DIR}" "${MEIPASS_FONTS}"

# ── 3. Prepare PyInstaller bundle structure ──
# Copy fonts into a `fonts/` directory that maps to sys._MEIPASS/fonts/ at runtime
cp "${PROJECT_DIR}/assets/fonts/"*.ttf "${MEIPASS_FONTS}/"

# ── 4. Pull Docker image if needed ──
echo "Pulling PyInstaller Windows image..."
docker pull "${DOCKER_IMAGE}"

# ── 5. Build .exe inside container ──
echo "Building GymBuddy.exe..."
docker run --rm -v "${PROJECT_DIR}:/src" "${DOCKER_IMAGE}" \
    bash -c "
        cd /src && \
        pip install PyQt6 PyYAML python-dateutil openai --quiet && \
        pyinstaller --onefile \
            --noconsole \
            --name 'GymBuddy' \
            --icon '/src/assets/gymbuddy.ico' \
            --add-data '/src/build/windows/meipass/fonts:fonts' \
            --hidden-import 'PyQt6.Qt6' \
            --hidden-import 'PyQt6.QtCore' \
            --hidden-import 'PyQt6.QtGui' \
            --hidden-import 'PyQt6.QtWidgets' \
            --hidden-import 'PyQt6.QtSvg' \
            --hidden-import 'PyQt6.QtCharts' \
            --hidden-import 'PyQt6.sip' \
            --collect-data 'workout_tracker' \
            '/src/workout_tracker/main.py'
    "

# ── 6. Copy .exe to dist ──
echo "Copying output..."
cp "${PROJECT_DIR}/dist/GymBuddy.exe" "${OUTPUT_DIR}/"

# ── 7. Clean up build artifacts ──
rm -rf "${PROJECT_DIR}/build/windows" "${PROJECT_DIR}/dist/GymBuddy.exe" "${PROJECT_DIR}/GymBuddy.spec"

echo ""
echo "=== Windows .exe built ==="
ls -lh "${OUTPUT_DIR}/GymBuddy.exe"
echo "File: ${OUTPUT_DIR}/GymBuddy.exe"
