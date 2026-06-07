--טריגר 1: בדיקת עדכון גודל קבוצה בטיול
CREATE OR REPLACE FUNCTION public.check_trip_groupsize_update()
RETURNS TRIGGER AS $$
DECLARE
    v_current_registered_count INTEGER;
BEGIN
    -- בדיקה האם גודל הקבוצה אכן השתנה
    IF NEW.groupsize IS DISTINCT FROM OLD.groupsize THEN
        
        -- הגנה בסיסית: מניעת ערכים קטנים או שווים ל-0
        IF NEW.groupsize <= 0 THEN
            RAISE EXCEPTION 'שגיאה: גודל קבוצה מקסימלי חייב להיות גדול מ-0.';
        END IF;

        -- ספירת המשתתפים הרשומים בפועל בטיול הנוכחי
        SELECT COUNT(DISTINCT pg.participantid)
        INTO v_current_registered_count
        FROM public.grouptrip gt
        JOIN public.participantgroup pg ON gt.groupid = pg.groupid
        WHERE gt.tripid = NEW.tripid;

        -- הגנה מתקדמת: מניעת הקטנה מתחת לכמות הרשומים בפועל
        IF NEW.groupsize < v_current_registered_count THEN
            RAISE EXCEPTION 'שגיאה: לא ניתן לעדכן את גודל הטיול ל-%, כיוון שכבר רשומים אליו % משתתפים בפועל.', 
                            NEW.groupsize, v_current_registered_count;
        END IF;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE; -- זריקת השגיאה הלאה לתוכנית הראשית המזמנת
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_check_trip_groupsize
BEFORE UPDATE ON public.trip
FOR EACH ROW
EXECUTE FUNCTION public.check_trip_groupsize_update();

-------------------------------------------------------------------------------------------

-- טריגר 2 - מניעת כפל שיבוצים באותו זמן למדריך
CREATE OR REPLACE FUNCTION public.validate_guide_availability_insert()
RETURNS TRIGGER AS $$
DECLARE
    v_guide_id INTEGER;
    v_conflicting_event_name VARCHAR(100);
BEGIN
    -- שליפת קוד המדריך המשויך לטיול של האירוע החדש
    SELECT guideid INTO v_guide_id 
    FROM public.trip 
    WHERE tripid = NEW.tripid;

    -- במידה ולטיול יש מדריך משובץ, נבדוק את זמינותו
    IF v_guide_id IS NOT NULL THEN
        -- חיפוש אירוע אחר של אותו מדריך שמתקיים בדיוק באותו תאריך ובאותה שעה
        SELECT e.eventname 
        INTO v_conflicting_event_name
        FROM public.event e
        JOIN public.trip t ON e.tripid = t.tripid
        WHERE t.guideid = v_guide_id
          AND e.eventdate = NEW.eventdate
          AND e.eventtime = NEW.eventtime
        LIMIT 1;

        -- אם נמצאה התנגשות (הסתעפות IF) - נזרוק שגיאה ונבלום את ה-INSERT
        IF v_conflicting_event_name IS NOT NULL THEN
            RAISE EXCEPTION 'שגיאה: המדריך (קוד %) כבר משובץ לאירוע "%" בתאריך % בשעה %.', 
                            v_guide_id, v_conflicting_event_name, NEW.eventdate, NEW.eventtime;
        END IF;
    END IF;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- שימוש בבלוק EXCEPTION לטיפול בחריגות
        RAISE NOTICE 'שגיאה בבדיקת זמינות מדריך: %', SQLERRM;
        RAISE;
END;
$$ LANGUAGE plpgsql;

-- 2. הצמדת הטריגר לטבלת event (לפני פעולת INSERT)
CREATE OR REPLACE TRIGGER trg_validate_guide_availability
BEFORE INSERT ON public.event
FOR EACH ROW
EXECUTE FUNCTION public.validate_guide_availability_insert();