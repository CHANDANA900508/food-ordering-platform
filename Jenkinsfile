pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Order API Docker image...'
                bat 'docker compose build order-api'
            }
        }

        stage('Start Environment') {
            steps {
                echo 'Starting PostgreSQL, Order API and Nginx...'
                bat 'docker compose up -d'
            }
        }

        stage('Wait for Services') {
            steps {
                echo 'Waiting for services...'
                bat 'timeout /t 15 /nobreak'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking Order API through Nginx...'
                bat 'curl --fail http://localhost:8080/health'
            }
        }

        stage('Create Test Order') {
            steps {
                echo 'Creating test food order...'
                bat 'curl --fail -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d "{\\"customer_name\\":\\"Jenkins\\",\\"food_item\\":\\"Burger\\",\\"quantity\\":2}"'
            }
        }

        stage('Retrieve Orders') {
            steps {
                echo 'Retrieving orders...'
                bat 'curl --fail http://localhost:8080/orders'
            }
        }
    }

    post {

        failure {
            echo 'Pipeline failed. Showing Docker Compose logs...'
            bat 'docker compose logs --tail=100'
        }

        always {
            echo 'Cleaning up application containers...'
            bat 'docker compose down'
        }
    }
}