#!/bin/bash
set -Eeuo pipefail

HOST="134.185.172.127"
USER="administrator"
FILE="datax_deploy_3003.tar.gz"
SSH_KEY="${SSH_KEY_PATH:-}"

if [ -z "$SSH_KEY" ]; then
    echo "Error: SSH_KEY_PATH is not set."
    exit 1
fi

echo "📦 Packing project..."
tar --exclude='node_modules' --exclude='.git' --exclude='dist' -czf $FILE .

echo "🚀 Uploading to $HOST..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no $FILE $USER@$HOST:/home/$USER/

echo "🛠️  Deploying on $HOST..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $USER@$HOST "mkdir -p intelligist_datax_deploy_3003_3003 && tar -xzf $FILE -C intelligist_datax_deploy_3003_3003 && cd intelligist_datax_deploy_3003_3003 && sudo docker-compose -f docker-compose.3003.yml up -d --build"

echo "✅ Done!"
rm $FILE
