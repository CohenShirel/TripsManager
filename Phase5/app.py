import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

# Default PostgreSQL Connection Settings
DEFAULT_CONFIG = {
    "db_host": "localhost",
    "db_port": 5432,
    "db_name": "postgres",
    "db_user": "postgres",
    "db_password": "postgres"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Load parent directory .env file if it exists
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(parent_dir, '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        parts = line.split('=', 1)
                        k = parts[0].strip()
                        v = parts[1].strip().strip("'").strip('"')
                        os.environ[k] = v
        except Exception:
            pass

    # Try to load from root .env or environment variables
    config = DEFAULT_CONFIG.copy()
    config["db_host"] = os.getenv("DB_HOST", config["db_host"])
    try:
        config["db_port"] = int(os.getenv("DB_PORT", config["db_port"]))
    except ValueError:
        config["db_port"] = 5432
    config["db_name"] = os.getenv("DB_NAME_SECRET", os.getenv("DB_NAME", config["db_name"]))
    config["db_user"] = os.getenv("DB_USER_SECRET", os.getenv("DB_USER", config["db_user"]))
    config["db_password"] = os.getenv("DB_PASSWORD_SECRET", os.getenv("DB_PASSWORD", config["db_password"]))
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_db_connection():
    config = load_config()
    conn = psycopg2.connect(
        host=config["db_host"],
        port=config["db_port"],
        database=config["db_name"],
        user=config["db_user"],
        password=config["db_password"]
    )
    return conn

# ----------------- Core Routes -----------------

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------- Auth Routes -----------------

def _ensure_auth_table_exists():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'System Manager'
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Auth Table Creation Error:", e)

@app.route('/api/auth/register', methods=['POST'])
def register():
    _ensure_auth_table_exists()
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if exists
        cur.execute("SELECT id FROM app_users WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"error": "Username already exists"}), 400
            
        # Insert
        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO app_users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    _ensure_auth_table_exists()
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM app_users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return jsonify({
                "message": "Login successful",
                "user": {"username": user['username'], "role": user['role']}
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Config APIs
@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        data = request.json
        config = {
            "db_host": data.get("db_host", "localhost"),
            "db_port": int(data.get("db_port", 5432)),
            "db_name": data.get("db_name", "postgres"),
            "db_user": data.get("db_user", "postgres"),
            "db_password": data.get("db_password", "postgres")
        }
        save_config(config)
        return jsonify({"status": "success", "message": "Configuration saved successfully."})
    else:
        config = load_config()
        # Do not return password for security
        safe_config = config.copy()
        safe_config["db_password"] = "********" if config["db_password"] else ""
        return jsonify(safe_config)

@app.route('/api/db-test', methods=['POST'])
def test_db_connection():
    data = request.json or {}
    config = load_config()
    
    # If custom data is sent (during test in settings), use it
    host = data.get("db_host") or config["db_host"]
    port = data.get("db_port") or config["db_port"]
    name = data.get("db_name") or config["db_name"]
    user = data.get("db_user") or config["db_user"]
    password = data.get("db_password")
    
    # Handle password masking/fallback
    if password == "********" or password is None:
        password = config["db_password"]

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=name,
            user=user,
            password=password,
            connect_timeout=3
        )
        conn.close()
        return jsonify({"status": "success", "message": "Successfully connected to the database."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ----------------- Dashboard APIs -----------------

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        stats = {}
        tables = ['trip', 'guide', 'participant', 'event', '"GROUP"', 'location']
        for table in tables:
            clean_name = table.replace('"', '').lower()
            try:
                cur.execute(f"SELECT COUNT(*) FROM public.{table};")
                stats[clean_name] = cur.fetchone()[0]
            except Exception:
                stats[clean_name] = 0
                conn.rollback()
                
        cur.close()
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upcoming-trips', methods=['GET'])
def get_upcoming_trips():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                t.tripid, t.tripname, t.startdate, t.enddate, t.groupsize, t.status, t.triptype,
                gu.guidename,
                r.route_name, r.region,
                tt.transport_type_name
            FROM public.trip t
            LEFT JOIN public.guide gu ON t.guideid = gu.guideid
            LEFT JOIN public.route r ON t.route_id = r.route_id
            LEFT JOIN public.transport_type tt ON t.transport_type_id = tt.transport_type_id
            ORDER BY t.startdate ASC
            LIMIT 5;
        """
        cur.execute(query)
        trips = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(trips)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/guides-by-region', methods=['GET'])
def get_guides_by_region():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT COALESCE(region, 'Other') as region, COUNT(*) as count 
            FROM public.guide 
            GROUP BY region 
            ORDER BY count DESC;
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recent-events', methods=['GET'])
def get_recent_events():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT e.eventid, e.eventname, e.eventdate::text, e.eventtime::text, e.start_hour::text, e.end_hour::text,
                   t.tripname, l.locationname
            FROM public.event e
            LEFT JOIN public.trip t ON e.tripid = t.tripid
            LEFT JOIN public.location l ON e.locationid = l.locationid
            ORDER BY e.eventdate ASC, e.eventtime ASC
            LIMIT 5;
        """
        cur.execute(query)
        events = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- Helper Lists APIs -----------------

@app.route('/api/helpers/<entity>', methods=['GET'])
def get_helpers(entity):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if entity == 'guides':
            cur.execute("SELECT guideid as id, guidename as name FROM public.guide ORDER BY name;")
        elif entity == 'routes':
            cur.execute("SELECT route_id as id, route_name || ' (' || COALESCE(region, '') || ')' as name FROM public.route ORDER BY name;")
        elif entity == 'poi':
            cur.execute("SELECT locationid as id, locationname as name FROM public.location ORDER BY name;")
        elif entity == 'transport-types':
            cur.execute("SELECT transport_type_id as id, transport_type_name as name FROM public.transport_type ORDER BY name;")
        elif entity == 'groups':
            cur.execute("SELECT groupid as id, groupname as name FROM public.\"GROUP\" ORDER BY name;")
        elif entity == 'trips':
            cur.execute("SELECT tripid as id, tripname as name FROM public.trip ORDER BY name;")
        else:
            return jsonify({"error": "Unknown helper entity"}), 400
            
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- CRUD Operations -----------------

# 1. TRIPS
@app.route('/api/trips', methods=['GET', 'POST'])
def handle_trips():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT t.*, gu.guidename, r.route_name, tt.transport_type_name
                FROM public.trip t
                LEFT JOIN public.guide gu ON t.guideid = gu.guideid
                LEFT JOIN public.route r ON t.route_id = r.route_id
                LEFT JOIN public.transport_type tt ON t.transport_type_id = tt.transport_type_id
                ORDER BY t.tripid DESC;
            """)
            trips = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(trips)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public.trip (tripid, tripname, startdate, enddate, groupsize, status, route_id, transport_type_id, triptype, guideid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING tripid;
            """, (
                data['tripid'], data['tripname'], data.get('startdate'), data.get('enddate'),
                data.get('groupsize'), data.get('status'), data.get('route_id'), data.get('transport_type_id'),
                data.get('triptype'), data.get('guideid')
            ))
            new_id = cur.fetchone()['tripid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/trips/<int:trip_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_trip(trip_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT 
                    tripid, tripname, startdate::text, enddate::text, groupsize, 
                    status, route_id, transport_type_id, triptype, guideid
                FROM public.trip WHERE tripid = %s;
            """, (trip_id,))
            trip = cur.fetchone()
            cur.close()
            conn.close()
            if not trip:
                return jsonify({"error": "Trip not found"}), 404
            return jsonify(trip)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public.trip 
                SET tripname=%s, startdate=%s, enddate=%s, groupsize=%s, status=%s, route_id=%s, transport_type_id=%s, triptype=%s, guideid=%s
                WHERE tripid=%s;
            """, (
                data['tripname'], data.get('startdate'), data.get('enddate'), data.get('groupsize'),
                data.get('status'), data.get('route_id'), data.get('transport_type_id'), data.get('triptype'),
                data.get('guideid'), trip_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            cur.execute("DELETE FROM public.eventregistration WHERE eventid IN (SELECT eventid FROM public.event WHERE tripid = %s);", (trip_id,))
            cur.execute("DELETE FROM public.event WHERE tripid = %s;", (trip_id,))
            cur.execute("DELETE FROM public.trip WHERE tripid = %s;", (trip_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

# 2. GUIDES
@app.route('/api/guides', methods=['GET', 'POST'])
def handle_guides():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM public.guide ORDER BY guideid DESC;")
            guides = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(guides)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public.guide (guideid, guidename, phone, email, specialization, region, experienceyears, license_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING guideid;
            """, (
                data['guideid'], data['guidename'], data.get('phone'), data.get('email'),
                data.get('specialization'), data.get('region'), data.get('experienceyears'), data.get('license_number')
            ))
            new_id = cur.fetchone()['guideid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/guides/<int:guide_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_guide(guide_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM public.guide WHERE guideid = %s;", (guide_id,))
            guide = cur.fetchone()
            cur.close()
            conn.close()
            if not guide:
                return jsonify({"error": "Guide not found"}), 404
            return jsonify(guide)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public.guide 
                SET guidename=%s, phone=%s, email=%s, specialization=%s, region=%s, experienceyears=%s, license_number=%s
                WHERE guideid=%s;
            """, (
                data['guidename'], data.get('phone'), data.get('email'), data.get('specialization'),
                data.get('region'), data.get('experienceyears'), data.get('license_number'), guide_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            cur.execute("UPDATE public.trip SET guideid = NULL WHERE guideid = %s;", (guide_id,))
            cur.execute("UPDATE public.\"GROUP\" SET guideid = NULL WHERE guideid = %s;", (guide_id,))
            cur.execute("DELETE FROM public.guide WHERE guideid = %s;", (guide_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

# 3. PARTICIPANTS
@app.route('/api/participants', methods=['GET', 'POST'])
def handle_participants():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM public.participant ORDER BY participantid DESC LIMIT 200;")
            participants = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(participants)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public.participant (participantid, firstname, lastname, phone, email, birthdate, age)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING participantid;
            """, (
                data['participantid'], data['firstname'], data['lastname'], data.get('phone'),
                data.get('email'), data.get('birthdate'), data.get('age')
            ))
            new_id = cur.fetchone()['participantid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/participants/<int:participant_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_participant(participant_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT 
                    participantid, firstname, lastname, phone, email, birthdate::text, age
                FROM public.participant WHERE participantid = %s;
            """, (participant_id,))
            participant = cur.fetchone()
            cur.close()
            conn.close()
            if not participant:
                return jsonify({"error": "Participant not found"}), 404
            return jsonify(participant)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public.participant 
                SET firstname=%s, lastname=%s, phone=%s, email=%s, birthdate=%s, age=%s
                WHERE participantid=%s;
            """, (
                data['firstname'], data['lastname'], data.get('phone'), data.get('email'),
                data.get('birthdate'), data.get('age'), participant_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            cur.execute("DELETE FROM public.eventregistration WHERE registrationid = %s;", (participant_id,))
            cur.execute("DELETE FROM public.participant WHERE participantid = %s;", (participant_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

# 4. GROUPS
@app.route('/api/groups', methods=['GET', 'POST'])
def handle_groups():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT g.*, gu.guidename
                FROM public."GROUP" g
                LEFT JOIN public.guide gu ON g.guideid = gu.guideid
                ORDER BY g.groupid DESC;
            """)
            groups = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(groups)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public."GROUP" (groupid, groupname, guideid, createddate)
                VALUES (%s, %s, %s, %s)
                RETURNING groupid;
            """, (
                data['groupid'], data['groupname'], data.get('guideid'), data.get('createddate')
            ))
            new_id = cur.fetchone()['groupid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/groups/<int:group_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_group(group_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT 
                    groupid, groupname, createddate::text, guideid
                FROM public."GROUP" WHERE groupid = %s;
            """, (group_id,))
            group = cur.fetchone()
            cur.close()
            conn.close()
            if not group:
                return jsonify({"error": "Group not found"}), 404
            return jsonify(group)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public."GROUP" 
                SET groupname=%s, guideid=%s, createddate=%s
                WHERE groupid=%s;
            """, (
                data['groupname'], data.get('guideid'), data.get('createddate'), group_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            cur.execute("DELETE FROM public.\"GROUP\" WHERE groupid = %s;", (group_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

# 5. EVENTS
@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT 
                    e.eventid, e.eventname, e.eventdate::text, e.tripid, 
                    e.start_hour::text, e.end_hour::text, e.cost::float, 
                    e.status, e.order_num, e.eventtime::text, e.locationid,
                    t.tripname, l.locationname
                FROM public.event e
                LEFT JOIN public.trip t ON e.tripid = t.tripid
                LEFT JOIN public.location l ON e.locationid = l.locationid
                ORDER BY e.eventid DESC;
            """)
            events = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(events)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public.event (eventid, eventname, eventdate, tripid, start_hour, end_hour, cost, status, order_num, eventtime, locationid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING eventid;
            """, (
                data['eventid'], data['eventname'], data.get('eventdate'), data.get('tripid'),
                data.get('start_hour'), data.get('end_hour'), data.get('cost'), data.get('status'),
                data.get('order_num'), data.get('eventtime'), data.get('locationid')
            ))
            new_id = cur.fetchone()['eventid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_event(event_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("""
                SELECT 
                    eventid, eventname, eventdate::text, tripid, 
                    start_hour::text, end_hour::text, cost::float, 
                    status, order_num, eventtime::text, locationid
                FROM public.event 
                WHERE eventid = %s;
            """, (event_id,))
            event = cur.fetchone()
            cur.close()
            conn.close()
            if not event:
                return jsonify({"error": "Event not found"}), 404
            return jsonify(event)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public.event 
                SET eventname=%s, eventdate=%s, tripid=%s, start_hour=%s, end_hour=%s, cost=%s, status=%s, order_num=%s, eventtime=%s, locationid=%s
                WHERE eventid=%s;
            """, (
                data['eventname'], data.get('eventdate'), data.get('tripid'), data.get('start_hour'),
                data.get('end_hour'), data.get('cost'), data.get('status'), data.get('order_num'),
                data.get('eventtime'), data.get('locationid'), event_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            # Cascade delete registrations first to avoid foreign key violations
            cur.execute("DELETE FROM public.eventregistration WHERE eventid = %s;", (event_id,))
            cur.execute("DELETE FROM public.event WHERE eventid = %s;", (event_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

# 6. LOCATIONS (Renamed to POI to avoid AdBlockers blocking 'locations' in fetch)
@app.route('/api/poi', methods=['GET', 'POST'])
def handle_locations():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM public.location ORDER BY locationid DESC;")
            locations = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(locations)
            
        elif request.method == 'POST':
            data = request.json
            cur.execute("""
                INSERT INTO public.location (locationid, locationname, region, address)
                VALUES (%s, %s, %s, %s)
                RETURNING locationid;
            """, (
                data['locationid'], data['locationname'], data.get('region'), data.get('address')
            ))
            new_id = cur.fetchone()['locationid']
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/poi/<int:location_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_location(location_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM public.location WHERE locationid = %s;", (location_id,))
            location = cur.fetchone()
            cur.close()
            conn.close()
            if not location:
                return jsonify({"error": "Location not found"}), 404
            return jsonify(location)
            
        elif request.method == 'PUT':
            data = request.json
            cur.execute("""
                UPDATE public.location 
                SET locationname=%s, region=%s, address=%s
                WHERE locationid=%s;
            """, (
                data['locationname'], data.get('region'), data.get('address'), location_id
            ))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
            
        elif request.method == 'DELETE':
            cur.execute("UPDATE public.event SET locationid = NULL WHERE locationid = %s;", (location_id,))
            cur.execute("DELETE FROM public.location WHERE locationid = %s;", (location_id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success"})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500


# ----------------- Custom Queries APIs -----------------

QUERIES = {
    1: ("אירועים במיקומים פופולריים (מעל 2 אירועים)", """
        SELECT e.eventname, l.locationname, e.eventdate
        FROM public.event e
        JOIN public.location l ON e.locationid = l.locationid
        WHERE e.locationid IN (
            SELECT locationid FROM public.event
            GROUP BY locationid
            HAVING COUNT(*) > 2
        ) LIMIT 50;
    """),
    2: ("מדריכים פנויים (ללא קבוצה משויכת)", """
        SELECT gu.guideid, gu.guidename
        FROM public.guide gu
        LEFT JOIN public."GROUP" g ON gu.guideid = g.guideid
        WHERE g.groupid IS NULL LIMIT 50;
    """),
    3: ("מדריכים שהדריכו קבוצות משנת 2025", """
        SELECT gu.guideid, gu.guidename, gu.specialization
        FROM public.guide gu
        WHERE EXISTS (
            SELECT 1 
            FROM public."GROUP" g 
            WHERE g.guideid = gu.guideid 
            AND EXTRACT(YEAR FROM g.createddate) = 2025
        ) LIMIT 50;
    """),
    4: ("מדריכים המעבירים יותר מטיול אחד", """
        SELECT gu.guideid, gu.guidename, COUNT(t.tripid) AS trip_count
        FROM public.guide gu
        JOIN public.trip t ON gu.guideid = t.guideid
        GROUP BY gu.guideid, gu.guidename
        HAVING COUNT(t.tripid) > 1
        ORDER BY trip_count DESC LIMIT 50;
    """),
    5: ("דו\"ח רישום שנתי/חודשי", """
        SELECT 
            EXTRACT(YEAR FROM registrationdate) AS reg_year,
            EXTRACT(MONTH FROM registrationdate) AS reg_month,
            COUNT(*) AS total_registrations
        FROM public.eventregistration
        GROUP BY reg_year, reg_month
        ORDER BY reg_year DESC, reg_month DESC LIMIT 50;
    """),
    6: ("קטלוג טיולים מלא (4 טבלאות)", """
        SELECT 
            t.tripname,
            g.groupname,
            gu.guidename,
            l.locationname,
            t.startdate
        FROM public.trip t
        JOIN public.grouptrip gt ON t.tripid = gt.tripid
        JOIN public."GROUP" g ON gt.groupid = g.groupid
        JOIN public.guide gu ON t.guideid = gu.guideid
        JOIN public.event e ON t.tripid = e.tripid
        JOIN public.location l ON e.locationid = l.locationid
        LIMIT 20;
    """),
    7: ("משתתפים בוגרים (30+) באזור הצפון", """
        SELECT DISTINCT p.firstname, p.lastname, p.age, l.locationname
        FROM public.participant p
        JOIN public.eventregistration er ON p.participantid = er.registrationid
        JOIN public.event e ON er.eventid = e.eventid
        JOIN public.location l ON e.locationid = l.locationid
        WHERE p.age > 30 AND l.region = 'North'
        ORDER BY p.age ASC LIMIT 50;
    """),
    8: ("אירועי בוקר קרובים", """
        SELECT 
            eventname, 
            eventdate,
            EXTRACT(HOUR FROM eventtime) AS hour_of_day,
            EXTRACT(MINUTE FROM eventtime) AS minute_of_hour
        FROM public.event
        WHERE eventtime BETWEEN '06:00:00' AND '12:00:00'
          AND eventdate > '2026-01-01'
        ORDER BY eventdate ASC LIMIT 50;
    """)
}

@app.route('/api/queries', methods=['GET'])
def list_queries():
    return jsonify([{ "id": k, "name": v[0] } for k, v in QUERIES.items()])

@app.route('/api/queries/<int:query_id>', methods=['POST'])
def run_query(query_id):
    if query_id not in QUERIES:
        return jsonify({"error": "Query not found"}), 404
        
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        sql = QUERIES[query_id][1]
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500


@app.route('/api/helpers/regions', methods=['GET'])
def helpers_regions():
    return jsonify(["North", "South", "Center", "East", "West", "Jerusalem", "Eilat"])

# ----------------- PL/SQL Execution APIs -----------------

@app.route('/api/plsql/calculate-cost', methods=['POST'])
def plsql_calculate_cost():
    data = request.json or {}
    trip_id = data.get("trip_id")
    if not trip_id:
        return jsonify({"error": "trip_id is required"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT fn_calculate_trip_total_cost(%s);", (trip_id,))
        result = cur.fetchone()[0]
        
        # Capture notices
        notices = []
        while conn.notices:
            notices.append(conn.notices.pop(0).strip())
            
        cur.close()
        conn.close()
        return jsonify({"status": "success", "cost": float(result), "notices": notices})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/plsql/trips-by-region', methods=['POST'])
def plsql_trips_by_region():
    data = request.json or {}
    region_name = data.get("region_name")
    if not region_name:
        return jsonify({"error": "region_name is required"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        
        # Ref cursors require transactions in postgres
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # psycopg2 automatically starts a transaction
        cur.execute("SELECT fn_get_trips_by_region_cursor(%s);", (region_name,))
        cursor_name = cur.fetchone()['fn_get_trips_by_region_cursor']
        
        cur.execute(f'FETCH ALL IN "{cursor_name}";')
        results = cur.fetchall()
        
        conn.commit()
        
        notices = []
        while conn.notices:
            notices.append(conn.notices.pop(0).strip())
            
        cur.close()
        conn.close()
        return jsonify({"status": "success", "data": results, "notices": notices})
    except Exception as e:
        if conn:
            try:
                cur.execute("ROLLBACK;")
            except Exception:
                pass
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/plsql/update-status-by-age', methods=['POST'])
def plsql_update_status_by_age():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # In PostgreSQL we CALL procedures
        cur.execute("CALL pr_update_trip_status_by_age();")
        conn.commit()
        
        notices = []
        while conn.notices:
            notices.append(conn.notices.pop(0).strip())
            
        cur.close()
        conn.close()
        return jsonify({"status": "success", "notices": notices})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/plsql/update-vip-trip-type', methods=['POST'])
def plsql_update_vip_trip_type():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CALL pr_update_vip_trip_type();")
        conn.commit()
        
        notices = []
        while conn.notices:
            notices.append(conn.notices.pop(0).strip())
            
        cur.close()
        conn.close()
        return jsonify({"status": "success", "notices": notices})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize config
    load_config()
    print("Starting TripManager GUI Server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
