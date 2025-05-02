#!/usr/bin/env python
"""
Run tests with coverage reporting using pytest.

This script runs pytest, generates a coverage report, and places the results
(including the HTML report) inside the tests directory.
"""
import os
import sys
import subprocess

def run_tests_with_coverage():
    """Run tests with coverage and generate reports"""
    # Ensure we run from the script's directory (tests)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir) # Get parent dir (backend)
    
    print(f"Running tests from: {backend_dir}")
    print(f"Using config: {os.path.join(script_dir, '.coveragerc')}")
    
    # Run pytest with coverage from the backend directory
    # Pass the config file explicitly
    cmd = [
        sys.executable,  # Use the same python interpreter running this script
        "-m", "pytest", 
        "--cov=.", 
        f"--cov-config={os.path.join(script_dir, '.coveragerc')}", # Explicit path to config
        script_dir # Tell pytest to look for tests in the tests dir
    ]
    
    # Use cwd to run pytest from the backend directory
    result = subprocess.run(cmd, cwd=backend_dir, check=False) # check=False to handle test failures
    
    # If tests passed (or failed but ran), generate an HTML report
    # Coverage data should be in tests/.coverage as per config
    if os.path.exists(os.path.join(script_dir, ".coverage")):
        print("\nGenerating HTML coverage report...")
        html_cmd = [
            sys.executable, "-m", "coverage", "html",
            f"--rcfile={os.path.join(script_dir, '.coveragerc')}" # Use explicit config path
        ]
        # Run coverage html from the backend directory
        subprocess.run(html_cmd, cwd=backend_dir, check=False)
        
        # Show location of the HTML report (inside tests/htmlcov)
        html_dir = os.path.join(script_dir, "htmlcov")
        print(f"\nHTML coverage report generated in: {html_dir}")
        # Try to provide a file URL for easy opening
        try:
            html_file_path = os.path.join(html_dir, "index.html")
            print(f"Open file://{html_file_path}")
        except Exception:
            pass # Ignore errors if path conversion fails
    else:
        print("\nCoverage data file not found. Skipping HTML report.")

    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests_with_coverage()
    sys.exit(exit_code) 