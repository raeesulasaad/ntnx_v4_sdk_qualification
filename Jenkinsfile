pipeline {
    agent { dockerContainer { image 'centos:centos7.7.1908'
                    args '-u root'} }
    environment {
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('install modules') {
            steps {
                sh '''
            yum -y install python3
            yum -y install git
            python3 -m pip  install -r requirements.txt
            '''
            }
        }
        stage('build') {
            steps {
                sh 'python3  --version'
            }
        }
        stage('test') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${JITA_CREDENTIALS}", 
                        usernameVariable: 'JITA_USER', 
                        passwordVariable: 'JITA_PASS'
                        ),
                usernamePassword(
                        credentialsId: 'SDK_QUAL_GIT_CRED', 
                        usernameVariable: 'GIT_USER', 
                        passwordVariable: 'GIT_PASS'
                        ),]) {
                    sh '''
                        PYTHONUNBUFFERED=1  python3 qualify_sdk.py  --job_profile ${JOB_PROFILE} --name_space ${NAMESPACE} --v4_version ${V4_VERSION} --pc_branch ${PC_BRANCH} --git_username ${GIT_USER} --git_token ${GIT_PASS} --jita_username ${JITA_USER} --jita_password ${JITA_PASS} 
                    '''
                }
              }
            }
        }
    }
