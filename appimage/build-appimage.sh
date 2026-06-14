#!/bin/bash
# Build a distribution-ready AppImage for GymBuddy
# Bundles portable Python (python-build-standalone) + all deps
set -e

VERSION="0.2.0"
PYTHON_VERSION="3.11.15"
PBS_RELEASE="20260610"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="${PROJECT_DIR}/appimage/AppDir"
BUILD_DIR="${PROJECT_DIR}/appimage/build"

PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PBS_RELEASE}/cpython-${PYTHON_VERSION}+${PBS_RELEASE}-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"

echo "=== Building GymBuddy AppImage v${VERSION} ==="

# Clean
rm -rf "${APPIMAGE_DIR}" "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
mkdir -p "${APPIMAGE_DIR}/usr/share/applications"
mkdir -p "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${APPIMAGE_DIR}/usr/share/fonts/gymbuddy"

# ── 1. Download & extract portable Python ──
PBS_CACHE="${BUILD_DIR}/python-build.tar.gz"
if [ ! -f "${PBS_CACHE}" ]; then
    echo "Downloading portable Python ${PYTHON_VERSION}..."
    curl -L "${PBS_URL}" -o "${PBS_CACHE}"
fi
echo "Extracting Python ${PYTHON_VERSION}..."
tar xzf "${PBS_CACHE}" -C "${BUILD_DIR}"
# tarball root is "python/", move contents into AppDir usr/
cp -r "${BUILD_DIR}/python/"* "${APPIMAGE_DIR}/usr/"
rm -rf "${BUILD_DIR}/python"

BUNDLED_PYTHON="${APPIMAGE_DIR}/usr/bin/python3"
echo "  Bundled: $(${BUNDLED_PYTHON} --version 2>&1)"

# ── 2. Install Python dependencies via bundled pip ──
echo "Installing dependencies into bundled Python..."
"${BUNDLED_PYTHON}" -m pip install --no-compile --no-cache-dir \
    PyQt6==6.11.0 \
    PyYAML==6.0.1 \
    python-dateutil==2.9.0.post0 \
    openai==1.30.1

# ── 3. Install GymBuddy source ──
echo "Installing GymBuddy..."
SITE_PACKAGES=$(find "${APPIMAGE_DIR}/usr/lib" -name "site-packages" -type d | head -1)
cp -r "${PROJECT_DIR}/workout_tracker" "${SITE_PACKAGES}/"

# ── 4. Copy Qt6 libraries to usr/lib for LD_LIBRARY_PATH ──
echo "Copying Qt6 libraries..."
QT_LIB_DIR="${SITE_PACKAGES}/PyQt6/Qt6/lib"
if [ -d "${QT_LIB_DIR}" ]; then
    mkdir -p "${APPIMAGE_DIR}/usr/lib"
    cp -r "${QT_LIB_DIR}/"* "${APPIMAGE_DIR}/usr/lib/"
fi

# ── 5. Copy desktop entry and icon ──
echo "Copying desktop entry and icon..."
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/usr/share/applications/"
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/gymbuddy.desktop"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps/gymbuddy.svg"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/gymbuddy.svg"

# ── 6. Copy fonts ──
echo "Copying fonts..."
cp "${PROJECT_DIR}/assets/fonts/"*.ttf "${APPIMAGE_DIR}/usr/share/fonts/gymbuddy/"

# ── 7. Create AppRun ──
cat > "${APPIMAGE_DIR}/AppRun" << 'APPRUN'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"

# Use bundled Python
PYTHON="${HERE}/usr/bin/python3"

# Point to bundled site-packages
SITE_PACKAGES=$(find "${HERE}/usr/lib" -name "site-packages" -type d | head -1)
export PYTHONPATH="${SITE_PACKAGES}:${PYTHONPATH}"

# Qt library path
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"

# Qt plugin path
QT_PLUGINS=$(find "${HERE}/usr/lib" -path "*/PyQt6/Qt6/plugins" -type d 2>/dev/null | head -1)
if [ -n "${QT_PLUGINS}" ]; then
    export QT_PLUGIN_PATH="${QT_PLUGINS}:${QT_PLUGIN_PATH}"
fi

# XDG paths
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"

# Create config directory if needed
mkdir -p "${HOME}/.config/workout-tracker"

# Run
cd "${HERE}"
exec "${PYTHON}" -m workout_tracker.main "$@"
APPRUN
chmod +x "${APPIMAGE_DIR}/AppRun"

# ── 8. Strip and clean ──
echo "Stripping binaries and cleaning..."
find "${APPIMAGE_DIR}/usr/lib" -name "*.so" -exec strip --strip-unneeded {} \; 2>/dev/null || true
find "${APPIMAGE_DIR}/usr/bin" -not -name "python3" -exec strip --strip-all {} \; 2>/dev/null || true
strip --strip-all "${APPIMAGE_DIR}/usr/bin/python3" 2>/dev/null || true
# Remove unnecessary Python stdlib components
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/test"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/idlelib"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/turtledemo"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/lib2to3"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/ensurepip"
rm -rf "${APPIMAGE_DIR}/usr/include"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/site-packages/pip"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/site-packages/setuptools"
rm -rf "${APPIMAGE_DIR}/usr/lib/python3.11/__pycache__"
find "${APPIMAGE_DIR}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "${APPIMAGE_DIR}" -name "*.pyc" -delete 2>/dev/null || true

# Remove .dist-info and .egg-info that aren't ours
find "${APPIMAGE_DIR}/usr/lib/python3.11/site-packages" \
    -maxdepth 1 \( -name "*.dist-info" -o -name "*.egg-info" \) \
    ! -name "workout_tracker*" \
    -exec rm -rf {} + 2>/dev/null || true

# ── 9. Download appimagetool ──
APPIMAGETOOL="${BUILD_DIR}/appimagetool-x86_64.AppImage"
if [ ! -f "${APPIMAGETOOL}" ]; then
    echo "Downloading appimagetool..."
    curl -L "${APPIMAGETOOL_URL}" -o "${APPIMAGETOOL}"
    chmod +x "${APPIMAGETOOL}"
fi

# ── 10. Build AppImage ──
echo "Building AppImage..."
cd "${PROJECT_DIR}/appimage"
ARCH=x86_64 "${APPIMAGETOOL}" --no-appstream AppDir "GymBuddy-${VERSION}-x86_64.AppImage"

echo ""
echo "=== AppImage built ==="
ls -lh "GymBuddy-${VERSION}-x86_64.AppImage"
echo "File: ${PROJECT_DIR}/appimage/GymBuddy-${VERSION}-x86_64.AppImage"
