pipeline {
    agent  {
        docker { image 'python:3.7-alpine'}
    }

    stages {
        stage ('Test') {
            steps {
                sh 'python --version'
                sh 'python3 -m venv env'
                sh 'source ./env/bin/activate'
                sh 'pip install -r test_requirements.txt'
            }
        }
    }
}
