-- Load data for Guide table
COPY guide FROM '/docker-entrypoint-initdb.d/generateData/guide.csv' DELIMITER ',' CSV HEADER;

-- Load data for Location table
COPY location FROM '/docker-entrypoint-initdb.d/generateData/location.csv' DELIMITER ',' CSV HEADER;

-- Load data for Participant table
COPY participant FROM '/docker-entrypoint-initdb.d/generateData/participant.csv' DELIMITER ',' CSV HEADER;

-- Load data for Trip table
COPY trip FROM '/docker-entrypoint-initdb.d/generateData/trip.csv' DELIMITER ',' CSV HEADER;

-- Load data for Group table (using double quotes because "group" is a reserved word)
COPY "GROUP" FROM '/docker-entrypoint-initdb.d/generateData/group.csv' DELIMITER ',' CSV HEADER;

-- Load data for Event table
COPY event FROM '/docker-entrypoint-initdb.d/generateData/event.csv' DELIMITER ',' CSV HEADER;

-- Load data for EventRegistration table
COPY eventregistration FROM '/docker-entrypoint-initdb.d/generateData/eventregistration.csv' DELIMITER ',' CSV HEADER;

-- Load data for ParticipantGroup table
COPY participantgroup FROM '/docker-entrypoint-initdb.d/generateData/participantgroup.csv' DELIMITER ',' CSV HEADER;

-- Load data for GroupTrip table
COPY grouptrip FROM '/docker-entrypoint-initdb.d/generateData/grouptrip.csv' DELIMITER ',' CSV HEADER;