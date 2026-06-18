import psycopg2
conn = psycopg2.connect('postgresql://my_admin_user:********@localhost:5432/trips_db')
cur = conn.cursor()
cur.execute('SELECT DISTINCT region FROM public.route;')
print("REGIONS:", cur.fetchall())
conn.close()
