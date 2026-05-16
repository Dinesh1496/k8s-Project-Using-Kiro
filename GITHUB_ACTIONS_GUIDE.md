# GitHub Actions Guide

## Current Setup

Your project already has GitHub Actions configured in `.github/workflows/ci.yml`.

### What It Does

✅ **Automatic Testing** on every push and pull request
- Runs on: `main`, `develop` branches
- Python 3.12 setup
- Dependency installation
- Linting with flake8
- Unit tests with pytest
- Coverage reporting

### How to Use It

#### 1. Push to GitHub

```powershell
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Flask CI/CD demo"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR-USERNAME/flask-cicd-demo.git
git branch -M main
git push -u origin main
```

#### 2. Watch the Workflow Run

1. Go to your GitHub repo
2. Click **Actions** tab
3. See the workflow running automatically
4. Click on the workflow run to see details

#### 3. View Results

- ✅ Green checkmark = All tests passed
- ❌ Red X = Tests failed
- 📊 Coverage report uploaded to Codecov (optional)

---

## Comparison: GitHub Actions vs Jenkins

| Feature | GitHub Actions | Jenkins |
|---------|---------------|---------|
| **Setup** | ✅ Already configured | ⬜ Requires server setup |
| **Trigger** | ✅ Automatic on push/PR | ✅ Webhook or manual |
| **Testing** | ✅ Lint + pytest | ✅ Lint + pytest |
| **Coverage** | ✅ Codecov upload | ✅ HTML report |
| **Docker Build** | ❌ Not included | ✅ Multi-stage build |
| **Security Scan** | ❌ Not included | ✅ Trivy CVE scan |
| **SonarQube** | ❌ Not included | ✅ Static analysis |
| **Docker Push** | ❌ Not included | ✅ To Docker Hub |
| **K8s Deploy** | ❌ Not included | ✅ Rolling update |
| **Cost** | ✅ Free (2000 min/month) | ⬜ Self-hosted or paid |
| **Best For** | Quick validation | Production deployment |

---

## Enhanced GitHub Actions (Optional)

Want GitHub Actions to do more? Here are three enhanced workflows:

### Option A: Add Docker Build

Create `.github/workflows/docker.yml`:

```yaml
name: Docker Build & Push

on:
  push:
    branches: [ "main" ]
    tags: [ 'v*' ]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/flask-cicd-demo:latest
            ${{ secrets.DOCKER_USERNAME }}/flask-cicd-demo:${{ github.sha }}
```

**Setup**:
1. Go to GitHub repo → Settings → Secrets → Actions
2. Add `DOCKER_USERNAME` (your Docker Hub username)
3. Add `DOCKER_PASSWORD` (your Docker Hub password/token)

### Option B: Add Security Scanning

Create `.github/workflows/security.yml`:

```yaml
name: Security Scan

on:
  push:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t flask-cicd-demo:${{ github.sha }} .
      
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: flask-cicd-demo:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

### Option C: Full CI/CD with Kubernetes Deploy

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [ "main" ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest tests/ -v
      
      - name: Build Docker image
        run: docker build -t ${{ secrets.DOCKER_USERNAME }}/flask-cicd-demo:${{ github.sha }} .
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Push Docker image
        run: docker push ${{ secrets.DOCKER_USERNAME }}/flask-cicd-demo:${{ github.sha }}
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Configure kubeconfig
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/namespace.yaml
          kubectl apply -f k8s/configmap.yaml
          kubectl apply -f k8s/secret.yaml
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml
          kubectl apply -f k8s/ingress.yaml
          kubectl apply -f k8s/hpa.yaml
          kubectl set image deployment/flask-app flask-app=${{ secrets.DOCKER_USERNAME }}/flask-cicd-demo:${{ github.sha }} -n flask-app
      
      - name: Verify deployment
        run: kubectl rollout status deployment/flask-app -n flask-app --timeout=120s
```

**Setup**:
1. Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets
2. Add `KUBECONFIG` secret (base64 encoded):
   ```powershell
   $kubeconfig = Get-Content ~/.kube/config -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($kubeconfig)
   $base64 = [Convert]::ToBase64String($bytes)
   Write-Output $base64
   # Copy this and add as KUBECONFIG secret
   ```

---

## Current Workflow Breakdown

### `.github/workflows/ci.yml`

```yaml
name: CI - Lint & Test

on:
  push:
    branches: [ "main", "develop" ]  # Triggers on push to these branches
  pull_request:
    branches: [ "main" ]             # Triggers on PR to main

jobs:
  test:
    runs-on: ubuntu-latest           # Uses GitHub-hosted Ubuntu runner
    
    steps:
      - uses: actions/checkout@v4    # Checkout code
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"     # Install Python 3.12
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: Lint with flake8
        run: flake8 app.py --max-line-length=120
      
      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml         # Upload to Codecov (optional)
```

