-- =====================================================================================
-- תיאור מילולי לדו"ח:
-- פונקציה זו מקבלת כמפתח קלט מזהה טיול ומחשבת את אומדן התקציב והעלות הכוללת שלו.
-- הפונקציה משלבת שליפה בסיסית של אורך מסלול הטיול מטבלת route ומכפילה אותו בעלות בסיס קבועה.
-- לאחר מכן, נעשה שימוש בסמן מפורש (Explicit Cursor) בלולאה על מנת לסרוק שורה-שורה את כל
-- האירועים המשויכים לאותו טיול מטבלת event ולסכום את עלויותיהם. הפונקציה כוללת מנגנון
-- בדיקת תקינות המוודא שהטיול קיים, ואם אינו קיים, היא מפעילה חריגה (Exception) מותאמת
-- אישית המונעת כשל במערכת ומחזירה ערך מוגן.
-- =====================================================================================

CREATE OR REPLACE FUNCTION fn_calculate_trip_total_cost(p_trip_id INT)
RETURNS NUMERIC AS $$
DECLARE
    v_total_cost NUMERIC := 0;
    v_event_cost NUMERIC;
    v_route_distance NUMERIC;
    v_trip_exists INT;

    -- אלמנט תכנות: סמן מפורש (Explicit Cursor) לשליפת עלויות האירועים של הטיול
    cur_events CURSOR FOR 
        SELECT COALESCE(cost, 0) FROM public.event WHERE tripid = p_trip_id;
BEGIN
    -- אלמנט תכנות: בדיקת תקינות וחריגה (Exception) לווידוא קיום הטיול
    SELECT COUNT(*) INTO v_trip_exists FROM public.trip WHERE tripid = p_trip_id;
    IF v_trip_exists = 0 THEN
        RAISE EXCEPTION 'Trip with ID % does not exist.', p_trip_id;
    END IF;

    -- אלמנט תכנות: שליפה בסיסית והסתעפות (LEFT JOIN לשילוב נתוני טבלת הטיול והמסלול)
    SELECT COALESCE(r.distance_km, 0) INTO v_route_distance
    FROM public.trip t
    LEFT JOIN public.route r ON t.route_id = r.route_id
    WHERE t.tripid = p_trip_id;

    -- חישוב עלות התחלתית על בסיס מרחק הנסיעה בקילומטרים כפול תעריף בסיס
    v_total_cost := v_route_distance * 5;

    -- אלמנט תכנות: לולאה פתוחה (LOOP) וסריקה שורה-שורה של ה-Cursor המפורש
    OPEN cur_events;
    LOOP
        FETCH cur_events INTO v_event_cost;
        EXIT WHEN NOT FOUND; -- תנאי יציאה מהלולאה כאשר נגמרות הרשומות

        -- צבירת עלויות האירועים לתוך משתנה העלות הכוללת
        v_total_cost := v_total_cost + v_event_cost;
    END LOOP;
    CLOSE cur_events;

    -- החזרת התוצאה הסופית מעוגלת לשתי ספרות לאחר הנקודה
    RETURN ROUND(v_total_cost, 2);

EXCEPTION
    -- אלמנט תכנות: מנגנון טיפול בשגיאות וחריגות מערכת (Exception Handling)
    WHEN OTHERS THEN
        RAISE NOTICE 'Error occurred in fn_calculate_trip_total_cost: %', SQLERRM;
        RETURN 0;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------------------------------------------
-- פקודות בדיקה להפקת צילומי מסך עבור הדו"ח:
-- -------------------------------------------------------------------------------------

-- פקודה 1: בדיקת הרצה תקינה (להראות ערך מספרי שחושב בלשונית Data Output)
SELECT fn_calculate_trip_total_cost(20001);

-- פקודה 2: בדיקת הכשלה מכוונת (להראות זריקת שגיאה באדום בלשונית Messages כהוכחת Exception)
SELECT fn_calculate_trip_total_cost(99999);



-- =====================================================================================
-- תיאור מילולי לדו"ח:
-- פונקציה זו מקבלת כפרמטר קלט שם של אזור גיאוגרפי ומחזירה סמן דינמי (Ref Cursor) 
-- המכיל את כל הטיולים המתוכננים באותו אזור. הפונקציה משלבת פקודת קשר (JOIN) בין טבלת
-- הטיולים trip לטבלת המסלולים route כדי לסנן את הנתונים בצורה מדויקת על בסיס האזור המבוקש.
-- בנוסף, הפונקציה כוללת מנגנון בדיקת תקינות קלט המונע הזנת ערכים ריקים או ריקים מתוכן,
-- ומפעיל חריגה (Exception) במקרה של קלט שגוי או חסר.
-- =====================================================================================

CREATE OR REPLACE FUNCTION fn_get_trips_by_region_cursor(p_region_name VARCHAR)
RETURNS refcursor AS $$
DECLARE
    -- אלמנט תכנות: הגדרת סמן הפניה דינמי (Ref Cursor) בשם מוגדר מראש
    v_trips_cursor refcursor := 'trips_by_region_cursor'; 
BEGIN
    -- אלמנט תכנות: בדיקת תקינות קלט והסתעפות (IF) - מוודאים שהמשתמש לא שלח ערך ריק או NULL
    IF p_region_name IS NULL OR p_region_name = '' THEN
        -- אלמנט תכנות: זריקת חריגה (Exception) מותאמת אישית המונעת הרצה של קלט שגוי
        RAISE EXCEPTION 'Region name cannot be empty or null.';
    END IF;

    -- אלמנט תכנות: פתיחת ה-Cursor הדינמי לשליפת הטיולים באזור המבוקש באמצעות קשר (JOIN) בין הטבלאות
    OPEN v_trips_cursor FOR 
        SELECT t.tripid, t.tripname, t.startdate, r.region, r.distance_km
        FROM public.trip t
        JOIN public.route r ON t.route_id = r.route_id
        WHERE UPPER(r.region) = UPPER(p_region_name);
        
    RETURN v_trips_cursor;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------------------------------------------
-- פקודות בדיקה להפקת צילומי מסך עבור הדו"ח (בדיקת Ref Cursor דורשת עטיפה בטרנזקציה פתוחה):
-- -------------------------------------------------------------------------------------

-- בלוק א': הוכחת הרצה תקינה ושליפת נתונים
BEGIN;
SELECT fn_get_trips_by_region_cursor('North'); -- זימון הפונקציה וקבלת שם הסמן
FETCH ALL IN "trips_by_region_cursor";          -- משיכת הנתונים מהסמן (לצלם את לשונית Data Output 2 עם השורות)
COMMIT;

-- בלוק ב': הוכחת מנגנון חסימת שגיאות (Exception)
BEGIN;
SELECT fn_get_trips_by_region_cursor('');      -- שליחת מחרוזת ריקה בכוונה להפעלת החריגה
FETCH ALL IN "trips_by_region_cursor";          -- (לצלם את הודעת השגיאה באדום בלשונית Messages)
COMMIT;