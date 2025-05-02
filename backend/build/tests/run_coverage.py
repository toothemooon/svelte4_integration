#!/usr/bin/env python
"""
Run tests with coverage reporting using pytest.

This script runs pytest, generates a coverage report, and places the results
(including the HTML report) inside the tests directory.

Usage:
    python run_coverage.py [options]

Options:
    --html        Generate HTML report (default)
    --xml         Generate XML report for CI integration
    --json        Generate JSON report
    --api         Run only API tests
    --unit        Run only unit tests
    --rbac        Run only role-based access control tests
    --all         Run all tests (default)
    --help        Show this help message
"""
import os
import sys
import subprocess
import argparse

def run_tests_with_coverage(args):
    """Run tests with coverage and generate reports based on args"""
    # Ensure we run from the script's directory (tests)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(script_dir)) # Get parent dir (backend)
    
    print(f"Running tests from: {backend_dir}")
    print(f"Using config: {os.path.join(script_dir, '.coveragerc')}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Prepare test marker if specified
    marker = ""
    if args.api and not args.unit and not args.rbac:
        marker = "api"
        print("Running API tests only")
    elif args.unit and not args.api and not args.rbac:
        marker = "unit"
        print("Running unit tests only")
    elif args.rbac and not args.api and not args.unit:
        # For RBAC tests, we'll use file pattern instead of marker
        print("Running Role-Based Access Control tests only")
    else:
        print("Running all tests")
    
    # First erase any old coverage data
    subprocess.run([sys.executable, "-m", "coverage", "erase"])
    
    # Run pytest with coverage
    cmd = [
        sys.executable, 
        "-m", "coverage", "run", 
        "--source=.", 
        f"--rcfile={os.path.join(script_dir, '.coveragerc')}",
        "-m", "pytest"
    ]
    
    # Add marker if specified (for api or unit tests)
    if marker:
        cmd.extend(["-m", marker])
    
    # For RBAC tests, specify the test file directly
    if args.rbac and not args.api and not args.unit:
        rbac_test_file = os.path.join(os.path.relpath(script_dir, backend_dir), "test_role_based_access.py")
        cmd.append(rbac_test_file)
    else:
        # Otherwise add the general test directory
        cmd.append(os.path.relpath(script_dir, backend_dir))
    
    # Run the tests with coverage
    result = subprocess.run(cmd)
    
    # Generate reports regardless of test success/failure
    # Check if coverage data file exists
    coverage_file = os.path.join(script_dir, ".coverage")
    if not os.path.exists(coverage_file):
        # Try looking for it in the current directory too
        coverage_file = ".coverage"
        if not os.path.exists(coverage_file):
            print("\nCoverage data file not found. Skipping reports.")
            return result.returncode
    
    # Always generate coverage report
    subprocess.run([
        sys.executable, "-m", "coverage", "report",
        f"--rcfile={os.path.join(script_dir, '.coveragerc')}"
    ])
    
    # Generate reports based on args
    if args.html or (not args.xml and not args.json):  # HTML is default
        generate_html_report(script_dir)
    
    if args.xml:
        generate_xml_report(script_dir)
        
    if args.json:
        generate_json_report(script_dir)

    return result.returncode

def generate_html_report(script_dir):
    """Generate HTML coverage report"""
    print("\nGenerating HTML coverage report...")
    html_cmd = [
        sys.executable, "-m", "coverage", "html",
        f"--rcfile={os.path.join(script_dir, '.coveragerc')}"
    ]
    # Run the command
    subprocess.run(html_cmd)
    
    # Show location of the HTML report
    html_dir = os.path.join(script_dir, "htmlcov")
    print(f"\nHTML coverage report generated in: {html_dir}")
    # Try to provide a file URL for easy opening
    try:
        html_file_path = os.path.join(html_dir, "index.html")
        print(f"Open file://{os.path.abspath(html_file_path)}")
    except Exception:
        pass # Ignore errors if path conversion fails

def generate_xml_report(script_dir):
    """Generate XML coverage report for CI integration"""
    print("\nGenerating XML coverage report...")
    xml_cmd = [
        sys.executable, "-m", "coverage", "xml",
        f"--rcfile={os.path.join(script_dir, '.coveragerc')}"
    ]
    # Run the command
    subprocess.run(xml_cmd)
    
    xml_file = os.path.join(script_dir, "coverage.xml")
    print(f"\nXML coverage report generated: {xml_file}")

def generate_json_report(script_dir):
    """Generate JSON coverage report"""
    print("\nGenerating JSON coverage report...")
    json_cmd = [
        sys.executable, "-m", "coverage", "json",
        f"--rcfile={os.path.join(script_dir, '.coveragerc')}"
    ]
    # Run the command
    subprocess.run(json_cmd)
    
    json_file = os.path.join(script_dir, "coverage.json")
    print(f"\nJSON coverage report generated: {json_file}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run tests with coverage reporting')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--xml', action='store_true', help='Generate XML report')
    parser.add_argument('--json', action='store_true', help='Generate JSON report')
    parser.add_argument('--api', action='store_true', help='Run only API tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--rbac', action='store_true', help='Run only role-based access control tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    exit_code = run_tests_with_coverage(args)
    sys.exit(exit_code) 