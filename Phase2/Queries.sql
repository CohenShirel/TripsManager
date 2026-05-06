-- ======================================================================
-- 1. שאילתות שליפה (SELECT)
-- ======================================================================
--1
--אירועים במיקומים שיש בהם מעל 10 אירועים

SELECT e.eventname, l.locationname, e.eventdate
FROM event e
JOIN location l ON e.locationid = l.locationid
WHERE e.locationid IN (
    SELECT locationid FROM event
    GROUP BY locationid
    HAVING COUNT(*) > 10
);

SELECT e.eventname, l.locationname, e.eventdate
FROM event e
JOIN (SELECT locationid FROM event GROUP BY locationid HAVING COUNT(*) > 10) temp 
  ON e.locationid = temp.locationid
JOIN location l ON e.locationid = l.locationid;

-- 2
-- מדריכים שאינם משויכים לאף קבוצה (פנויים)
SELECT gu.guideid, gu.guidename
FROM guide gu
LEFT JOIN "GROUP" g ON gu.guideid = g.guideid
WHERE g.groupid IS NULL;


SELECT guideid, guidename
FROM guide
WHERE guideid NOT IN (SELECT guideid FROM "GROUP");

--3
-- המטרה: להציג את המדריכים שהדריכו לפחות קבוצה אחת שנוצרה בשנת 2025.
SELECT gu.guideid, gu.guidename, gu.specialization
FROM guide gu
WHERE EXISTS (
    SELECT 1 
    FROM "GROUP" g 
    WHERE g.guideid = gu.guideid 
    AND EXTRACT(YEAR FROM g.createddate) = 2025
);

SELECT guideid, guidename, specialization
FROM guide
WHERE guideid IN (
    SELECT guideid 
    FROM "GROUP" 
    WHERE EXTRACT(YEAR FROM createddate) = 2025
);


-- 4
-- להציג את רשימת המדריכים שמעבירים יותר מטיול אחד.
SELECT gu.guideid, gu.guidename, COUNT(t.tripid) AS trip_count
FROM guide gu
JOIN trip t ON gu.guideid = t.guideid
GROUP BY gu.guideid, gu.guidename
HAVING COUNT(t.tripid) > 1
ORDER BY trip_count DESC;

SELECT gu.guideid, gu.guidename
FROM guide gu
WHERE (SELECT COUNT(*) FROM trip t WHERE t.guideid = gu.guideid) > 1
ORDER BY gu.guidename;

--5
-- שאילתה 5: דו"ח רישום שנתי/חודשי (פירוק תאריכים)
SELECT 
    EXTRACT(YEAR FROM registrationdate) AS reg_year,
    EXTRACT(MONTH FROM registrationdate) AS reg_month,
    COUNT(*) AS total_registrations
FROM eventregistration
GROUP BY reg_year, reg_month
ORDER BY reg_year DESC, reg_month DESC;

--6
-- שאילתה 6: קטלוג טיולים מלא (חיבור 4 טבלאות)
SELECT 
    t.tripname,
    g.groupname,
    gu.guidename,
    l.locationname,
    t.startdate
FROM trip t
JOIN grouptrip gt ON t.tripid = gt.tripid
JOIN "GROUP" g ON gt.groupid = g.groupid
JOIN guide gu ON t.guideid = gu.guideid
JOIN event e ON t.tripid = e.tripid
JOIN location l ON e.locationid = l.locationid
LIMIT 20; 

--7
-- שאילתה 7: משתתפים מעל גיל 30 הרשומים לאירועים במיקום ספציפי
SELECT DISTINCT p.firstname, p.lastname, p.age, l.locationname
FROM participant p
JOIN eventregistration er ON p.participantid = er.registrationid
JOIN event e ON er.eventid = e.eventid
JOIN location l ON e.locationid = l.locationid
WHERE p.age > 30 AND l.region = 'North'
ORDER BY p.age ASC;

--8
-- שאילתה 8: אירועים קרובים בשעות הבוקר (פירוק זמן)
SELECT 
    eventname, 
    eventdate,
    EXTRACT(HOUR FROM eventtime) AS hour_of_day,
    EXTRACT(MINUTE FROM eventtime) AS minute_of_hour
