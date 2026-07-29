#!/bin/bash

HOST="110.78.210.129"
USER="administrator"
PASS="P@ssw0rd1234"
FILE="datax_deploy_3001.tar.gz"

echo "📦 Packing project..."
tar --exclude='node_modules' --exclude='.git' --exclude='dist' -czf $FILE .

echo "🚀 Uploading to $HOST..."
expect <<EOF
set timeout 600
spawn scp $FILE $USER@$HOST:/home/$USER/
expect {
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    "password:" {
        send "$PASS\r"
    }
}
expect eof
EOF

echo "🛠️  Deploying on $HOST..."
expect <<EOF
set timeout 1800
spawn ssh -t $USER@$HOST "mkdir -p intelligist_datax_deploy_3001_3001 && tar -xzf $FILE -C intelligist_datax_deploy_3001_3001 && cd intelligist_datax_deploy_3001_3001 && sudo docker-compose -f docker-compose.3001.yml up -d --build"
expect {
    "password for administrator:" {
        send "$PASS\r"
        exp_continue
    }
    "password:" {
        send "$PASS\r"
        exp_continue
    }
    eof
}
EOF

echo "✅ Done!"
rm $FILE
