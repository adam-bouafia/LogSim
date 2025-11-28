#!/bin/bash
set -e

echo "⚠️  Publishing LogSim to PRODUCTION PyPI..."
echo ""
echo "🚨 This will publish to REAL PyPI (pypi.org) - package will be public!"
echo ""
read -p "Are you absolutely sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

# Build package
echo ""
echo "🔨 Building package..."
bash scripts/build_package.sh

# Final confirmation
echo ""
echo "📦 Ready to publish:"
ls -lh dist/
echo ""
read -p "Proceed with upload? (yes/no): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi

# Upload to PyPI
echo ""
echo "📤 Uploading to PyPI..."
twine upload dist/* --config-file .pypirc

echo ""
echo "✅ Published to PyPI!"
echo "🔗 View at: https://pypi.org/project/logsim/"
echo ""
echo "📦 Users can now install with:"
echo "   pip install logsim"
echo ""
echo "🎉 Congratulations on publishing your package!"
