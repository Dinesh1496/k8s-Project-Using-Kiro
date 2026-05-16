# Jenkins CI/CD Pipeline Setup Guide

Complete guide to set up Jenkins for automated CI/CD pipeline with GitHub integration.

---

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Kubernetes cluster running (Docker Desktop)
- ✅ GitHub account
- ✅ Docker Hub account
- ⬜ Jenkins server (we'll set this up)

---

## Part 1: Install Jenkins

### Option A: Jenkins in Docker (Recommended for Testing)

```powershell
# Create Jenkins volume for persistence
docker volume create jenkins_home

# Run Jenkins with Docker and Kubernetes access
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  -v ${HOME}/.kube:/root/.kube `
  --restart unless-stopped `
  jenkins/jenkins:lts

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**Access Jenkins**: http://localhost:8080

### Option B: Jenkins on Windows (Native)

1. Download Jenkins: https://www.jenkins.io/download/
2. Install Jenkins Windows installer
3. Service runs on http://localhost:8080
4. Initial password: `C:\Program Files\Jenkins\secrets\initialAdminPassword`

---

## Part 2: Initial Jenkins Configuration

### Step 1: Unlock Jenkins

1. Open http://localhost:8080
2. Paste the initial admin password
3. Click **Continue**

### Step 2: Install Plugins

Select **Install suggested plugins**, then add these additional plugins:

**Required Plugins**:
- Pipeline
- Git
- GitHub
- Docker Pipeline
- Kubernetes CLI
- Credentials Binding
- HTML Publisher
- SonarQube Scanner (optional)

**Install via**: Manage Jenkins → Plugins → Available Plugins

### Step 3: Create Admin User

- Username: `admin`
- Password: `your-secure-password`
- Full name: `Your Name`
- Email: `your-email@example.com`

---

## Part 3: Configure Credentials

Go to: **Manage Jenkins → Credentials → System → Global credentials**

### 1. Docker Hub Credentials

- **Kind**: Username with password
- **ID**: `dockerhub-credentials`
- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub password or access token
- **Description**: Docker Hub Login

### 2. Kubeconfig File

```powershell
# Copy your kubeconfig
cat ~/.kube/config
```

- **Kind**: Secret file
- **ID**: `kubeconfig-credentials`
- **File**: Upload your `~/.kube/config` file
- **Description**: Kubernetes Config

### 3. SonarQube Token (Optional)

If using SonarQube:
- **Kind**: Secret text
- **ID**: `sonarqube-token`
- **Secret**: Your SonarQube authentication token
- **Description**: SonarQube Auth Token

---

## Part 4: Install Required Tools in Jenkins

### If using Jenkins in Docker:

```powershell
# Enter Jenkins container
docker exec -it -u root jenkins bash

# Install Docker CLI
apt-get update
apt-get install -y docker.io

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/

# Install Python and pip
apt-get install -y python3 python3-pip python3-venv

# Install Trivy (security scanner)
apt-get install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list
apt-get update
apt-get install -y trivy

# Install SonarQube Scanner (optional)
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip
mv sonar-scanner-5.0.1.3006-linux /opt/sonar-scanner
ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# Exit container
exit
```

### If using Jenkins on Windows:

Install these tools and add to PATH:
- Docker Desktop (already installed)
- kubectl (already installed)
- Python 3.12+
- Trivy: https://github.com/aquasecurity/trivy/releases
- SonarQube Scanner: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarqube-scanner/

---

## Part 5: Create Jenkins Pipeline Job

### Step 1: Create New Job

1. Click **New Item**
2. Enter name: `flask-cicd-demo`
3. Select **Pipeline**
4. Click **OK**

### Step 2: Configure Pipeline

**General**:
- ✅ GitHub project
- Project url: `https://github.com/YOUR-USERNAME/flask-cicd-demo`

**Build Triggers**:
- ✅ GitHub hook trigger for GITScm polling

**Pipeline**:
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/YOUR-USERNAME/flask-cicd-demo.git`
- **Credentials**: (add GitHub credentials if private repo)
- **Branch**: `*/main`
- **Script Path**: `Jenkinsfile`

Click **Save**

---

## Part 6: Update Jenkinsfile Configuration

Before running the pipeline, update these values in `Jenkinsfile`:

```groovy
environment {
    DOCKER_REGISTRY = "your-dockerhub-username"  // ← Change this
    SONAR_HOST      = "http://sonarqube:9000"    // ← Change if using SonarQube
}
```

**Update in your project**:

```powershell
# Edit Jenkinsfile
code Jenkinsfile

# Update DOCKER_REGISTRY to your Docker Hub username
# Save the file
```

---

## Part 7: Push Code to GitHub

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `flask-cicd-demo`
3. Visibility: Public or Private
4. Click **Create repository**

### Step 2: Push Your Code

```powershell
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Flask CI/CD demo with Kubernetes"

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/flask-cicd-demo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Part 8: Configure GitHub Webhook

### Step 1: Get Jenkins URL

If Jenkins is running locally, you need a public URL. Options:

**Option A: ngrok (for testing)**
```powershell
# Install ngrok: https://ngrok.com/download
ngrok http 8080

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Use your public Jenkins server URL**
```
https://your-jenkins-server.com
```

### Step 2: Add Webhook in GitHub

1. Go to your GitHub repo
2. **Settings → Webhooks → Add webhook**
3. **Payload URL**: `http://YOUR-JENKINS-URL/github-webhook/`
   - Example: `https://abc123.ngrok.io/github-webhook/`
4. **Content type**: `application/json`
5. **Which events**: Just the push event
6. ✅ Active
7. Click **Add webhook**

### Step 3: Test Webhook

```powershell
# Make a small change
echo "# Test webhook" >> README.md

# Commit and push
git add README.md
git commit -m "Test webhook trigger"
git push

# Jenkins should automatically start building!
```

---

## Part 9: Run the Pipeline

### Manual Trigger (First Time)

1. Go to Jenkins → `flask-cicd-demo` job
2. Click **Build Now**
3. Watch the pipeline execute through all 9 stages

### Pipeline Stages

The pipeline will execute:

1. **Clone Code** — Checkout from GitHub
2. **Install Dependencies** — Create venv, install requirements
3. **Run Tests** — pytest with coverage
4. **SonarQube Scan** — Static analysis (optional, skip if no SonarQube)
5. **Build Docker Image** — Multi-stage build
6. **Trivy Image Scan** — Security vulnerability scan
7. **Push Docker Image** — Push to Docker Hub
8. **Deploy to Kubernetes** — Apply manifests, rolling update
9. **Verify Deployment** — Check rollout status

### Expected Duration

- First run: ~5-10 minutes (downloads dependencies)
- Subsequent runs: ~3-5 minutes

---

## Part 10: Monitor Pipeline Execution

### View Console Output

1. Click on the build number (e.g., `#1`)
2. Click **Console Output**
3. Watch real-time logs

### View Test Results

After build completes:
- **Test Results**: Shows pytest results
- **Coverage Report**: HTML coverage report

### View Artifacts

- **Trivy Report**: Security scan results
- **Coverage Report**: Code coverage HTML

---

## Part 11: Verify Deployment

After pipeline succeeds:

```powershell
# Check deployment
kubectl rollout status deployment/flask-app -n flask-app

# Check pods
kubectl get pods -n flask-app

# Check the new image was deployed
kubectl describe deployment flask-app -n flask-app | Select-String "Image:"

# Test the app
Invoke-WebRequest -Uri http://localhost:8080/ -UseBasicParsing
```

---

## Troubleshooting

### Issue: Docker permission denied in Jenkins

**Solution**:
```bash
# In Jenkins container
docker exec -it -u root jenkins bash
usermod -aG docker jenkins
exit

# Restart Jenkins
docker restart jenkins
```

### Issue: kubectl not found

**Solution**: Install kubectl in Jenkins (see Part 4)

### Issue: SonarQube stage fails

**Solution**: Either:
1. Install SonarQube: `docker run -d -p 9000:9000 sonarqube:lts`
2. Or comment out the SonarQube stage in Jenkinsfile

### Issue: Trivy not found

**Solution**: Install Trivy in Jenkins (see Part 4) or comment out the stage

### Issue: GitHub webhook not triggering

**Check**:
1. Webhook shows green checkmark in GitHub
2. Jenkins job has "GitHub hook trigger" enabled
3. Jenkins is accessible from internet (use ngrok for local)
4. Payload URL ends with `/github-webhook/`

### Issue: Image pull fails in Kubernetes

**Solution**: Verify Docker Hub credentials and image name match

---

## Optional: SonarQube Setup

### Install SonarQube

```powershell
# Run SonarQube
docker run -d `
  --name sonarqube `
  -p 9000:9000 `
  sonarqube:lts

# Access: http://localhost:9000
# Default login: admin/admin
```

### Configure SonarQube

1. Login to http://localhost:9000
2. Change password
3. Create project: `flask-cicd-demo`
4. Generate token
5. Add token to Jenkins credentials as `sonarqube-token`
6. Update `SONAR_HOST` in Jenkinsfile

---

## Pipeline Architecture

```
Developer Push to GitHub
         │
         ▼
   GitHub Webhook
         │
         ▼
   Jenkins Pipeline
   ┌─────────────────────────────────────┐
   │ 1. Clone Code                       │
   │ 2. Install Dependencies             │
   │ 3. Run Tests (pytest + coverage)    │
   │ 4. SonarQube Scan (SAST)            │
   │ 5. Build Docker Image               │
   │ 6. Trivy Scan (CVE detection)       │
   │ 7. Push to Docker Hub               │
   │ 8. Deploy to Kubernetes             │
   │ 9. Verify Rollout                   │
   └─────────────────────────────────────┘
         │
         ▼
   Kubernetes Cluster
   ┌─────────────────────────────────────┐
   │ Rolling Update (zero downtime)      │
   │ 2 pods → new version                │
   │ Health checks pass                  │
   │ Traffic switched                    │
   └─────────────────────────────────────┘
```

---

## Complete CI/CD Workflow

### Development Workflow

1. **Developer makes changes locally**
   ```powershell
   # Edit code
   code app.py
   
   # Run tests locally
   pytest tests/ -v
   
   # Commit changes
   git add .
   git commit -m "Add new feature"
   ```

2. **Push to GitHub**
   ```powershell
   git push origin main
   ```

3. **Jenkins automatically triggered**
   - GitHub webhook notifies Jenkins
   - Pipeline starts immediately
   - All 9 stages execute

4. **Automated testing**
   - Unit tests run
   - Coverage report generated
   - SonarQube analyzes code quality

5. **Automated security scanning**
   - Trivy scans Docker image
   - Reports vulnerabilities
   - Fails build if critical issues found

6. **Automated deployment**
   - Image pushed to Docker Hub
   - Kubernetes deployment updated
   - Rolling update ensures zero downtime
   - Health checks verify new pods

7. **Verification**
   - Pipeline confirms rollout success
   - Pods are healthy
   - Application serving traffic

### Rollback if Needed

```powershell
# View rollout history
kubectl rollout history deployment/flask-app -n flask-app

# Rollback to previous version
kubectl rollout undo deployment/flask-app -n flask-app

# Or rollback to specific revision
kubectl rollout undo deployment/flask-app --to-revision=2 -n flask-app
```

---

## Best Practices

### 1. Branch Strategy

```
main (production)
  ├── develop (staging)
  └── feature/* (feature branches)
```

Configure Jenkins to:
- Deploy `main` → production
- Deploy `develop` → staging
- Run tests only on `feature/*`

### 2. Environment-Specific Deployments

Create multiple Jenkinsfiles:
- `Jenkinsfile` (production)
- `Jenkinsfile.staging`
- `Jenkinsfile.dev`

### 3. Secrets Management

Never commit secrets to Git:
- Use Jenkins credentials
- Use Kubernetes secrets
- Consider HashiCorp Vault
- Use AWS Secrets Manager / Azure Key Vault

### 4. Notifications

Add Slack/Email notifications to Jenkinsfile:

```groovy
post {
    success {
        slackSend(color: 'good', message: "Build ${BUILD_NUMBER} succeeded!")
    }
    failure {
        slackSend(color: 'danger', message: "Build ${BUILD_NUMBER} failed!")
    }
}
```

### 5. Quality Gates

Add quality gates in Jenkinsfile:

```groovy
stage('Quality Gate') {
    steps {
        script {
            def coverage = readFile('coverage.txt').trim().toFloat()
            if (coverage < 80) {
                error("Coverage ${coverage}% is below 80% threshold")
            }
        }
    }
}
```

---

## Resume Points

After completing this setup, you can claim:

✅ **Implemented full CI/CD pipeline** with Jenkins, GitHub webhooks, and automated deployments

✅ **Configured automated testing** with pytest, coverage reporting, and quality gates

✅ **Integrated security scanning** with Trivy for CVE detection in Docker images

✅ **Automated zero-downtime deployments** to Kubernetes with rolling updates and health checks

✅ **Implemented GitOps workflow** with automated builds triggered by Git push events

✅ **Configured multi-stage pipeline** covering build, test, scan, deploy, and verify phases

---

## Quick Reference Commands

```powershell
# Jenkins
docker logs jenkins -f                    # View Jenkins logs
docker restart jenkins                    # Restart Jenkins
docker exec -it jenkins bash              # Enter Jenkins container

# Pipeline
# Trigger manually in Jenkins UI or:
curl -X POST http://localhost:8080/job/flask-cicd-demo/build --user admin:your-token

# Kubernetes
kubectl get pods -n flask-app -w          # Watch pods
kubectl logs -l app=flask-app -n flask-app -f  # Follow logs
kubectl rollout status deployment/flask-app -n flask-app  # Check rollout

# Docker Hub
docker login                              # Login to Docker Hub
docker images | grep flask-cicd-demo      # List local images
docker push your-username/flask-cicd-demo:latest  # Manual push
```

---

## Next Steps

1. ✅ Set up Jenkins (Part 1-4)
2. ✅ Configure credentials (Part 3)
3. ✅ Create pipeline job (Part 5)
4. ✅ Push code to GitHub (Part 7)
5. ✅ Configure webhook (Part 8)
6. ✅ Run first pipeline (Part 9)
7. ⬜ Add monitoring (Prometheus/Grafana)
8. ⬜ Configure alerts
9. ⬜ Set up staging environment
10. ⬜ Implement blue-green deployment

---

**Your complete CI/CD pipeline is ready to deploy!** 🚀
