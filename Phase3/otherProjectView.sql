-- מחיקת המבט מהזיכרון במידה והוא קיים מניסיונות קודמים
DROP VIEW IF EXISTS v_trip_participants_details;

-- יצירת המבט החדש על בסיס מבנה הטבלאות המדויק מה-Backup השני
CREATE VIEW v_trip_participants_details AS
SELECT 
    p.participant_id,
    p.first_name,
    p.last_name,
    p.birth_date,
    t.trip_id,
    t.trip_name,
    t.start_date,
    t.status AS trip_status,
    g.license_number,
    g.experience_years
FROM 
    public.participants p
JOIN 
    public.trip_participants tp ON p.participant_id = tp.participant_id -- חיבור טבלת הקשר של השיבוכים לטיול
JOIN 
    public.trips t ON tp.trip_id = t.trip_id -- חיבור טבלת הטיולים כדי לקבל את שם הטיול ותאריכו
LEFT JOIN 
    public.guides g ON p.participant_id = g.participant_id;--חיבור טבלת המדריכים כדי לזהות מי מהם מדריך 



-- מה היא עושה? פונה למבט, סופרת את כמות המשתתפים ומקבצת אותם לפי שם הטיול.
SELECT 
    trip_name, 
    COUNT(participant_id) AS total_participants
FROM 
    v_trip_participants_details
GROUP BY 
    trip_name
ORDER BY 
    total_participants DESC;


-- מה היא עושה? מסננת מתוך המבט רק את השורות שבהן למשתתף יש רישיון מדריך ויש לו מעל 3 שנות ניסיון.
SELECT DISTINCT
    trip_name,
    start_date,
    trip_status
FROM 
    v_trip_participants_details
WHERE 
    license_number IS NOT NULL 
    AND experience_years > 3
ORDER BY 
    start_date ASC;
