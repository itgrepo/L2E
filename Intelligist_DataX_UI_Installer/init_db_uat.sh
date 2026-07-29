#!/bin/bash
echo "🗄️ Performing Intelligist DataX Database Restoration..."

# Check if sudo is needed for docker commands
DOCKER_PREFIX=""
if ! docker ps >/dev/null 2>&1; then
    if sudo docker ps >/dev/null 2>&1; then
        DOCKER_PREFIX="sudo "
        echo "ℹ️  Using sudo for Docker commands"
    fi
fi

# Load database configurations from .env if it exists
MYSQL_USER="astro"
MYSQL_PASSWORD="password123"
MYSQL_DATABASE="datax_db_3001"

if [ -f .env ]; then
    echo "Reading credentials from .env..."
    # Parse unquoted or quoted values safely
    ENV_USER=$(grep -E "^MYSQL_USER=" .env | cut -d'=' -f2- | tr -d "'\"")
    ENV_PASS=$(grep -E "^MYSQL_PASSWORD=" .env | cut -d'=' -f2- | tr -d "'\"")
    ENV_DB=$(grep -E "^MYSQL_DATABASE=" .env | cut -d'=' -f2- | tr -d "'\"")
    
    if [ ! -z "$ENV_USER" ]; then MYSQL_USER="$ENV_USER"; fi
    if [ ! -z "$ENV_PASS" ]; then MYSQL_PASSWORD="$ENV_PASS"; fi
    if [ ! -z "$ENV_DB" ]; then MYSQL_DATABASE="$ENV_DB"; fi
fi

# Wait for DB initialization to be complete (temporary server finished setup)
echo "Waiting for MariaDB initialization to complete..."
MAX_TRIES=15
COUNT=0
while ! ${DOCKER_PREFIX}docker logs datax_db_3001 2>&1 | grep -q "init process done"; do
    echo "Waiting for init process... ($((++COUNT))/$MAX_TRIES)"
    sleep 2
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo "⚠️ Warning: MariaDB initialization log not found, proceeding anyway."
        break
    fi
done

# Wait for DB socket to be ready
echo "Waiting for MariaDB port to start..."
COUNT=0
while ! ${DOCKER_PREFIX}docker exec -e MYSQL_PWD="${MYSQL_PASSWORD}" datax_db_3001 mysqladmin ping -u"${MYSQL_USER}" --silent; do
    echo "Waiting for database connection... ($((++COUNT))/$MAX_TRIES)"
    sleep 2
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo "❌ Error: MariaDB did not start in time."
        exit 1
    fi
done

# 1. Full Database Dump
if [ -f intelligist_datax_full_dump.sql ]; then
    echo "Step 1: Importing full Intelligist DataX database dump (intelligist_datax_full_dump.sql)..."
    ${DOCKER_PREFIX}docker exec -i -e MYSQL_PWD="${MYSQL_PASSWORD}" datax_db_3001 mysql -u"${MYSQL_USER}" "${MYSQL_DATABASE}" < intelligist_datax_full_dump.sql
else
    echo "❌ Error: intelligist_datax_full_dump.sql not found!"
    exit 1
fi

echo "✅ Intelligist DataX Database restoration complete!"
