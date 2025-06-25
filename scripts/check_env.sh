#!/bin/bash
echo "🐍 Python Check:"
echo "Which python3: $(which python3)"
echo "Virtual env: $VIRTUAL_ENV"
echo "Working dir: $(pwd)"

echo ""
echo "📦 Testing psutil:"
python3 -c "import psutil; print('✅ psutil works')" 2>/dev/null || echo "❌ psutil missing"

echo ""
echo "💡 Quick fixes:"
echo "1. Activate virtual env: source your_venv/bin/activate"
echo "2. Install psutil: pip install psutil"
echo "3. Use minimal diagnostic: python3 scripts/minimal_diagnose.py"