---

## Workflow Status Badge

Add this to your README.md to show build status:

```markdown
![CI Status](https://github.com/YOUR-USERNAME/flask-cicd-demo/workflows/CI%20-%20Lint%20%26%20Test/badge.svg)
```

Result: ![CI Status](https://github.com/YOUR-USERNAME/flask-cicd-demo/workflows/CI%20-%20Lint%20%26%20Test/badge.svg)

---

## GitHub Actions vs Jenkins: When to Use What

### Use GitHub Actions When:
- ✅ You want automatic testing on every push/PR
- ✅ You're working on an open-source project
- ✅ You want quick feedback without infrastructure
- ✅ You need basic CI (test, lint, build)
- ✅ You want free CI/CD (2000 minutes/month free)

### Use Jenkins When:
- ✅ You need full control over the pipeline
- ✅ You're deploying to production
- ✅ You need custom stages (SonarQube, Trivy, etc.)
- ✅ You have complex deployment requirements
- ✅ You need to integrate with enterprise tools

### Use Both When:
- ✅ GitHub Actions for PR validation (fast feedback)
- ✅ Jenkins for production deployment (full pipeline)

**Example workflow**:
1. Developer creates PR
2. GitHub Actions runs tests (2 minutes)
3. If tests pass, merge to main
4. Jenkins webhook triggers full pipeline (5 minutes)
5. Jenkins deploys to Kubernetes

---

## Viewing GitHub Actions Results

### On GitHub
1. Go to your repo
2. Click **Actions** tab
3. See all workflow runs
4. Click on a run to see:
   - Job status
   - Step-by-step logs
   - Test results
   - Coverage reports

### In Pull Requests
- ✅ Green checkmark = All checks passed
- ❌ Red X = Some checks failed
- 🟡 Yellow dot = Checks running
- Click "Details" to see logs

### Notifications
- Email notifications on failure (configurable)
- Slack integration available
- GitHub mobile app notifications

---

## Troubleshooting GitHub Actions

### Workflow Not Running?

**Check**:
1. Workflow file is in `.github/workflows/` directory
2. File has `.yml` or `.yaml` extension
3. YAML syntax is valid (use yamllint)
4. Branch name matches trigger condition

### Tests Failing?

**Check**:
1. Click on failed workflow run
2. Expand failed step
3. Read error message
4. Fix locally and push again

### Secrets Not Working?

**Check**:
1. Secrets are added in repo Settings → Secrets → Actions
2. Secret names match exactly (case-sensitive)
3. Secrets are available in the workflow scope

---

## Cost & Limits

### GitHub Actions Free Tier
- **Public repos**: Unlimited minutes
- **Private repos**: 2000 minutes/month free
- **Storage**: 500 MB free
- **Concurrent jobs**: 20 for free accounts

### Pricing (if you exceed free tier)
- $0.008/minute for Linux runners
- $0.016/minute for Windows runners
- $0.08/minute for macOS runners

**This project uses ~2-3 minutes per run**, so you can run ~600-1000 builds/month for free.

---

## Best Practices

### 1. Cache Dependencies
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements-dev.txt') }}
```

### 2. Matrix Testing
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

### 3. Conditional Steps
```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: ./deploy.sh
```

### 4. Reusable Workflows
Create `.github/workflows/reusable-test.yml` and call it from other workflows.

---

## Summary

### What You Have Now
✅ GitHub Actions configured for automatic testing
✅ Runs on every push to `main` or `develop`
✅ Linting with flake8
✅ Testing with pytest
✅ Coverage reporting

### What You Can Add (Optional)
⬜ Docker build and push
⬜ Security scanning with Trivy
⬜ Kubernetes deployment
⬜ Multi-environment deployments
⬜ Slack notifications

### Recommendation
- **Keep current setup** for quick PR validation
- **Add Jenkins** for production deployments (see JENKINS_SETUP_GUIDE.md)
- **Use both** for best of both worlds

---

## Quick Start

```powershell
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/flask-cicd-demo.git
git push -u origin main

# 2. Watch Actions tab on GitHub
# Workflow runs automatically!

# 3. Make a change and push
echo "# Test" >> README.md
git add README.md
git commit -m "Test GitHub Actions"
git push

# 4. See the workflow run again
```

---

**GitHub Actions is ready to use as soon as you push to GitHub!** 🚀
