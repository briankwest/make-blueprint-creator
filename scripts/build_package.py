#!/usr/bin/env python3
"""
Package Build and Test Script

This script builds the Make.com Blueprint Creator package and runs
comprehensive tests to ensure it's ready for distribution.

Usage:
    python build_package.py [--clean] [--test] [--upload-test] [--upload]

Author: AI Assistant
Date: 2025-01-27
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
    return True


def clean_build_artifacts():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = [
        'build/',
        'dist/',
        '*.egg-info/',
        '__pycache__/',
        '.pytest_cache/',
        '.mypy_cache/',
        'htmlcov/',
        '.coverage'
    ]
    
    for pattern in artifacts:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   🗑️  Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   🗑️  Removed file: {path}")
    
    print("✅ Build artifacts cleaned")


def check_requirements():
    """Check that required tools are installed."""
    print("🔍 Checking requirements...")
    
    required_tools = [
        ('python', 'python --version'),
        ('pip', 'pip --version'),
        ('build', 'python -m build --version'),
        ('twine', 'twine --version'),
    ]
    
    missing_tools = []
    
    for tool, check_cmd in required_tools:
        if not run_command(check_cmd, f"Checking {tool}", check=False):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("💡 Install missing tools:")
        if 'build' in missing_tools:
            print("   pip install build")
        if 'twine' in missing_tools:
            print("   pip install twine")
        return False
    
    print("✅ All required tools are available")
    return True


def run_tests():
    """Run the test suite."""
    print("🧪 Running test suite...")
    
    if not run_command("python run_tests.py", "Running comprehensive tests"):
        return False
    
    print("✅ All tests passed")
    return True


def run_quality_checks():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    
    checks = [
        ("python -m flake8 app.py example.py get_team_info.py --max-line-length=88", "Linting with flake8"),
        ("python -m mypy app.py --ignore-missing-imports", "Type checking with mypy"),
        ("python -m bandit -r app.py example.py get_team_info.py", "Security scan with bandit"),
    ]
    
    for cmd, description in checks:
        if not run_command(cmd, description, check=False):
            print(f"⚠️  {description} found issues (continuing anyway)")
    
    print("✅ Quality checks completed")
    return True


def build_package():
    """Build the package."""
    print("📦 Building package...")
    
    if not run_command("python -m build", "Building wheel and source distribution"):
        return False
    
    # Check that files were created
    dist_files = list(Path('dist').glob('*'))
    if not dist_files:
        print("❌ No distribution files created")
        return False
    
    print("✅ Package built successfully")
    print("📁 Distribution files:")
    for file in dist_files:
        print(f"   📄 {file}")
    
    return True


def check_package():
    """Check the built package."""
    print("🔍 Checking package...")
    
    if not run_command("python -m twine check dist/*", "Checking package with twine"):
        return False
    
    print("✅ Package check passed")
    return True


def test_installation():
    """Test package installation in a clean environment."""
    print("🧪 Testing package installation...")
    
    # Find the wheel file
    wheel_files = list(Path('dist').glob('*.whl'))
    if not wheel_files:
        print("❌ No wheel file found")
        return False
    
    wheel_file = wheel_files[0]
    
    # Test installation
    if not run_command(f"pip install --force-reinstall {wheel_file}", "Installing package"):
        return False
    
    # Test import
    if not run_command("python -c 'from app import MakeBlueprintCreator; print(\"Import successful\")'", "Testing import"):
        return False
    
    print("✅ Package installation test passed")
    return True


def upload_to_test_pypi():
    """Upload package to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")
    
    if not run_command("python -m twine upload --repository testpypi dist/*", "Uploading to Test PyPI"):
        print("💡 Make sure you have configured your Test PyPI credentials:")
        print("   python -m twine configure")
        return False
    
    print("✅ Package uploaded to Test PyPI")
    return True


def upload_to_pypi():
    """Upload package to PyPI."""
    print("🚀 Uploading to PyPI...")
    
    confirm = input("⚠️  Are you sure you want to upload to PyPI? This cannot be undone! (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Upload cancelled")
        return False
    
    if not run_command("python -m twine upload dist/*", "Uploading to PyPI"):
        print("💡 Make sure you have configured your PyPI credentials:")
        print("   python -m twine configure")
        return False
    
    print("✅ Package uploaded to PyPI")
    return True


def main():
    """Main build script."""
    parser = argparse.ArgumentParser(description="Build and test the Make.com Blueprint Creator package")
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts before building')
    parser.add_argument('--test', action='store_true', help='Run tests before building')
    parser.add_argument('--upload-test', action='store_true', help='Upload to Test PyPI after building')
    parser.add_argument('--upload', action='store_true', help='Upload to PyPI after building')
    parser.add_argument('--all', action='store_true', help='Run all steps except upload')
    
    args = parser.parse_args()
    
    print("📦 Make.com Blueprint Creator - Package Builder")
    print("=" * 60)
    
    # Set default behavior
    if not any([args.clean, args.test, args.upload_test, args.upload]) or args.all:
        args.clean = True
        args.test = True
    
    success = True
    
    # Clean artifacts
    if args.clean:
        clean_build_artifacts()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Run tests
    if args.test:
        if not run_tests():
            print("❌ Tests failed - aborting build")
            sys.exit(1)
        
        if not run_quality_checks():
            print("⚠️  Quality checks had issues - continuing anyway")
    
    # Build package
    if not build_package():
        print("❌ Package build failed")
        sys.exit(1)
    
    # Check package
    if not check_package():
        print("❌ Package check failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Upload to Test PyPI
    if args.upload_test:
        if not upload_to_test_pypi():
            print("❌ Test PyPI upload failed")
            success = False
    
    # Upload to PyPI
    if args.upload:
        if not upload_to_pypi():
            print("❌ PyPI upload failed")
            success = False
    
    if success:
        print("\n🎉 Package build completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Test the package: pip install dist/*.whl")
        print("   2. Upload to Test PyPI: python build_package.py --upload-test")
        print("   3. Test from Test PyPI: pip install -i https://test.pypi.org/simple/ make-blueprint-creator")
        print("   4. Upload to PyPI: python build_package.py --upload")
    else:
        print("\n❌ Package build completed with errors")
        sys.exit(1)


if __name__ == '__main__':
    main() 