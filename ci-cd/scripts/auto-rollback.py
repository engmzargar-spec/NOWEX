#!/usr/bin/env python3
"""
Auto-rollback script for CI/CD pipelines.
Automatically rolls back to previous version if deployment fails.
"""

import sys
import os
import subprocess
import shutil
import logging
from datetime import datetime
from typing import Optional, Dict, List
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DeploymentHistory:
    def __init__(self, history_file: str = "deployment-history.json"):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self) -> Dict:
        """Load deployment history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
                return {'deployments': []}
        return {'deployments': []}
    
    def save_history(self):
        """Save deployment history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Deployment history saved to {self.history_file}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def add_deployment(self, deployment_id: str, environment: str, 
                      version: str, timestamp: str, status: str):
        """Add a deployment record to history."""
        deployment = {
            'id': deployment_id,
            'environment': environment,
            'version': version,
            'timestamp': timestamp,
            'status': status,
            'rollback_to': None,
            'rollback_at': None
        }
        
        self.history.setdefault('deployments', []).append(deployment)
        
        # Keep only last 20 deployments
        if len(self.history['deployments']) > 20:
            self.history['deployments'] = self.history['deployments'][-20:]
        
        self.save_history()
        logger.info(f"Added deployment record: {deployment_id} ({environment})")
    
    def update_deployment_status(self, deployment_id: str, status: str):
        """Update deployment status."""
        for deployment in self.history.get('deployments', []):
            if deployment['id'] == deployment_id:
                deployment['status'] = status
                deployment['updated_at'] = datetime.now().isoformat()
                self.save_history()
                logger.info(f"Updated deployment {deployment_id} status to {status}")
                return True
        return False
    
    def get_previous_successful_deployment(self, environment: str) -> Optional[Dict]:
        """Get the previous successful deployment for an environment."""
        deployments = self.history.get('deployments', [])
        
        # Filter by environment and successful status
        env_deployments = [
            d for d in deployments 
            if d['environment'] == environment and d['status'] == 'success'
        ]
        
        # Sort by timestamp (newest first)
        env_deployments.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Return the second most recent (previous) successful deployment
        if len(env_deployments) > 1:
            return env_deployments[1]
        
        return None

