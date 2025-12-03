#!/usr/bin/env bash
# ci-cd/scripts/run-tests.sh

set -euo pipefail

# توابع کمکی
run_python_tests() {
    echo "🧪 اجرای تست‌های پایتون..."
    
    # فعال کردن محیط مجازی
    if [ -d "venv" ]; then
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # ویندوز
            source venv/Scripts/activate
        else
            # لینوکس/Mac
            source venv/bin/activate
        fi
    fi
    
    # اجرای تست‌ها
    python -m pytest backend/apps/ \
        --cov=backend/apps \
        --cov-report=xml \
        --cov-report=html \
        --cov-report=term \
        -v
    
    # بررسی coverage
    COVERAGE=$(python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('backend/coverage.xml')
cov = float(tree.getroot().attrib['line-rate']) * 100
print(f'{cov:.1f}%')
exit(0) if cov >= 80 else exit(1)
    ")
    
    echo "📊 Coverage: $COVERAGE"
}

run_api_tests() {
    echo "🔗 اجرای تست‌های API..."
    
    # شروع سرور تست در پس‌زمینه
    echo "🚀 شروع سرور تست..."
    
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # ویندوز
        start /B python backend/main.py --test
        SERVER_PID=$!
    else
        # لینوکس
        python backend/main.py --test &
        SERVER_PID=$!
    fi
    
    # منتظر بمان سرور بالا بیاید
    sleep 10
    
    # اجرای تست‌های API
    python ci-cd/tests/check-essential-endpoints.py
    
    # متوقف کردن سرور
    kill $SERVER_PID 2>/dev/null || true
}

# اجرای اصلی
main() {
    echo "🎯 شروع تست‌ها..."
    
    run_python_tests
    run_api_tests
    
    echo "✅ همه تست‌ها با موفقیت اجرا شدند"
}

main "$@"