# Flask CI/CD Demo — Production-Ready Kubernetes Deployment

A production-grade Python Flask application with a full CI/CD pipeline using Jenkins, Docker, and Kubernetes.

---

## Architecture Overview

```
Developer → GitHub Push
              │
              ▼
         Jenkins Pipeline
         ┌─────────────────────────────────────────────┐
         │ 1. Clone Code                               │
         │ 2. Install Dependencies                     │
         │ 3. Run Tests (pytest + coverage)            │
         │ 4. SonarQube Static Analysis                │
         │ 5. Build Docker Image (multi-stage)         │
         │ 6. Trivy Security Scan                      │
         │ 7. Push to Docker Hub                       │
         │ 8. Deploy to Kubernetes (kubectl apply)     │
         │ 9. Verify Rollout                           │
         └─────────────────────────────────────────────┘
              │
              ▼
         Kubernetes Cluster (Minikube / EKS / GKE)
         ┌─────────────────────────────────────────────┐
         │  Namespace: flask-app                       │
         │  ┌──────────┐   ┌──────────┐               │
         │  │  Pod 1   │   │  Pod 2   │  ← HPA scales │
         │  │ Flask+   │   │ Flask+   │    2–10 pods   │
         │  │ Gunicorn │   │ Gunicorn │               │
         │  └────┬─────┘   └────┬─────┘               │
         │       └──────┬───────┘                      │
         │          Service (ClusterIP :80)             │
         │              │                              │
         │          Ingress (nginx)                    │
         └─────────────────────────────────────────────┘
              │
              ▼
         Monitoring: Prometheus + Grafana
```

---

## Project Structure

```
flask-cicd-demo/
├── app.py                          # Flask application
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Dev/test dependencies
├── Dockerfile                      # Multi-stage Docker build
├── .dockerignore
├── Jenkinsfile                     # Jenkins declarative pipeline
│
├── k8s/                            # Raw Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml             # Rolling update, probes, resources
│   ├── service.yaml                # ClusterIP
│   ├── ingress.yaml                # nginx ingress
│   └── hpa.yaml                   # Horizontal Pod Autoscaler
│
├── helm/flask-app/                 # Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── _helpers.tpl
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       └── hpa.yaml
│
├── monitoring/
│   └── prometheus-values.yaml      # kube-prometheus-stack overrides
│
├── tests/
│   ├── __init__.py
│   └── test_app.py
│
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions (lint + test)
```

---

## Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Docker | 24+ |
| kubectl | 1.29+ |
| Minikube | 1.33+ (local) |
| Helm | 3.15+ |
| Jenkins | 2.460+ |

### 1. Run Locally

```bash
# Clone
git clone https://github.com/your-org/flask-cicd-demo.git
cd flask-cicd-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Start app
python app.py
# Visit: http://localhost:5000
```

### 2. Build & Run with Docker

```bash
# Build
docker build -t flask-cicd-demo:latest .

# Run
docker run -p 5000:5000 \
  -e APP_ENV=production \
  -e SECRET_KEY=mysecret \
  flask-cicd-demo:latest

# Test
curl http://localhost:5000/health
```

### 3. Deploy to Kubernetes (Minikube)

```bash
# Start Minikube
minikube start --driver=docker

# Enable ingress addon
minikube addons enable ingress

# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Get Minikube IP
minikube ip

# Add to /etc/hosts (replace <MINIKUBE_IP>)
echo "<MINIKUBE_IP> flask-app.example.com" | sudo tee -a /etc/hosts

# Test
curl http://flask-app.example.com/health
```

### 4. Deploy with Helm

```bash
# Install
helm install flask-app ./helm/flask-app \
  --namespace flask-app \
  --create-namespace \
  --set image.tag=1.0.0

# Upgrade
helm upgrade flask-app ./helm/flask-app \
  --set image.tag=2.0.0

# Rollback
helm rollback flask-app 1

# Uninstall
helm uninstall flask-app -n flask-app
```

---

## Jenkins Pipeline Setup

