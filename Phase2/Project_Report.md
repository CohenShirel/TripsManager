# דוח פרויקט בסיסי נתונים - שלב ב': שאילתות ואילוצים

**מטרת השלב:** תשאול בסיס הנתונים, עדכון נתונים, הוספת אילוצים ואינדקסים תוך בחינת יעילות (Performance Tuning) והבנת ההבדלים בין גישות כתיבה שונות.

---

## 1. שאילתות אחזור נתונים (SELECT) - השוואת יעילות

<details>
<summary><b>1. אירועים במיקומים פופולריים (מעל 10 אירועים)</b></summary>
<br>
<b>תיאור:</b> מציג אירועים המתקיימים במיקומים פעילים במיוחד כדי לאתר עומסים לוגיסטיים.

<b>דרך א' (IN):</b>

```sql
SELECT e.eventname, l.locationname, e.eventdate
FROM event e
JOIN location l ON e.locationid = l.locationid
WHERE e.locationid IN (
    SELECT locationid FROM event
    GROUP BY locationid
    HAVING COUNT(*) > 10
);
```

<b>דרך ב' (JOIN עם טבלה זמנית):</b>

```sql
SELECT e.eventname, l.locationname, e.eventdate
FROM event e
JOIN (SELECT locationid FROM event GROUP BY locationid HAVING COUNT(*) > 10) temp 
  ON e.locationid = temp.locationid
JOIN location l ON e.locationid = l.locationid;
```

**תמונה דרך ב':**
![דרך ב](./images/SELECT1.JPEG)

> **השוואת יעילות:** דרך ב' (JOIN) יעילה יותר. המנוע מבצע את חישוב הקיבוץ פעם אחת בלבד ומחבר את התוצאה, בעוד ששימוש ב-IN עלול להריץ את הבדיקה באופן חוזר או פחות אופטימלי עבור קבוצות נתונים גדולות.

</details>

<details>
<summary><b>2. מדריכים פנויים (ללא קבוצה משויכת)</b></summary>
<br>
<b>תיאור:</b> איתור מדריכים שאינם משובצים לאף קבוצה כרגע.

<b>דרך א' (LEFT JOIN):</b>

```sql
SELECT gu.guideid, gu.guidename
FROM guide gu
LEFT JOIN "GROUP" g ON gu.guideid = g.guideid
WHERE g.groupid IS NULL;
```

**תמונה דרך א':**
![דרך א](./images/SELECT2.JPEG)

<b>דרך ב' (NOT IN):</b>

```sql
SELECT guideid, guidename
FROM guide
WHERE guideid NOT IN (SELECT guideid FROM "GROUP");
```

> **השוואת יעילות:** דרך א' (LEFT JOIN) יציבה ויעילה יותר ברוב מנועי ה-SQL. שימוש ב-NOT IN נחשב למסוכן כי אם תת-השאילתה תחזיר ערך NULL אחד, כל השאילתה החיצונית לא תחזיר תוצאות כלל.

</details>

<details>
<summary><b>3. מדריכים שהדריכו קבוצות משנת 2025</b></summary>
<br>
<b>תיאור:</b> שליפת מדריכים פעילים לפי שנת יצירת הקבוצה.

<b>דרך א' (EXISTS):</b>

```sql
SELECT gu.guideid, gu.guidename, gu.specialization
FROM guide gu
WHERE EXISTS (
    SELECT 1 
    FROM "GROUP" g 
    WHERE g.guideid = gu.guideid 
    AND EXTRACT(YEAR FROM g.createddate) = 2025
);
```

**תמונות דרך א':**
![דרך א](./images/SELECT3.JPEG)

<b>דרך ב' (IN):</b>

```sql
SELECT guideid, guidename, specialization
FROM guide
WHERE guideid IN (
    SELECT guideid 
    FROM "GROUP" 
    WHERE EXTRACT(YEAR FROM createddate) = 2025
);
```

> **השוואת יעילות:** EXISTS יעיל יותר מ-IN מכיוון שהוא מבוסס על יציאה מוקדמת – הוא מפסיק את הסריקה ברגע שהוא מוצא את ההתאמה הראשונה, במקום לבנות ולסרוק רשימה מלאה של כל הערכים.

</details>

<details>
<summary><b>4. מדריכים המעבירים יותר מטיול אחד</b></summary>
<br>
<b>תיאור:</b> איתור מדריכים העובדים במספר טיולים להערכת עומס.

<b>דרך א' (GROUP BY):</b>

