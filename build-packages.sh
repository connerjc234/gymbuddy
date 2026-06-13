#!/bin/bash
# Build script for creating .deb and .rpm packages

set -e

VERSION="0.1.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building GymBuddy packages v${VERSION} ==="

# Clean previous builds
rm -rf build dist *.egg-info debian/gymbuddy

# Build wheel
echo "Building wheel..."
python3 -m build --wheel

# --- Build .deb ---
echo "Building .deb package..."
cd "$PROJECT_DIR"
dpkg-buildpackage -us -uc -b

# --- Build .rpm ---
echo "Building .rpm package..."
cd "$PROJECT_DIR"

# Create source tarball for rpm
mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
tar --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.egg-info' --exclude='build' --exclude='dist' --exclude='.mypy_cache' --exclude='.ruff_cache' --exclude='rpmbuild' -czf rpmbuild/SOURCES/gymbuddy-${VERSION}.tar.gz .

# Build RPM
rpmbuild --define "_topdir ${PROJECT_DIR}/rpmbuild" -ba gymbuddy.spec

echo ""
echo "=== Build complete ==="
echo ".deb packages: $(ls -1 *.deb 2>/dev/null || echo 'none')"
echo ".rpm packages: $(ls -1 rpmbuild/RPMS/noarch/*.rpm 2>/dev/null || echo 'none')"