# Installation Guide: Make.com Blueprint Creator

This guide covers all installation methods for the Make.com Blueprint Creator package.

## 📦 Installation Methods

### Method 1: Install from PyPI (Recommended)

Once published to PyPI, you can install the package using pip:

```bash
# Install the latest stable version
pip install make-blueprint-creator

# Install with development dependencies
pip install make-blueprint-creator[dev]

# Install with test dependencies only
pip install make-blueprint-creator[test]
```

### Method 2: Install from Source (Current)

Since the package isn't published to PyPI yet, install from source:

```bash
# Clone the repository
git clone https://github.com/briankwest/make-blueprint-creator.git
cd make-blueprint-creator

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Method 3: Install from Local Directory

If you have the source code locally:

```bash
# Navigate to the package directory
cd /path/to/make-blueprint-creator

# Install the package
pip install .

# Or install in editable mode for development
pip install -e .
```

### Method 4: Install from GitHub

Install directly from GitHub:

```bash
# Install from main branch
pip install git+https://github.com/briankwest/make-blueprint-creator.git

# Install from specific branch or tag
pip install git+https://github.com/briankwest/make-blueprint-creator.git@v1.0.0
```

## 🔧 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB RAM
- **Network**: Internet connection for Make.com API access

### Python Dependencies

#### Core Dependencies (automatically installed)
- `requests>=2.28.0` - HTTP library for API calls
- `python-dotenv>=0.19.0` - Environment variable management

#### Development Dependencies (optional)
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage plugin for pytest
- `coverage>=7.0.0` - Code coverage measurement
- `black>=22.0.0` - Code formatter
- `flake8>=5.0.0` - Code linter
- `mypy>=1.0.0` - Static type checker
- `safety>=2.0.0` - Security vulnerability scanner
- `bandit>=1.7.0` - Security linter

## 🚀 Quick Start

### 1. Install the Package

```bash
pip install make-blueprint-creator
```

### 2. Set Up Environment Variables

Create a `.env` file in your project directory:

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your Make.com credentials
MAKE_API_TOKEN=your_make_api_token_here
MAKE_TEAM_ID=your_team_id_here
MAKE_API_BASE_URL=https://us2.make.com/api/v2
```

### 3. Basic Usage

```python
from make_blueprint_creator import MakeBlueprintCreator, MakeConfig

# Configure the client
config = MakeConfig(
    api_token="your_api_token",
    team_id=123456,
    base_url="https://us2.make.com/api/v2"
)

# Create the blueprint creator
creator = MakeBlueprintCreator(config)

# List existing scenarios
scenarios = creator.list_scenarios()
print(f"Found {len(scenarios)} scenarios")

# Create a simple blueprint
blueprint = creator.create_simple_blueprint(
    name="My First Automation",
    description="A simple webhook to email scenario"
)

# Create a scenario from the blueprint
scenario = creator.create_scenario(blueprint, "Test Scenario")
print(f"Created scenario: {scenario['name']} (ID: {scenario['id']})")
```

## 🛠️ Development Installation

For contributors and developers:

### 1. Clone and Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/briankwest/make-blueprint-creator.git
cd make-blueprint-creator

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e .[dev]
```

### 2. Run Tests

```bash
# Run the test suite
cd tests && python run_tests.py

# Or use pytest directly
pytest

# Run with coverage
pytest --cov=src/make_blueprint_creator
```

### 3. Code Quality Checks

```bash
# Format code with black
black .

# Lint code with flake8
flake8 .

# Type check with mypy
mypy src/make_blueprint_creator/

# Security scan
bandit -r .
safety check
```

## 📱 Command Line Tools

After installation, you'll have access to these command-line tools:

### `make-blueprint`
Main blueprint creator tool:
```bash
make-blueprint --help
```

### `make-examples`
Run example scenarios:
```bash
make-examples
```

### `make-team-info`
Get team and organization information:
```bash
make-team-info
```

## 🔐 Authentication Setup

### Getting Your Make.com API Token

1. **Log in to Make.com**
   - Go to [make.com](https://make.com)
   - Sign in to your account

2. **Navigate to API Settings**
   - Go to your profile settings
   - Find the "API" or "Tokens" section

3. **Generate API Token**
   - Create a new API token
   - Copy the token (keep it secure!)

4. **Find Your Team/Organization ID**
   - Use the `make-team-info` command after installation
   - Or check your Make.com account settings

### Environment Configuration

Create a `.env` file in your project:

```bash
# Required: Your Make.com API token
MAKE_API_TOKEN=your_actual_api_token_here

# Required: Either team_id OR organization_id
MAKE_TEAM_ID=123456
# OR
MAKE_ORGANIZATION_ID=789012

# Optional: API base URL (defaults to US region)
MAKE_API_BASE_URL=https://us2.make.com/api/v2

# For EU region, use:
# MAKE_API_BASE_URL=https://eu1.make.com/api/v2
```

## 🐛 Troubleshooting

### Common Installation Issues

#### Issue: `pip install` fails with permission error
**Solution**: Use virtual environment or `--user` flag:
```bash
pip install --user make-blueprint-creator
```

#### Issue: Python version compatibility
**Solution**: Ensure Python 3.8+ is installed:
```bash
python --version
# Should show 3.8.0 or higher
```

#### Issue: Missing dependencies
**Solution**: Update pip and try again:
```bash
pip install --upgrade pip
pip install make-blueprint-creator
```

### Common Usage Issues

#### Issue: "Invalid API token" error
**Solution**: 
1. Verify your API token is correct
2. Check that the token has proper permissions
3. Ensure you're using the correct API base URL for your region

#### Issue: "Team not found" error
**Solution**:
1. Use `make-team-info` to find your correct team/organization ID
2. Verify you have access to the specified team

#### Issue: Rate limiting errors
**Solution**:
1. Add delays between API calls
2. Use the built-in retry mechanisms
3. Consider upgrading your Make.com plan for higher rate limits

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**: Check out the [README.md](../README.md) for detailed usage examples
2. **Run Examples**: Try the example scripts to understand the capabilities
3. **Explore the API**: Review the [API documentation](https://developers.make.com/api-documentation)
4. **Join the Community**: Connect with other users and contributors

## 🆘 Getting Help

If you encounter issues:

1. **Check the Documentation**: Review all `.md` files in the repository
2. **Search Issues**: Look through existing GitHub issues
3. **Create an Issue**: Report bugs or request features on GitHub
4. **Security Issues**: Report security vulnerabilities privately

## 📄 License

This package is licensed under the MIT License. See [LICENSE](../LICENSE) for details. 