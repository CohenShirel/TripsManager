import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "tripsmanager"
DB_USER = "postgres"
DB_PASSWORD = "password"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("Testing GET...")
    cur.execute("SELECT * FROM public.location ORDER BY locationid DESC LIMIT 1;")
    print("GET OK:", cur.fetchall())

    print("Testing DELETE with a fake ID...")
    cur.execute("DELETE FROM public.location WHERE locationid = %s;", (999999,))
    conn.commit()
    print("DELETE OK")

    print("Testing POST...")
    cur.execute("""
        INSERT INTO public.location (locationid, locationname, region, address)
        VALUES (%s, %s, %s, %s)
        RETURNING locationid;
    """, (94257, "SHIREL", "South", "Birinboim 4"))
    new_id = cur.fetchone()[0]
    conn.commit()
    print("POST OK, new_id:", new_id)
    
    print("Testing DELETE of new_id...")
    cur.execute("DELETE FROM public.location WHERE locationid = %s;", (new_id,))
    conn.commit()
    print("DELETE OK")

    cur.close()
    conn.close()
except Exception as e:
    print("ERROR:", e)
