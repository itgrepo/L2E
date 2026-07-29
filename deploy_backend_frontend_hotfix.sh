#!/bin/bash
set -Eeuo pipefail
HOST="134.185.172.127"
USER="ubuntu"
KEY="${SSH_KEY_PATH:-}"
DIR="~/Intelligist_DataX_Deploy_3003"

echo "Syncing files..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'dist' -e "ssh -i $KEY -o StrictHostKeyChecking=no" ./backendold/Astro_backend/ $USER@$HOST:$DIR/backend/
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'dist' -e "ssh -i $KEY -o StrictHostKeyChecking=no" ./frontend/ $USER@$HOST:$DIR/frontend/

echo "Redeploying backend and frontend..."
ssh -i $KEY -o StrictHostKeyChecking=no $USER@$HOST << 'SSH_EOF'
cd ~/Intelligist_DataX_Deploy_3003
sudo docker-compose -f docker-compose.3003.yml stop backend frontend
sudo docker-compose -f docker-compose.3003.yml rm -f backend frontend
sudo docker-compose -f docker-compose.3003.yml up -d --build backend frontend
SSH_EOF
echo "Hotfix Deployed."