```sql
SELECT gu.guideid, gu.guidename, COUNT(t.tripid) AS trip_count
FROM guide gu
JOIN trip t ON gu.guideid = t.guideid
GROUP BY gu.guideid, gu.guidename
HAVING COUNT(t.tripid) > 1
ORDER BY trip_count DESC;
```

**תמונה דרך א':**
![דרך א](./images/SELECT4.JPEG)


<b>דרך ב' (Correlated Subquery):</b>

```sql
SELECT gu.guideid, gu.guidename
FROM guide gu
WHERE (SELECT COUNT(*) FROM trip t WHERE t.guideid = gu.guideid) > 1
ORDER BY gu.guidename;
```

> **השוואת יעילות:** דרך א' (GROUP BY) יעילה משמעותית. דרך ב' משתמשת בתת-שאילתה מקושרת שרצה מחדש עבור כל שורה בטבלת המדריכים, מה שיוצר עומס חישובי כבד מאד ככל שהטבלאות גדלות.

</details>

---

## 2. שאילתות אחזור נתונים מורכבות (SELECT)

### 5. דו"ח רישום חודשי ושנתי (פירוק תאריכים)
**תיאור:** פירוק תאריכי ההרשמה לקבלת התפלגות נרשמים לאורך זמן.

```sql
SELECT 
    EXTRACT(YEAR FROM registrationdate) AS reg_year,
    EXTRACT(MONTH FROM registrationdate) AS reg_month,
    COUNT(*) AS total_registrations
FROM eventregistration
GROUP BY reg_year, reg_month
ORDER BY reg_year DESC, reg_month DESC;
```

**הרצה ותוצאה:**
![הרצה ותוצאה ששאילתה 5](./images/SELECT5.JPEG)

### 6. קטלוג טיולים מלא (חיבור 4 טבלאות)
**תיאור:** תצוגה מרכזית המחברת נתוני טיולים, קבוצות, מדריכים ומיקומים.

```sql
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
```

**הרצה ותוצאה:**
![הרצה ותוצאה ששאילתה 6](./images/SELECT6.JPEG)

### 7. משתתפים בוגרים (30+) באזור הצפון
**תיאור:** פילוח משתתפים לפי גיל ואזור גיאוגרפי.

```sql
SELECT DISTINCT p.firstname, p.lastname, p.age, l.locationname
FROM participant p
JOIN eventregistration er ON p.participantid = er.registrationid
JOIN event e ON er.eventid = e.eventid
JOIN location l ON e.locationid = l.locationid
WHERE p.age > 30 AND l.region = 'North'
ORDER BY p.age ASC;
```

**הרצה ותוצאה:**
![הרצה ותוצאה ששאילתה 7](./images/SELECT7.JPEG)

### 8. אירועי בוקר (פירוק זמנים)
**תיאור:** שליפת אירועים המתקיימים בין השעות 06:00 ל-12:00 בבוקר.

```sql
SELECT 
    eventname, 
    eventdate,
    EXTRACT(HOUR FROM eventtime) AS hour_of_day,
    EXTRACT(MINUTE FROM eventtime) AS minute_of_hour
FROM event
WHERE eventtime BETWEEN '06:00:00' AND '12:00:00'
  AND eventdate > '2026-01-01'
ORDER BY eventdate ASC;
```

**הרצה ותוצאה:**
![הרצה ותוצאה ששאילתה 8](./images/SELECT8.JPEG)

---

## 3. שאילתות מחיקה (DELETE)

**1. ניקוי הרשמות משתתפים מקבוצות ללא טיולים עתידיים**

**תיאור:** מחיקת משתתפים מקבוצות שאין להן טיולים עתידיים, כדי לנקות נתונים היסטוריים לא פעילים.

```sql
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
```

* ![DB לפני מחיקה 1](./images/BDelete1.jpg)
* ![פעולת עדכון 3](./images/Delete1.jpg)
* ![הרצה ו-DB אחרי מחיקה 1](./images/ADelete1.jpg)

**2. הסרת הרשמות לאירועים בטיולים ללא משתתפים בפועל**

**תיאור:** הסרת הרשמות מאירועי עבר ריקים (שלא הגיע אליהם אף משתתף בפועל), לייעול בסיס הנתונים.

```sql
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
```


* ![DB לפני מחיקה 2](./images/BDelete2.jpg)
* ![פעולת עדכון 3](./images/Delete2.jpg)
* ![הרצה ו-DB אחרי מחיקה 2](./images/ADelete2.jpg)

**3. מחיקת מדריכים מתחילים באזורים צפופים (כולל העברת היסטוריה)**

