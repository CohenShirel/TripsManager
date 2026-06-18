import psycopg2
import random

def update_event_costs():
    conn = psycopg2.connect(
        host="localhost",
        database="tripsmanager",
        user="postgres"
    )
    cur = conn.cursor()
    
    cur.execute("SELECT eventid FROM event")
    events = cur.fetchall()
    
    for (eventid,) in events:
        random_cost = round(random.uniform(50.0, 500.0), 2)
        cur.execute("UPDATE event SET cost = %s WHERE eventid = %s", (random_cost, eventid))
        
    conn.commit()
    cur.close()
    conn.close()
    print("Updated event costs successfully!")

if __name__ == "__main__":
    update_event_costs()
