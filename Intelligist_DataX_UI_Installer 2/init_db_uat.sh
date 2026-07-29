#!/bin/bash
echo "🗄️ Performing Intelligist DataX Database Restoration..."

# Load environment variables if .env exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Wait for DB to be ready
echo "Waiting for MariaDB to start (datax_db_3001)..."
MAX_TRIES=15
COUNT=0
while ! sudo docker exec datax_db_3001 mysqladmin ping -u${MYSQL_USER:-astro} -p${MYSQL_PASSWORD:-password123} --silent; do
    echo "Waiting for database connection... ($((++COUNT))/$MAX_TRIES)"
    sleep 2
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo "❌ Error: MariaDB did not start in time."
        exit 1
    fi
done

DB_CMD="sudo docker exec -i datax_db_3001 mysql -u${MYSQL_USER:-astro} -p${MYSQL_PASSWORD:-password123} ${MYSQL_DATABASE:-datax_db_3001}"

# 1. Full Database Dump
if [ -f intelligist_datax_full_dump.sql ]; then
    echo "Step 1: Importing full Intelligist DataX database dump (intelligist_datax_full_dump.sql)..."
    $DB_CMD < intelligist_datax_full_dump.sql
else
    echo "❌ Error: intelligist_datax_full_dump.sql not found!"
    exit 1
fi

echo "✅ Intelligist DataX Database restoration complete!"
