-- 1. Guides table: Added constraints for positive experience and unique contact info
CREATE TABLE GUIDE
(
  GuideId SERIAL PRIMARY KEY,
  GuideName VARCHAR(100) NOT NULL,
  Phone VARCHAR(15) UNIQUE,
  Email VARCHAR(100) UNIQUE CHECK (Email LIKE '%@%'),
  Specialization VARCHAR(100) NOT NULL,
  Region VARCHAR(50) NOT NULL,
  ExperienceYears INT NOT NULL CHECK (ExperienceYears >= 0)
);

-- 2. Participants table: Added age validation and unique email
CREATE TABLE PARTICIPANT
(
  ParticipantID SERIAL PRIMARY KEY,
  LastName VARCHAR(100) NOT NULL,
  FirstName VARCHAR(100) NOT NULL,
  Phone VARCHAR(15),
  Email VARCHAR(100) UNIQUE CHECK (Email LIKE '%@%'),
  Age INT NOT NULL CHECK (Age > 0)
);

-- 3. Locations table
CREATE TABLE LOCATION
(
  LocationID SERIAL PRIMARY KEY,
  LocationName VARCHAR(100) NOT NULL,
  Region VARCHAR(50) NOT NULL,
  Address VARCHAR(255) NOT NULL,
  Description TEXT
);

-- 4. Trips table: Added constraint to ensure EndDate is not before StartDate
CREATE TABLE TRIP
(
  TripId SERIAL PRIMARY KEY,
  TripName VARCHAR(100) NOT NULL,
  StartDate DATE NOT NULL,
  EndDate DATE NOT NULL,
  TripType VARCHAR(50) NOT NULL,
  GuideId INT NOT NULL,
  CONSTRAINT check_trip_dates CHECK (EndDate >= StartDate),
  FOREIGN KEY (GuideId) REFERENCES GUIDE(GuideId)
);

-- 5. Groups table: Added default current date for creation
CREATE TABLE "GROUP"
(
  GroupId SERIAL PRIMARY KEY,
  GroupName VARCHAR(100) NOT NULL,
  Description TEXT,
  CreatedDate DATE NOT NULL DEFAULT CURRENT_DATE,
  GuideId INT NOT NULL,
  FOREIGN KEY (GuideId) REFERENCES GUIDE(GuideId)
);

-- 6. Events table: Added unique constraint to prevent double-booking a location at the same time
CREATE TABLE EVENT
(
  EventId SERIAL PRIMARY KEY,
  EventName VARCHAR(100) NOT NULL,
  EventDate DATE NOT NULL,
  EventTime TIME NOT NULL,
  TripId INT NOT NULL,
  LocationID INT NOT NULL,
  UNIQUE (LocationID, EventDate, EventTime),
  FOREIGN KEY (TripId) REFERENCES TRIP(TripId),
  FOREIGN KEY (LocationID) REFERENCES LOCATION(LocationID)
);

-- 7. Event Registration table: Added default registration date
CREATE TABLE EVENTREGISTRATION
(
  RegistrationId SERIAL PRIMARY KEY,
  RegistrationDate DATE NOT NULL DEFAULT CURRENT_DATE,
  EventId INT NOT NULL,
  FOREIGN KEY (EventId) REFERENCES EVENT(EventId)
);

-- 8. Junction table: Participants and Groups (Many-to-Many)
CREATE TABLE PARTICIPANTGROUP
(
  ParticipantID INT NOT NULL,
  GroupId INT NOT NULL,
  PRIMARY KEY (ParticipantID, GroupId),
  FOREIGN KEY (ParticipantID) REFERENCES PARTICIPANT(ParticipantID),
  FOREIGN KEY (GroupId) REFERENCES "GROUP"(GroupId)
);

-- 9. Junction table: Groups and Trips (Many-to-Many)
CREATE TABLE GROUPTRIP
(
  GroupId INT NOT NULL,
  TripId INT NOT NULL,
  PRIMARY KEY (GroupId, TripId),
  FOREIGN KEY (GroupId) REFERENCES "GROUP"(GroupId),
  FOREIGN KEY (TripId) REFERENCES TRIP(TripId)
);