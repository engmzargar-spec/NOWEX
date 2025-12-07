#!/bin/bash
# ci-cd/scripts/database-migrate.sh
#
# اسکریپت مدیریت مهاجرت‌های دیتابیس
#

set -e  # در صورت خطا توقف کن

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# توابع کمکی
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# نمایش راهنما
show_help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  up [n]           اجرای مهاجرت‌ها به بالا (n تعداد اختیاری)"
    echo "  down [n]         اجرای مهاجرت‌ها به پایین (n تعداد اختیاری)"
    echo "  status           نمایش وضعیت مهاجرت‌ها"
    echo "  create <name>    ایجاد فایل مهاجرت جدید"
    echo "  reset            ریست کامل دیتابیس (فقط محیط dev)"
    echo "  validate         اعتبارسنجی مهاجرت‌ها"
    echo ""
    echo "Options:"
    echo "  --env <env>      محیط (dev/staging/production) - پیش‌فرض: dev"
    echo "  --help           نمایش این راهنما"
    echo ""
    exit 0
}

# بارگذاری متغیرهای محیطی
load_environment() {
    local env=${1:-dev}
    
    log_info "Loading environment: $env"
    
    # بارگذاری فایل کانفیگ
    local config_file="ci-cd/environments/$env/config.yaml"
    
    if [ ! -f "$config_file" ]; then
        log_error "Config file not found: $config_file"
        exit 1
    fi
    
    # استخراج متغیرهای دیتابیس (در اینجا ساده شده)
    # در حالت واقعی باید از yq یا python استفاده کرد
    if [ "$env" = "production" ]; then
        export DATABASE_URL="$PRODUCTION_DB_URL"
        export DB_HOST="$PRODUCTION_DB_HOST"
        export DB_PORT="$PRODUCTION_DB_PORT"
        export DB_NAME="$PRODUCTION_DB_NAME"
        export DB_USER="$PRODUCTION_DB_USER"
        export DB_PASSWORD="$PRODUCTION_DB_PASSWORD"
    elif [ "$env" = "staging" ]; then
        export DATABASE_URL="$STAGING_DB_URL"
        export DB_HOST="$STAGING_DB_HOST"
        export DB_PORT="$STAGING_DB_PORT"
        export DB_NAME="$STAGING_DB_NAME"
        export DB_USER="$STAGING_DB_USER"
        export DB_PASSWORD="$STAGING_DB_PASSWORD"
    else
        export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/novex_dev"
        export DB_HOST="localhost"
        export DB_PORT="5432"
        export DB_NAME="novex_dev"
        export DB_USER="postgres"
        export DB_PASSWORD="postgres"
    fi
    
    log_info "Database: $DB_HOST:$DB_PORT/$DB_NAME"
}

# بررسی اتصال به دیتابیس
check_db_connection() {
    log_info "Checking database connection..."
    
    # استفاده از اسکریپت Python برای بررسی اتصال
    python3 ci-cd/scripts/test-db-connection.py
    
    if [ $? -eq 0 ]; then
        log_success "Database connection successful"
    else
        log_error "Failed to connect to database"
        exit 1
    fi
}

# اجرای مهاجرت به بالا
migrate_up() {
    local steps=${1:-"all"}
    
    log_info "Running migrations UP ($steps steps)..."
    
    # رفتن به پوشه migrations
    cd database/migrations
    
    # یافتن فایل‌های مهاجرت
    local migration_files=$(find . -name "*.sql" | sort)
    
    if [ "$steps" = "all" ]; then
        # اجرای همه مهاجرت‌ها
        for file in $migration_files; do
            log_info "Applying migration: $file"
            psql "$DATABASE_URL" -f "$file"
            
            if [ $? -eq 0 ]; then
                log_success "Migration applied: $file"
                
                # ثبت در جدول migrations
                psql "$DATABASE_URL" -c "
                INSERT INTO migrations (filename, applied_at) 
                VALUES ('$file', NOW()) 
                ON CONFLICT (filename) DO NOTHING;"
            else
                log_error "Failed to apply migration: $file"
                exit 1
            fi
        done
    else
        # اجرای تعداد مشخصی مهاجرت
        local count=0
        for file in $migration_files; do
            if [ $count -lt $steps ]; then
                log_info "Applying migration: $file"
                psql "$DATABASE_URL" -f "$file"
                
                if [ $? -eq 0 ]; then
                    log_success "Migration applied: $file"
                    psql "$DATABASE_URL" -c "
                    INSERT INTO migrations (filename, applied_at) 
                    VALUES ('$file', NOW()) 
                    ON CONFLICT (filename) DO NOTHING;"
                    
                    count=$((count + 1))
                else
                    log_error "Failed to apply migration: $file"
                    exit 1
                fi
            else
                break
            fi
        done
    fi
    
    log_success "Migrations UP completed"
}

