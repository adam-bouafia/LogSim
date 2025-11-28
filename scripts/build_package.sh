#!/bin/bash
set -e

echo "🔨 Building LogSim Python package..."
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info logsim.egg-info

# Install build tools
echo "📦 Installing build tools..."
pip install --upgrade build twine

# Build package
echo "🏗️  Building package..."
python -m build

# Check package
echo "✅ Checking package..."
twine check dist/*

echo ""
echo "✅ Package built successfully!"
echo "📦 Packages created:"
ls -lh dist/

echo ""
echo "📋 Package contents:"
tar -tzf dist/logsim-0.1.0.tar.gz | head -20

echo ""
echo "🎉 Build complete!"
