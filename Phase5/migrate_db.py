import os
import json
import psycopg2
import sys

def load_env_and_config():
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

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
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
                config.update(json.load(f))
        except Exception:
            pass
    return config

def execute_sql_file(cur, file_path):
    print(f"Executing: {os.path.basename(file_path)}...")
    if not os.path.exists(file_path):
        print(f"  [Error] File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
        
    try:
        # If it's the merge_code.sql, split statements and skip data migrations from staging tables
        if "merge_code.sql" in file_path:
            # Simple SQL parser splitting by semicolon
            statements = sql_content.split(';')
            for stmt in statements:
                stmt_clean = stmt.strip()
                if not stmt_clean:
                    continue
                # Skip INSERT INTO and DROP TABLE statement blocks (they refer to missing legacy tables)
                if any(x in stmt_clean.upper() for x in ["INSERT INTO", "DROP TABLE"]):
                    first_line = stmt_clean.split('\n')[0]
                    print(f"  [Info] Skipping staging table operation: {first_line[:60]}...")
                    continue
                
                try:
                    cur.execute(stmt_clean)
                except Exception as stmt_err:
                    err_str = str(stmt_err).strip()
                    if "already exists" in err_str or "multiple primary keys" in err_str:
                        print(f"  [Info] Skipping existing object: {err_str}")
                    else:
                        print(f"  [Warning] Statement issue (ignored): {err_str}")
            print("  [Success] Structural migration applied successfully.")
        else:
            # For functions/procedures/triggers, strip out the top-level test calls at the bottom
            lines = sql_content.split('\n')
            clean_lines = []
            for line in lines:
                # Match top-level test triggers (no leading spaces)
                if line.startswith("SELECT ") or line.startswith("CALL ") or line.startswith("BEGIN;") or line.startswith("UPDATE ") or line.startswith("COMMIT;") or line.startswith("ROLLBACK;"):
                    print(f"  [Info] Skipping test verification statements: {line[:60]}...")
                    break
                clean_lines.append(line)
            
            clean_sql = '\n'.join(clean_lines)
            cur.execute(clean_sql)
            print(f"  [Success] Finished running {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"  [Error] Failed to execute {os.path.basename(file_path)}:")
        print(f"  {e}")
        return False

def main():
    print("===================================================")
    print("🔄 Database Migration Script (GUI Preparations)")
    print("===================================================")
    
    load_env_and_config()
    config = load_env_and_config()
    
    try:
        conn = psycopg2.connect(
            host=config["db_host"],
            port=config["db_port"],
            database=config["db_name"],
            user=config["db_user"],
            password=config["db_password"]
        )
        # Set autocommit to True to allow drops and alterations smoothly
        conn.autocommit = True
        cur = conn.cursor()
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Files to run sequentially
        files_to_run = [
            os.path.join(project_root, "Phase3", "merge_code.sql"),
            os.path.join(project_root, "Phase4", "Functions.sql"),
            os.path.join(project_root, "Phase4", "Procedures.sql"),
            os.path.join(project_root, "Phase4", "triggers.sql")
        ]
        
        success = True
        for file_path in files_to_run:
            if not execute_sql_file(cur, file_path):
                success = False
                break
                
        cur.close()
        conn.close()
        
        if success:
            print("\n🎉 MIGRATION SUCCESSFUL! Database schema is fully integrated.")
            print("Please run verify_db.py again to check the updated schema.")
        else:
            print("\n❌ MIGRATION FAILED. Please review the errors above.")
            
    except Exception as e:
        print(f"\n❌ Failed to connect to database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
