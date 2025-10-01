#!/usr/bin/env python3
"""
MouseAlerts Test Runner - Web Scraping Tests

This script runs the Disney web scraping tests from the proper test directory.
"""

import sys
import os
import subprocess

def main():
    """Run the scraping tests"""
    print("🎭 MouseAlerts - Running Web Scraping Tests")
    print("=" * 60)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, "api", "test_scraping.py")
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    print(f"📁 Running test: {test_file}")
    print("-" * 60)
    
    try:
        # Run the test
        result = subprocess.run([sys.executable, test_file], cwd=os.path.join(script_dir, "..", "api"))
        return result.returncode
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
