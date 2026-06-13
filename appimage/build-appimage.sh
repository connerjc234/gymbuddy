#!/bin/bash
# Build AppImage for GymBuddy

set -e

VERSION="0.1.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APPIMAGE_DIR="${PROJECT_DIR}/appimage/AppDir"
BUILD_DIR="${PROJECT_DIR}/appimage/build"

echo "=== Building GymBuddy AppImage v${VERSION} ==="

# Clean previous builds
rm -rf "${APPIMAGE_DIR}" "${BUILD_DIR}"
mkdir -p "${APPIMAGE_DIR}/usr/bin"
mkdir -p "${APPIMAGE_DIR}/usr/lib/python3/site-packages"
mkdir -p "${APPIMAGE_DIR}/usr/share/applications"
mkdir -p "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${APPIMAGE_DIR}/usr/etc/fonts"
mkdir -p "${BUILD_DIR}"

# Copy source code
echo "Copying source..."
cp -r "${PROJECT_DIR}/workout_tracker" "${APPIMAGE_DIR}/usr/lib/python3/site-packages/"

# Install dependencies with pip into AppDir
echo "Installing dependencies..."
pip install --target="${APPIMAGE_DIR}/usr/lib/python3/site-packages" \
    --no-compile \
    --no-deps \
    PyQt6==6.6.1 \
    PyYAML==6.0.1 \
    python-dateutil==2.9.0.post0 \
    openai==1.30.1 \
    2>/dev/null || echo "Some deps may need manual handling"

# Copy PyQt6 from system (it has binary components)
echo "Copying PyQt6 binaries..."
PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
if [ -d "${PYTHON_SITE}/PyQt6" ]; then
    cp -r "${PYTHON_SITE}/PyQt6" "${APPIMAGE_DIR}/usr/lib/python3/site-packages/"
fi
if [ -d "${PYTHON_SITE}/PyQt6.Qt6" ]; then
    cp -r "${PYTHON_SITE}/PyQt6.Qt6" "${APPIMAGE_DIR}/usr/lib/python3/site-packages/"
fi

# Copy Qt6 libraries
echo "Copying Qt6 libraries..."
mkdir -p "${APPIMAGE_DIR}/usr/lib/x86_64-linux-gnu"
QT_LIB_DIRS="/usr/lib64 /usr/lib/x86_64-linux-gnu /usr/lib"
for qt_dir in ${QT_LIB_DIRS}; do
    if [ -d "${qt_dir}" ]; then
        for lib in Qt6Core Qt6Gui Qt6Widgets Qt6Network Qt6DBus Qt6OpenGL Qt6PrintSupport Qt6Svg Qt6Qml Qt6Quick Qt6QmlModels Qt6QmlWorkerScript; do
            find "${qt_dir}" -maxdepth 1 -name "lib${lib}.so*" -exec cp -L {} "${APPIMAGE_DIR}/usr/lib/x86_64-linux-gnu/" \; 2>/dev/null || true
        done
    fi
done

# Also copy libstdc++, libgcc, etc. that Qt depends on
for lib in libstdc++.so.6 libgcc_s.so.1 libm.so.6 libc.so.6 libdl.so.2 libpthread.so.0 librt.so.1; do
    find /lib64 /lib /usr/lib64 /usr/lib -maxdepth 1 -name "${lib}*" -exec cp -L {} "${APPIMAGE_DIR}/usr/lib/x86_64-linux-gnu/" \; 2>/dev/null || true
done

# Copy desktop file and icon
echo "Copying desktop entry and icon..."
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/gymbuddy.desktop"
cp "${PROJECT_DIR}/assets/gymbuddy.desktop" "${APPIMAGE_DIR}/usr/share/applications/"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/usr/share/icons/hicolor/scalable/apps/gymbuddy.svg"
cp "${PROJECT_DIR}/assets/gymbuddy.svg" "${APPIMAGE_DIR}/gymbuddy.svg"

# Copy AppRun
cp "${PROJECT_DIR}/appimage/AppRun" "${APPIMAGE_DIR}/AppRun"
chmod +x "${APPIMAGE_DIR}/AppRun"

# Create minimal fontconfig
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
echo "Building AppImage..."
cd "${PROJECT_DIR}/appimage"
ARCH=x86_64 "${APPIMAGETOOL}" AppDir "GymBuddy-${VERSION}-x86_64.AppImage"

echo ""
echo "=== AppImage built ==="
ls -lh "GymBuddy-${VERSION}-x86_64.AppImage"