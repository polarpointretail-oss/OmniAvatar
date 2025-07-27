# GitHub Repository Setup Guide

This guide will help you configure your GitHub repository for automated deployment of the OmniAvatar project.

## Required Configurations

### 1. Repository Secrets

Go to your repository: `https://github.com/polarpointretail-oss/OmniAvatar`

1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `PYPI_API_TOKEN` | PyPI API token for package deployment | [Create at PyPI](https://pypi.org/manage/account/token/) |

#### Creating PyPI API Token:
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Set scope to "Entire account" or specific to your project
4. Copy the token (starts with `pypi-`)
5. Add it as `PYPI_API_TOKEN` secret in GitHub

### 2. GitHub Pages Configuration

1. Go to **Settings** → **Pages**
2. Under **Source**, select "GitHub Actions"
3. Save the settings

This will enable automatic documentation deployment to:
`https://polarpointretail-oss.github.io/OmniAvatar`

### 3. Repository Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, ensure:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

### 4. Branch Protection (Optional but Recommended)

1. Go to **Settings** → **Branches**
2. Click **Add rule** for your main branch
3. Configure:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

## Verification Steps

### 1. Test Workflow Trigger

After setup, push a change to trigger the workflow:

```bash
# In your local repository
git add .
git commit -m "Test deployment workflow"
git push origin main
```

### 2. Monitor Workflow Execution

1. Go to **Actions** tab in your repository
2. You should see "Deploy OmniAvatar" workflow running
3. Click on the workflow to see detailed logs

### 3. Verify Outputs

After successful deployment:

- **Documentation**: Check `https://polarpointretail-oss.github.io/OmniAvatar`
- **Artifacts**: Available in the workflow run under "Artifacts"
- **Package**: For tagged releases, check PyPI

## Testing Release Process

### Create a Test Release

```bash
# Create and push a test tag
git tag v0.1.0-test
git push origin v0.1.0-test
```

This should trigger:
- Full test suite
- Package building
- GitHub release creation
- PyPI deployment (if token configured)

### Verify Release

1. **GitHub Release**: Check releases page
2. **PyPI Package**: Visit `https://pypi.org/project/omni-avatar/`
3. **Documentation**: Should be updated automatically

## Troubleshooting

### Common Setup Issues

1. **Workflow fails with permissions error**:
   - Check repository permissions in Settings → Actions
   - Ensure secrets are properly set

2. **PyPI deployment fails**:
   - Verify `PYPI_API_TOKEN` secret is correct
   - Check if package name is available on PyPI
   - Ensure version is incremented for new releases

3. **Documentation deployment fails**:
   - Verify GitHub Pages is enabled
   - Check workflow logs for specific errors
   - Ensure all markdown files are valid

4. **Secrets not accessible**:
   - Repository secrets are case-sensitive
   - Check secret names match exactly
   - Verify you have admin access to repository

### Getting Help

If you encounter issues:

1. Check the **Actions** tab for detailed error logs
2. Review the workflow file `.github/workflows/deploy.yml`
3. Test locally using `./deploy.sh --test`
4. Verify all prerequisites are met

## Security Notes

- Never commit secrets to the repository
- Rotate PyPI tokens regularly
- Review workflow permissions periodically
- Monitor deployment logs for suspicious activity

## Next Steps

After setup:

1. Test the deployment with a small change
2. Create your first official release with a proper tag
3. Monitor the automated processes
4. Update documentation as needed

Your deployment pipeline is now ready! 🚀