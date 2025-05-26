#!/usr/bin/env python3
"""
Test Runner for Make.com Blueprint Creator

This script runs all tests and generates coverage reports.
It provides a comprehensive test suite for the entire project.

Usage:
    python run_tests.py

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from unittest.mock import patch


def setup_environment():
    """Set up environment variables for testing."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Set test environment variables to prevent actual API calls
    test_env_vars = {
        'MAKE_API_TOKEN': 'test_token_for_testing_only',
        'MAKE_TEAM_ID': '123456',
        'MAKE_ORGANIZATION_ID': '789012',
        'MAKE_API_BASE_URL': 'https://test.make.com/api/v2',
        # Disable actual HTTP requests in tests
        'TESTING': 'true',
        'NO_NETWORK': 'true'
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("🔧 Environment configured for testing")
    print(f"   🔑 API Token: {os.environ.get('MAKE_API_TOKEN', 'Not set')[:20]}...")
    print(f"   👥 Team ID: {os.environ.get('MAKE_TEAM_ID', 'Not set')}")
    print(f"   🏢 Organization ID: {os.environ.get('MAKE_ORGANIZATION_ID', 'Not set')}")
    print(f"   🌐 Base URL: {os.environ.get('MAKE_API_BASE_URL', 'Not set')}")


def discover_test_files():
    """Discover all test files in the current directory."""
    test_files = []
    for file_path in Path('.').glob('test_*.py'):
        test_files.append(file_path.name)
    
    test_files.sort()  # Ensure consistent order
    return test_files


def run_tests_with_coverage():
    """Run all tests with coverage analysis."""
    print("📊 Running tests with coverage analysis...")
    
    # Run tests with coverage
    cmd = [
        sys.executable, '-m', 'coverage', 'run',
        '--source=app,get_team_info,example',
        '--omit=test_*.py,run_tests.py',
        '-m', 'unittest', 'discover',
        '-s', '.', '-p', 'test_*.py',
        '-v'
    ]
    
    try:
        # Patch requests to prevent any actual HTTP calls during testing
        with patch('requests.Session.request') as mock_request, \
             patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post, \
             patch('requests.put') as mock_put, \
             patch('requests.delete') as mock_delete:
            
            # Configure default mock responses
            from unittest.mock import Mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True, "scenarios": []}
            mock_response.text = '{"success": true}'
            mock_response.raise_for_status.return_value = None
            
            # Set all HTTP methods to return the mock response
            mock_request.return_value = mock_response
            mock_get.return_value = mock_response
            mock_post.return_value = mock_response
            mock_put.return_value = mock_response
            mock_delete.return_value = mock_response
            
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return True


def generate_coverage_report():
    """Generate and display coverage report."""
    print("\n📈 Generating coverage report...")
    
    # Generate text report
    cmd = [sys.executable, '-m', 'coverage', 'report', '--show-missing']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n📋 Coverage Report:")
        print("-" * 40)
        print(result.stdout)
        
        # Extract overall coverage percentage
        lines = result.stdout.strip().split('\n')
        total_line = [line for line in lines if line.startswith('TOTAL')]
        if total_line:
            coverage_info = total_line[0].split()
            if len(coverage_info) >= 4:
                coverage_percent = coverage_info[3]
                print(f"🎯 Overall Coverage: {coverage_percent}")
                
                # Determine coverage quality
                try:
                    coverage_num = float(coverage_percent.rstrip('%'))
                    if coverage_num >= 95:
                        print("🏆 Excellent coverage! (≥95%)")
                    elif coverage_num >= 85:
                        print("🟢 Good coverage! (≥85%)")
                    elif coverage_num >= 70:
                        print("🟡 Acceptable coverage (≥70%)")
                    else:
                        print("🔴 Coverage needs improvement (<70%)")
                except ValueError:
                    pass
    else:
        print("❌ Failed to generate coverage report")
        print("STDERR:", result.stderr)
        return False
    
    # Generate HTML report
    html_cmd = [sys.executable, '-m', 'coverage', 'html']
    html_result = subprocess.run(html_cmd, capture_output=True, text=True)
    
    if html_result.returncode == 0:
        print("📄 HTML coverage report generated in 'htmlcov/' directory")
        print("   Open htmlcov/index.html in your browser to view detailed coverage")
    else:
        print("⚠️  Failed to generate HTML coverage report")
    
    return True


def main():
    """Main test runner function."""
    print("🚀 Make.com Blueprint Creator - Test Suite Runner")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Discover test files
    test_files = discover_test_files()
    print(f"✅ Found {len(test_files)} test files: {', '.join(test_files)}")
    
    print("🧪 Running Make.com Blueprint Creator Test Suite")
    print("=" * 60)
    
    # Run tests with coverage
    if not run_tests_with_coverage():
        print("\n❌ Test execution failed!")
        sys.exit(1)
    
    # Generate coverage report
    if not generate_coverage_report():
        print("\n⚠️  Coverage report generation failed!")
        sys.exit(1)
    
    print("\n🎉 Test suite completed successfully!")


if __name__ == '__main__':
    main() 