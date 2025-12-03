#!/bin/bash

# ci-cd/scripts/health-check.sh
# اسکریپت بررسی سلامت سرویس‌ها

set -e  # در صورت خطا، اجرا متوقف شود

echo "🏥 Running health checks..."

# تنظیمات پیش‌فرض
APP_URL=${APP_URL:-"http://localhost:8000"}
MAX_RETRIES=${MAX_RETRIES:-10}
RETRY_INTERVAL=${RETRY_INTERVAL:-10}  # ثانیه
TIMEOUT=${TIMEOUT:-5}  # ثانیه برای curl

# لیست endpoint های حیاتی برای بررسی
CRITICAL_ENDPOINTS=(
    "/api/health"
    "/api/v1/health"
    "/health"
    "/"
)

# لیست endpoint های سرویس‌های خاص
SERVICE_ENDPOINTS=(
    "/api/auth/health"
    "/api/finance/health"
    "/api/kyc/health"
    "/api/admin/health"
)

echo "🔍 Target URL: $APP_URL"
echo "🔄 Max retries: $MAX_RETRIES"
echo "⏱️ Retry interval: ${RETRY_INTERVAL}s"

# تابع بررسی endpoint
check_endpoint() {
    local endpoint=$1
    local full_url="${APP_URL}${endpoint}"
    
    echo "   Checking: $endpoint"
    
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time $TIMEOUT \
        "$full_url" || echo "000")
    
    if [ "$response_code" = "200" ] || [ "$response_code" = "201" ] || [ "$response_code" = "204" ]; then
        echo "   ✅ $endpoint - HTTP $response_code"
        return 0
    else
        echo "   ❌ $endpoint - HTTP $response_code"
        return 1
    fi
}

# تابع بررسی اتصال به دیتابیس (اگر اسکریپت وجود دارد)
check_database() {
    if [ -f "ci-cd/scripts/test-db-connection.py" ]; then
        echo "🗄️ Checking database connection..."
        python ci-cd/scripts/test-db-connection.py
        if [ $? -eq 0 ]; then
            echo "   ✅ Database connection successful"
            return 0
        else
            echo "   ❌ Database connection failed"
            return 1
        fi
    fi
    return 0
}

# بررسی اصلی با retry logic
echo "🔄 Starting health checks (retry $MAX_RETRIES times)..."

for ((i=1; i<=MAX_RETRIES; i++)); do
    echo ""
    echo "Attempt $i of $MAX_RETRIES:"
    
    ALL_CHECKS_PASSED=true
    
    # بررسی endpoint های حیاتی
    echo "📡 Checking critical endpoints..."
    for endpoint in "${CRITICAL_ENDPOINTS[@]}"; do
        if ! check_endpoint "$endpoint"; then
            ALL_CHECKS_PASSED=false
        fi
    done
    
    # بررسی endpoint های سرویس‌ها (اگر حداقل یک endpoint حیاتی پاسخ داد)
    if [ "$ALL_CHECKS_PASSED" = true ]; then
        echo "🔧 Checking service endpoints..."
        for endpoint in "${SERVICE_ENDPOINTS[@]}"; do
            check_endpoint "$endpoint" || true  # خطاهای سرویس‌ها fatal نیستند
        done
    fi
    
    # بررسی دیتابیس
    check_database || true
    
    if [ "$ALL_CHECKS_PASSED" = true ]; then
        echo ""
        echo "🎉 All health checks passed!"
        
        # گزارش نهایی
        echo "📊 Final status:"
        echo "   ✅ Application is healthy"
        echo "   ✅ All critical endpoints responding"
        echo "   ✅ Ready to serve traffic"
        
        exit 0
    else
        if [ $i -lt $MAX_RETRIES ]; then
            echo "⏳ Some checks failed. Retrying in ${RETRY_INTERVAL} seconds..."
            sleep $RETRY_INTERVAL
        fi
    fi
done

echo ""
echo "🚨 Health check failed after $MAX_RETRIES attempts"
echo "🔍 Debug information:"
echo "   Application URL: $APP_URL"
echo "   Time: $(date)"
echo "   Last error: Check application logs"

exit 1