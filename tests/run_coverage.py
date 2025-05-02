#!/usr/bin/env python
"""
Run tests with coverage reporting

This script runs tests with coverage reporting and stores the result in the tests directory.
"""
import os
import sys
import subprocess

def run_coverage():
    """Run tests with coverage and generate reports"""
    # Get the directory where this script is located (tests directory)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the parent directory (backend)
    os.chdir(os.path.dirname(tests_dir))
    
    # Run pytest with coverage
    cmd = [
        "python", "-m", "pytest", 
        "--cov=.", 
        "--cov-config=tests/.coveragerc",
        "tests/"
    ]
    
    result = subprocess.run(cmd)
    
    # If tests passed, generate an HTML report
    if result.returncode == 0:
        print("\nGenerating HTML coverage report...")
        html_cmd = [
            "python", "-m", "coverage", "html",
            "--rcfile=tests/.coveragerc"
        ]
        subprocess.run(html_cmd)
        
        # Show location of the HTML report
        html_dir = os.path.join(tests_dir, "htmlcov")
        print(f"\nHTML coverage report available at: {html_dir}/index.html")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_coverage()) 