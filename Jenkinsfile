pipeline {
    agent  {
        docker { image 'python:3.7-alpine'}
    }

    stages {
        stage ('Test') {
            steps {
                script {
                    python --version
                    python3 -m venv env
                    source ./env/bin/activate
                    pip install -r test_requirements.txt
                }
            }
        }
    }
}
