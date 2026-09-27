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
                  NET="opspilot-test-${BUILD_NUMBER}"
                  DB="opspilot-test-db-${BUILD_NUMBER}"

                  docker rm -f "$DB" >/dev/null 2>&1 || true
                  docker network rm "$NET" >/dev/null 2>&1 || true
                  docker network create "$NET"

                  docker run -d \
                    --name "$DB" \
                    --network "$NET" \
                    --network-alias db \
                    -e POSTGRES_USER=opspilot \
                    -e POSTGRES_PASSWORD=opspilot \
                    -e POSTGRES_DB=opspilot \
                    pgvector/pgvector:pg16

                  READY=0
                  for i in $(seq 1 30); do
                    if docker exec "$DB" pg_isready -U opspilot -d opspilot >/dev/null 2>&1; then
                      READY=1
                      break
                    fi
                    sleep 2
                  done

                  if [ "$READY" -ne 1 ]; then
                    echo "PostgreSQL did not become ready"
                    docker logs "$DB"
                    docker rm -f "$DB" >/dev/null 2>&1 || true
                    docker network rm "$NET" >/dev/null 2>&1 || true
                    exit 1
                  fi

                  set +e

                  docker run --rm \
                    --network "$NET" \
                    --volumes-from jenkins \
                    -w "$WORKSPACE" \
                    -e PYTHONPATH="$WORKSPACE" \
                    -e DATABASE_URL="postgresql+psycopg://opspilot:opspilot@db:5432/opspilot" \
                    -e AWS_REGION="ap-south-1" \
                    -e AWS_DEFAULT_REGION="ap-south-1" \
                    -e BEDROCK_MODEL_ID="apac.amazon.nova-lite-v1:0" \
                    -e EMBEDDING_MODEL_ID="amazon.titan-embed-text-v2:0" \
                    python:3.13-slim \
                    sh -ec '
                      pip install --no-cache-dir -r backend/requirements.txt >/dev/null

                      python - <<PY
from sqlalchemy import text
from backend.database import Base, engine
import backend.models

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

Base.metadata.create_all(bind=engine)
print("TEST_DATABASE_READY")
PY

                      uvicorn backend.main:app \
                        --host 127.0.0.1 \
                        --port 8000 \
                        >/tmp/opspilot-test-app.log 2>&1 &

                      APP_PID=$!

                      cleanup() {
                        kill "$APP_PID" >/dev/null 2>&1 || true
                      }
                      trap cleanup EXIT

                      python - <<PY
import time
import urllib.request

url = "http://127.0.0.1:8000/health"

for attempt in range(30):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                print("TEST_APP_READY")
                break
    except Exception:
        time.sleep(1)
else:
    print(open("/tmp/opspilot-test-app.log").read())
    raise SystemExit("OpsPilot test server did not become ready")
PY

                      pytest -q
                    '

                  TEST_STATUS=$?

                  docker rm -f "$DB" >/dev/null 2>&1 || true
                  docker network rm "$NET" >/dev/null 2>&1 || true

                  exit "$TEST_STATUS"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('OpsPilot SonarQube') {
                    sh '''
                      docker run --rm \
                        --network opspilot-ci \
                        --volumes-from jenkins \
                        -w "$WORKSPACE" \
                        -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                        -e SONAR_TOKEN="$SONAR_AUTH_TOKEN" \
                        sonarsource/sonar-scanner-cli:latest \
                        -Dsonar.projectKey=opspilot-ai \
                        -Dsonar.projectName="OpsPilot AI" \
                        -Dsonar.sources=backend,frontend \
                        -Dsonar.tests=tests \
                        -Dsonar.python.version=3.13 \
                        -Dsonar.host.url="$SONAR_HOST_URL" \
                        -Dsonar.token="$SONAR_AUTH_TOKEN"
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
                  docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy:latest image \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    ${APP_NAME}:${IMAGE_TAG}
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
        always {
            sh '''
              docker ps -aq --filter "name=opspilot-test-db-${BUILD_NUMBER}" | xargs -r docker rm -f >/dev/null 2>&1 || true
              docker network rm "opspilot-test-${BUILD_NUMBER}" >/dev/null 2>&1 || true
            '''
        }
    }
}
