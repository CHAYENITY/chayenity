# 🚀 Quick Start Checklist - Jenkins Pipeline Setup

Use this checklist alongside the detailed [JENKINS_SETUP_GUIDE.md](./JENKINS_SETUP_GUIDE.md) for step-by-step implementation.

## ✅ Phase 1: Environment Setup (30 minutes)

### Docker Containers
- [ ] **Build Jenkins custom image**
  ```bash
  cd c:\Users\phats\WorkOnly\chayenity\partCI_CD
  docker build -t jenkins-chayenity:latest -f Dockerfile .
  ```

- [ ] **Start Jenkins container**
  ```bash
  docker run -d --name jenkins-chayenity -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock --restart unless-stopped jenkins-chayenity:latest
  ```

- [ ] **Start PostgreSQL test database**
  ```bash
  docker run -d --name postgres-test -e POSTGRES_DB=chayenity_test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 --restart unless-stopped postgres:15-alpine
  ```

- [ ] **Start SonarQube**
  ```bash
  docker run -d --name sonarqube -p 9000:9000 -v sonarqube_data:/opt/sonarqube/data --restart unless-stopped sonarqube:community
  ```

### Verify All Containers Running
- [ ] Check with: `docker ps`
- [ ] Should see: jenkins-chayenity, postgres-test, sonarqube

## ✅ Phase 2: Jenkins Initial Setup (15 minutes)

### Jenkins Web Access
- [ ] **Open Jenkins**: http://localhost:8080
- [ ] **Get admin password**: `docker exec jenkins-chayenity cat /var/jenkins_home/secrets/initialAdminPassword`
- [ ] **Install suggested plugins** (wait for completion)
- [ ] **Create admin user** with secure credentials

### Install Required Plugins
- [ ] Go to "Manage Jenkins" → "Plugin Manager" → "Available plugins"
- [ ] Install and restart:
  - [ ] SonarQube Scanner
  - [ ] Docker Pipeline
  - [ ] Credentials Binding
  - [ ] Pipeline: Stage View

## ✅ Phase 3: Credentials Configuration (10 minutes)

### Docker Hub Credentials
- [ ] **Go to**: "Manage Jenkins" → "Credentials" → "System" → "Global credentials"
- [ ] **Add**: Username/Password
  - ID: `dockerhub-cred`
  - Username: [Your Docker Hub username]
  - Password: [Your Docker Hub password]

### GitHub Credentials (if needed)
- [ ] **Add**: Username/Password
  - ID: `github-cred`
  - Username: [Your GitHub username]
  - Password: [Your GitHub token]

## ✅ Phase 4: SonarQube Setup (15 minutes)

### SonarQube Configuration
- [ ] **Open SonarQube**: http://localhost:9000
- [ ] **Login**: admin/admin (change password when prompted)
- [ ] **Create project**:
  - Project key: `chayenity-server`
  - Display name: `Chayenity Server API`
- [ ] **Generate token**: "My Account" → "Security" → "Generate Tokens"
  - Name: `jenkins-token`
  - **Copy the token!**

### Add SonarQube Token to Jenkins
- [ ] **In Jenkins**: "Manage Jenkins" → "Credentials"
- [ ] **Add**: Secret text
  - ID: `sonarqube_token`
  - Secret: [Paste the SonarQube token]

### Configure SonarQube Server in Jenkins
- [ ] **Go to**: "Manage Jenkins" → "Configure System"
- [ ] **SonarQube servers section**:
  - Name: `Sonarqube`
  - Server URL: `http://host.docker.internal:9000`
  - Token: Select `sonarqube_token`

## ✅ Phase 5: Pipeline Creation (10 minutes)

### Create Pipeline Job
- [ ] **Jenkins Dashboard** → "New Item"
- [ ] **Name**: `chayenity-pipeline`
- [ ] **Type**: Pipeline
- [ ] **Description**: `Chayenity FastAPI CI/CD Pipeline`

### Pipeline Configuration
- [ ] **Pipeline Definition**: Pipeline script from SCM
- [ ] **SCM**: Git
- [ ] **Repository URL**: `https://github.com/CHAYENITY/chayenity.git`
- [ ] **Branch**: `feat/srv/buddy-system`
- [ ] **Script Path**: `partCI_CD/main/Jenkinsfile`
- [ ] **Save**

## ✅ Phase 6: First Pipeline Run (5-15 minutes)

### Execute Pipeline
- [ ] **Click**: "Build Now"
- [ ] **Monitor**: Console Output
- [ ] **Verify stages**:
  - [ ] Checkout ✅
  - [ ] Setup Environment ✅
  - [ ] Run Tests & Coverage ✅
  - [ ] SonarQube Analysis ✅
  - [ ] Build Docker Image ✅
  - [ ] Deploy Container ✅
  - [ ] Push to Registry ✅

### Verification
- [ ] **Jenkins**: All stages green
- [ ] **SonarQube**: Project visible at http://localhost:9000
- [ ] **Docker**: Image pushed to Docker Hub
- [ ] **Application**: Running at http://localhost:8000

## 🔧 Quick Troubleshooting

### If Build Fails at Docker Stage:
```bash
docker restart jenkins-chayenity
```

### If SonarQube Connection Fails:
```bash
docker logs sonarqube
# Wait for "SonarQube is operational"
```

### If Tests Fail:
```bash
docker logs postgres-test
# Ensure database is running
```

### Check All Containers:
```bash
docker ps -a
```

## 📊 Success Indicators

After successful setup, you should see:
- ✅ **4 containers running**: jenkins-chayenity, postgres-test, sonarqube, chayenity-server-container
- ✅ **Jenkins pipeline**: All stages completed successfully
- ✅ **SonarQube project**: Code analysis completed
- ✅ **Docker image**: Available in your Docker Hub repository
- ✅ **Application**: Accessible and healthy at http://localhost:8000

## ⏱️ Total Setup Time: ~90 minutes

**Next Steps**: Set up automated triggers, monitoring, and deployment to staging/production environments.

---
**Quick Start Guide v1.0** | Created for Chayenity Project | October 2025