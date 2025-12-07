# ci-cd/scripts/update-monitoring.py
#!/usr/bin/env python3
"""
اسکریپت بروزرسانی سیستم مانیتورینگ پس از استقرار
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
import logging

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """پارامترهای ورودی را پردازش می‌کند"""
    parser = argparse.ArgumentParser(description='Update monitoring system after deployment')
    parser.add_argument('--deployment-id', required=True, help='Deployment ID')
    parser.add_argument('--environment', required=True, choices=['dev', 'staging', 'production'], help='Environment name')
    parser.add_argument('--version', required=True, help='Version/SHA of deployment')
    parser.add_argument('--grafana-url', default=os.getenv('GRAFANA_URL', 'http://localhost:3000'))
    parser.add_argument('--grafana-api-key', default=os.getenv('GRAFANA_API_KEY'))
    parser.add_argument('--prometheus-url', default=os.getenv('PROMETHEUS_URL', 'http://localhost:9090'))
    
    return parser.parse_args()

def send_grafana_annotation(args):
    """ارسال annotation به Grafana برای نشان‌گذاری استقرار"""
    if not args.grafana_api_key:
        logger.warning("Grafana API key not provided, skipping annotation")
        return
    
    url = f"{args.grafana_url}/api/annotations"
    headers = {
        "Authorization": f"Bearer {args.grafana_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "text": f"Deployment {args.deployment_id} - {args.environment}",
        "tags": ["deployment", args.environment, args.version],
        "time": int(datetime.now().timestamp() * 1000)
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Grafana annotation added successfully: {response.json().get('id')}")
        else:
            logger.error(f"Failed to add Grafana annotation: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending Grafana annotation: {str(e)}")

def update_prometheus_targets(args):
    """بروزرسانی targets در Prometheus (اگر نیاز باشد)"""
    # در اینجا می‌توانید منطق بروزرسانی Prometheus را اضافه کنید
    # مثلاً بروزرسانی فایل prometheus.yml یا استفاده از API
    logger.info(f"Prometheus targets would be updated for {args.environment} environment")
    
    # مثال: بروزرسانی از طریق فایل کانفیگ
    prometheus_config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s'
        },
        'scrape_configs': [
            {
                'job_name': f'novex-{args.environment}',
                'static_configs': [{'targets': [f'backend.{args.environment}.novex.ir:8000']}],
                'metrics_path': '/metrics'
            }
        ]
    }
    
    # ذخیره کانفیگ (این یک مثال است)
    config_path = f'/tmp/prometheus-{args.environment}.yml'
    with open(config_path, 'w') as f:
        import yaml
        yaml.dump(prometheus_config, f)
    
    logger.info(f"Prometheus config saved to {config_path}")

def create_deployment_dashboard(args):
    """ایجاد داشبورد مخصوص استقرار"""
    dashboard_config = {
        "dashboard": {
            "title": f"Deployment {args.deployment_id} - {args.environment}",
            "tags": ["deployment", args.environment],
            "timezone": "browser",
            "panels": [
                {
                    "title": "Deployment Info",
                    "type": "text",
                    "mode": "html",
                    "content": f"""
                    <div style="padding: 20px;">
                        <h2>Deployment Information</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Deployment ID:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{args.deployment_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Environment:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{args.environment}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Version:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{args.version}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                            </tr>
                        </table>
                    </div>
                    """
                }
            ]
        },
        "overwrite": True
    }
    
    # در اینجا می‌توانید داشبورد را به Grafana ارسال کنید
    logger.info(f"Dashboard configuration created for deployment {args.deployment_id}")

def send_notification(args):
    """ارسال نوتیفیکیشن درباره استقرار"""
    # اینجا می‌توانید به Slack, Telegram, Email و ... ارسال کنید
    message = {
        "text": f"🚀 Deployment Monitor Updated\n"
                f"• Environment: {args.environment}\n"
                f"• Deployment ID: {args.deployment_id}\n"
                f"• Version: {args.version}\n"
                f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    logger.info(f"Notification prepared: {message['text']}")
    
    # مثال ارسال به Slack
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        try:
            response = requests.post(slack_webhook, json=message, timeout=5)
            logger.info(f"Slack notification sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")

def main():
    """تابع اصلی"""
    args = parse_arguments()
    
    logger.info(f"Starting monitoring update for deployment {args.deployment_id}")
    
    try:
        # 1. ارسال annotation به Grafana
        send_grafana_annotation(args)
        
        # 2. بروزرسانی Prometheus targets
        update_prometheus_targets(args)
        
        # 3. ایجاد داشبورد (اختیاری)
        create_deployment_dashboard(args)
        
        # 4. ارسال نوتیفیکیشن
        send_notification(args)
        
        logger.info("Monitoring update completed successfully")
        
    except Exception as e:
        logger.error(f"Error in monitoring update: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()