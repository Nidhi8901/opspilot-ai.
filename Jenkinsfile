pipeline {
    agent any

    environment {
        APP_NAME = 'opspilot-ai'
        IMAGE_TAG = "jenkins-${BUILD_NUMBER}"
        SONAR_HOST_URL = 'http://opspilot-sonarqube:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                  docker run --rm                     --volumes-from jenkins                     -w "$WORKSPACE"                     python:3.13-slim                     sh -c "pip install --no-cache-dir -r backend/requirements.txt >/dev/null && pytest -q"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('OpsPilot SonarQube') {
                    sh '''
                      docker run --rm                         --network opspilot-ci                         --volumes-from jenkins                         -w "$WORKSPACE"                         -e SONAR_HOST_URL="$SONAR_HOST_URL"                         -e SONAR_TOKEN="$SONAR_AUTH_TOKEN"                         sonarsource/sonar-scanner-cli:latest                         -Dsonar.projectKey=opspilot-ai                         -Dsonar.projectName="OpsPilot AI"                         -Dsonar.sources=backend,frontend                         -Dsonar.tests=tests                         -Dsonar.python.version=3.13                         -Dsonar.host.url="$SONAR_HOST_URL"                         -Dsonar.token="$SONAR_AUTH_TOKEN"
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                  docker build -t ${APP_NAME}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                  docker run --rm                     -v /var/run/docker.sock:/var/run/docker.sock                     aquasec/trivy:latest image                     --severity HIGH,CRITICAL                     --exit-code 0                     ${APP_NAME}:${IMAGE_TAG}
                '''
            }
        }
    }

    post {
        success {
            echo 'OpsPilot CI pipeline completed successfully.'
        }
        failure {
            echo 'OpsPilot CI pipeline failed. Check the failed stage logs.'
        }
    }
}
