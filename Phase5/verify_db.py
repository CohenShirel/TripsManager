import os
import json
import sys

def verify():
    print("===================================================")
    print("🔍 Database Verification Tool")
    print("===================================================")
    
    # Load parent directory .env file if it exists
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
        print("Loaded environment variables from project root .env file.")

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Retrieve credentials from loaded env variables with default fallbacks
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 5432))
    name = os.getenv("DB_NAME_SECRET", os.getenv("DB_NAME", "postgres"))
    user = os.getenv("DB_USER_SECRET", os.getenv("DB_USER", "postgres"))
    password = os.getenv("DB_PASSWORD_SECRET", os.getenv("DB_PASSWORD", "postgres"))

    config = {
        "db_host": host,
        "db_port": port,
        "db_name": name,
        "db_user": user,
        "db_password": password
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("Loaded connection configuration from config.json (overrides .env)")
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}")
    
    # Mask password for printing
    masked_pwd = "********" if config['db_password'] else "none"
    print(f"Connection Target: {config['db_user']}@{config['db_host']}:{config['db_port']}/{config['db_name']} (Password: {masked_pwd})")
    
    try:
        import psycopg2
    except ImportError:
        print("[ERROR] psycopg2-binary package is not installed.")
        print("Please run: pip install psycopg2-binary")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=config["db_host"],
            port=config["db_port"],
            database=config["db_name"],
            user=config["db_user"],
            password=config["db_password"],
            connect_timeout=3
        )
        cur = conn.cursor()
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [r[0] for r in cur.fetchall()]
        
        print("\n✅ CONNECTION SUCCESSFUL!")
        print(f"Found {len(tables)} tables in 'public' schema:")
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM public.\"{t}\";")
            count = cur.fetchone()[0]
            print(f"  - {t} ({count} records)")
            
        # Check functions
        cur.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
        """)
        funcs = [r[0] for r in cur.fetchall()]
        print(f"\nFound {len(funcs)} functions:")
        for f in funcs:
            if 'calculate' in f or 'region' in f or 'update' in f:
                print(f"  - {f} (Routine matches!)")
            else:
                print(f"  - {f}")
                
        cur.close()
        conn.close()
        print("\nVerification completed successfully. You are ready to run the app!")
        
    except Exception as e:
        print("\n❌ CONNECTION FAILED!")
        print("Error Details:")
        print(f"  {e}")
        print("\nPossible solutions:")
        print("1. Make sure your docker containers are running: 'docker-compose up -d'")
        print("2. Verify your port mapping (usually 5432).")
        print("3. Check username, password and database name credentials.")
        print("4. Update your settings in the GUI config panel once launched.")
        sys.exit(1)

if __name__ == '__main__':
    verify()
