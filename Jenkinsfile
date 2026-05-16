pipeline {
    agent any

    environment {
        // ── Project settings ──────────────────────────────────────────────
        APP_NAME        = "flask-cicd-demo"
        DOCKER_REGISTRY = "your-dockerhub-username"          // ← change this
        IMAGE_NAME      = "${DOCKER_REGISTRY}/${APP_NAME}"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        IMAGE_FULL      = "${IMAGE_NAME}:${IMAGE_TAG}"
        IMAGE_LATEST    = "${IMAGE_NAME}:latest"

        // ── Kubernetes settings ───────────────────────────────────────────
        K8S_NAMESPACE   = "flask-app"
        K8S_DEPLOYMENT  = "flask-app"

        // ── Credential IDs (configure in Jenkins Credentials store) ───────
        DOCKER_CREDS    = "dockerhub-credentials"
        KUBECONFIG_CRED = "kubeconfig-credentials"
        SONAR_TOKEN     = "sonarqube-token"

        // ── SonarQube ─────────────────────────────────────────────────────
        SONAR_PROJECT   = "flask-cicd-demo"
        SONAR_HOST      = "http://sonarqube:9000"            // ← change this
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10"))
        timeout(time: 30, unit: "MINUTES")
        disableConcurrentBuilds()
        timestamps()
    }

    stages {

        // ─────────────────────────────────────────────────────────────────
        stage("Clone Code") {
            steps {
                echo "📥 Cloning repository..."
                checkout scm
                sh "git log --oneline -5"
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Install Dependencies") {
            steps {
                echo "📦 Installing Python dependencies..."
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                """
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Run Tests") {
            steps {
                echo "🧪 Running unit tests with coverage..."
                sh """
                    . venv/bin/activate
                    pytest tests/ \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov \
                        --junitxml=test-results.xml \
                        -v
                """
            }
            post {
                always {
                    junit "test-results.xml"
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "htmlcov",
                        reportFiles: "index.html",
                        reportName: "Coverage Report"
                    ])
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("SonarQube Scan") {
            steps {
                echo "🔍 Running SonarQube static analysis..."
                withCredentials([string(credentialsId: "${SONAR_TOKEN}", variable: "SONAR_AUTH_TOKEN")]) {
                    sh """
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST} \
                            -Dsonar.login=${SONAR_AUTH_TOKEN} \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.exclusions=venv/**,tests/**,htmlcov/**
                    """
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Build Docker Image") {
            steps {
                echo "🐳 Building Docker image: ${IMAGE_FULL}"
                sh """
                    docker build \
                        --no-cache \
                        --label "build.number=${BUILD_NUMBER}" \
                        --label "git.commit=${GIT_COMMIT}" \
                        -t ${IMAGE_FULL} \
                        -t ${IMAGE_LATEST} \
                        .
                """
                sh "docker images | grep ${APP_NAME}"
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Trivy Image Scan") {
            steps {
                echo "🛡️  Scanning Docker image with Trivy..."
                sh """
                    trivy image \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --output trivy-report.txt \
                        ${IMAGE_FULL}
                    cat trivy-report.txt
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: "trivy-report.txt", allowEmptyArchive: true
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Push Docker Image") {
            steps {
                echo "📤 Pushing image to Docker Hub..."
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDS}",
                    usernameVariable: "DOCKER_USER",
                    passwordVariable: "DOCKER_PASS"
                )]) {
                    sh """
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        docker push ${IMAGE_FULL}
                        docker push ${IMAGE_LATEST}
                        docker logout
                    """
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Deploy to Kubernetes") {
            steps {
                echo "☸️  Deploying to Kubernetes namespace: ${K8S_NAMESPACE}"
                withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: "KUBECONFIG")]) {
                    sh """
                        # Apply all manifests
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml
                        kubectl apply -f k8s/secret.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/ingress.yaml
                        kubectl apply -f k8s/hpa.yaml

                        # Update image tag for rolling update
                        kubectl set image deployment/${K8S_DEPLOYMENT} \
                            ${APP_NAME}=${IMAGE_FULL} \
                            -n ${K8S_NAMESPACE}
                    """
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        stage("Verify Deployment") {
            steps {
                echo "✅ Verifying rollout..."
                withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: "KUBECONFIG")]) {
                    sh """
                        kubectl rollout status deployment/${K8S_DEPLOYMENT} \
                            -n ${K8S_NAMESPACE} \
                            --timeout=120s

                        echo "--- Pods ---"
                        kubectl get pods -n ${K8S_NAMESPACE} -l app=${APP_NAME}

                        echo "--- Services ---"
                        kubectl get svc -n ${K8S_NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline succeeded! Image: ${IMAGE_FULL}"
        }
        failure {
            echo "❌ Pipeline failed. Check logs above."
        }
        always {
            // Clean up local Docker images to save disk space
            sh "docker rmi ${IMAGE_FULL} ${IMAGE_LATEST} || true"
            cleanWs()
        }
    }
}