### Step 1 — Install Jenkins Plugins

- Pipeline
- Git
- Docker Pipeline
- Kubernetes CLI
- SonarQube Scanner
- HTML Publisher
- Credentials Binding

### Step 2 — Configure Credentials

In Jenkins → Manage Jenkins → Credentials → Global:

| ID | Type | Description |
|----|------|-------------|
| `dockerhub-credentials` | Username/Password | Docker Hub login |
| `kubeconfig-credentials` | Secret File | `~/.kube/config` |
| `sonarqube-token` | Secret Text | SonarQube auth token |

### Step 3 — Create Pipeline Job

1. New Item → Pipeline
2. Pipeline Definition: **Pipeline script from SCM**
3. SCM: Git → your repo URL
4. Script Path: `Jenkinsfile`
5. Save

### Step 4 — GitHub Webhook

In your GitHub repo → Settings → Webhooks → Add webhook:

- Payload URL: `http://<JENKINS_URL>/github-webhook/`
- Content type: `application/json`
- Events: **Just the push event**

Jenkins job → Configure → Build Triggers → ✅ **GitHub hook trigger for GITScm polling**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | App info and version |
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/v1/items` | List all items |
| GET | `/api/v1/items/<id>` | Get item by ID |

---

## Deployment Verification Commands

```bash
# Check all pods are Running
kubectl get pods -n flask-app

# Watch pod status in real time
kubectl get pods -n flask-app -w

# Check rollout status
kubectl rollout status deployment/flask-app -n flask-app

# View rollout history
kubectl rollout history deployment/flask-app -n flask-app

# Rollback to previous version
kubectl rollout undo deployment/flask-app -n flask-app

# View pod logs
kubectl logs -l app=flask-app -n flask-app --tail=50

# Describe a pod (events, resource usage)
kubectl describe pod -l app=flask-app -n flask-app

# Check HPA status
kubectl get hpa -n flask-app

# Port-forward for local testing
kubectl port-forward svc/flask-app-service 8080:80 -n flask-app
curl http://localhost:8080/health
```

---

## Monitoring Setup

### Install kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

### Access Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Open: http://localhost:3000
# Default login: admin / admin
```

The Flask app exposes Prometheus metrics at `/metrics` via `prometheus-flask-exporter`. Grafana dashboard ID **9628** is pre-configured.

---

## Troubleshooting

### ImagePullBackOff

**Cause:** Kubernetes cannot pull the Docker image.

```bash
kubectl describe pod <pod-name> -n flask-app
```

**Fixes:**
- Verify image name/tag in `deployment.yaml` matches what was pushed
- Check Docker Hub credentials: `kubectl get secret -n flask-app`
- For private registries, create an `imagePullSecret`:
  ```bash
  kubectl create secret docker-registry regcred \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=<user> \
    --docker-password=<pass> \
    -n flask-app
  ```

### CrashLoopBackOff

**Cause:** Container starts but immediately exits.

```bash
kubectl logs <pod-name> -n flask-app --previous
```

**Fixes:**
- Check app logs for Python exceptions
- Verify environment variables are set (ConfigMap/Secret)
- Confirm the container port matches `containerPort: 5000`
- Test the image locally: `docker run flask-cicd-demo:latest`

### Pending Pods

**Cause:** Scheduler cannot place the pod on any node.

```bash
kubectl describe pod <pod-name> -n flask-app | grep -A 10 Events
```

**Fixes:**
- Insufficient resources → reduce `resources.requests` or add nodes
- Node selector mismatch → check `nodeSelector` in deployment
- Taints/tolerations → `kubectl describe node | grep Taint`

### Jenkins Docker Permission Issue

**Cause:** Jenkins user cannot access the Docker socket.

```bash
# On the Jenkins host
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

Or in Docker-in-Docker setups, mount the socket:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

### Minikube Ingress Not Working

```bash
# Enable ingress addon
minikube addons enable ingress

# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Get Minikube IP and add to hosts
echo "$(minikube ip) flask-app.example.com" | sudo tee -a /etc/hosts

