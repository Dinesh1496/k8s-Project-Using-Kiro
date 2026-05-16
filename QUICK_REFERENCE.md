# Flask CI/CD Demo — Quick Reference Card

## 🚀 Quick Start Commands

### Local Development
```powershell
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Run app locally
python app.py
# Visit: http://localhost:5000
```

### Docker
```powershell
# Build
docker build -t flask-cicd-demo:latest .

# Run
docker run -p 5000:5000 flask-cicd-demo:latest

# Test
Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
```

### Kubernetes
```powershell
# Deploy all
kubectl apply -f k8s/

# Check status
kubectl get all -n flask-app

# View logs
kubectl logs -l app=flask-app -n flask-app --tail=50

# Port forward
kubectl port-forward svc/flask-app-service 8080:80 -n flask-app

# Delete all
kubectl delete namespace flask-app
```

### Helm
```powershell
# Install
helm install flask-app ./helm/flask-app -n flask-app --create-namespace

# Upgrade
helm upgrade flask-app ./helm/flask-app --set image.tag=2.0.0

# Rollback
helm rollback flask-app 1

# Uninstall
helm uninstall flask-app -n flask-app
```

---

## 📡 API Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | App info | `{"status":"running","version":"1.0.0"}` |
| `/health` | GET | Liveness probe | `{"status":"healthy"}` |
| `/ready` | GET | Readiness probe | `{"status":"ready"}` |
| `/metrics` | GET | Prometheus metrics | Text format |
| `/api/v1/items` | GET | List all items | `{"count":3,"items":[...]}` |
| `/api/v1/items/<id>` | GET | Get item by ID | `{"id":1,"name":"Item One"}` |

---

## 🔍 Debugging Commands

### Pod Issues
```powershell
# Describe pod
kubectl describe pod <pod-name> -n flask-app

# Get logs
kubectl logs <pod-name> -n flask-app

# Previous logs (if crashed)
kubectl logs <pod-name> -n flask-app --previous

# Exec into pod
kubectl exec -it <pod-name> -n flask-app -- /bin/bash

# Check environment
kubectl exec <pod-name> -n flask-app -- env
```

### Deployment Issues
```powershell
# Rollout status
kubectl rollout status deployment/flask-app -n flask-app

# Rollout history
kubectl rollout history deployment/flask-app -n flask-app

# Rollback
kubectl rollout undo deployment/flask-app -n flask-app

# Describe deployment
kubectl describe deployment flask-app -n flask-app
```

### Service & Networking
```powershell
# Test service internally
kubectl run test-pod --rm -it --image=curlimages/curl -- sh
curl http://flask-app-service.flask-app.svc.cluster.local/health

# Check endpoints
kubectl get endpoints -n flask-app

# Check ingress
kubectl describe ingress flask-app-ingress -n flask-app
```

---

## 📊 Monitoring Commands

```powershell
# Watch pods
kubectl get pods -n flask-app -w

# Watch HPA
kubectl get hpa -n flask-app -w

# Top pods (resource usage)
kubectl top pods -n flask-app

# Top nodes
kubectl top nodes

# Events
kubectl get events -n flask-app --sort-by='.lastTimestamp'
```

---

## 🔐 Secrets Management

```powershell
# View secret (base64 encoded)
kubectl get secret flask-app-secret -n flask-app -o yaml

# Decode secret
kubectl get secret flask-app-secret -n flask-app -o jsonpath='{.data.SECRET_KEY}' | base64 -d

# Create secret from literal
kubectl create secret generic my-secret --from-literal=key=value -n flask-app

# Create secret from file
kubectl create secret generic my-secret --from-file=./secret.txt -n flask-app
```

---

## 🏗️ Jenkins Pipeline

### Trigger Build
```powershell
# Via webhook (automatic on git push)
git push origin main

# Manual trigger
# Go to Jenkins UI → flask-cicd-demo → Build Now
```

### View Logs
```powershell
# Jenkins container logs
docker logs jenkins -f

# Pipeline console output
# Jenkins UI → Build #X → Console Output
```

---

## 🐳 Docker Commands

```powershell
# List images
docker images | grep flask-cicd-demo

# Remove image
docker rmi flask-cicd-demo:latest

# Inspect image
docker inspect flask-cicd-demo:latest

# Image history
docker history flask-cicd-demo:latest

# Run with environment variables
docker run -p 5000:5000 `
  -e APP_ENV=development `
  -e SECRET_KEY=mysecret `
  flask-cicd-demo:latest
```

---

## 📦 Helm Commands

```powershell
# List releases
helm list -n flask-app

# Get values
helm get values flask-app -n flask-app

# Get manifest
helm get manifest flask-app -n flask-app

# Template (dry-run)
helm template flask-app ./helm/flask-app

# Lint chart
helm lint ./helm/flask-app

# Package chart
helm package ./helm/flask-app
```

---

## 🔄 Scaling Commands

```powershell
# Manual scale
kubectl scale deployment/flask-app --replicas=5 -n flask-app

