#!/bin/bash
echo "Redeploying backend and frontend..."
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "cd intelligist_dataX/backendold/Astro_backend && sudo docker build -t intel_backend:latest ."
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "cd intelligist_dataX/frontend && npm install && npm run build"
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "cd intelligist_dataX && sudo docker build -t l2e-frontend -f frontend/Dockerfile frontend"
ssh -i ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 "cd intelligist_dataX && sudo docker-compose -f docker-compose.3003.yml up -d --force-recreate astro_backend_3003 frontend_3003"
echo "Done"