class RollbackManager:
    def __init__(self, environment: str, deployment_id: str):
        self.environment = environment
        self.deployment_id = deployment_id
        self.history = DeploymentHistory()
        
        # Configuration based on environment
        self.config = self.get_environment_config()
    
    def get_environment_config(self) -> Dict:
        """Get configuration for the environment."""
        configs = {
            'development': {
                'backup_dir': '/tmp/novex_backups/dev',
                'deploy_dir': '/var/www/novex/dev',
                'service_name': 'novex-dev',
                'health_check_url': 'http://localhost:8001/health'
            },
            'staging': {
                'backup_dir': '/tmp/novex_backups/staging',
                'deploy_dir': '/var/www/novex/staging',
                'service_name': 'novex-staging',
                'health_check_url': 'http://staging.novex.ir/api/health'
            },
            'production': {
                'backup_dir': '/tmp/novex_backups/prod',
                'deploy_dir': '/var/www/novex/prod',
                'service_name': 'novex-prod',
                'health_check_url': 'https://novex.ir/api/health'
            }
        }
        
        return configs.get(self.environment, configs['development'])
    
    def create_backup(self) -> bool:
        """Create backup of current deployment."""
        try:
            deploy_dir = self.config['deploy_dir']
            backup_dir = self.config['backup_dir']
            
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
            
            # Copy deployment directory
            if os.path.exists(deploy_dir):
                shutil.copytree(deploy_dir, backup_path)
                logger.info(f"✅ Backup created: {backup_path}")
                
                # Save backup info
                backup_info = {
                    'timestamp': timestamp,
                    'path': backup_path,
                    'deployment_id': self.deployment_id,
                    'environment': self.environment
                }
                
                backup_info_file = os.path.join(backup_dir, 'backup_info.json')
                with open(backup_info_file, 'w') as f:
                    json.dump(backup_info, f, indent=2)
                
                return True
            else:
                logger.warning(f"Deployment directory not found: {deploy_dir}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the application service."""
        try:
            service_name = self.config['service_name']
            
            # Try systemctl first
            commands = [
                ['systemctl', 'stop', service_name],
                ['service', service_name, 'stop'],
                ['pm2', 'stop', service_name]
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Service stopped: {service_name}")
                        return True
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            logger.warning(f"Could not stop service {service_name} with standard methods")
            
            # Try killing process by port (last resort)
            if self.environment == 'development':
                subprocess.run(['pkill', '-f', 'python.*main.py'], timeout=10)
                logger.info("Attempted to kill Python processes")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start the application service."""
        try:
            service_name = self.config['service_name']
            
            # Try systemctl first
            commands = [
                ['systemctl', 'start', service_name],
                ['service', service_name, 'start'],
                ['pm2', 'start', service_name]
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Service started: {service_name}")
                        
                        # Wait a bit for service to initialize
                        import time
                        time.sleep(5)
                        
                        return True
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            # Fallback: direct Python startup for development
            if self.environment == 'development':
                deploy_dir = self.config['deploy_dir']
                venv_python = os.path.join(deploy_dir, 'venv', 'bin', 'python')
                main_file = os.path.join(deploy_dir, 'backend', 'main.py')
                
                if os.path.exists(venv_python) and os.path.exists(main_file):
                    # Start in background
                    subprocess.Popen(
                        [venv_python, main_file],
                        cwd=deploy_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    logger.info("✅ Started Python application directly")
                    time.sleep(5)
                    return True
            
            logger.error(f"❌ Could not start service {service_name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start service: {e}")
            return False
    
    def health_check(self, max_retries: int = 10, retry_interval: int = 5) -> bool:
        """Check if service is healthy."""
        import time
        import requests
        
        health_url = self.config['health_check_url']
        
        for attempt in range(max_retries):
            try:
                response = requests.get(health_url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ Health check passed (attempt {attempt + 1}/{max_retries})")
                    
                    # Parse health response
                    try:
                        health_data = response.json()
                        if health_data.get('status') == 'healthy':
                            logger.info(f"   Service status: healthy")
                        else:
                            logger.warning(f"   Service status: {health_data.get('status')}")
                    except:
                        pass
                    
                    return True
                else:
                    logger.warning(f"Health check failed: HTTP {response.status_code} (attempt {attempt + 1}/{max_retries})")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Health check error: {e} (attempt {attempt + 1}/{max_retries})")
            
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
        
        logger.error(f"❌ Health check failed after {max_retries} attempts")
        return False
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup."""
        try:
            deploy_dir = self.config['deploy_dir']
            
            # Remove current deployment
            if os.path.exists(deploy_dir):
                shutil.rmtree(deploy_dir)
                logger.info(f"Removed current deployment: {deploy_dir}")
            
            # Restore from backup
            shutil.copytree(backup_path, deploy_dir)
            logger.info(f"✅ Restored from backup: {backup_path}")
            
            # Fix permissions
            subprocess.run(['chmod', '-R', '755', deploy_dir], timeout=30)
            logger.info("Fixed permissions")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restore backup: {e}")
            return False
    
    def get_latest_backup(self) -> Optional[str]:
        """Get the latest backup directory."""
        backup_dir = self.config['backup_dir']
        
        if not os.path.exists(backup_dir):
            return None
        
        # Find all backup directories
        backups = []
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path) and item.startswith('backup_'):
                backups.append(item_path)
        
        # Sort by creation time (newest first)
        backups.sort(key=os.path.getctime, reverse=True)
        
        if backups:
            return backups[0]
        
        return None
    
    def execute_rollback(self, use_latest_backup: bool = True) -> bool:
        """Execute the rollback process."""
        logger.info(f"🚨 Initiating rollback for {self.environment}")
        logger.info(f"Deployment ID: {self.deployment_id}")
        logger.info("="*60)
        
        # Step 1: Stop the service
        logger.info("\n1. Stopping service...")
        if not self.stop_service():
            logger.error("Failed to stop service, continuing anyway...")
        
        # Step 2: Find backup to restore
        logger.info("\n2. Finding backup to restore...")
        
        backup_path = None
        if use_latest_backup:
            backup_path = self.get_latest_backup()
            if backup_path:
                logger.info(f"Found latest backup: {backup_path}")
            else:
                logger.error("No backup found!")
                return False
        else:
            # Get previous successful deployment from history
            prev_deployment = self.history.get_previous_successful_deployment(self.environment)
            if prev_deployment:
                # In a real scenario, you would fetch the specific version
                logger.info(f"Previous successful deployment: {prev_deployment['id']}")
                backup_path = self.get_latest_backup()  # Fallback to latest backup
            else:
                logger.warning("No previous successful deployment found in history")
                backup_path = self.get_latest_backup()
        
        if not backup_path:
            logger.error("❌ No backup available for rollback!")
            return False
        
        # Step 3: Restore from backup
        logger.info("\n3. Restoring from backup...")
        if not self.restore_backup(backup_path):
            return False
        
        # Step 4: Start the service
        logger.info("\n4. Starting service...")
        if not self.start_service():
            return False
        
        # Step 5: Health check
        logger.info("\n5. Performing health check...")
        if not self.health_check():
            logger.error("❌ Health check failed after rollback!")
            return False
        
        # Step 6: Update deployment history
        logger.info("\n6. Updating deployment history...")
        self.history.update_deployment_status(self.deployment_id, 'rolled_back')
        
        # Add rollback record
        for deployment in self.history.history.get('deployments', []):
            if deployment['id'] == self.deployment_id:
                deployment['rollback_to'] = os.path.basename(backup_path)
                deployment['rollback_at'] = datetime.now().isoformat()
                deployment['status'] = 'rolled_back'
                break
        
        self.history.save_history()
        
        logger.info("="*60)
        logger.info("✅ Rollback completed successfully!")
        logger.info(f"Restored from: {os.path.basename(backup_path)}")
        
        return True
    
    def send_notification(self, success: bool, message: str = ""):
        """Send rollback notification."""
        try:
            # This would integrate with Slack, Email, etc.
            # For now, just log it
            
            notification = {
                'environment': self.environment,
                'deployment_id': self.deployment_id,
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'message': message,
                'type': 'rollback'
            }
            
            logger.info("📢 Rollback Notification:")
            logger.info(f"   Environment: {self.environment}")
            logger.info(f"   Status: {'SUCCESS' if success else 'FAILED'}")
            logger.info(f"   Message: {message}")
            
            # Save notification to file
            notifications_dir = 'notifications'
            os.makedirs(notifications_dir, exist_ok=True)
            
            notification_file = os.path.join(
                notifications_dir, 
                f'rollback_{self.deployment_id}.json'
            )
            
            with open(notification_file, 'w') as f:
                json.dump(notification, f, indent=2)
            
            logger.info(f"Notification saved: {notification_file}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-rollback script for failed deployments')
    parser.add_argument('--environment', required=True,
                       choices=['development', 'staging', 'production'],
                       help='Environment to rollback')
    parser.add_argument('--deployment-id', required=True,
                       help='ID of the failed deployment')
    parser.add_argument('--use-latest-backup', action='store_true', default=True,
                       help='Use latest backup for rollback (default: True)')
    parser.add_argument('--no-notification', action='store_true',
                       help='Skip sending notifications')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("🔄 AUTO-ROLLBACK INITIATED")
    logger.info("="*60)
    
    # Initialize rollback manager
    manager = RollbackManager(args.environment, args.deployment_id)
    
    # Execute rollback
    success = manager.execute_rollback(use_latest_backup=args.use_latest_backup)
    
    # Send notification
    if not args.no_notification:
        message = "Rollback completed successfully" if success else "Rollback failed"
        manager.send_notification(success, message)
    
    # Exit with appropriate code
    if success:
        logger.info("🎉 Rollback process completed successfully")
        sys.exit(0)
    else:
        logger.error("💥 Rollback process failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