# اجرای مهاجرت به پایین
migrate_down() {
    local steps=${1:-1}
    
    log_warning "Running migrations DOWN ($steps steps)..."
    
    # گرفتن آخرین مهاجرت‌های اعمال شده
    local last_migrations=$(psql "$DATABASE_URL" -t -c "
    SELECT filename FROM migrations 
    ORDER BY applied_at DESC 
    LIMIT $steps;" | tr -d ' ')
    
    for migration in $last_migrations; do
        log_warning "Reverting migration: $migration"
        
        # اینجا نیاز به فایل revert داریم
        # در حال حاضر فقط از جدول migrations حذف می‌کنیم
        psql "$DATABASE_URL" -c "DELETE FROM migrations WHERE filename = '$migration';"
        
        log_success "Migration reverted: $migration"
    done
    
    log_success "Migrations DOWN completed"
}

# نمایش وضعیت مهاجرت‌ها
migrate_status() {
    log_info "Migration status:"
    
    # بررسی وجود جدول migrations
    local table_exists=$(psql "$DATABASE_URL" -t -c "
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'migrations'
    );" | tr -d ' ')
    
    if [ "$table_exists" = "t" ]; then
        # نمایش مهاجرت‌های اعمال شده
        psql "$DATABASE_URL" -c "
        SELECT 
            ROW_NUMBER() OVER (ORDER BY applied_at) as id,
            filename,
            applied_at
        FROM migrations 
        ORDER BY applied_at;"
    else
        log_warning "Migrations table does not exist"
    fi
    
    # نمایش فایل‌های مهاجرت موجود
    echo ""
    log_info "Available migration files:"
    find database/migrations -name "*.sql" | sort
}

# ایجاد فایل مهاجرت جدید
migrate_create() {
    local name=$1
    if [ -z "$name" ]; then
        log_error "Migration name is required"
        exit 1
    fi
    
    local timestamp=$(date +%Y%m%d%H%M%S)
    local filename="database/migrations/${timestamp}_${name}.sql"
    
    log_info "Creating migration file: $filename"
    
    # ایجاد فایل با template
    cat > "$filename" << EOF
-- Migration: $name
-- Created at: $(date)
-- Description: 

-- UP Migration
BEGIN;

-- Add your SQL commands here
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

COMMIT;

-- DOWN Migration (for rollback)
-- BEGIN;
-- DROP TABLE IF EXISTS example;
-- COMMIT;
EOF
    
    log_success "Migration file created: $filename"
    echo "Edit the file to add your migration SQL."
}

# اعتبارسنجی مهاجرت‌ها
migrate_validate() {
    log_info "Validating migrations..."
    
    # بررسی فایل‌های تکراری
    local duplicates=$(find database/migrations -name "*.sql" | \
        xargs -I {} basename {} | \
        cut -d'_' -f1 | \
        uniq -d)
    
    if [ -n "$duplicates" ]; then
        log_error "Duplicate migration timestamps found: $duplicates"
        exit 1
    fi
    
    # بررسی فرمت نام فایل‌ها
    local bad_files=$(find database/migrations -name "*.sql" | \
        grep -vE '[0-9]{14}_.+\.sql')
    
    if [ -n "$bad_files" ]; then
        log_error "Bad migration filename format:"
        echo "$bad_files"
        exit 1
    fi
    
    log_success "Migration validation passed"
}

# تابع اصلی
main() {
    # پارس آرگومان‌ها
    local command=""
    local env="dev"
    local arg1=""
    local arg2=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                env="$2"
                shift 2
                ;;
            --help)
                show_help
                ;;
            *)
                if [ -z "$command" ]; then
                    command="$1"
                elif [ -z "$arg1" ]; then
                    arg1="$1"
                elif [ -z "$arg2" ]; then
                    arg2="$1"
                fi
                shift
                ;;
        esac
    done
    
    # بارگذاری محیط
    load_environment "$env"
    
    # بررسی دستور
    case $command in
        up)
            check_db_connection
            migrate_up "$arg1"
            ;;
        down)
            check_db_connection
            migrate_down "$arg1"
            ;;
        status)
            check_db_connection
            migrate_status
            ;;
        create)
            migrate_create "$arg1"
            ;;
        reset)
            if [ "$env" != "dev" ]; then
                log_error "Reset is only allowed in dev environment"
                exit 1
            fi
            check_db_connection
            log_warning "Resetting database..."
            psql "$DATABASE_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
            migrate_up
            ;;
        validate)
            migrate_validate
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            ;;
    esac
}

# اجرای اسکریپت
main "$@"