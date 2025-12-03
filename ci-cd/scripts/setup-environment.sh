#!/usr/bin/env bash
# ci-cd/scripts/setup-environment.sh

set -euo pipefail

# راهنمای استفاده
show_help() {
    cat << EOF
استفاده: setup-environment.sh [محیط] [گزینه‌ها]

محیط‌ها:
  dev          محیط توسعه
  staging      محیط staging
  production   محیط production

گزینه‌ها:
  --python-version   نسخه پایتون (پیش‌فرض: 3.11)
  --skip-venv        رد کردن ساخت محیط مجازی
  --help             نمایش این راهنما

مثال:
  ./setup-environment.sh dev
  ./setup-environment.sh staging --python-version 3.10
EOF
    exit 0
}

# متغیرهای پیش‌فرض
PYTHON_VERSION="3.11"
ENVIRONMENT="dev"
SKIP_VENV=false

# پردازش آرگومان‌ها
while [[ $# -gt 0 ]]; do
    case $1 in
        dev|staging|production)
            ENVIRONMENT="$1"
            shift
            ;;
        --python-version)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "⚠ آرگومان ناشناخته: $1"
            show_help
            ;;
    esac
done

echo "🔧 راه‌اندازی محیط: $ENVIRONMENT"
echo "🐍 نسخه پایتون: $PYTHON_VERSION"

# بررسی وجود پایتون
check_python() {
    echo "🔍 بررسی پایتون..."
    
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py"
    else
        echo "❌ پایتون پیدا نشد!"
        echo "📥 لطفاً پایتون را نصب کنید: https://www.python.org/downloads/"
        exit 1
    fi
    
    # بررسی نسخه
    $PYTHON_CMD --version
    echo "✅ پایتون پیدا شد: $PYTHON_CMD"
}

# ساخت محیط مجازی
create_venv() {
    if [ "$SKIP_VENV" = true ]; then
        echo "⏩ ساخت محیط مجازی رد شد"
        return
    fi
    
    echo "🏗️ ساخت محیط مجازی..."
    
    if [ -d "venv" ]; then
        echo "♻️ محیط مجازی از قبل وجود دارد"
    else
        $PYTHON_CMD -m venv venv
        echo "✅ محیط مجازی ساخته شد"
    fi
    
    # فعال کردن محیط مجازی
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # ویندوز
        VENV_ACTIVATE="venv/Scripts/activate"
    else
        # لینوکس/Mac
        VENV_ACTIVATE="venv/bin/activate"
    fi
    
    if [ -f "$VENV_ACTIVATE" ]; then
        source "$VENV_ACTIVATE"
        echo "✅ محیط مجازی فعال شد"
    else
        echo "⚠ فایل activate پیدا نشد: $VENV_ACTIVATE"
    fi
}

# نصب dependencies
install_dependencies() {
    echo "📦 نصب dependencies..."
    
    # ارتقای pip
    python -m pip install --upgrade pip
    
    # نصب dependencies اصلی
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
        echo "✅ dependencies اصلی نصب شدند"
    fi
    
    # نصب dependencies محیط
    ENV_REQ_FILE="ci-cd/environments/$ENVIRONMENT/requirements.txt"
    if [ -f "$ENV_REQ_FILE" ]; then
        pip install -r "$ENV_REQ_FILE"
        echo "✅ dependencies محیط $ENVIRONMENT نصب شدند"
    fi
    
    # نصب tools تست
    pip install pytest pytest-cov pytest-asyncio
    pip install bandit safety flake8 black isort
    echo "✅ tools تست نصب شدند"
}

# اعتبارسنجی محیط
validate_environment() {
    echo "🔎 اعتبارسنجی محیط..."
    
    # بررسی فایل‌های ضروری
    REQUIRED_FILES=(
        "backend/main.py"
        "backend/requirements.txt"
        "ci-cd/environments/$ENVIRONMENT/config.yaml"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file پیدا نشد!"
            exit 1
        fi
    done
    
    # تست import پایتون
    echo "🧪 تست import ماژول‌ها..."
    python -c "
import sys
try:
    from backend.main import app
    print('✅ FastAPI app import شد')
except Exception as e:
    print(f'❌ خطا در import: {e}')
    sys.exit(1)
    "
    
    echo "✅ محیط $ENVIRONMENT معتبر است"
}

# تابع اصلی
main() {
    echo "🎬 شروع راه‌اندازی محیط..."
    
    check_python
    create_venv
    install_dependencies
    validate_environment
    
    echo ""
    echo "✨✨✨ راه‌اندازی کامل شد ✨✨✨"
    echo "✅ محیط: $ENVIRONMENT"
    echo "✅ پایتون: $(python --version 2>/dev/null || echo 'unknown')"
    echo "✅ مسیر: $(pwd)"
    echo ""
    echo "📝 دستورات مفید:"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "   source venv/Scripts/activate  # فعال کردن محیط (ویندوز)"
    else
        echo "   source venv/bin/activate  # فعال کردن محیط (لینوکس/Mac)"
    fi
    echo "   pytest backend/              # اجرای تست‌ها"
    echo "   python backend/main.py       # شروع سرور"
}

# اجرای تابع اصلی
main