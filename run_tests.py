#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API

This script can be used to run tests in different modes:
- Basic test run
- Test with coverage
- Test with verbose output
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle the output"""
    print(f"\n🔍 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner function"""
    # Get the project root directory
    project_root = Path(__file__).parent
    python_path = project_root / ".venv" / "bin" / "python"
    
    if not python_path.exists():
        print("❌ Virtual environment not found. Please run 'configure_python_environment' first.")
        sys.exit(1)
    
    print("🧪 Mergington High School Activities API - Test Suite")
    print("=" * 60)
    
    # Run basic tests
    basic_tests_cmd = f"{python_path} -m pytest tests/ -v"
    if not run_command(basic_tests_cmd, "Running basic tests"):
        sys.exit(1)
    
    # Run tests with coverage
    coverage_cmd = f"{python_path} -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html"
    if not run_command(coverage_cmd, "Running tests with coverage"):
        sys.exit(1)
    
    print("\n🎉 All tests passed successfully!")
    print("📊 Coverage report saved to htmlcov/index.html")
    print("🚀 Your API is ready for deployment!")

if __name__ == "__main__":
    main()