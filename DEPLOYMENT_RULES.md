# OmniAvatar Deployment Rules

This document outlines the deployment process for the OmniAvatar project from Cursor to GitHub repository: `https://github.com/polarpointretail-oss/OmniAvatar`

## Overview

The deployment system is designed to:
- Automatically test and validate code changes
- Build and package the Python application
- Deploy to PyPI for easy installation
- Generate and deploy documentation
- Create GitHub releases for tagged versions

## Deployment Methods

### 1. Automated Deployment (Recommended)

The project uses GitHub Actions for automated CI/CD. The workflow is triggered by:

- **Push to main/master branch**: Runs tests, builds package, deploys docs
- **Pull requests**: Runs tests only
- **Git tags (v*)**: Full deployment including PyPI release
- **Manual trigger**: Can be triggered manually from GitHub Actions tab

#### Workflow Features:
- ✅ Automated testing with Python 3.9
- ✅ Code linting with flake8
- ✅ Package building and artifact storage
- ✅ PyPI deployment for tagged releases
- ✅ Documentation generation and GitHub Pages deployment
- ✅ GitHub release creation for tags

### 2. Manual Deployment

Use the provided `deploy.sh` script for local deployments:

```bash
# Make script executable
chmod +x deploy.sh

# Full deployment
./deploy.sh

# Specific operations
./deploy.sh --test      # Run tests only
./deploy.sh --build     # Build package only
./deploy.sh --pypi      # Deploy to PyPI
```

## Prerequisites

### GitHub Repository Setup

1. **Secrets Configuration** (GitHub Settings → Secrets and variables → Actions):
   ```
   PYPI_API_TOKEN     # PyPI API token for package deployment
   ```

2. **GitHub Pages** (Repository Settings → Pages):
   - Source: GitHub Actions
   - This enables automatic documentation deployment

3. **Repository Permissions**:
   - Ensure Actions have write permissions for releases and pages

### Local Development Setup

1. **Required Tools**:
   - Python 3.9 or higher
   - Git
   - pip (latest version)

2. **Environment Variables** (for PyPI deployment):
   ```bash
   export PYPI_API_TOKEN="your_pypi_token_here"
   ```

## Deployment Workflows

### For Regular Development

1. **Code Changes**:
   ```bash
   # Make your changes in Cursor
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Automatic Process**:
   - GitHub Actions runs tests
   - Builds package if tests pass
   - Deploys documentation to GitHub Pages
   - Stores build artifacts

### For Releases

1. **Create and Push Tag**:
   ```bash
   # Create a version tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Automatic Process**:
   - Runs all tests
   - Builds Python package
   - Creates GitHub release
   - Deploys to PyPI (if token configured)
   - Updates documentation

### For Hotfixes

1. **Direct Branch Push**:
   ```bash
   git checkout -b hotfix/issue-name
   # Make changes
   git commit -m "Fix: description"
   git push origin hotfix/issue-name
   # Create PR or merge to main
   ```

## Configuration Files

### GitHub Actions Workflow
- **File**: `.github/workflows/deploy.yml`
- **Purpose**: Automated CI/CD pipeline
- **Triggers**: Push, PR, tags, manual

### Deployment Script
- **File**: `deploy.sh`
- **Purpose**: Local deployment automation
- **Usage**: `./deploy.sh [--option]`

### Package Configuration
- **File**: `setup.py` (auto-generated)
- **Purpose**: Python package metadata
- **Content**: Project info, dependencies, entry points

### Documentation Configuration
- **File**: `mkdocs.yml` (auto-generated)
- **Purpose**: Documentation site configuration
- **Output**: GitHub Pages site

## Directory Structure After Deployment

```
OmniAvatar/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD workflow
├── OmniAvatar/                 # Main package
├── scripts/                    # Deployment scripts
├── docs/                       # Documentation source
├── dist/                       # Built packages
├── release/                    # Release archives
├── deploy.sh                   # Deployment script
├── setup.py                    # Package configuration
├── mkdocs.yml                  # Documentation config
└── DEPLOYMENT_RULES.md         # This file
```

## Deployment Checklist

### Before Deployment
- [ ] All tests pass locally
- [ ] Code is properly committed
- [ ] Version numbers updated (if needed)
- [ ] Dependencies in `requirements.txt` are current
- [ ] Documentation is updated

### For Releases
- [ ] CHANGELOG updated
- [ ] Version tag follows semantic versioning
- [ ] Release notes prepared
- [ ] PyPI token is configured
- [ ] GitHub permissions are correct

### After Deployment
- [ ] Verify GitHub Actions completed successfully
- [ ] Check PyPI package is available
- [ ] Verify documentation updated on GitHub Pages
- [ ] Test installation: `pip install omni-avatar`

## Troubleshooting

### Common Issues

1. **Tests Fail in CI**:
   - Check Python version compatibility
   - Verify all dependencies are in `requirements.txt`
   - Check for missing imports

2. **PyPI Deployment Fails**:
   - Verify `PYPI_API_TOKEN` secret is set
   - Check if package name already exists
   - Ensure version number is incremented

3. **Documentation Build Fails**:
   - Check markdown syntax in docs
   - Verify mkdocs configuration
   - Ensure all referenced files exist

4. **Local Script Issues**:
   - Make script executable: `chmod +x deploy.sh`
   - Check Python virtual environment
   - Verify Git repository state

### Getting Help

1. **Check GitHub Actions logs** in the repository's Actions tab
2. **Review error messages** in the workflow output
3. **Verify configuration** files are properly formatted
4. **Test locally** using the deployment script

## Security Considerations

1. **Secrets Management**:
   - Never commit API tokens to the repository
   - Use GitHub Secrets for sensitive data
   - Rotate tokens regularly

2. **Code Quality**:
   - All code goes through automated testing
   - Linting enforces code standards
   - Import validation prevents broken deployments

3. **Access Control**:
   - Deployment requires write access to repository
   - PyPI deployment only on tagged releases
   - Documentation deployment only from main branch

## Monitoring and Maintenance

### Regular Tasks
- Monitor GitHub Actions for failures
- Update dependencies quarterly
- Review and update documentation
- Check PyPI package installation

### Version Management
- Use semantic versioning (vX.Y.Z)
- Tag releases consistently
- Maintain CHANGELOG
- Archive old releases

## Integration with Cursor

### Recommended Workflow in Cursor

1. **Development**:
   - Make changes in Cursor editor
   - Use integrated terminal for git operations
   - Test locally before pushing

2. **Deployment**:
   - Commit changes via Cursor's git integration
   - Push to GitHub to trigger automated deployment
   - Monitor progress in GitHub Actions

3. **Release Management**:
   - Create tags via command line or Cursor terminal
   - Push tags to trigger release deployment
   - Verify deployment success

This deployment system provides a robust, automated pipeline for maintaining and deploying the OmniAvatar project while ensuring code quality and reliability.