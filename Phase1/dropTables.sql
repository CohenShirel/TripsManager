-- dropTables.sql

-- 1. Drop junction tables and dependent tables first (due to Foreign Key constraints)
DROP TABLE IF EXISTS GROUPTRIP;
DROP TABLE IF EXISTS PARTICIPANTGROUP;
DROP TABLE IF EXISTS EVENTREGISTRATION;

-- 2. Drop tables that are referenced by the ones above
DROP TABLE IF EXISTS EVENT;
DROP TABLE IF EXISTS "GROUP";
DROP TABLE IF EXISTS TRIP;

-- 3. Drop base tables (Master tables)
DROP TABLE IF EXISTS LOCATION;
DROP TABLE IF EXISTS PARTICIPANT;
DROP TABLE IF EXISTS GUIDE;