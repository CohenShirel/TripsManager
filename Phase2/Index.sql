-- ======================================================================
-- שלב ב: אופטימיזציה באמצעות אינדקסים
-- ======================================================================

-- 1. אינדקס על גיל המשתתף (לשיפור שאילתות סינון ופילוח דמוגרפי)
CREATE INDEX idx_participant_age ON public.participant(age);

-- בדיקת ביצועים (צלמי את ה-Execution Time):
EXPLAIN ANALYZE 
SELECT * FROM public.participant 
WHERE age BETWEEN 20 AND 30;


-- 2. אינדקס על תאריך האירוע (לשיפור שליפות של לוחות זמנים ואירועים קרובים)
CREATE INDEX idx_event_date ON public.event(eventdate);

-- בדיקת ביצועים:
EXPLAIN ANALYZE 
SELECT * FROM public.event 
WHERE eventdate BETWEEN '2026-01-01' AND '2026-12-31';


-- 3. אינדקס על locationid (לשיפור ביצועי JOIN בין אירועים למיקומים)
CREATE INDEX idx_event_locationid ON public.event(locationid);

-- בדיקת ביצועים:
EXPLAIN ANALYZE 
SELECT e.eventname, l.locationname 
FROM event e 
JOIN location l ON e.locationid = l.locationid 
WHERE l.region = 'North';