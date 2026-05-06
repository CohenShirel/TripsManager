-- 1. אילוץ CHECK: מוודא שגיל המשתתף הוא לפחות 5 (מניעת טעויות הקלדה)
ALTER TABLE public.participant 
ADD CONSTRAINT chk_participant_age_min CHECK (age >= 5);

INSERT INTO public.participant (firstname, lastname, age) 
VALUES ('TEST', 'TEST', 2);

-- 2. אילוץ UNIQUE: מוודא שאימייל של מדריך לא יופיע פעמיים במערכת
ALTER TABLE public.guide 
ADD CONSTRAINT uni_guide_email UNIQUE (email);

INSERT INTO public.guide (guidename, email, specialization) 
VALUES ('TEST', 'guide1@example.com', 'TEST');

-- 3. אילוץ NOT NULL: מוודא ששם המיקום תמיד יוזן (שדה חובה)
ALTER TABLE public.location 
ALTER COLUMN locationname SET NOT NULL;

INSERT INTO public.location (locationname, region, address) 
VALUES (NULL, 'TEST', 'TEST');