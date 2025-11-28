#!/bin/bash
set -e

echo "🧪 Testing LogSim package installation..."
echo ""

# Create test environment
echo "🔧 Creating test environment..."
rm -rf test_env
python -m venv test_env
source test_env/bin/activate

echo "📦 Installing package from wheel..."
pip install dist/*.whl

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Testing imports..."
python -c "
from logsim import SemanticCompressor, QueryEngine
from logsim.models import Token, LogTemplate, CompressedLog
print('✓ All imports successful!')
"

echo ""
echo "✅ Testing CLI..."
python -m logsim --help

echo ""
echo "✅ Testing version..."
python -c "import logsim; print(f'LogSim version: {logsim.__version__}')"

echo ""
echo "🧹 Cleaning up..."
deactivate
rm -rf test_env

echo ""
echo "✅ Package installation test passed!"
