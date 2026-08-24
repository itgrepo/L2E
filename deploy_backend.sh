#!/bin/bash
echo "Deploying backend..."
rsync -avz --exclude 'venv' --exclude '__pycache__' -e "ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no" ./backendold/Astro_backend/app/ServiceConfig/access_service.py ubuntu@134.185.172.127:~/intelligist_dataX/backendold/Astro_backend/app/ServiceConfig/access_service.py
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "sudo docker rm -f datax_backend_3003 && cd intelligist_dataX && sudo docker-compose -f docker-compose.3003.yml --project-name intelligist_datax_deploy_3003_3003 up -d --build backend"
echo "Done"
