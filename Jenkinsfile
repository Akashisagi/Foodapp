pipeline {
    agent any

    stages {
        stage('checkout') {
            steps {
                git "https://github.com/Akashisagi/Foodapp.git"
            }
        }

        stage('test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    python -m unittest discover -s tests
                '''
            }
        }

        stage('build') {
            steps {
                sh "docker build -t foodapp ."
            }
        }

        stage('cont-test') {
            steps {
                sh '''
                    docker run -itd --name test-cont -p 8081:5000 foodapp

                    success=1

                    for i in {1..10}; do
                        echo "HTTP check attempt $i"

                        if curl -f http://localhost:8081/; then
                            success=0
                            break
                        fi

                        sleep 2
                    done

                    if ["$success" -ne 0]; then
                        echo "Application health check failed"
                        exit 1
                    fi

                    echo "Application is healthy"
                '''
            }

            post {
                always {
                    sh "docker rm -f test-cont"
                }
            }
        }
        stage('push') {
          steps{
            withCredentials([usernamePassword(
              credentialID: 'dockerhub-creds',
              usernameVariable: 'dockerhub_user',
              passwordVariable: 'dockerhub_token'
            )]) {
             sh '''
               echo "$dockerhub_token" | docker login -u "$dockerhub_user" --password-stdin
               docker push akashyogi/foodapp:1
             '''
             }
          }
        }
    }
}

