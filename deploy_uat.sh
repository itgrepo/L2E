#!/bin/bash

echo "🚀 Starting UAT Deployment..."

# 1. Build and Start Containers
sudo docker-compose -f docker-compose.uat.yml build --no-cache frontend
sudo docker-compose -f docker-compose.uat.yml up -d --build

# 2. Initialize Database
chmod +x init_db_uat.sh
./init_db_uat.sh

echo "---------------------------------------"
echo "✅ Deployment Complete!"
echo "---------------------------------------"
echo "Frontend: http://localhost:3001"
echo "Backend:  http://localhost:3000"
echo "Database: localhost:3307"
echo "---------------------------------------"
echo "💡 Tip: หากต้องการดู Logs ให้รัน: docker-compose -f docker-compose.uat.yml logs -f"
