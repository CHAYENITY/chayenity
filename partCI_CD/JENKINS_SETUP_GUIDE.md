# Jenkins CI/CD Pipeline Setup Guide for Chayenity Project

This guide will walk you through setting up and running a complete CI/CD pipeline for the Chayenity FastAPI project using Jenkins, Docker, and SonarQube.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Jenkins Container Setup](#jenkins-container-setup)
3. [Initial Jenkins Configuration](#initial-jenkins-configuration)
4. [Required Credentials Setup](#required-credentials-setup)
5. [SonarQube Integration](#sonarqube-integration)
6. [Pipeline Creation](#pipeline-creation)
7. [Database Setup for Tests](#database-setup-for-tests)
8. [Running the Pipeline](#running-the-pipeline)
9. [Troubleshooting](#troubleshooting)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

## 🔧 Prerequisites

Before starting, ensure you have:

- **Docker Desktop** installed and running
- **Git** installed
- **Administrative access** to your system
- **GitHub repository** access to chayenity project
- **Docker Hub account** (for image registry)
- **Basic knowledge** of Docker, Jenkins, and CI/CD concepts

## 🐳 Jenkins Container Setup

### Step 1: Build Custom Jenkins Image

1. **Navigate to the project directory:**
   ```bash
   cd c:\Users\phats\WorkOnly\chayenity\partCI_CD
   ```

2. **Build the Jenkins image with Python 3.11 and SonarQube Scanner:**
   ```bash
   docker build -t jenkins-chayenity:latest -f Dockerfile .
   ```
   
   This builds a custom Jenkins image using **Python 3.11 compiled from source** (most reliable method) that includes:
   - Jenkins LTS with JDK 17
   - Python 3.11.9 compiled with optimizations
   - Docker CLI
   - SonarQube Scanner
   - Poetry (Python dependency management)
   
   **Build time:** ~10-15 minutes (due to Python compilation, but guaranteed to work)
   
   This builds a custom Jenkins image that includes:
   - Jenkins LTS with JDK 17
   - Python 3.11
   - Docker CLI
   - SonarQube Scanner
   - Poetry (Python dependency management)

### Step 2: Run Jenkins Container

1. **Start the Jenkins container:**
   ```bash
   docker run -d ^
     --name jenkins-chayenity ^
     -p 8080:8080 ^
     -p 50000:50000 ^
     -v jenkins_home:/var/jenkins_home ^
     -v /var/run/docker.sock:/var/run/docker.sock ^
     -v "%cd%\main":/var/jenkins_workspace ^
     --restart unless-stopped ^
     jenkins-chayenity:latest
   ```

   **Port Explanations:**
   - `8080`: Jenkins web interface
   - `50000`: Jenkins agent communication
   
   **Volume Explanations:**
   - `jenkins_home`: Persistent Jenkins data
   - `docker.sock`: Docker daemon access for building images
   - `main folder`: Workspace with pipeline files

2. **Verify container is running:**
   ```bash
   docker ps
   ```

### Step 3: Access Jenkins Web Interface

1. **Open your browser and go to:**
   ```
   http://localhost:8080
   ```

2. **Get the initial admin password:**
   ```bash
   docker exec jenkins-chayenity cat /var/jenkins_home/secrets/initialAdminPassword
   ```

3. **Copy the password and paste it in the Jenkins setup wizard**

## ⚙️ Initial Jenkins Configuration

### Step 1: Install Suggested Plugins

1. Click **"Install suggested plugins"** in the setup wizard
2. Wait for all plugins to install (this may take 5-10 minutes)

### Step 2: Create Admin User

1. Fill in the admin user details:
   - **Username:** `admin`
   - **Password:** `your-secure-password`
   - **Full name:** `Chayenity Admin`
   - **Email:** `your-email@example.com`

### Step 3: Install Additional Required Plugins

1. Go to **"Manage Jenkins" → "Plugin Manager"**
2. Click on **"Available plugins"** tab
3. Search and install these plugins:
   - **SonarQube Scanner**
   - **Docker Pipeline**
   - **Pipeline: Stage View**
   - **Blue Ocean** (optional, for better UI)
   - **Credentials Binding**

4. **Restart Jenkins after installation:**
   ```bash
   docker restart jenkins-chayenity
   ```

## 🔐 Required Credentials Setup

### Step 1: GitHub Access (if using private repository)

1. Go to **"Manage Jenkins" → "Credentials" → "System" → "Global credentials"**
2. Click **"Add Credentials"**
3. Select **"Username with password"**
4. Fill in:
   - **Username:** Your GitHub username
   - **Password:** Your GitHub personal access token
   - **ID:** `github-cred`
   - **Description:** `GitHub Credentials`

### Step 2: Docker Hub Credentials

1. Add new credentials with:
   - **Kind:** Username with password
   - **Username:** Your Docker Hub username
   - **Password:** Your Docker Hub password
   - **ID:** `dockerhub-cred`
   - **Description:** `Docker Hub Credentials`

### Step 3: SonarQube Token (will be set up later)

We'll create this after setting up SonarQube.

## 📊 SonarQube Integration

### Step 1: Run SonarQube Container

1. **Start SonarQube server:**
   ```bash
   docker run -d ^
     --name sonarqube ^
     -p 9000:9000 ^
     -v sonarqube_data:/opt/sonarqube/data ^
     -v sonarqube_logs:/opt/sonarqube/logs ^
     -v sonarqube_extensions:/opt/sonarqube/extensions ^
     --restart unless-stopped ^
     sonarqube:community
   ```

2. **Wait for SonarQube to start (2-3 minutes):**
   ```bash
   docker logs -f sonarqube
   ```
   Look for "SonarQube is operational"

### Step 2: Configure SonarQube

1. **Access SonarQube:**
   ```
   http://localhost:9000
   ```

2. **Login with default credentials:**
   - Username: `admin`
   - Password: `admin`

3. **Change the default password when prompted**

4. **Create a new project:**
   - Project key: `chayenity-server`
   - Display name: `Chayenity Server API`

5. **Generate a token:**
   - Go to **"My Account" → "Security" → "Generate Tokens"**
   - Name: `jenkins-token`
   - Copy the generated token

### Step 3: Add SonarQube Token to Jenkins

1. **In Jenkins, go to "Manage Jenkins" → "Credentials"**
2. **Add new credential:**
   - **Kind:** Secret text
   - **Secret:** The SonarQube token you copied
   - **ID:** `sonarqube_token`
   - **Description:** `SonarQube Token`

### Step 4: Configure SonarQube Server in Jenkins

1. **Go to "Manage Jenkins" → "Configure System"**
2. **Scroll to "SonarQube servers" section**
3. **Click "Add SonarQube":**
   - **Name:** `Sonarqube`
   - **Server URL:** `http://host.docker.internal:9000`
   - **Server authentication token:** Select `sonarqube_token`

## 🚀 Pipeline Creation

### Step 1: Create New Pipeline Job

1. **From Jenkins dashboard, click "New Item"**
2. **Enter item name:** `chayenity-pipeline`
3. **Select "Pipeline"**
4. **Click "OK"**

### Step 2: Configure Pipeline

1. **In the pipeline configuration:**
   - **Description:** `Chayenity FastAPI CI/CD Pipeline`
   - **Discard old builds:** Check this and set to keep 10 builds

2. **Pipeline Definition:**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/CHAYENITY/chayenity.git`
   - **Credentials:** Select your GitHub credentials (if needed)
   - **Branch:** `feat/srv/buddy-system`
   - **Script Path:** `partCI_CD/main/Jenkinsfile`

3. **Click "Save"**

## 🗄️ Database Setup for Tests

### Step 1: Run PostgreSQL for Testing

1. **Create a test database container:**
   ```bash
   docker run -d ^
     --name postgres-test ^
     -e POSTGRES_DB=chayenity_test ^
     -e POSTGRES_USER=postgres ^
     -e POSTGRES_PASSWORD=password ^
     -p 5432:5432 ^
     --restart unless-stopped ^
     postgres:15-alpine
   ```

2. **Verify database is running:**
   ```bash
   docker logs postgres-test
   ```

### Step 2: Create Docker Network (Optional)

For better container communication:

```bash
docker network create chayenity-network
docker network connect chayenity-network jenkins-chayenity
docker network connect chayenity-network postgres-test
docker network connect chayenity-network sonarqube
```

## ▶️ Running the Pipeline

### Step 1: Manual Pipeline Execution

1. **From Jenkins dashboard, click on "chayenity-pipeline"**
2. **Click "Build Now"**
3. **Monitor the build progress in real-time**

### Step 2: Understanding Pipeline Stages

The pipeline includes these stages:

1. **Checkout:** Downloads code from GitHub
2. **Setup Environment:** Installs Python dependencies using Poetry
3. **Run Tests & Coverage:** Executes unit and integration tests
4. **SonarQube Analysis:** Performs code quality analysis
5. **Build Docker Image:** Creates production Docker image
6. **Deploy Container:** Runs the application container
7. **Push to Registry:** Uploads image to Docker Hub

### Step 3: Monitoring Build Progress

1. **Click on the build number** (e.g., "#1")
2. **Click "Console Output"** to see detailed logs
3. **Use "Pipeline Steps"** view for stage-by-stage progress

### Expected Build Time: 5-15 minutes (depending on your system)

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Docker Permission Denied
```
Error: Got permission denied while trying to connect to Docker daemon
```
**Solution:**
```bash
# Restart Jenkins container with proper Docker access
docker restart jenkins-chayenity
```

#### Issue 2: SonarQube Connection Failed
```
Error: Unable to connect to SonarQube server
```
**Solution:**
1. Verify SonarQube is running: `docker ps | grep sonarqube`
2. Check SonarQube logs: `docker logs sonarqube`
3. Ensure correct URL in Jenkins configuration

#### Issue 3: Python/Poetry Installation Issues
```
Error: poetry: command not found
```
**Solution:**
1. Rebuild Jenkins image: `docker build -t jenkins-chayenity:latest -f Dockerfile .`
2. Restart container with new image

#### Issue 4: Database Connection Issues
```
Error: could not connect to server: Connection refused
```
**Solution:**
1. Ensure PostgreSQL container is running
2. Check network connectivity between containers

### Debug Commands

```bash
# Check all containers status
docker ps -a

# View container logs
docker logs jenkins-chayenity
docker logs sonarqube
docker logs postgres-test

# Enter Jenkins container for debugging
docker exec -it jenkins-chayenity bash

# Check Jenkins disk usage
docker exec jenkins-chayenity df -h
```

## 📊 Monitoring and Maintenance

### Daily Monitoring

1. **Check build status** on Jenkins dashboard
2. **Review SonarQube** code quality metrics
3. **Monitor Docker Hub** for successful image pushes

### Weekly Maintenance

1. **Clean up old Docker images:**
   ```bash
   docker image prune -f
   docker container prune -f
   ```

2. **Backup Jenkins configuration:**
   ```bash
   docker exec jenkins-chayenity tar -czf /tmp/jenkins-backup.tar.gz /var/jenkins_home
   docker cp jenkins-chayenity:/tmp/jenkins-backup.tar.gz ./jenkins-backup-$(date +%Y%m%d).tar.gz
   ```

3. **Update SonarQube** if needed

### Performance Optimization

1. **Increase Jenkins memory** if builds are slow:
   ```bash
   # Stop container and run with more memory
   docker stop jenkins-chayenity
   docker run -d --name jenkins-chayenity -m 4g --memory-swap 4g [other options]
   ```

2. **Enable parallel test execution** in Jenkinsfile
3. **Use Docker layer caching** for faster builds

## 🎯 Success Metrics

A successful pipeline should show:

- ✅ **All stages green** in Jenkins
- ✅ **Code coverage > 80%** in SonarQube
- ✅ **No critical security vulnerabilities**
- ✅ **Docker image successfully pushed** to registry
- ✅ **Application healthy** on http://localhost:8000

## 🔗 Useful URLs

- **Jenkins Dashboard:** http://localhost:8080
- **SonarQube Dashboard:** http://localhost:9000
- **Application (after deployment):** http://localhost:8000
- **Application Health Check:** http://localhost:8000/health

## 📞 Support

If you encounter issues:

1. **Check this troubleshooting section**
2. **Review container logs** using debug commands
3. **Consult Jenkins and SonarQube documentation**
4. **Ask team members** familiar with the setup

---

**Note:** This guide assumes you're running on Windows with Docker Desktop. Adjust commands for Linux/macOS if needed.

**Created:** October 2025  
**Version:** 1.0  
**Project:** Chayenity FastAPI CI/CD Pipeline