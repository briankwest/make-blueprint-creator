#!/usr/bin/env python3
"""
Setup script for Make.com Blueprint Creator

This package provides programmatic access to Make.com's API for creating,
managing, and deploying automation scenarios (blueprints).

Author: AI Assistant
Date: 2025-01-27
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    """Read README.md for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Make.com Blueprint Creator - Programmatic automation scenario management"

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.28.0', 'python-dotenv>=0.19.0']

setup(
    name="make-blueprint-creator",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@cursor.com",
    description="Programmatic Make.com automation scenario creator and manager",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/briankwest/make-blueprint-creator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'coverage>=7.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
            'safety>=2.0.0',
            'bandit>=1.7.0',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'coverage>=7.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'make-blueprint=make_blueprint_creator.cli.main:main',
            'make-examples=make_blueprint_creator.cli.examples:main',
            'make-team-info=make_blueprint_creator.cli.team_info:main',
            'make-google-calendar-swaig=make_blueprint_creator.cli.google_calendar_swaig:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': [
            'blueprints/*.json',
            'env.example',
            '*.md',
        ],
    },
    keywords=[
        'make.com',
        'automation',
        'workflow',
        'blueprint',
        'scenario',
        'api',
        'integration',
        'no-code',
        'low-code'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/briankwest/make-blueprint-creator/issues',
        'Source': 'https://github.com/briankwest/make-blueprint-creator',
        'Documentation': 'https://github.com/briankwest/make-blueprint-creator#readme',
    },
) 