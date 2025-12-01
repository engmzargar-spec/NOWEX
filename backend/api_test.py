import requests
import os
from datetime import datetime

# Path to Downloads folder
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

# Unique log filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(downloads_path, f"api_test_{timestamp}.log")

BASE_URL = "http://localhost:8000"

# Ask user for token input
raw_token = input("Please paste your JWT token from Swagger (without 'Bearer'): ").strip()
TOKEN = f"Bearer {raw_token}"

# Ask user which endpoints to test
choice = input("Which endpoints do you want to test? (user/admin/both): ").strip().lower()

# User endpoints
user_endpoints = [
    ("GET", "/api/v1/kyc/profile"),
    ("PUT", "/api/v1/kyc/profile"),
    ("POST", "/api/v1/kyc/profile"),
    ("POST", "/api/v1/kyc/submit"),
    ("POST", "/api/v1/kyc/verify"),
    ("POST", "/api/v1/kyc/documents"),
    ("GET", "/api/v1/kyc/status"),
    ("GET", "/api/v1/kyc/state/transitions"),
    ("GET", "/api/v1/scoring/score"),
    ("POST", "/api/v1/scoring/calculate"),
    ("GET", "/api/v1/scoring/history"),
    ("GET", "/api/v1/scoring/leaderboard"),
    ("GET", "/api/v1/scoring/benefits"),
    ("GET", "/api/v1/referral/code"),
    ("POST", "/api/v1/referral/code/generate"),
    ("POST", "/api/v1/referral/apply"),
    ("GET", "/api/v1/referral/stats"),
    ("GET", "/api/v1/referral/relationships"),
    ("GET", "/api/v1/referral/leaderboard"),
    ("GET", "/api/v1/referral/invite-link"),
]

# Admin endpoints
admin_endpoints = [
    ("GET", "/api/v1/admin/admin/kyc/profiles"),
    ("GET", "/api/v1/admin/admin/kyc/pending"),
    ("POST", "/api/v1/admin/admin/kyc/approve"),
    ("POST", "/api/v1/admin/admin/kyc/reject"),
    ("GET", "/api/v1/admin/admin/kyc/stats"),
]

# Select endpoints based on choice
if choice == "user":
    endpoints = user_endpoints
elif choice == "admin":
    endpoints = admin_endpoints
else:
    endpoints = user_endpoints + admin_endpoints

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "accept": "application/json"
}

# In-memory log buffer
logs = []

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

def add_log(level, message):
    line = f"{now()} - {level} - {message}"
    print(line)
    logs.append(line)

def test_endpoint(method, path):
    url = BASE_URL + path
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json={}, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json={}, timeout=5)
        else:
            add_log("WARNING", f"Method {method} not supported for {path}")
            return

        if response.status_code == 200:
            add_log("INFO", f"{method} {path} SUCCESS ✅")
        else:
            add_log("ERROR", f"{method} {path} FAILED ❌ ({response.status_code}) - {response.text[:200]}")
    except requests.exceptions.Timeout:
        add_log("ERROR", f"{method} {path} ERROR ❌ - request timeout")
    except Exception as e:
        add_log("ERROR", f"{method} {path} ERROR ❌ - {str(e)}")

if __name__ == "__main__":
    add_log("INFO", f"Starting API tests. Log file will be saved as: {log_file}")
    for method, path in endpoints:
        test_endpoint(method, path)

    # Write logs to file
    with open(log_file, "w", encoding="utf-8") as f:
        for line in logs:
            f.write(line + "\n")

    print(f"All endpoints tested. Results saved in {log_file}")
