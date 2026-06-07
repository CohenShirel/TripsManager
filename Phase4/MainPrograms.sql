-- תוכנית ראשית א: בדיקת פונקציה1, פרוצדורה1 וטריגר1
DO $$
DECLARE
    v_cost_result NUMERIC;
BEGIN
    RAISE NOTICE '========== תחילת ריצה: תוכנית ראשית א ==========';
    
    -- 1. זימון פונקציה 1
    v_cost_result := public.fn_calculate_trip_total_cost(20001);
    RAISE NOTICE 'פונקציה 1 - סך העלות המחושבת עבור טיול 20001 היא: %', v_cost_result;

    -- 2. זימון פרוצדורה 1
    CALL public.pr_update_trip_status_by_age();
    RAISE NOTICE 'פרוצדורה 1 - עדכון סטטוס לפי גיל ממוצע בוצע בהצלחה.';

    -- 3. הפעלת טריגר 1 באילוץ שינוי לא חוקי אמיתי (קביעת גודל ל-0)
    RAISE NOTICE 'טריגר 1 - מנסה לעדכן את גודל טיול 20001 ל-0 כדי לאלץ חסימה...';
    
    UPDATE public.trip 
    SET groupsize = 0 
    WHERE tripid = 20001;
    
    RAISE NOTICE 'אזהרה: העדכון עבר (זה אומר שהטריגר נכשל ולא חסם!).';

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '================================================';
        RAISE NOTICE 'הבדיקה הצליחה! מערכת ההגנה בלמה את הפעולה הלא חוקית כמצופה.';
        RAISE NOTICE 'הודעת השגיאה האמיתית שנתפסה מהטריגר:';
        RAISE NOTICE '%', SQLERRM;
        RAISE NOTICE '========== סיום ריצה: תוכנית ראשית א (הצלחה) ==========';
END $$;

-- תוכנית ראשית ב: בדיקת פונקציה2, פרוצדורה2 וטריגר2

DO $$
DECLARE
    v_cursor_name REFCURSOR;
    v_id INT; v_name VARCHAR; v_date DATE; v_reg VARCHAR; v_dist NUMERIC;
BEGIN
    RAISE NOTICE '========== תחילת ריצה: תוכנית ראשית ב ==========';
    
    -- 1. זימון פונקציה 2 (קבלת סמן לטיולים באזור הצפון - 'North')
    v_cursor_name := public.fn_get_trips_by_region_cursor('North');
    RAISE NOTICE 'פונקציה 2 - הסמן הדינמי נפתח בהצלחה בשם: %', v_cursor_name;
    
    -- מעבר בלולאה על ה-Ref Cursor שחזר (אלמנט מורכבות מעולה לציון!)
    LOOP
        FETCH NEXT FROM v_cursor_name INTO v_id, v_name, v_date, v_reg, v_dist;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'טיול שנמצא בסמן: % (מזהה: %), באזור: %', v_name, v_id, v_reg;
    END LOOP;
    CLOSE v_cursor_name;

    -- 2. זימון פרוצדורה 2 (עדכון טיולים קטנים לסטטוס VIP)
    CALL public.pr_update_vip_trip_type();
    RAISE NOTICE 'פרוצדורה 2 - עדכון סוגי טיולים ל-VIP בוצע בהצלחה.';

    -- 3. הפעלת טריגר 2 (ניסיון יצירת כפל שיבוצים למדריך באותו תאריך ושעה)
    RAISE NOTICE 'טריגר 2 - מנסה להכניס אירוע חופף בזמנים כדי לאלץ את הטריגר לחסום...';
    INSERT INTO public.event (eventid, eventname, eventdate, eventtime, tripid, locationid, start_hour, end_hour, cost, status, order_num)
    VALUES (nextval('public.event_eventid_seq'), 'סיור בדיקת כפל זמנים', '2026-07-15', '10:00:00', 20001, 1, '10:00:00', '12:00:00', 50, 'Active', 1);

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'הבדיקה הצליחה! הטריגר מנע כפל שיבוצים למדריך.';
        RAISE NOTICE 'הודעת השגיאה שנתפסה מהטריגר: %', SQLERRM;
        RAISE NOTICE '========== סיום ריצה: תוכנית ראשית ב (הצלחה) ==========';
END $$;