**תיאור:** מחיקת מדריכים חסרי ניסיון מאזורים עמוסים שאין להם שיבוצים עתידיים, תוך העברת היסטוריית ההדרכה שלהם למדריך ברירת מחדל כדי למנוע נתונים יתומים.

```sql
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
```
```sql
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
```

-- שלב ב': המחיקה עצמה מתוך טבלת המדריכים
```sql
DELETE FROM guide
WHERE experienceyears < 3
AND region IN (
    SELECT region FROM guide GROUP BY region HAVING COUNT(*) > 10
)
AND NOT EXISTS (
    SELECT 1 FROM trip t WHERE t.guideid = guide.guideid AND t.startdate > CURRENT_DATE
);
```

* ![DB לפני מחיקה 3](./images/BDelete3.jpg)
* ![פעולת עדכון 3](./images/Delete3.jpg)
* ![הרצה ו-DB אחרי מחיקה 3](./images/ADelete3.jpg)

---

## 4. שאילתות עדכון (UPDATE)

**1. עדכון טיולים מלאים לסטטוס "Sold Out"**

**תיאור:** עדכון סטטוס אוטומטי ל-"Sold Out" עבור טיולים עתידיים שכבר נרשמו אליהם 2 משתתפים ומעלה.

```sql
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
```

* ![DB לפני עדכון 1](./images/BUpdate1.jpg)
* ![פעולת עדכון 3](./images/Update1.jpg)
* ![הרצה ו-DB אחרי עדכון 1](./images/AUpdate1.jpg)

**2. קידום מדריכים מנוסים ל-"Senior Guide"**

**תיאור:** קידום מדריכים פעילים (שהדריכו בשנה האחרונה) עם לפחות 3 שנות ותק לסטטוס 'Senior Guide'.

```sql
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
```

* ![DB לפני עדכון 2](./images/BUpdate2.jpg)
* ![פעולת עדכון 3](./images/Update2.jpg)
* ![הרצה ו-DB אחרי עדכון 2](./images/AUpdate2.jpg)

**3. סימון אירועים עתידיים בצפון כ-"Premium"**

**תיאור:** הוספת התגית '(Premium)' לשם האירוע עבור כל האירועים העתידיים המתוכננים לאזור הצפון.

```sql
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
```

* ![DB לפני עדכון 3](./images/BUpdate3.jpg)
* ![פעולת עדכון 3](./images/Update3.jpg)
* ![הרצה ו-DB אחרי עדכון 3](./images/AUpdate3.jpg)

---

## 5. אילוצים חדשים (Constraints)

**1. אילוץ CHECK: גיל מינימלי למשתתף (5+)**
* **תיאור:** מטרת האילוץ היא למנוע טעויות הקלדה בהזנת נתוני המשתתפים.
* **פקודה:**
```sql
ALTER TABLE public.participant 
ADD CONSTRAINT chk_participant_age_min CHECK (age >= 5);
```
* **ניסיון הכנסת נתון שגוי:** 
```sql
INSERT INTO public.participant (firstname, lastname, age) 
VALUES ('TEST', 'TEST', 2);
```
* **שגיאת הרצה:** ![שגיאת אילוץ 1](./images/Constraints2.jpeg)

**2. אילוץ UNIQUE: כתובת אימייל ייחודית למדריך**
* **תיאור:** מטרת האילוץ היא למנוע כפילויות של מדריכים במערכת.
* **פקודה:**
```sql
ALTER TABLE public.guide 
ADD CONSTRAINT uni_guide_email UNIQUE (email);
```
* **ניסיון הכנסת נתון שגוי:** 
```sql
INSERT INTO public.guide (guidename, email, specialization) 
VALUES ('TEST', 'guide1@example.com', 'TEST');
```
* **שגיאת הרצה:** ![שגיאת אילוץ 2](./images/Constraints3.jpeg)

**3. אילוץ NOT NULL: חובת הזנת שם מיקום**
* **תיאור:** מטרת האילוץ לוודא שאין מיקומים חסרי שם במערכת.
* **פקודה:**
```sql
ALTER TABLE public.location 
ALTER COLUMN locationname SET NOT NULL;
```
* **ניסיון הכנסת נתון שגוי:** 
```sql
INSERT INTO public.location (locationname, region, address) 
VALUES (NULL, 'TEST', 'TEST');
```
* **שגיאת הרצה:** ![שגיאת אילוץ 3](./images/Constraints4.jpeg)

---

## 6. אינדקסים ושיפור ביצועים (Indexes)

