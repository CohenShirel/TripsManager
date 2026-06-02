------------------------
--1
-------------------
-- יצירה או עדכון של הפרוצדורה הראשונה: עדכון סטטוס טיול לפי ממוצע גילאי המשתתפים
CREATE OR REPLACE PROCEDURE pr_update_trip_status_by_age()
AS $$
DECLARE
    -- אלמנט תכנות: שימוש ברשומה (Record) לצורך לולאת הסמן
    v_trip_record RECORD;
    
    -- משתנה לאחסון תוצאת חישוב הגיל הממוצע
    v_avg_age NUMERIC;
BEGIN
    -- אלמנט תכנות: לולאת סמן משתמע (Implicit Cursor Loop) שעוברת טיול-טיול על כל הטיולים במערכת
    FOR v_trip_record IN SELECT tripid, tripname FROM public.trip LOOP
        
        -- חישוב ממוצע הגילאים של המשתתפים המשויכים לקבוצה הרלוונטית של הטיול הנוכחי
        SELECT AVG(p.age) INTO v_avg_age
        FROM public.participant p
        JOIN public.participantgroup pg ON p.participantid = pg.participantid
        JOIN public."GROUP" g ON pg.groupid = g.groupid
        WHERE g.guideid = (SELECT guideid FROM public.trip WHERE tripid = v_trip_record.tripid);

        -- אלמנט תכנות: הסתעפות לוגית (IF) - בדיקה האם הגיל הממוצע גבוה מ-30
        IF v_avg_age > 30 THEN
            
            -- אלמנט תכנות: פקודת עדכון פיזית (DML - UPDATE) בטבלת הטיולים
            UPDATE public.trip 
            SET status = 'Adults Only' 
            WHERE tripid = v_trip_record.tripid;
            
            -- הדפסת הודעת פלט ומעקב אופרטיבית למסך (בלשונית Messages)
            RAISE NOTICE 'Trip "%" (ID: %) updated to Adults Only. Avg Age: %', 
                v_trip_record.tripname, v_trip_record.tripid, ROUND(v_avg_age, 1);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- פקודת זימון והפעלת הפרוצדורה הראשונה לבדיקת הנתונים
CALL pr_update_trip_status_by_age();




---------------------
--2
---------------
-- שלב 1: הכנת נתוני הבדיקה - עדכון זמני של טיול 20001 לצורך הצגת מצב "לפני השינוי"
UPDATE public.trip SET groupsize = 8, triptype = 'Regular' WHERE tripid = 20001;

-- שלב 2: שאילתת שליפה להצגת הנתונים המקוריים של הטיול בדו"ח (הוכחת מצב "לפני")
SELECT tripid, tripname, groupsize, triptype FROM public.trip WHERE tripid = 20001;

-- שלב 3: יצירה או עדכון של הפרוצדורה השנייה: עדכון סוג הטיול ל-VIP עבור קבוצות קטנות
CREATE OR REPLACE PROCEDURE pr_update_vip_trip_type()
AS $$
DECLARE
    -- אלמנט תכנות: שימוש ברשומה (Record) לצורך לולאת הסמן
    v_trip_record RECORD;
BEGIN
    -- אלמנט תכנות: לולאת סמן משתמע (Implicit Cursor Loop) שעוברת טיול-טיול על כל הטיולים במערכת
    FOR v_trip_record IN SELECT tripid, tripname, groupsize FROM public.trip LOOP
        
        -- אלמנט תכנות: הסתעפות לוגית (IF) - בדיקה האם גודל הקבוצה קטן או שווה ל-10 משתתפים
        IF v_trip_record.groupsize <= 10 THEN
            
            -- אלמנט תכנות: פקודת עדכון פיזית וברורה (DML - UPDATE) של סוג הטיול בטבלה
            UPDATE public.trip 
            SET triptype = 'VIP' 
            WHERE tripid = v_trip_record.tripid;
            
            -- הדפסת הודעת פלט ומעקב אופרטיבית למסך (בלשונית Messages)
            RAISE NOTICE 'Trip "%" (ID: %) with group size % updated to VIP type.', 
                v_trip_record.tripname, v_trip_record.tripid, v_trip_record.groupsize;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- שלב 4: פקודת זימון והפעלת הפרוצדורה השנייה במערכת
CALL pr_update_vip_trip_type();

-- שלב 5: שאילתת שליפה סופית להצגת השינוי בדו"ח (הוכחת מצב "אחרי השינוי" - סוג הטיול הפך ל-VIP)
SELECT tripid, tripname, groupsize, triptype FROM public.trip WHERE tripid = 20001;