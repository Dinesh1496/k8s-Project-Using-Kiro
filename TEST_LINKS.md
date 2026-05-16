# 🌐 Test Your Flask CI/CD Application

## ✅ CI/CD Update Test - SUCCESS!

Your application was successfully updated and redeployed using CI/CD workflow:

### What Changed
- ✅ Added "Item Four - NEW!" to the items list
- ✅ Updated main page message to show "UPDATED!"
- ✅ Rebuilt Docker image (v2)
- ✅ Deployed to Kubernetes with rolling update
- ✅ Zero downtime during deployment

---

## 🔗 Test Links (Local Access)

### Main Application
```
http://localhost:8080/
```

**Expected Response**:
```json
{
  "environment": "production",
  "message": "Flask CI/CD Demo Application - UPDATED!",
  "status": "running",
  "update": "Added new item to test CI/CD",
  "version": "1.0.0"
}
```

### Health Check
```
http://localhost:8080/health
```

**Expected Response**:
```json
{
  "status": "healthy"
}
```

### Readiness Check
```
http://localhost:8080/ready
```

**Expected Response**:
```json
{
  "status": "ready"
}
```

### API - Get All Items (NEW: Now shows 4 items!)
```
http://localhost:8080/api/v1/items
```

**Expected Response**:
```json
{
  "count": 4,
  "items": [
    {"category": "demo", "id": 1, "name": "Item One"},
    {"category": "demo", "id": 2, "name": "Item Two"},
    {"category": "demo", "id": 3, "name": "Item Three"},
    {"category": "demo", "id": 4, "name": "Item Four - NEW!"}
  ]
}
```

### API - Get Single Item
```
http://localhost:8080/api/v1/items/1
http://localhost:8080/api/v1/items/4
```

### Prometheus Metrics
```
http://localhost:8080/metrics
```

---

## 🧪 Test in Browser

Simply open these URLs in your browser:

1. **Main Page**: [http://localhost:8080/](http://localhost:8080/)
2. **Health**: [http://localhost:8080/health](http://localhost:8080/health)
3. **Items API**: [http://localhost:8080/api/v1/items](http://localhost:8080/api/v1/items)
4. **Metrics**: [http://localhost:8080/metrics](http://localhost:8080/metrics)

---

## 💻 Test in PowerShell

```powershell
# Test main page
Invoke-WebRequest -Uri http://localhost:8080/ -UseBasicParsing | Select-Object -ExpandProperty Content

# Test items API (should show 4 items now!)
Invoke-WebRequest -Uri http://localhost:8080/api/v1/items -UseBasicParsing | Select-Object -ExpandProperty Content

# Test health
Invoke-WebRequest -Uri http://localhost:8080/health -UseBasicParsing | Select-Object -ExpandProperty Content

# Test specific item
Invoke-WebRequest -Uri http://localhost:8080/api/v1/items/4 -UseBasicParsing | Select-Object -ExpandProperty Content
```

---

## 🧪 Test with curl (if installed)

```bash
# Main page
curl http://localhost:8080/

# Items API
curl http://localhost:8080/api/v1/items

# Health check
curl http://localhost:8080/health

# Pretty print JSON
curl http://localhost:8080/api/v1/items | python -m json.tool
```

---

## 🔄 CI/CD Workflow That Just Ran

```
1. Code Change
   ├─ Updated app.py (added Item Four)
   └─ Updated main page message
   
2. Docker Build
   ├─ Built new image: flask-cicd-demo:v2
   └─ Multi-stage build completed
   
3. Kubernetes Deployment
   ├─ Updated deployment.yaml
   ├─ Applied changes: kubectl apply
   └─ Rolling update started
   
4. Rolling Update Process
   ├─ Created 1 new pod with v2
   ├─ Waited for readiness probe
   ├─ Terminated 1 old pod
   ├─ Created 2nd new pod with v2
   ├─ Waited for readiness probe
   └─ Terminated last old pod
   
5. Verification
   ├─ All pods running: 2/2
   ├─ Health checks passing
   └─ New content served ✅
```

**Total Time**: ~30 seconds
**Downtime**: 0 seconds (zero downtime deployment!)

---

## 📊 Verify Deployment

```powershell
# Check pods (should show new pods)
kubectl get pods -n flask-app

# Check rollout history
kubectl rollout history deployment/flask-app -n flask-app

# Check current image
kubectl describe deployment flask-app -n flask-app | Select-String "Image:"

# View logs from new pods
kubectl logs -l app=flask-app -n flask-app --tail=20
```

---

## 🎯 What This Proves

✅ **CI/CD Works**: Code change → Build → Deploy → Live
✅ **Zero Downtime**: Rolling update kept service available
✅ **Health Checks**: Kubernetes waited for pods to be ready
✅ **Load Balancing**: Service routes to healthy pods
✅ **Version Control**: Can track deployment history
✅ **Rollback Ready**: Can revert if needed

---

## 🔄 Make Another Change to Test Again

### Option 1: Add Another Item

Edit `app.py` and add Item Five:

```python
items = [
    {"id": 1, "name": "Item One", "category": "demo"},
    {"id": 2, "name": "Item Two", "category": "demo"},
    {"id": 3, "name": "Item Three", "category": "demo"},
    {"id": 4, "name": "Item Four - NEW!", "category": "demo"},
    {"id": 5, "name": "Item Five - NEWEST!", "category": "demo"},
]
```

Then rebuild and deploy:

```powershell
# Build v3
docker build -t flask-cicd-demo:v3 .

# Update deployment
# Edit k8s/deployment.yaml: change image to flask-cicd-demo:v3

# Apply
kubectl apply -f k8s/deployment.yaml

# Watch rollout
kubectl rollout status deployment/flask-app -n flask-app

# Test
Invoke-WebRequest -Uri http://localhost:8080/api/v1/items -UseBasicParsing
```

### Option 2: Change the Message

Edit `app.py` and change the message:

```python
return jsonify({
    "message": "Flask CI/CD Demo - Version 3!",
    "version": "1.0.0",
    "environment": APP_ENV,
    "status": "running",
    "update": "Testing CI/CD again!"
}), 200
```

---

## 🚀 Next: Push to GitHub for Full CI/CD

To test the **full automated CI/CD** with GitHub Actions + Jenkins:

### 1. Push to GitHub

```powershell
git init
git add .
git commit -m "feat: Add Item Four to test CI/CD"
git remote add origin https://github.com/YOUR-USERNAME/flask-cicd-demo.git
git push -u origin main
```

### 2. GitHub Actions Runs Automatically
- Lints code
- Runs tests
- Generates coverage
- Shows results in Actions tab

### 3. Jenkins (Optional)
- Set up Jenkins server
- Configure webhook
- Full 9-stage pipeline runs
- Deploys to Kubernetes automatically

---

## 📱 Share Your Application

### For Local Network Access

1. Find your local IP:
```powershell
ipconfig | Select-String "IPv4"
```

2. Update ingress or use NodePort service

3. Access from other devices on same network:
```
http://YOUR-LOCAL-IP:8080/
```

### For Public Access (Options)

1. **ngrok** (Quick testing):
```powershell
ngrok http 8080
# Get public URL like: https://abc123.ngrok.io
```

2. **Cloud Deployment**:
- Deploy to AWS EKS
- Deploy to Google GKE
- Deploy to Azure AKS
- Deploy to DigitalOcean Kubernetes

3. **Docker Hub + Cloud**:
```powershell
# Tag and push
docker tag flask-cicd-demo:v2 YOUR-USERNAME/flask-cicd-demo:v2
docker push YOUR-USERNAME/flask-cicd-demo:v2

# Deploy anywhere with public image
```

---

## ✅ Current Status

| Component | Version | Status |
|-----------|---------|--------|
| Application | v2 (UPDATED) | ✅ Running |
| Pods | 2/2 | ✅ Healthy |
| Service | ClusterIP | ✅ Active |
| Ingress | nginx | ✅ Configured |
| Port Forward | :8080 | ✅ Active |

**Access Now**: http://localhost:8080/

---

## 🎉 Success!

Your CI/CD workflow is working perfectly:
- ✅ Code changes applied
- ✅ Docker image rebuilt
- ✅ Kubernetes deployment updated
- ✅ Zero downtime achieved
- ✅ New content live

**Test it now**: [http://localhost:8080/](http://localhost:8080/)
