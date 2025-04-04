pipeline {
    agent { dockerfile true } // Use Dockerfile in workspace

    environment {
        TARGET_ENV = ''
        CREDENTIALS_ID = ''
        TARGET_ORG_ID = ''
    }

    options { timestamps() }

    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    // Ensure env.BRANCH_NAME is available (usually set by Jenkins)
                    def currentBranch = env.BRANCH_NAME ?: error("Could not determine branch name.")
                    echo "Building branch: ${currentBranch}"

                    if (currentBranch == 'qa') {
                        env.TARGET_ENV = 'qa'
                        env.CREDENTIALS_ID = 'qa-target-api-key'
                        env.TARGET_ORG_ID = env.QA_TARGET_ORG_ID ?: error("Jenkins Global Variable QA_TARGET_ORG_ID not set.")
                        echo "Configured for QA environment."
                    } else if (currentBranch == 'prod') {
                        env.TARGET_ENV = 'prod'
                        env.CREDENTIALS_ID = 'prod-target-api-key'
                        env.TARGET_ORG_ID = env.PROD_TARGET_ORG_ID ?: error("Jenkins Global Variable PROD_TARGET_ORG_ID not set.")
                        echo "Configured for Production environment."
                    } else {
                        error("Branch ${currentBranch} is not a deployable branch (qa or prod).")
                    }

                    if (env.CREDENTIALS_ID == '' || env.TARGET_ORG_ID == '') {
                         error("Failed to set environment variables correctly for branch ${currentBranch}.")
                    }
                }
            }
        }

    stage('Install Dependencies') {
        steps {
            sh 'echo "Creating Python virtual environment..."'
            // Create a virtual environment named '.venv' in the workspace
            sh 'python3 -m venv .venv'

            sh 'echo "Installing Python dependencies into venv..."'
            // Use the pip from the virtual environment to install packages
            sh '.venv/bin/pip install --no-cache-dir -r requirements.txt' // Changed command

            sh 'echo "Installing Node.js dependencies..."'
            sh 'npm ci --omit=dev'
        }
    }

stage('Push Configuration') {
     steps {
         withCredentials([string(credentialsId: env.CREDENTIALS_ID, variable: 'TARGET_API_KEY')]) {
             script {
                 echo "Running push_config.py for environment: ${env.TARGET_ENV}"
                 echo "Using ORG_ID: ${env.TARGET_ORG_ID}"
                 echo "API Key is set (value will be masked in logs)"
                 sh '''
                    export PATH=$(pwd)/node_modules/.bin:$PATH
                    echo "Executing python script using venv..."
                    # Use the python from the venv
                    .venv/bin/python push_config.py
                 ''' // Changed command
             }
         }
     }
 }
    } // End stages

    post {
        always { echo 'Pipeline finished.' }
        success { echo 'Configuration push succeeded!' }
        failure { echo 'Configuration push failed!' }
    } // End post
} // End pipeline