# Use minikube tunnel for LoadBalancer services
minikube tunnel
```

---

## Security Best Practices

| Practice | Implementation |
|----------|---------------|
| Non-root container | `runAsUser: 1001`, `runAsNonRoot: true` |
| Read-only filesystem | `readOnlyRootFilesystem: true` |
| Drop all capabilities | `capabilities.drop: [ALL]` |
| No privilege escalation | `allowPrivilegeEscalation: false` |
| Secrets management | Kubernetes Secrets (use Sealed Secrets / Vault in prod) |
| Image scanning | Trivy in Jenkins pipeline |
| Least privilege | Dedicated namespace, no cluster-admin |
| Resource limits | CPU/memory limits on every container |

**Production secret management** — never commit real secrets to Git. Use:
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [HashiCorp Vault](https://www.vaultproject.io/)
- AWS Secrets Manager / GCP Secret Manager

---

## Resume Project Points

- Designed and implemented a production-ready Flask microservice with Prometheus metrics, structured logging, and health/readiness endpoints
- Built a multi-stage Docker image reducing final image size by ~60%, running as a non-root user with read-only filesystem
- Authored a 9-stage Jenkins declarative pipeline covering testing, SonarQube SAST, Trivy CVE scanning, Docker Hub push, and zero-downtime Kubernetes rolling deployment
- Deployed to Kubernetes with HPA (2–10 replicas), resource quotas, liveness/readiness probes, and pod anti-affinity for high availability
- Created a reusable Helm chart with parameterized values for multi-environment deployments
- Integrated Prometheus scraping and Grafana dashboards for real-time observability

---

## Interview Questions & Answers

**Q: What is a multi-stage Docker build and why use it?**
A: A multi-stage build uses multiple `FROM` instructions in one Dockerfile. The first stage (builder) installs compilers and build tools; the final stage copies only the compiled artifacts. This keeps the runtime image small and free of build-time attack surface.

**Q: What is the difference between liveness and readiness probes?**
A: A liveness probe tells Kubernetes whether to restart the container (is it alive?). A readiness probe tells Kubernetes whether to send traffic to the pod (is it ready to serve?). A pod can be alive but not ready — for example, during startup or when a downstream dependency is unavailable.

**Q: How does a Kubernetes rolling update work?**
A: Kubernetes gradually replaces old pods with new ones. With `maxSurge: 1` and `maxUnavailable: 0`, it creates one new pod, waits for it to pass the readiness probe, then terminates one old pod — repeating until all pods are updated. This ensures zero downtime.

**Q: What is an HPA and when does it scale?**
A: A HorizontalPodAutoscaler watches CPU/memory metrics from the metrics-server and adjusts the replica count between `minReplicas` and `maxReplicas`. It scales up when average CPU exceeds the target utilization and scales down after a stabilization window to avoid flapping.

**Q: How do you handle secrets securely in Kubernetes?**
A: Kubernetes Secrets are base64-encoded (not encrypted by default). For production, enable etcd encryption at rest, use RBAC to restrict secret access, and integrate with an external secrets manager (Vault, AWS Secrets Manager) via the External Secrets Operator or Sealed Secrets.

**Q: What is the purpose of SonarQube in the pipeline?**
A: SonarQube performs static application security testing (SAST) — it analyzes source code for bugs, code smells, security vulnerabilities, and test coverage gaps without running the application. It acts as a quality gate before the image is built.

**Q: Why use Helm over raw kubectl manifests?**
A: Helm packages Kubernetes manifests into versioned, parameterized charts. It supports templating (so one chart works across dev/staging/prod), atomic upgrades, and one-command rollbacks (`helm rollback`), which raw `kubectl apply` does not provide natively.

**Q: What does Trivy scan for?**
A: Trivy scans container images for known CVEs in OS packages and language-specific dependencies (pip, npm, etc.). It can also scan IaC files (Kubernetes YAML, Terraform) and Git repositories for secrets.

---

## License

MIT — see [LICENSE](LICENSE) for details.
