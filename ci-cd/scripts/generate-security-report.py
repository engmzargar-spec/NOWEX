#!/usr/bin/env python3
"""
Generate security report from various security scanning tools.
Aggregates results from Bandit, Safety, and other security tools.
"""

import sys
import os
import json
import glob
import logging
from datetime import datetime
from typing import Dict, List, Any
import html

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityReportGenerator:
    def __init__(self, output_dir: str = "security-reports"):
        self.output_dir = output_dir
        self.reports = {}
        self.summary = {
            'total_issues': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'tools_run': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def load_bandit_report(self, filepath: str = "bandit-report.json"):
        """Load and parse Bandit security scan report."""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Bandit report not found: {filepath}")
                return
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            issues = []
            for result in data.get('results', []):
                issue = {
                    'tool': 'bandit',
                    'severity': result.get('issue_severity', 'MEDIUM').upper(),
                    'confidence': result.get('issue_confidence', 'MEDIUM').upper(),
                    'file': result.get('filename', ''),
                    'line': result.get('line_number', 0),
                    'code': result.get('code', ''),
                    'description': result.get('issue_text', ''),
                    'test_id': result.get('test_id', ''),
                    'test_name': result.get('test_name', '')
                }
                issues.append(issue)
            
            self.reports['bandit'] = {
                'tool': 'Bandit',
                'issues': issues,
                'metrics': data.get('metrics', {}),
                'timestamp': data.get('generated_at', '')
            }
            
            # Update summary
            self.summary['tools_run'].append('bandit')
            for issue in issues:
                self.summary['total_issues'] += 1
                severity = issue['severity']
                if severity == 'HIGH':
                    self.summary['high_issues'] += 1
                elif severity == 'MEDIUM':
                    self.summary['medium_issues'] += 1
                elif severity == 'LOW':
                    self.summary['low_issues'] += 1
            
            logger.info(f"✅ Loaded Bandit report: {len(issues)} issues found")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Bandit report: {e}")
    
    def load_safety_report(self, filepath: str = "safety-report.json"):
        """Load and parse Safety dependency scan report."""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Safety report not found: {filepath}")
                return
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            issues = []
            for vuln in data.get('vulnerabilities', []):
                issue = {
                    'tool': 'safety',
                    'severity': vuln.get('severity', 'MEDIUM').upper(),
                    'package': vuln.get('package_name', ''),
                    'version': vuln.get('analyzed_version', ''),
                    'vulnerability_id': vuln.get('vulnerability_id', ''),
                    'advisory': vuln.get('advisory', ''),
                    'cve': vuln.get('CVE', ''),
                    'cvss_score': vuln.get('cvss_score', 0),
                    'affected_versions': vuln.get('affected_versions', ''),
                    'more_info': vuln.get('more_info_url', '')
                }
                issues.append(issue)
            
            self.reports['safety'] = {
                'tool': 'Safety',
                'issues': issues,
                'scanned': data.get('scanned', []),
                'timestamp': datetime.now().isoformat()
            }
            
            # Update summary
            self.summary['tools_run'].append('safety')
            for issue in issues:
                self.summary['total_issues'] += 1
                severity = issue['severity']
                if severity == 'CRITICAL':
                    self.summary['critical_issues'] += 1
                elif severity == 'HIGH':
                    self.summary['high_issues'] += 1
                elif severity == 'MEDIUM':
                    self.summary['medium_issues'] += 1
                elif severity == 'LOW':
                    self.summary['low_issues'] += 1
            
            logger.info(f"✅ Loaded Safety report: {len(issues)} vulnerabilities found")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Safety report: {e}")
    
    def generate_json_report(self):
        """Generate JSON security report."""
        report_data = {
            'summary': self.summary,
            'reports': self.reports,
            'generated_at': datetime.now().isoformat(),
            'project': 'NOWEX Platform'
        }
        
        output_file = os.path.join(self.output_dir, 'security-report.json')
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"✅ JSON report generated: {output_file}")
        return output_file
    
    def generate_html_report(self):
        """Generate HTML security report."""
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Report - NOWEX Platform</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .critical {{ color: #d63031; font-weight: bold; }}
                .high {{ color: #e17055; font-weight: bold; }}
                .medium {{ color: #fdcb6e; font-weight: bold; }}
                .low {{ color: #00b894; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .tool-section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .severity-badge {{ padding: 3px 8px; border-radius: 3px; font-size: 12px; color: white; }}
                .severity-critical {{ background: #d63031; }}
                .severity-high {{ background: #e17055; }}
                .severity-medium {{ background: #fdcb6e; }}
                .severity-low {{ background: #00b894; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Security Report - NOWEX Platform</h1>
                <p>Generated: {self.summary['timestamp']}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Security Summary</h2>
                <p>Tools Run: {', '.join(self.summary['tools_run'])}</p>
                <p>Total Issues: <strong>{self.summary['total_issues']}</strong></p>
                <p>Critical Issues: <span class="critical">{self.summary['critical_issues']}</span></p>
                <p>High Issues: <span class="high">{self.summary['high_issues']}</span></p>
                <p>Medium Issues: <span class="medium">{self.summary['medium_issues']}</span></p>
                <p>Low Issues: <span class="low">{self.summary['low_issues']}</span></p>
            </div>
        '''
        
        # Add tool-specific sections
        for tool_name, tool_data in self.reports.items():
            issues = tool_data.get('issues', [])
            if not issues:
                continue
            
            html_content += f'''
            <div class="tool-section">
                <h2>🛡️ {tool_data['tool']} Findings</h2>
                <p>Total Issues: {len(issues)}</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Location</th>
                            <th>Description</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            for issue in issues:
                severity_class = f'severity-{issue["severity"].lower()}'
                severity_badge = f'<span class="severity-badge {severity_class}">{issue["severity"]}</span>'
                
                location = ''
                if issue['tool'] == 'bandit':
                    location = f'{issue["file"]}:{issue["line"]}'
                elif issue['tool'] == 'safety':
                    location = f'{issue["package"]} {issue["version"]}'
                
                description = html.escape(issue.get('description', ''))[:200]
                
                details = ''
                if issue['tool'] == 'bandit':
                    details = f'Test: {issue.get("test_name", "")}'
                elif issue['tool'] == 'safety':
                    if issue.get('cve'):
                        details = f'CVE: {issue["cve"]}'
                    elif issue.get('vulnerability_id'):
                        details = f'ID: {issue["vulnerability_id"]}'
                
                html_content += f'''
                <tr>
                    <td>{severity_badge}</td>
                    <td><code>{location}</code></td>
                    <td>{description}</td>
                    <td>{details}</td>
                </tr>
                '''
            
            html_content += '''
                    </tbody>
                </table>
            </div>
            '''
        
        # Add recommendations
        html_content += '''
            <div class="tool-section">
                <h2>📋 Security Recommendations</h2>
                <ul>
                    <li>Address all Critical and High severity issues immediately</li>
                    <li>Review Medium severity issues in the next development cycle</li>
                    <li>Monitor Low severity issues for future updates</li>
                    <li>Keep dependencies updated regularly</li>
                    <li>Implement regular security scanning in CI/CD pipeline</li>
                </ul>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                <p><strong>Report Generated By:</strong> NOWEX CI/CD Security Scanner</p>
                <p><strong>Contact:</strong> security@novex.ir</p>
            </div>
        </body>
        </html>
        '''
        
        output_file = os.path.join(self.output_dir, 'security-report.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML report generated: {output_file}")
        return output_file
    
    def generate_markdown_report(self):
        """Generate Markdown security report."""
        md_content = f'''# 🔒 Security Report - NOWEX Platform

**Generated:** {self.summary['timestamp']}

## 📊 Security Summary

- **Tools Run:** {', '.join(self.summary['tools_run'])}
- **Total Issues:** {self.summary['total_issues']}
- **Critical Issues:** **{self.summary['critical_issues']}**
- **High Issues:** **{self.summary['high_issues']}**
- **Medium Issues:** **{self.summary['medium_issues']}**
- **Low Issues:** **{self.summary['low_issues']}**

'''
        
        # Add tool-specific sections
        for tool_name, tool_data in self.reports.items():
            issues = tool_data.get('issues', [])
            if not issues:
                continue
            
            md_content += f'''## 🛡️ {tool_data['tool']} Findings

**Total Issues:** {len(issues)}

| Severity | Location | Description | Details |
|----------|----------|-------------|---------|
'''
            
            for issue in issues:
                severity = issue['severity']
                
                location = ''
                if issue['tool'] == 'bandit':
                    location = f'`{issue["file"]}:{issue["line"]}`'
                elif issue['tool'] == 'safety':
                    location = f'`{issue["package"]} {issue["version"]}`'
                
                description = issue.get('description', '')[:150].replace('|', '\\|')
                
                details = ''
                if issue['tool'] == 'bandit':
                    details = f'Test: {issue.get("test_name", "")}'
                elif issue['tool'] == 'safety':
                    if issue.get('cve'):
                        details = f'CVE: {issue["cve"]}'
                    elif issue.get('vulnerability_id'):
                        details = f'ID: {issue["vulnerability_id"]}'
                
                md_content += f'| **{severity}** | {location} | {description} | {details} |\n'
            
            md_content += '\n'
        
        # Add recommendations
        md_content += '''## 📋 Security Recommendations

1. **Address all Critical and High severity issues immediately**
2. **Review Medium severity issues in the next development cycle**
3. **Monitor Low severity issues for future updates**
4. **Keep dependencies updated regularly**
5. **Implement regular security scanning in CI/CD pipeline**

---

**Report Generated By:** NOWEX CI/CD Security Scanner  
**Contact:** security@novex.ir
'''
        
        output_file = os.path.join(self.output_dir, 'security-report.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"✅ Markdown report generated: {output_file}")
        return output_file
    
    def check_security_threshold(self, max_critical: int = 0, max_high: int = 2) -> bool:
        """
        Check if security issues are within acceptable thresholds.
        
        Returns: True if within thresholds, False otherwise
        """
        if self.summary['critical_issues'] > max_critical:
            logger.error(f"❌ Critical issues ({self.summary['critical_issues']}) exceed threshold ({max_critical})")
            return False
        
        if self.summary['high_issues'] > max_high:
            logger.error(f"❌ High issues ({self.summary['high_issues']}) exceed threshold ({max_high})")
            return False
        
        logger.info(f"✅ Security thresholds met: Critical <= {max_critical}, High <= {max_high}")
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate security report')
    parser.add_argument('--bandit-report', default='bandit-report.json',
                       help='Path to Bandit JSON report (default: bandit-report.json)')
    parser.add_argument('--safety-report', default='safety-report.json',
                       help='Path to Safety JSON report (default: safety-report.json)')
    parser.add_argument('--output-dir', default='security-reports',
                       help='Output directory for reports (default: security-reports)')
    parser.add_argument('--format', choices=['all', 'json', 'html', 'md'], default='all',
                       help='Output format (default: all)')
    parser.add_argument('--max-critical', type=int, default=0,
                       help='Maximum allowed critical issues (default: 0)')
    parser.add_argument('--max-high', type=int, default=2,
                       help='Maximum allowed high issues (default: 2)')
    
    args = parser.parse_args()
    
    logger.info("Generating security report...")
    logger.info(f"Bandit report: {args.bandit_report}")
    logger.info(f"Safety report: {args.safety_report}")
    
    generator = SecurityReportGenerator(args.output_dir)
    
    # Load reports
    generator.load_bandit_report(args.bandit_report)
    generator.load_safety_report(args.safety_report)
    
    # Generate reports
    generated_files = []
    
    if args.format in ['all', 'json']:
        json_file = generator.generate_json_report()
        generated_files.append(json_file)
    
    if args.format in ['all', 'html']:
        html_file = generator.generate_html_report()
        generated_files.append(html_file)
    
    if args.format in ['all', 'md']:
        md_file = generator.generate_markdown_report()
        generated_files.append(md_file)
    
    # Check thresholds
    logger.info("\n" + "="*60)
    logger.info("SECURITY THRESHOLD CHECK:")
    
    threshold_passed = generator.check_security_threshold(
        max_critical=args.max_critical,
        max_high=args.max_high
    )
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("REPORT SUMMARY:")
    logger.info(f"Total issues found: {generator.summary['total_issues']}")
    logger.info(f"Critical issues: {generator.summary['critical_issues']}")
    logger.info(f"High issues: {generator.summary['high_issues']}")
    logger.info(f"Medium issues: {generator.summary['medium_issues']}")
    logger.info(f"Low issues: {generator.summary['low_issues']}")
    logger.info(f"Generated files: {len(generated_files)}")
    
    for file in generated_files:
        logger.info(f"  📄 {file}")
    
    logger.info("="*60)
    
    if threshold_passed:
        logger.info("✅ Security scan PASSED thresholds")
        sys.exit(0)
    else:
        logger.error("❌ Security scan FAILED thresholds")
        sys.exit(1)

if __name__ == "__main__":
    main()
