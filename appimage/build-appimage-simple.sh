#!/bin/bash
# Build AppImage using appimagetool directly with PyQt6 bundled libraries

set -e

VERSION="0.1.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="${PROJECT_DIR}/appimage/AppDir"
BUILD_DIR="${PROJECT_DIR}/appimage/build"

echo "=== Building GymBuddy AppImage v${VERSION} (simple method) ==="

# Clean previous builds
rm -rf "${APPIMAGE_DIR}" "${BUILD_DIR}"
mkdir -p "${APPIMAGE_DIR}/usr/bin"
mkdir -p "${APPIMAGE_DIR}/usr/lib"
mkdir -p "${APPIMAGE_DIR}/usr/share/applications"
mkdir -p "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${BUILD_DIR}"

# Install the package and dependencies into AppDir
echo "Installing package and dependencies..."
cd "${PROJECT_DIR}"

# Copy source code directly (avoid editable install issues)
mkdir -p "${APPIMAGE_DIR}/usr/lib/python3.14/site-packages"
cp -r "${PROJECT_DIR}/workout_tracker" "${APPIMAGE_DIR}/usr/lib/python3.14/site-packages/"

pip install --target="${APPIMAGE_DIR}/usr/lib/python3.14/site-packages" \
    --ignore-installed \
    PyQt6==6.11.0 \
    PyYAML==6.0.1 \
    python-dateutil==2.9.0.post0 \
    openai==1.30.1

# Copy Qt6 libraries from PyQt6 package to AppDir lib
echo "Copying Qt6 libraries..."
PYQT6_QT_LIB="${APPIMAGE_DIR}/usr/lib/python3.14/site-packages/PyQt6/Qt6/lib"
if [ -d "${PYQT6_QT_LIB}" ]; then
    mkdir -p "${APPIMAGE_DIR}/usr/lib"
    cp -r "${PYQT6_QT_LIB}"/* "${APPIMAGE_DIR}/usr/lib/"
    echo "Copied Qt6 libraries from PyQt6 package"
else
    echo "WARNING: PyQt6 Qt6 lib directory not found at ${PYQT6_QT_LIB}"
fi

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

# Python path
export PYTHONPATH="${HERE}/usr/lib/python3.14/site-packages:${PYTHONPATH}"
export PATH="${HERE}/usr/bin:${PATH}"

# Library path - prioritize bundled Qt libraries
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"

# Qt plugin path
export QT_PLUGIN_PATH="${HERE}/usr/lib/python3.14/site-packages/PyQt6/Qt6/plugins:${QT_PLUGIN_PATH}"
export QML2_IMPORT_PATH="${HERE}/usr/lib/python3.14/site-packages/PyQt6/Qt6/qml:${QML2_IMPORT_PATH}"

# Font config
export FONTCONFIG_FILE="${HERE}/usr/etc/fonts/fonts.conf"
export FONTCONFIG_PATH="${HERE}/usr/etc/fonts"

# XDG paths
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
export XDG_CONFIG_DIRS="${HERE}/usr/etc/xdg:${XDG_CONFIG_DIRS}"

# Create config directory if needed
mkdir -p "${HOME}/.config/workout-tracker"

# Run the application using system Python with bundled libraries
cd "${HERE}"
exec python3 -m workout_tracker.main "$@"
EOF
chmod +x "${APPIMAGE_DIR}/AppRun"

# Create minimal fontconfig
mkdir -p "${APPIMAGE_DIR}/usr/etc/fonts"
cat > "${APPIMAGE_DIR}/usr/etc/fonts/fonts.conf" << 'EOF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>/usr/share/fonts</dir>
  <dir>/usr/local/share/fonts</dir>
  <dir prefix="xdg">fonts</dir>
  <cachedir>/var/cache/fontconfig</cachedir>
  <cachedir prefix="xdg">fontconfig</cachedir>
</fontconfig>
EOF

# Download appimagetool if not present
APPIMAGETOOL="${BUILD_DIR}/appimagetool-x86_64.AppImage"
if [ ! -f "${APPIMAGETOOL}" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O "${APPIMAGETOOL}"
    chmod +x "${APPIMAGETOOL}"
fi

# Build AppImage
echo "Building AppImage with appimagetool..."
cd "${PROJECT_DIR}/appimage"
ARCH=x86_64 "${APPIMAGETOOL}" AppDir "GymBuddy-${VERSION}-x86_64.AppImage"

echo ""
echo "=== AppImage built ==="
ls -lh "GymBuddy-${VERSION}-x86_64.AppImage"