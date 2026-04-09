-- 1. Inserting 10 Guides
INSERT INTO GUIDE (GuideName, Phone, Email, Specialization, Region, ExperienceYears) VALUES
('Avi Cohen', '050-1112222', 'avi.c@example.com', 'Hiking', 'North', 10),
('Maya Levi', '050-3334444', 'maya.l@example.com', 'Urban Tours', 'Center', 5),
('Yossi Israeli', '052-5556666', 'yossi.i@example.com', 'Extreme', 'South', 12),
('Dana Ron', '054-7778888', 'dana.r@example.com', 'History', 'Jerusalem', 3),
('Ronit Tal', '053-9990000', 'ronit.t@example.com', 'Culinary', 'Center', 7),
('Erez Golan', '050-1234567', 'erez.g@example.com', 'Biking', 'North', 15),
('Noa Sela', '052-2345678', 'noa.s@example.com', 'Photography', 'South', 4),
('Itay Barak', '054-3456789', 'itay.b@example.com', 'Jeep Tours', 'Desert', 8),
('Shira Gal', '053-4567890', 'shira.g@example.com', 'Botany', 'North', 6),
('Gal Or', '050-5678901', 'gal.o@example.com', 'Archeology', 'Jerusalem', 20);

-- 2. Inserting 10 Participants
INSERT INTO PARTICIPANT (LastName, FirstName, Phone, Email, Age) VALUES
('Levi', 'David', '050-1002000', 'david.l@mail.com', 28),
('Cohen', 'Sarah', '050-2003000', 'sarah.c@mail.com', 35),
('Mizrahi', 'Omer', '052-3004000', 'omer.m@mail.com', 22),
('Peretz', 'Noam', '054-4005000', 'noam.p@mail.com', 41),
('Biton', 'Michal', '053-5006000', 'michal.b@mail.com', 19),
('Aharoni', 'Amit', '050-6007000', 'amit.a@mail.com', 50),
('Dahan', 'Lior', '052-7008000', 'lior.d@mail.com', 31),
('Katz', 'Tali', '054-8009000', 'tali.k@mail.com', 27),
('Friedman', 'Eyal', '053-9001000', 'eyal.f@mail.com', 64),
('Goldberg', 'Roni', '050-1113333', 'roni.g@mail.com', 24);

-- 3. Inserting 10 Locations
INSERT INTO LOCATION (LocationName, Region, Address, Description) VALUES
('Banias Nature Reserve', 'North', 'Route 99', 'Beautiful waterfalls and hiking trails'),
('Masada Fortress', 'South', 'Dead Sea Road', 'Historic desert fortress'),
('Old Jaffa Port', 'Center', 'Jaffa', 'Ancient port with art galleries'),
('Mount Arbel', 'North', 'Near Tiberias', 'Cliff with panoramic view of Sea of Galilee'),
('Western Wall', 'Jerusalem', 'Old City', 'Holy site and historical plaza'),
('Ein Gedi Oasis', 'South', 'Dead Sea', 'Desert spring and botanical garden'),
('Tel Dan Reserve', 'North', 'Upper Galilee', 'Source of Jordan river'),
('Ramon Crater', 'South', 'Mitzpe Ramon', 'Largest erosion crater in the world'),
('Mount Meron', 'North', 'Galilee', 'Highest peak in Israel outside Hermon'),
('Caesarea National Park', 'Center', 'Coast', 'Roman ruins and ancient theater');

-- 4. Inserting 10 Trips
INSERT INTO TRIP (TripName, StartDate, EndDate, TripType, GuideId) VALUES
('Winter North Hike', '2025-01-10', '2025-01-12', 'Hiking', 1),
('History of Jerusalem', '2025-02-05', '2025-02-05', 'Educational', 4),
('Dead Sea Relaxation', '2025-03-15', '2025-03-17', 'Leisure', 3),
('Culinary Tel Aviv', '2025-04-20', '2025-04-20', 'Culinary', 5),
('Galilee Biking Tour', '2025-05-10', '2025-05-13', 'Extreme', 6),
('Desert Star Gazing', '2025-06-12', '2025-06-13', 'Educational', 8),
('Photography Workshop', '2025-07-01', '2025-07-03', 'Workshop', 7),
('Archaeology week', '2025-08-10', '2025-08-17', 'Professional', 10),
('Spring Flowers Tour', '2025-03-22', '2025-03-22', 'Nature', 9),
('City Lights Jaffa', '2025-09-05', '2025-09-05', 'Urban', 2);

-- 5. Inserting 10 Groups
INSERT INTO "GROUP" (GroupName, Description, GuideId) VALUES
('Nature Lovers', 'Focusing on plants and wildlife', 9),
('The Explorers', 'Challenging hiking group', 1),
('History Buffs', 'Academic level history tours', 4),
('Gourmet Club', 'Foodies visiting markets', 5),
('Desert Wolves', 'Jeep and extreme enthusiasts', 8),
('Shutterbugs', 'Photography students', 7),
('Archeo-Team', 'Volunteer diggers', 10),
('North Stars', 'Local hiking enthusiasts', 6),
('Tel Aviv Vibes', 'Urban culture seekers', 2),
('The Chillers', 'Low-pace weekend travelers', 3);

-- 6. Inserting 10 Events
INSERT INTO EVENT (EventName, EventDate, EventTime, TripId, LocationID) VALUES
('Morning Hike Banias', '2025-01-10', '09:00:00', 1, 1),
('Masada Sunrise Visit', '2025-03-16', '05:30:00', 3, 2),
('Wall Prayer Session', '2025-02-05', '10:00:00', 2, 5),
('Jaffa Gallery Walk', '2025-09-05', '18:00:00', 10, 3),
('Arbel Cliff Sunset', '2025-05-11', '17:30:00', 5, 4),
('Ramon Crater Jeep Trip', '2025-06-12', '20:00:00', 6, 8),
('Ein Gedi Water Hike', '2025-03-16', '12:00:00', 3, 6),
('Dan River Archeology', '2025-08-11', '11:00:00', 8, 7),
('Meron Summit View', '2025-01-11', '14:00:00', 1, 9),
('Caesarea Theater Show', '2025-04-20', '20:00:00', 4, 10);

-- 7. Inserting 10 Event Registrations
INSERT INTO EVENTREGISTRATION (EventId) VALUES 
(1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- 8. Linking Participants to Groups (Many-to-Many) - 10 records
INSERT INTO PARTICIPANTGROUP (ParticipantID, GroupId) VALUES
(1, 2), (2, 2), (3, 1), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9);

-- 9. Linking Groups to Trips (Many-to-Many) - 10 records
INSERT INTO GROUPTRIP (GroupId, TripId) VALUES
(2, 1), (3, 2), (10, 3), (4, 4), (8, 5), (5, 6), (6, 7), (7, 8), (1, 9), (9, 10);
COMMIT;