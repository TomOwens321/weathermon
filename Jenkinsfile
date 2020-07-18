pipeline {
    agent 'rpi4b-1' {
        docker { image 'python:3.7-alpine'}
    }

    stages {
        stage ('Test') {
            steps {
                sh 'python --version'
            }
        }
    }
}