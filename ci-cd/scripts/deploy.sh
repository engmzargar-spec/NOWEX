#!/usr/bin/env bash
# ci-cd/scripts/deploy.sh - سازگار با ویندوز/لینوکس

set -euo pipefail

# تشخیص سیستم عامل
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

OS=$(detect_os)
echo "سیستم عامل: $OS"

# پارامترها
ENVIRONMENT=${1:-"dev"}
DEPLOY_USER=${2:-"deploy"}
SERVER_HOST=${3:-"localhost"}

deploy_linux() {
    echo "🚀 استقرار روی لینوکس..."
    
    # ساخت package
    tar -czf deploy-package.tar.gz \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        .
    
    # انتقال به سرور
    scp -o StrictHostKeyChecking=no \
        deploy-package.tar.gz \
        ${DEPLOY_USER}@${SERVER_HOST}:/tmp/
    
    # اجرای استقرار روی سرور
    ssh -o StrictHostKeyChecking=no \
        ${DEPLOY_USER}@${SERVER_HOST} \
        "cd /tmp && \
         tar -xzf deploy-package.tar.gz && \
         cd nowex-platform && \
         ./ci-cd/scripts/setup-environment.sh ${ENVIRONMENT}"
}

deploy_windows() {
    echo "🪟 استقرار از ویندوز..."
    
    # در ویندوز، احتمالاً از PowerShell برای deploy استفاده می‌کنیم
    # یا مستقیماً به سرور لینوکس deploy می‌کنیم
    
    # ساخت package با ۷-zip یا tar ویندوز
    if command -v tar &> /dev/null; then
        tar -czf deploy-package.tar.gz \
            --exclude='.git' \
            --exclude='node_modules' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            .
    else
        # استفاده از ۷-zip
        echo "⚠ tar موجود نیست، از ۷-zip استفاده کنید"
        exit 1
    fi
    
    echo "✅ Package ساخته شد"
    echo "📤 برای آپلود دستی به سرور آماده است"
}

# اجرای بر اساس سیستم عامل
case "$OS" in
    "linux"|"macos")
        deploy_linux
        ;;
    "windows")
        deploy_windows
        ;;
    *)
        echo "❌ سیستم عامل پشتیبانی نمی‌شود"
        exit 1
        ;;
esac

echo "🎉 استقرار کامل شد"