# Autoscale
kubectl autoscale deployment flask-app --min=2 --max=10 --cpu-percent=70 -n flask-app

# Check HPA
kubectl get hpa -n flask-app

# Delete HPA
kubectl delete hpa flask-app-hpa -n flask-app
```

---

## 🧪 Testing Commands

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_app.py::test_health -v

# Run with markers
pytest tests/ -m "not slow" -v

# Lint code
flake8 app.py --max-line-length=120

# Format code
black app.py

# Type check
mypy app.py
```

---

## 🌐 Access Methods

### Port Forward (Local)
```powershell
kubectl port-forward svc/flask-app-service 8080:80 -n flask-app
Invoke-WebRequest -Uri http://localhost:8080/ -UseBasicParsing
```

### Ingress (with Host header)
```powershell
Invoke-WebRequest -Uri http://localhost/ -Headers @{"Host"="flask-app.local"} -UseBasicParsing
```

### Ingress (with hosts file)
```powershell
# Add to C:\Windows\System32\drivers\etc\hosts (as Admin)
127.0.0.1 flask-app.local

# Then access
Invoke-WebRequest -Uri http://flask-app.local/ -UseBasicParsing
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application |
| `Dockerfile` | Container build instructions |
| `Jenkinsfile` | CI/CD pipeline definition |
| `k8s/*.yaml` | Kubernetes manifests |
| `helm/flask-app/` | Helm chart |
| `requirements.txt` | Production dependencies |
| `requirements-dev.txt` | Development dependencies |
| `tests/test_app.py` | Unit tests |

---

## 📝 Environment Variables

### Application
```
APP_ENV=production          # Environment (development/production)
APP_VERSION=1.0.0          # Application version
PORT=5000                  # Server port
SECRET_KEY=changeme        # Flask secret key
DB_PASSWORD=secret         # Database password (from Secret)
LOG_LEVEL=info            # Logging level
```

### Jenkins
```
DOCKER_REGISTRY=username   # Docker Hub username
IMAGE_NAME=flask-cicd-demo # Image name
IMAGE_TAG=latest          # Image tag
K8S_NAMESPACE=flask-app   # Kubernetes namespace
```

---

## 🚨 Common Issues & Fixes

### ImagePullBackOff
```powershell
# Check image name
kubectl describe pod <pod-name> -n flask-app | Select-String "Image"

# For local images, set imagePullPolicy: Never
# For Docker Hub, check credentials
```

### CrashLoopBackOff
```powershell
# Check logs
kubectl logs <pod-name> -n flask-app --previous

# Common causes:
# - Application error on startup
# - Missing environment variables
# - Port mismatch
```

### Pending Pods
```powershell
# Check events
kubectl describe pod <pod-name> -n flask-app

# Common causes:
# - Insufficient resources
# - Node selector mismatch
# - PVC not bound
```

### Service Not Accessible
```powershell
# Check service endpoints
kubectl get endpoints -n flask-app

# Check pod labels match service selector
kubectl get pods -n flask-app --show-labels
kubectl describe svc flask-app-service -n flask-app
```

---

## 📊 Resource Specifications

### Pod Resources
```yaml
requests:
  cpu: 100m      # 0.1 CPU core
  memory: 128Mi  # 128 megabytes
limits:
  cpu: 500m      # 0.5 CPU core
  memory: 256Mi  # 256 megabytes
```

### HPA Thresholds
```yaml
minReplicas: 2
maxReplicas: 10
targetCPU: 70%
targetMemory: 80%
```

---

## 🔗 Useful URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Application | http://localhost:8080 | - |
| Jenkins | http://localhost:8080 | admin/password |
| SonarQube | http://localhost:9000 | admin/admin |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |

---

## 📚 Documentation Links

- **README.md** — Complete project documentation
- **DEPLOYMENT_STATUS.md** — Current deployment status
- **JENKINS_SETUP_GUIDE.md** — Jenkins CI/CD setup
- **PROJECT_SUMMARY.md** — Project overview & interview prep
- **QUICK_REFERENCE.md** — This file

---

## 🎯 Key Metrics

| Metric | Value |
|--------|-------|
| Test Coverage | 100% (7/7 tests) |
| Docker Image Size | ~150MB |
| Build Time | ~3-5 minutes |
| Deployment Time | ~30 seconds |
| Pod Startup | ~15 seconds |
| Replicas | 2-10 (auto-scaled) |

---

## ✅ Deployment Checklist

- [x] Docker image built
- [x] Tests passing (7/7)
- [x] Kubernetes namespace created
- [x] ConfigMap applied
- [x] Secret applied
- [x] Deployment rolled out (2/2 pods)
- [x] Service created
- [x] Ingress configured
- [x] HPA active
- [x] All endpoints verified
- [ ] Monitoring installed (optional)
- [ ] Jenkins configured (optional)

---

**Status**: ✅ **FULLY OPERATIONAL**

Application is live at: http://localhost:8080 (via port-forward)
