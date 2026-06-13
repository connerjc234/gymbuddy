#!/bin/bash
# Build AppImage using linuxdeploy

set -e

VERSION="0.1.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="${PROJECT_DIR}/appimage/AppDir"
BUILD_DIR="${PROJECT_DIR}/appimage/build"

echo "=== Building GymBuddy AppImage v${VERSION} with linuxdeploy ==="

# Clean previous builds
rm -rf "${APPIMAGE_DIR}" "${BUILD_DIR}"
mkdir -p "${APPIMAGE_DIR}/usr/bin"
mkdir -p "${APPIMAGE_DIR}/usr/share/applications"
mkdir -p "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${BUILD_DIR}"

# Install the package in development mode into AppDir
echo "Installing package..."
cd "${PROJECT_DIR}"
pip install --prefix="${APPIMAGE_DIR}/usr" --no-deps -e .

# Install dependencies
echo "Installing dependencies..."
pip install --prefix="${APPIMAGE_DIR}/usr" \
    PyQt6==6.6.1 \
    PyYAML==6.0.1 \
    python-dateutil==2.9.0.post0 \
    openai==1.30.1

# Copy desktop file and icon
echo "Copying desktop entry and icon..."
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/usr/share/applications/"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps/gymbuddy.svg"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/gymbuddy.svg"
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/gymbuddy.desktop"

# Create AppRun
cat > "${APPIMAGE_DIR}/AppRun" << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export PYTHONPATH="${HERE}/usr/lib/python3.14/site-packages:${HERE}/usr/lib64/python3.14/site-packages:${PYTHONPATH}"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${HERE}/usr/lib64:${HERE}/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
mkdir -p "${HOME}/.config/workout-tracker"
cd "${HERE}"
exec "${HERE}/usr/bin/python3" -m workout_tracker.main "$@"
EOF
chmod +x "${APPIMAGE_DIR}/AppRun"

# Run linuxdeploy
echo "Running linuxdeploy..."
cd "${PROJECT_DIR}/appimage"
export ARCH=x86_64
export QMAKE="${APPIMAGE_DIR}/usr/lib/python3.14/site-packages/PyQt6/Qt6/bin/qmake"
./linuxdeploy-x86_64.AppImage \
    --appdir AppDir \
    --plugin qt \
    --output appimage \
    --desktop-file AppDir/gymbuddy.desktop \
    --icon-file AppDir/gymbuddy.svg

# The AppImage will be in the current directory
APPIMAGE_OUTPUT=$(ls -1 GymBuddy-*.AppImage 2>/dev/null | head -1)
if [ -n "${APPIMAGE_OUTPUT}" ]; then
    mv "${APPIMAGE_OUTPUT}" "GymBuddy-${VERSION}-x86_64.AppImage"
    echo ""
    echo "=== AppImage built ==="
    ls -lh "GymBuddy-${VERSION}-x86_64.AppImage"
else
    echo "ERROR: AppImage not found"
    exit 1
fi