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
                sh "docker tag foodapp akashyogi/foodapp:${BUILD_NUMBER}"
            }
        }

        stage('cont-test') {
            steps {
                sh '''#!/bin/bash
                    docker run -itd --name test-cont -p 8081:5000 akashyogi/foodapp:${BUILD_NUMBER}
                    sleep 3

                    success=1

                    for i in {1..10}; do
                        echo "HTTP check attempt $i"

                        if curl -f http://localhost:8081/; then
                            success=0
                            break
                        fi

                        sleep 2
                    done

                    if [ "$success" -ne 0 ]; then
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
              credentialsId: 'dockerhub-creds',
              usernameVariable: 'dockerhub_user',
              passwordVariable: 'dockerhub_token'
            )]) {
             sh '''
               echo "$dockerhub_token" | docker login -u "$dockerhub_user" --password-stdin
               docker push akashyogi/foodapp:${BUILD_NUMBER}
             '''
             }
          }
        }
        stage('deploy') {
          steps{
            sshagent(credentials: ['jenkinsid']){
               sh '''
                   ssh ubuntu@10.0.90.76 "BUILD_NUMBER=$BUILD_NUMBER" bash -s <<'REMOTE'
                   set -e
                   docker pull akashyogi/foodapp:${BUILD_NUMBER}
                   docker rm -f food 2>/dev/null || true
                   docker run -itd --name food -p 80:5000 akashyogi/foodapp:${BUILD_NUMBER}
                   success=1
                   for i in $(seq 1 10);do 
                         echo "Health check attempt $i"
                         if curl -f http://localhost; then
                         echo "Application is healthy"
                                success=0
                                break
                                fi
                         if [ "$i" -lt 10 ]; then
                                sleep 3
                         fi
                   done
                   if [ "$success" -eq 1 ];then
                   echo "Application health check failed"
                   exit 1
                   fi
                   echo "application deployed successfully"
                   REMOTE
               '''
            }
          }
        }
    }
}

