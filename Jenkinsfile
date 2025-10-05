// Jenkinsfile for CI/CD pipeline using Jenkins
pipeline {
    agent any

    environment {
        // SonarQube token (stored in Jenkins credentials)
        SONARQUBE = credentials('sonarqube_token')
        
        // Test secrets (safe for CI)
        REFRESH_SECRET_KEY = 'test_refresh_secret_key_for_ci'
        ACCESS_SECRET_KEY = 'test_access_secret_key_for_ci'
        FRONTEND_URL = 'http://localhost:3000'
        BACKEND_URL = 'http://localhost:8000'
    }

    stages {
        stage('Setup Python Environment') {
            steps {
                dir('server') {
                    sh '''
                    echo "===== Setting up Python Virtual Environment ====="
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install poetry
                    poetry config virtualenvs.create false
                    
                    echo "===== Poetry version: $(poetry --version) ====="
                    
                    echo "===== Checking and updating poetry.lock ====="
                    if [ -f poetry.lock ]; then
                        echo "poetry.lock exists, checking if it needs update..."
                        # Try to install first, if it fails due to lock file issues, regenerate
                        if poetry install; then
                            echo "✅ Dependencies installed successfully"
                        else
                            echo "⚠️ Install failed, regenerating lock file..."
                            poetry lock
                            poetry install
                        fi
                    else
                        echo "poetry.lock not found, generating..."
                        poetry lock
                        poetry install
                    fi
                    
                    pip install pytest-cov

                    echo "Python version: $(python --version)"
                    echo "Poetry version: $(poetry --version)"
                    pip list | grep -E "pytest|coverage|poetry"
                    '''
                }
            }
        }

        stage('Configure Test Environment (SQLite)') {
            steps {
                dir('server') {
                    sh '''
                    echo "===== Configuring SQLite for tests ====="
                    cat > .env << EOF
                    ENVIRONMENT=test
                    POSTGRES_SERVER=sqlite
                    POSTGRES_DB=test.db
                    POSTGRES_USER=test
                    POSTGRES_PASSWORD=test
                    POSTGRES_PORT=0
                    REFRESH_SECRET_KEY=test_refresh_secret_key_for_ci
                    ACCESS_SECRET_KEY=test_access_secret_key_for_ci
                    FRONTEND_URL=http://localhost:3000
                    BACKEND_URL=http://localhost:8000
                    EOF

                    echo "Final .env:"
                    cat .env
                    '''
                }
            }
        }

        stage('Run Tests & Generate Coverage') {
            steps {
                dir('server') {
            sh '''
            . venv/bin/activate

            echo "=== Verifying configuration ==="
            
            # Create a temporary Python script
            cat > verify_config.py << 'EOF'
            try:
                from app.configs.app_config import app_config
                print('✅ Configuration loaded successfully')
                print(f'DB URI: {app_config.SQLALCHEMY_DATABASE_URI}')
            except Exception as e:
                print(f'❌ Configuration failed: {e}')
                exit(1)
            EOF

            python verify_config.py
            rm verify_config.py

            echo "=== Running tests ==="
            pytest app/tests/ \
                --maxfail=1 \
                --disable-warnings \
                -v \
                --cov=app \
                --cov-report=xml:coverage.xml \
                --cov-report=term-missing \
                --ignore=app/tests/dev \
                --ignore=app/tests/integration

            if [ -f coverage.xml ]; then
                echo "✅ Coverage report generated"
                ls -lh coverage.xml
            else
                echo "⚠️ Warning: coverage.xml not found"
            fi
            '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                dir('server') {
                    withSonarQubeEnv('Sonarqube') {
                        sh '''
                        if [ ! -f coverage.xml ]; then
                            echo "⚠️ No coverage.xml — SonarQube will run without coverage"
                        fi

                        sonar-scanner \
                            -Dsonar.projectKey=chayenity-server \
                            -Dsonar.sources=app \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.exclusions=**/*.pyc,**/.venv/**,**/venv/**,**/__pycache__/**,**/migrations/**,**/uploads/**,**/scripts/**
                        '''
                    }
                }
            }
        }

        // ===== DEPLOYMENT STAGES (only on main branch) =====
        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                dir('server') {
                    sh '''
                    echo "===== Building Docker Image ====="
                    docker build -t chayenity-server:latest .
                    '''
                }
            }
        }

        stage('Push to Docker Registry') {
            when {
                branch 'main'
            }
            steps {
                dir('server') {
                    withCredentials([string(
                        credentialsId: 'dockerhub-token',
                        variable: 'DOCKER_TOKEN'
                    )]) {
                        sh '''
                        DOCKER_USER="${DOCKER_HUB_USER:-psu6510110357}"

                        echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin

                        IMAGE_TAG=${BUILD_NUMBER:-latest}
                        GIT_SHA=$(git rev-parse --short=8 HEAD 2>/dev/null || echo "unknown")

                        docker tag chayenity-server:latest $DOCKER_USER/chayenity-server:${IMAGE_TAG}
                        docker push $DOCKER_USER/chayenity-server:${IMAGE_TAG}

                        docker tag chayenity-server:latest $DOCKER_USER/chayenity-server:${GIT_SHA}
                        docker push $DOCKER_USER/chayenity-server:${GIT_SHA}

                        docker tag chayenity-server:latest $DOCKER_USER/chayenity-server:latest
                        docker push $DOCKER_USER/chayenity-server:latest

                        docker logout

                        echo "✅ Pushed images:"
                        echo "  - $DOCKER_USER/chayenity-server:${IMAGE_TAG}"
                        echo "  - $DOCKER_USER/chayenity-server:${GIT_SHA}"
                        echo "  - $DOCKER_USER/chayenity-server:latest"
                        '''
                    }
                }
            }
        }

        // Optional: Uncomment if you want to deploy to a test server on main
        /*
        stage('Deploy Container') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                docker stop chayenity-server-container || true
                docker rm chayenity-server-container || true
                docker run -d --name chayenity-server-container -p 8000:8000 \
                    -e POSTGRES_SERVER=host.docker.internal \
                    -e POSTGRES_DB=chayenity \
                    -e POSTGRES_USER=postgres \
                    -e POSTGRES_PASSWORD=password \
                    -e REFRESH_SECRET_KEY=production_refresh_secret \
                    -e ACCESS_SECRET_KEY=production_access_secret \
                    -e FRONTEND_URL=http://localhost:3000 \
                    -e BACKEND_URL=http://localhost:8000 \
                    chayenity-server:latest
                '''
            }
        }
        */
    }

    post {
        always {
            echo "Pipeline finished. Cleaning up..."
            // Clean up any leftover test containers (if you ever re-enable them)
            sh 'docker stop postgres-test 2>/dev/null || true'
            sh 'docker rm postgres-test 2>/dev/null || true'
        }
    }
}