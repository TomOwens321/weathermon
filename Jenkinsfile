pipeline {
    agent  { ('any') }

    stages {
        stage ('Test') {
            steps {
                sh 'python --version'
                sh 'python3 -m venv env'
                sh 'source ./env/bin/activate'
            }
        }
    }
}
