pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master',
                    url: 'https://github.com/Akashisagi/Foodapp.git'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -e
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    python -m unittest discover -s tests
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -e
                    docker build -t foodapp:${BUILD_NUMBER} .
                    docker tag foodapp:${BUILD_NUMBER} akashyogi/foodapp:${BUILD_NUMBER}
                '''
            }
        }

        stage('Container Test') {
            steps {
                sh '''
                    set -e
                    docker rm -f test-cont 2>/dev/null || true
                    docker run -d --name test-cont \
                        -p 8081:5000 \
                        akashyogi/foodapp:${BUILD_NUMBER}

                    success=1

                    for i in $(seq 1 10); do
                        echo "HTTP check attempt $i"

                        if curl -fsS http://localhost:8081/; then
                            success=0
                            break
                        fi

                        sleep 2
                    done

                    if [ "$success" -ne 0 ]; then
                        echo "Application health check failed"
                        docker logs test-cont
                        exit 1
                    fi

                    echo "Application is healthy"
                '''
            }

            post {
                always {
                    sh 'docker rm -f test-cont 2>/dev/null || true'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'dockerhub_user',
                        passwordVariable: 'dockerhub_token'
                    )
                ]) {
                    sh '''
                        set -e
                        echo "$dockerhub_token" |
                            docker login -u "$dockerhub_user" --password-stdin

                        docker push akashyogi/foodapp:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sshagent(credentials: ['jenkinsid']) {
                    sh '''
ssh ubuntu@10.0.90.76 "BUILD_NUMBER=$BUILD_NUMBER bash -s" <<'REMOTE'
set -e

echo "Pulling image version: $BUILD_NUMBER"
docker pull akashyogi/foodapp:$BUILD_NUMBER

echo "Stopping previous application container..."
docker rm -f food 2>/dev/null || true

echo "Starting new application container..."
docker run -d --name food -p 80:5000 akashyogi/foodapp:$BUILD_NUMBER

success=1

for i in $(seq 1 10); do
    echo "Deployment health check attempt $i"

    if curl -fsS http://localhost/ > /dev/null; then
        success=0
        echo "Application is healthy"
        break
    fi

    sleep 3
done

if [ "$success" -ne 0 ]; then
    echo "Deployment health check failed"
    docker logs food
    exit 1
fi

echo "Application deployed successfully"
REMOTE
                    '''
                }
            }
        }
    }
}

         
