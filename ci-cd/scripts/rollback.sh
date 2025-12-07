#!/bin/bash

# ci-cd/scripts/rollback.sh
# اسکریپت بازگشت به نسخه قبلی

set -e  # در صورت خطا، اجرا متوقف شود

echo "↩️ Starting rollback procedure..."

# پارامترها
ENVIRONMENT=${1:-"staging"}
ROLLBACK_VERSION=${2:-"latest"}
APP_NAME="nowex-platform"
APP_DIR="/opt/$APP_NAME"
BACKUP_DIR="/opt/backups/$APP_NAME"
DEPLOY_USER=${DEPLOY_USER:-"deploy"}
SERVER_HOST=${SERVER_HOST:-"localhost"}

echo "🔄 Rollback Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Version: $ROLLBACK_VERSION"
echo "   App Directory: $APP_DIR"
echo "   Backup Directory: $BACKUP_DIR"

# اعتبارسنجی محیط
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo "❌ Invalid environment: $ENVIRONMENT"
    exit 1
fi

# تابع اجرای دستور
run_cmd() {
    local cmd="$1"
    if [ "$SERVER_HOST" != "localhost" ]; then
        ssh $DEPLOY_USER@$SERVER_HOST "$cmd"
    else
        eval "$cmd"
    fi
}

# توقف سرویس فعلی
echo "🛑 Stopping current service..."
run_cmd "sudo systemctl stop ${APP_NAME}.service 2>/dev/null || true"
run_cmd "pm2 stop $APP_NAME 2>/dev/null || true"

# پیدا کردن backup برای rollback
echo "🔍 Finding backup for rollback..."
if [ "$ROLLBACK_VERSION" = "latest" ]; then
    # پیدا کردن آخرین backup
    BACKUP_FILE=$(run_cmd "ls -t $BACKUP_DIR/${APP_NAME}_*.tar.gz 2>/dev/null | head -1")
else
    BACKUP_FILE="$BACKUP_DIR/${APP_NAME}_${ROLLBACK_VERSION}.tar.gz"
fi

if [ -z "$BACKUP_FILE" ] || [ "$BACKUP_FILE" = " " ]; then
    echo "❌ No backup found for rollback!"
    echo "   Backup directory: $BACKUP_DIR"
    echo "   Pattern: ${APP_NAME}_*.tar.gz"
    exit 1
fi

echo "   Found backup: $(basename $BACKUP_FILE)"

# تایید rollback
if [ -z "$FORCE_ROLLBACK" ]; then
    echo ""
    echo "⚠️  WARNING: This will restore from backup and replace current deployment!"
    echo "   Backup: $(basename $BACKUP_FILE)"
    echo "   Target: $APP_DIR"
    echo ""
    read -p "Continue with rollback? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Rollback cancelled"
        exit 0
    fi
fi

# حذف دایرکتوری فعلی
echo "🗑️ Removing current deployment..."
run_cmd "rm -rf $APP_DIR"

# استخراج backup
echo "📦 Restoring from backup..."
run_cmd "tar -xzf '$BACKUP_FILE' -C /opt"
run_cmd "chown -R $DEPLOY_USER:$DEPLOY_USER $APP_DIR"

# نصب وابستگی‌ها (اگر لازم باشد)
echo "📦 Reinstalling dependencies..."
if run_cmd "[ -f '$APP_DIR/requirements.txt' ]"; then
    run_cmd "cd $APP_DIR && python3 -m venv venv 2>/dev/null || true"
    run_cmd "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"
fi

# راه‌اندازی مجدد سرویس
echo "▶️ Starting service..."
run_cmd "sudo systemctl daemon-reload"
run_cmd "sudo systemctl start ${APP_NAME}.service"

# بررسی سلامت
echo "🏥 Verifying rollback..."
sleep 10

# Health check
if [ "$SERVER_HOST" != "localhost" ]; then
    STATUS=$(ssh $DEPLOY_USER@$SERVER_HOST "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health || echo '000'")
else
    STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health || echo '000')
fi

if [ "$STATUS" = "200" ]; then
    echo "✅ Rollback successful!"
    echo ""
    echo "📊 Rollback Summary:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Restored from: $(basename $BACKUP_FILE)"
    echo "   Status: ✅ Running (HTTP $STATUS)"
    echo "   Time: $(date)"
else
    echo "❌ Rollback verification failed (HTTP $STATUS)"
    echo "   Service may not be responding correctly"
    exit 1
fi