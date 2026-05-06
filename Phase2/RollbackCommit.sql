-- ======================================================================
-- חלק 3: בקרת טרנזקציות (Rollback & Commit)
-- ======================================================================

-- תרחיש 1: בדיקת ROLLBACK (ביטול שינויים)
BEGIN; 

-- עדכון זמני של שם המדריך
UPDATE public.guide SET guidename = 'TEST ROLLBACK' WHERE guideid = 1;

-- בדיקה בתוך הטרנזקציה 
SELECT * FROM public.guide WHERE guideid = 1;

ROLLBACK; 

--בדיקה לאחר ביטול 
SELECT * FROM public.guide WHERE guideid = 1;


-- תרחיש 2: בדיקת COMMIT (קיבוע שינויים)
-- --------------------------------------------------------------
BEGIN; 

-- עדכון התמחות למדריך מספר 2
UPDATE public.guide SET specialization = 'Expert Hiker' WHERE guideid = 2;

--בדיקה
SELECT guideid, guidename, specialization FROM public.guide WHERE guideid = 2;

COMMIT; 

--בדיקה סופית
SELECT guideid, guidename, specialization FROM public.guide WHERE guideid = 2;