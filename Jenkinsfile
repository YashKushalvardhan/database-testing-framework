pipeline {
    agent any

environment {
    DB_HOST = 'host.docker.internal'
    DB_PORT = '5433'
    DB_NAME = 'ecommerce_test_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
}

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Start Postgres (Docker)') {
            steps {
                sh 'docker compose down -v || true'
                sh 'docker compose up -d'
                sh 'sleep 10'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install --upgrade pip'
                sh './venv/bin/pip install -r requirements.txt'
            }
        }
        stage('Load Database Schema') {
            steps {
                sh '''
                ./venv/bin/python -c "
        import psycopg2
        conn = psycopg2.connect(host='host.docker.internal', port='5433', dbname='ecommerce_test_db', user='postgres', password='postgres')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(open('db/schema.sql').read())
        cur.execute(open('db/seed_data.sql').read())
        cur.close()
        conn.close()
        print('Schema and seed data loaded successfully')
        "
                '''
            }
}
        stage('Run Tests') {
            steps {
                sh './venv/bin/python -m pytest -v --html=report.html --self-contained-html'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report.html', allowEmptyArchive: true
            sh 'docker compose down -v || true'
        }
    }
}