FROM event
WHERE eventtime BETWEEN '06:00:00' AND '12:00:00'
  AND eventdate > '2026-01-01'
ORDER BY eventdate ASC;
-- ======================================================================
-- 2. שאילתות מחיקה (DELETE)
-- ======================================================================

-- 1. ניקוי הרשמות משתתפים מקבוצות ללא טיולים עתידיים
DELETE FROM participantgroup
WHERE groupid IN (
    SELECT pg.groupid
    FROM participantgroup pg
    WHERE NOT EXISTS (
        SELECT 1
        FROM grouptrip gt
        JOIN trip t ON gt.tripid = t.tripid
        WHERE gt.groupid = pg.groupid
        AND t.startdate > CURRENT_DATE
    )
);

-- 2. הסרת הרשמות לאירועים בטיולים ללא משתתפים בפועל

DELETE FROM eventregistration
WHERE eventid IN (
    SELECT e.eventid
    FROM event e
    JOIN trip t ON e.tripid = t.tripid
    WHERE t.startdate < CURRENT_DATE
    AND NOT EXISTS (
        SELECT 1
        FROM grouptrip gt
        JOIN participantgroup pg ON gt.groupid = pg.groupid
        WHERE gt.tripid = t.tripid
    )
);

-- 3. מחיקת מדריכים מתחילים באזורים צפופים ללא צפי עבודה
-- שלב א': העברת היסטוריה למדריך ברירת מחדל (1)
UPDATE trip
SET guideid = 1
WHERE guideid IN (
    SELECT guideid FROM guide
    WHERE experienceyears < 3
    AND region IN (
        SELECT region FROM guide GROUP BY region HAVING COUNT(*) > 10
    )
    AND NOT EXISTS (
        SELECT 1 FROM trip t WHERE t.guideid = guide.guideid AND t.startdate > CURRENT_DATE
    )
);

UPDATE "GROUP"
SET guideid = 1
WHERE guideid IN (
    SELECT guideid FROM guide
    WHERE experienceyears < 3
    AND region IN (
        SELECT region FROM guide GROUP BY region HAVING COUNT(*) > 10
    )
    AND NOT EXISTS (
        SELECT 1 FROM trip t WHERE t.guideid = guide.guideid AND t.startdate > CURRENT_DATE
    )
);

-- שלב ב': המחיקה עצמה מתוך טבלת המדריכים
DELETE FROM guide
WHERE experienceyears < 3
AND region IN (
    SELECT region FROM guide GROUP BY region HAVING COUNT(*) > 10
)
AND NOT EXISTS (
    SELECT 1 FROM trip t WHERE t.guideid = guide.guideid AND t.startdate > CURRENT_DATE
);


-- ======================================================================
-- 3. שאילתות עדכון (UPDATE)
-- ======================================================================

-- 1. עדכון טיולים מלאים (2 משתתפים ומעלה) לסטטוס "Sold Out"
UPDATE trip
SET triptype = 'Sold Out'
WHERE tripid IN (
    SELECT t.tripid
    FROM trip t
    JOIN grouptrip gt ON t.tripid = gt.tripid
    JOIN participantgroup pg ON gt.groupid = pg.groupid
    WHERE t.startdate > CURRENT_DATE
    GROUP BY t.tripid
    HAVING COUNT(pg.participantid) >= 2
);

-- 2. קידום מדריכים פעילים עם וותק של 3+ שנים ל-"Senior Guide"
UPDATE guide
SET specialization = 'Senior Guide'
WHERE guideid IN (
    SELECT g.guideid
    FROM guide g
    WHERE g.experienceyears >= 3
      AND (SELECT COUNT(*) 
           FROM trip t 
           WHERE t.guideid = g.guideid 
             AND t.enddate > CURRENT_DATE - INTERVAL '1 year') > 0
);

-- 3. סימון אירועים עתידיים באזור הצפון כ-"Premium"
UPDATE event ev
SET eventname = eventname || ' (Premium)'
WHERE EXISTS (
    SELECT 1
    FROM trip t
    JOIN location l ON ev.locationid = l.locationid
    WHERE t.tripid = ev.tripid
      AND l.region = 'North'
      AND t.startdate > CURRENT_DATE
);

