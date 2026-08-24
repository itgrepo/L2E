#!/bin/bash
set -Eeuo pipefail

HOST="134.185.172.127"
USER="ubuntu"
FILE="datax_deploy_3003.tar.gz"
SSH_KEY="${SSH_KEY_PATH:-}"

if [ -z "$SSH_KEY" ]; then
    echo "Error: SSH_KEY_PATH is not set."
    exit 1
fi

echo "📦 Packing project..."
tar --exclude='node_modules' --exclude='.git' --exclude='dist' --exclude='*.tar.gz' --exclude='*.zip' -czf $FILE .

echo "🚀 Uploading to $HOST..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no $FILE $USER@$HOST:/home/$USER/

echo "🛠️  Deploying on $HOST..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $USER@$HOST "mkdir -p intelligist_datax_deploy_3003_3003 && tar -xzf $FILE -C intelligist_datax_deploy_3003_3003 && cd intelligist_datax_deploy_3003_3003 && sudo docker rm -f \$(sudo docker ps -aq -f name=backend_3003) \$(sudo docker ps -aq -f name=frontend_3003) 2>/dev/null || true && sudo docker-compose -f docker-compose.3003.yml up -d --build frontend backend"

echo "✅ Done!"
rm $FILE
