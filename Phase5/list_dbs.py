import os
import psycopg2

def load_env():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(parent_dir, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    k = parts[0].strip()
                    v = parts[1].strip().strip("'").strip('"')
                    os.environ[k] = v

def main():
    load_env()
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 5432))
    user = os.getenv("DB_USER_SECRET", os.getenv("DB_USER", "postgres"))
    password = os.getenv("DB_PASSWORD_SECRET", os.getenv("DB_PASSWORD", "postgres"))

    try:
        # Connect to default database 'postgres' to list all databases
        conn = psycopg2.connect(
            host=host,
            port=port,
            database="postgres",
            user=user,
            password=password
        )
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [r[0] for r in cur.fetchall()]
        print("Available databases in your PostgreSQL server:")
        for db in dbs:
            print(f"  - {db}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