**1. אינדקס על גיל המשתתף (Age)**
* **מוטיבציה ותועלת:** מאפשר פילוח ושליפה מהירה של קבוצות גיל ספציפיות, תוך מניעת סריקה מלאה של הטבלה ומעבר לגישה ישירה.
* **פקודה:**
```sql
CREATE INDEX idx_participant_age ON public.participant(age);
```

* **זמני ריצה:** * לפני אינדקס: ![זמן לפני 1](./images/INDEX1.jpeg)
  * אחרי אינדקס: ![זמן אחרי 1](./images/INDEX2.jpeg)

>> **הסבר התוצאות:** זמן הריצה ירד מ-**1.735ms** ל-**1.326ms**. השיפור (אפילו בטבלה קטנה) מראה שהמנוע עבר מחיפוש איטי שסורק את כל הטבלה (Full Table Scan) לגישה מהירה וישירה לנתונים (Index Scan).

**2. אינדקס על תאריך האירוע (Eventdate)**
* **מוטיבציה ותועלת:** מקצר משמעותית את זמן החיפוש עבור אירועים עתידיים או בטווחי תאריכים ספציפיים.
* **פקודה:**
```sql
CREATE INDEX idx_event_date ON public.event(eventdate);
```
* **זמני ריצה:** * לפני אינדקס: ![זמן לפני 2](./images/INDEX11.jpeg)
  * אחרי אינדקס: ![זמן אחרי 2](./images/INDEX22.jpeg)

> **הסבר התוצאות:** נרשם שיפור דרמטי מאוד! זמן הריצה צנח מ-**3.174ms** ל-**0.111ms**. זה מעיד על כך שחיפוש וסינון אירועים לפי תאריך מבוצעים כעת ביעילות מקסימלית ובשבריר מהזמן המקורי.

**3. אינדקס על מפתח זר (Locationid בטבלת Event)**
* **מוטיבציה ותועלת:** מאיץ ביצועי JOIN בין טבלת האירועים לטבלת המיקומים, פעולה נפוצה מאוד במערכת סיורים וטיולים.
* **פקודה:** 
```sql
CREATE INDEX idx_event_locationid ON public.event(locationid);
```
* **זמני ריצה:** * לפני אינדקס: ![זמן לפני 3](./images/INDEX111.jpeg)
  * אחרי אינדקס: ![זמן אחרי 3](./images/INDEX222.jpeg)


> **הסבר התוצאות:** גם כאן נרשם שיפור עצום – זמן הריצה ירד מ-**5.254ms** ל-**0.415ms** (יותר מפי 10 מהר יותר). הדבר מוכיח שהאינדקס מייעל בצורה משמעותית את עומס החישוב בעת ביצוע פעולות JOIN בין הטבלאות.

---

## 7. בקרת טרנזקציות (Rollback & Commit)

**תרחיש 1: בדיקת Rollback**
עדכון נתון וביטול הפעולה כדי לוודא יכולת התאוששות וחזרה לאחור.
```sql
BEGIN; 

-- עדכון זמני של שם המדריך
UPDATE public.guide SET guidename = 'TEST ROLLBACK' WHERE guideid = 1;

-- בדיקה בתוך הטרנזקציה 
SELECT * FROM public.guide WHERE guideid = 1;

ROLLBACK; 

--בדיקה לאחר ביטול 
SELECT * FROM public.guide WHERE guideid = 1;
```

* פעולת העדכון בתוך הטרנזקציה (הודעת הצלחה): ![הרצת העדכון](./images/ROLBACK1.jpeg)
* מצב לפני ה-Rollback (בתוך הטרנזקציה): ![לפני Rollback](./images/ROLBACK2.jpeg)
* מצב אחרי ה-Rollback (החזרה לאחור): ![אחרי Rollback](./images/ROLBACK3.jpeg)


**תרחיש 2: בדיקת Commit**
עדכון נתון ושמירתו הסופית בבסיס הנתונים.
```sql
BEGIN; 

-- עדכון התמחות למדריך מספר 2
UPDATE public.guide SET specialization = 'Expert Hiker' WHERE guideid = 2;

--בדיקה
SELECT guideid, guidename, specialization FROM public.guide WHERE guideid = 2;

COMMIT; 

--בדיקה סופית
SELECT guideid, guidename, specialization FROM public.guide WHERE guideid = 2;
```

* מצב בתוך הטרנזקציה (לפני Commit): ![לפני Commit](./images/COMMIT1.jpeg)
* מצב אחרי ה-Commit (השמירה): ![אחרי Commit](./images/COMMIT2.jpeg)