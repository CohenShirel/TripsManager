-- selectAll.sql

-- 1. Basic selection from all tables
SELECT * FROM GUIDE;
SELECT * FROM PARTICIPANT;
SELECT * FROM LOCATION;
SELECT * FROM TRIP;
SELECT * FROM "GROUP";
SELECT * FROM EVENT;
SELECT * FROM EVENTREGISTRATION;
SELECT * FROM PARTICIPANTGROUP;
SELECT * FROM GROUPTRIP;

---------------------------------------------------------
-- 2. Advanced Queries (Joined Data for better readability)
---------------------------------------------------------

-- View Trips with their assigned Guides
SELECT t.TripName, t.StartDate, g.GuideName, g.Specialization
FROM TRIP t
JOIN GUIDE g ON t.GuideId = g.GuideId;

-- View Events with their Locations and related Trips
SELECT e.EventName, e.EventDate, e.EventTime, l.LocationName, t.TripName
FROM EVENT e
JOIN LOCATION l ON e.LocationID = l.LocationID
JOIN TRIP t ON e.TripId = t.TripId;

-- View which Participants are in which Groups
SELECT p.FirstName, p.LastName, g.GroupName
FROM PARTICIPANTGROUP pg
JOIN PARTICIPANT p ON pg.ParticipantID = p.ParticipantID
JOIN "GROUP" g ON pg.GroupId = g.GroupId;

-- View Trips assigned to each Group
SELECT g.GroupName, t.TripName, t.StartDate
FROM GROUPTRIP gt
JOIN "GROUP" g ON gt.GroupId = g.GroupId
JOIN TRIP t ON gt.TripId = t.TripId;