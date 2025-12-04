import os
import sys

def test_project_structure():
    """بررسی ساختار اصلی پروژه"""
    assert os.path.exists("apps"), "apps directory should exist"
    assert os.path.exists("main.py"), "main.py should exist"
    assert os.path.exists("requirements.txt"), "requirements.txt should exist"
    print("✅ Project structure is valid")

def test_python_version():
    """بررسی نسخه پایتون"""
    version = sys.version_info
    assert version.major == 3, "Python 3 is required"
    assert version.minor >= 9, "Python 3.9 or higher is required"
    print(f"✅ Python version: {sys.version}")