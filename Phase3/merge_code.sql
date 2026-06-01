-- ==========================================
-- שלב 1: יצירת הטבלאות הייחודיות החדשות
-- ==========================================

CREATE TABLE IF NOT EXISTS transport_type (
    transport_type_id integer NOT NULL PRIMARY KEY,
    transport_type_name character varying(100)
);

CREATE TABLE IF NOT EXISTS route (
    route_id integer NOT NULL PRIMARY KEY,
    route_name character varying(100),
    region character varying(100),
    distance_km numeric,
    duration_hours numeric,
    difficulty_level character varying(50)
);

CREATE TABLE IF NOT EXISTS schedule (
    trip_id integer NOT NULL, 
    order_num integer NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    description text,
    sch_date date,
    PRIMARY KEY (trip_id, order_num)
);

CREATE TABLE IF NOT EXISTS action (
    action_id integer NOT NULL PRIMARY KEY,
    address character varying(255),
    action_type character varying(100),
    action_name character varying(100),
    event_id integer
);

-- ==========================================
-- שלב 2: הוספת העמודות לטבלאות בסיס האם
-- ==========================================

ALTER TABLE trip ADD COLUMN IF NOT EXISTS groupsize INTEGER;
ALTER TABLE trip ADD COLUMN IF NOT EXISTS status VARCHAR(50);
ALTER TABLE trip ADD COLUMN IF NOT EXISTS route_id INTEGER;
ALTER TABLE trip ADD COLUMN IF NOT EXISTS transport_type_id INTEGER;
ALTER TABLE trip ALTER COLUMN triptype DROP NOT NULL;
ALTER TABLE trip ALTER COLUMN guideid DROP NOT NULL;

ALTER TABLE event ADD COLUMN IF NOT EXISTS start_hour TIME;
ALTER TABLE event ADD COLUMN IF NOT EXISTS end_hour TIME;
ALTER TABLE event ADD COLUMN IF NOT EXISTS cost NUMERIC;
ALTER TABLE event ADD COLUMN IF NOT EXISTS status VARCHAR(50);
ALTER TABLE event ADD COLUMN IF NOT EXISTS order_num INTEGER;
ALTER TABLE event ALTER COLUMN eventtime DROP NOT NULL;
ALTER TABLE event ALTER COLUMN locationid DROP NOT NULL;

ALTER TABLE participant ADD COLUMN IF NOT EXISTS birthdate DATE;
ALTER TABLE participant ALTER COLUMN age DROP NOT NULL;

ALTER TABLE guide ADD COLUMN IF NOT EXISTS license_number VARCHAR(100);

-- ==========================================
-- שלב 3: שאיבת הנתונים (כולל תוספת 20,000 ל-IDs הרלוונטיים)
-- ==========================================

INSERT INTO participant (participantid, firstname, lastname, phone, email, birthdate)
SELECT participant_id + 20000, first_name, last_name, phone, email, birth_date
FROM participants;

INSERT INTO guide (guideid, guidename, phone, email, specialization, region, experienceyears, license_number)
SELECT 
    g.participant_id + 20000, 
    COALESCE(p.first_name || ' ' || p.last_name, 'Unknown'), 
    p.phone, 
    p.email, 
    'General', 
    'Unknown', 
    g.experience_years, 
    g.license_number
FROM guides g
LEFT JOIN participants p ON g.participant_id = p.participant_id;

INSERT INTO transport_type (transport_type_id, transport_type_name)
SELECT transport_type_id, transport_type_name
FROM transport_types;

INSERT INTO route (route_id, route_name, region, distance_km, duration_hours, difficulty_level)
SELECT route_id, route_name, region, distance_km, duration_hours, difficulty_level
FROM routes;

INSERT INTO trip (tripid, tripname, startdate, enddate, groupsize, status, route_id, transport_type_id)
SELECT trip_id + 20000, trip_name, start_date, end_date, group_size, status, route_id, transport_type_id
FROM trips;

INSERT INTO event (eventid, eventname, eventdate, tripid, start_hour, end_hour, cost, status, order_num)
SELECT event_id + 20000, event_name, event_date, trip_id + 20000, start_hour, end_hour, cost, status, order_num
FROM events;

INSERT INTO schedule (trip_id, order_num, start_time, end_time, description, sch_date)
SELECT trip_id + 20000, order_num, start_time, end_time, description, sch_date
FROM schedules;

INSERT INTO action (action_id, address, action_type, action_name, event_id)
SELECT action_id, address, action_type, action_name, event_id + 20000
FROM actions;

-- ==========================================
-- שלב 4: החזרת קשרים (Foreign Keys)
-- ==========================================

ALTER TABLE action ADD CONSTRAINT fk_action_event FOREIGN KEY (event_id) REFERENCES event(eventid);
ALTER TABLE schedule ADD CONSTRAINT fk_schedule_trip FOREIGN KEY (trip_id) REFERENCES trip(tripid);
ALTER TABLE trip ADD CONSTRAINT fk_trip_route FOREIGN KEY (route_id) REFERENCES route(route_id);
ALTER TABLE trip ADD CONSTRAINT fk_trip_transport FOREIGN KEY (transport_type_id) REFERENCES transport_type(transport_type_id);

-- ==========================================
-- שלב 5: ניקיון! מחיקת הטבלאות הכפולות מהקובץ השני
-- ==========================================

DROP TABLE IF EXISTS actions CASCADE;
DROP TABLE IF EXISTS schedules CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS transport_types CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS guides CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TABLE IF EXISTS trip_participants CASCADE;