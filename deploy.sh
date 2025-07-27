#!/bin/bash

# OmniAvatar Deployment Script
# This script handles local deployment and can be used as a reference for CI/CD

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/polarpointretail-oss/OmniAvatar"
PYTHON_VERSION="3.9"
PROJECT_NAME="omni-avatar"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    log_success "System requirements met"
}

setup_environment() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install PyTorch (CPU version for deployment)
    pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cpu
    
    # Install project dependencies
    pip install -r requirements.txt
    
    # Install build tools
    pip install build wheel setuptools twine
    
    log_success "Environment setup complete"
}

run_tests() {
    log_info "Running tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install test dependencies
    pip install flake8 pytest
    
    # Run linting
    log_info "Running code linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || log_warning "Linting issues found"
    
    # Test imports
    log_info "Testing imports..."
    python -c "import OmniAvatar; print('OmniAvatar import successful')" || {
        log_error "Import test failed"
        exit 1
    }
    
    log_success "Tests completed"
}

build_package() {
    log_info "Building package..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Create setup.py if it doesn't exist
    if [ ! -f setup.py ]; then
        log_info "Creating setup.py..."
        cat > setup.py << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="omni-avatar",
    version="0.1.0",
    author="OmniAvatar Team",
    description="Efficient Audio-Driven Avatar Video Generation with Adaptive Body Animation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/polarpointretail-oss/OmniAvatar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "omni-avatar=scripts.inference:main",
        ],
    },
)
EOF
    fi
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/
    
    # Build the package
    python -m build
    
    log_success "Package built successfully"
}

create_release() {
    log_info "Creating release archive..."
    
    # Get current git commit hash
    COMMIT_HASH=$(git rev-parse --short HEAD)
    
    # Create release directory
    mkdir -p release
    
    # Create archive
    tar -czf release/omni-avatar-${COMMIT_HASH}.tar.gz \
        --exclude='.git' \
        --exclude='release' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='dist' \
        --exclude='build' \
        --exclude='*.egg-info' \
        .
    
    log_success "Release archive created: release/omni-avatar-${COMMIT_HASH}.tar.gz"
}

deploy_to_pypi() {
    log_info "Deploying to PyPI..."
    
    # Check if PYPI_API_TOKEN is set
    if [ -z "$PYPI_API_TOKEN" ]; then
        log_warning "PYPI_API_TOKEN not set. Skipping PyPI deployment."
        log_info "To deploy to PyPI, set PYPI_API_TOKEN environment variable and run:"
        log_info "  export PYPI_API_TOKEN=your_token_here"
        log_info "  ./deploy.sh --pypi"
        return
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upload to PyPI
    python -m twine upload dist/* --username __token__ --password "$PYPI_API_TOKEN" --skip-existing
    
    log_success "Package deployed to PyPI"
}

git_operations() {
    log_info "Performing git operations..."
    
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "There are uncommitted changes. Consider committing them first."
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "Current branch: $CURRENT_BRANCH"
    
    # Push to remote
    log_info "Pushing to remote repository..."
    git push origin "$CURRENT_BRANCH"
    
    log_success "Git operations completed"
}

show_help() {
    echo "OmniAvatar Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --help              Show this help message"
    echo "  --check             Only check requirements"
    echo "  --setup             Setup environment"
    echo "  --test              Run tests only"
    echo "  --build             Build package only"
    echo "  --release           Create release archive only"
    echo "  --pypi              Deploy to PyPI (requires PYPI_API_TOKEN)"
    echo "  --git               Perform git operations only"
    echo "  --full              Full deployment (default)"
    echo ""
    echo "Environment Variables:"
    echo "  PYPI_API_TOKEN      PyPI API token for package deployment"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full deployment"
    echo "  $0 --build          # Build package only"
    echo "  PYPI_API_TOKEN=xxx $0 --pypi  # Deploy to PyPI"
}

# Main deployment function
main() {
    log_info "Starting OmniAvatar deployment..."
    
    case "${1:-full}" in
        --help)
            show_help
            exit 0
            ;;
        --check)
            check_requirements
            ;;
        --setup)
            check_requirements
            setup_environment
            ;;
        --test)
            run_tests
            ;;
        --build)
            check_requirements
            setup_environment
            build_package
            ;;
        --release)
            create_release
            ;;
        --pypi)
            check_requirements
            setup_environment
            build_package
            deploy_to_pypi
            ;;
        --git)
            git_operations
            ;;
        --full|full)
            check_requirements
            setup_environment
            run_tests
            build_package
            create_release
            git_operations
            log_success "Full deployment completed successfully!"
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"