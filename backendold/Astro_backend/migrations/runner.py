import mysql.connector
import os
import sys

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', '127.0.0.1'),
        user=os.environ.get('MYSQL_USER', 'astro'),
        password=os.environ.get('MYSQL_PASSWORD', 'password123'),
        database=os.environ.get('MYSQL_DATABASE', 'datax_db_3003'),
        port=os.environ.get('MYSQL_PORT', 3306)
    )

def init_migrations(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR(255) PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

def apply_migrations():
    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    
    init_migrations(cursor)
    
    migrations_dir = os.path.dirname(__file__)
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql') and f.startswith('V')])
    
    cursor.execute("SELECT version FROM schema_migrations")
    applied_versions = set([row[0] for row in cursor.fetchall()])
    
    for filename in migration_files:
        version = filename.split('__')[0]
        if version not in applied_versions:
            print(f"Applying {filename}...")
            filepath = os.path.join(migrations_dir, filename)
            with open(filepath, 'r') as f:
                sql = f.read()
            
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            try:
                for statement in statements:
                    cursor.execute(statement)
                cursor.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
                conn.commit()
                print(f"Successfully applied {filename}")
            except Exception as e:
                conn.rollback()
                print(f"Error applying {filename}: {e}")
                sys.exit(1)
        else:
            print(f"Skipping {filename}, already applied.")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    apply_migrations()
