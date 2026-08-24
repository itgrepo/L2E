#!/bin/bash
echo "Deploying frontend components..."
rsync -avz --exclude 'node_modules' --exclude '.git' -e "ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no" ./frontend/src/views/CatalogView.vue ubuntu@134.185.172.127:~/intelligist_dataX/frontend/src/views/CatalogView.vue
rsync -avz --exclude 'node_modules' --exclude '.git' -e "ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no" ./frontend/src/views/DatasetDetailView.vue ubuntu@134.185.172.127:~/intelligist_dataX/frontend/src/views/DatasetDetailView.vue
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "sudo docker rm -f datax_frontend_3003 && cd intelligist_dataX && sudo docker-compose -f docker-compose.3003.yml --project-name intelligist_datax_deploy_3003_3003 up -d --build frontend"
echo "Done"
