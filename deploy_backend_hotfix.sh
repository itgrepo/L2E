#!/bin/bash
set -Eeuo pipefail
HOST="134.185.172.127"
USER="ubuntu"
KEY="${SSH_KEY_PATH:-}"
DIR="~/Intelligist_DataX_Deploy_3003"

echo "Syncing backend files..."
rsync -avz --exclude '__pycache__' --exclude 'venv' -e "ssh -i $KEY -o StrictHostKeyChecking=no" ./backendold/Astro_backend/ $USER@$HOST:$DIR/backendold/Astro_backend/

echo "Redeploying backend container..."
ssh -i $KEY -o StrictHostKeyChecking=no $USER@$HOST << 'SSH_EOF'
cd ~/Intelligist_DataX_Deploy_3003
sudo docker-compose -f docker-compose.3003.yml stop backend
sudo docker-compose -f docker-compose.3003.yml rm -f backend
sudo docker-compose -f docker-compose.3003.yml up -d --build backend
SSH_EOF
echo "Backend Hotfix Deployed."
