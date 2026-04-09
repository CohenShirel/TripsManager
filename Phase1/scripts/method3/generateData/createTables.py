import csv
import random
from datetime import datetime, timedelta

def random_date(start_year=2025, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime('%Y-%m-%d')

def generate_all_data():
    # 1. GUIDE (500 rows)
    with open('guide.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['guideid', 'guidename', 'phone', 'email', 'specialization', 'region', 'experienceyears'])
        for i in range(1, 501):
            w.writerow([i, f"Guide_{i}", f"050-{random.randint(1000000, 9999999)}", f"guide{i}@trip.com", 
                        random.choice(['Hiking', 'Culinary', 'History', 'Extreme']), 
                        random.choice(['North', 'South', 'Center', 'Jerusalem']), random.randint(1, 30)])

    # 2. PARTICIPANT (20,000 rows)
    with open('participant.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['participantid', 'lastname', 'firstname', 'phone', 'email', 'age'])
        for i in range(1, 20001):
            w.writerow([i, f"Last_{i}", f"First_{i}", f"052-{random.randint(1000000, 9999999)}", f"user{i}@gmail.com", random.randint(18, 80)])

    # 3. LOCATION (500 rows)
    with open('location.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['locationid', 'locationname', 'region', 'address', 'description'])
        for i in range(1, 501):
            w.writerow([i, f"Location_{i}", random.choice(['North', 'South', 'Center']), f"Street {i}", "Beautiful spot"])

    # 4. TRIP (500 rows)
    with open('trip.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['tripid', 'tripname', 'startdate', 'enddate', 'triptype', 'guideid'])
        for i in range(1, 501):
            s_date = datetime(2026, random.randint(1, 6), random.randint(1, 28))
            e_date = s_date + timedelta(days=random.randint(1, 5))
            w.writerow([i, f"Trip_Plan_{i}", s_date.strftime('%Y-%m-%d'), e_date.strftime('%Y-%m-%d'), 
                        random.choice(['Day Trip', 'Overnight']), random.randint(1, 500)])

    # 5. GROUP (500 rows)
    with open('group.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['groupid', 'groupname', 'description', 'createddate', 'guideid'])
        for i in range(1, 501):
            w.writerow([i, f"Group_{i}", "Fun group", random_date(2025, 2025), random.randint(1, 500)])

    # 6. EVENT (500 rows)
    with open('event.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['eventid', 'eventname', 'eventdate', 'eventtime', 'tripid', 'locationid'])
        for i in range(1, 501):
            w.writerow([i, f"Event_{i}", random_date(2026, 2026), f"{random.randint(8,20)}:00:00", random.randint(1, 500), random.randint(1, 500)])

    # 7. EVENTREGISTRATION (20,000 rows)
    with open('eventregistration.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['registrationid', 'registrationdate', 'eventid'])
        for i in range(1, 20001):
            w.writerow([i, random_date(2026, 2026), random.randint(1, 500)])

    # 8. GROUPTRIP (1,000 rows)
    with open('grouptrip.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['groupid', 'tripid'])
        for _ in range(1000):
            w.writerow([random.randint(1, 500), random.randint(1, 500)])

    # 9. PARTICIPANTGROUP (20,000 rows)
    with open('participantgroup.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['participantid', 'groupid'])
        for i in range(1, 20001):
            w.writerow([i, random.randint(1, 500)])

    print("Success! All 9 CSV files created.")

generate_all_data()