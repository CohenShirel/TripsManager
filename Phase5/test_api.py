import requests
import json
import traceback

BASE_URL = "http://127.0.0.1:5000/api"

endpoints = [
    ("/trips", "trip"),
    ("/groups", "group"),
    ("/guides", "guide"),
    ("/participants", "participant"),
    ("/events", "event"),
    ("/poi", "location")
]

results = {"success": [], "error": []}

for endpoint, name in endpoints:
    try:
        res = requests.get(f"{BASE_URL}{endpoint}")
        if res.status_code == 200:
            data = res.json()
            results["success"].append(f"GET {endpoint} (Loaded {len(data)} items)")
            
            # If we have items, test GET single item
            if len(data) > 0:
                pk_field = [k for k in data[0].keys() if 'id' in k.lower()]
                if pk_field:
                    test_id = data[0][pk_field[0]]
                    single_res = requests.get(f"{BASE_URL}{endpoint}/{test_id}")
                    if single_res.status_code == 200:
                        results["success"].append(f"GET {endpoint}/{test_id} (Success)")
                    else:
                        results["error"].append(f"GET {endpoint}/{test_id} Failed: {single_res.status_code} - {single_res.text}")
        else:
            results["error"].append(f"GET {endpoint} Failed: {res.status_code} - {res.text}")
    except Exception as e:
        results["error"].append(f"GET {endpoint} Exception: {str(e)}")

print("Test Results:")
for s in results["success"]:
    print("✅", s)
for e in results["error"]:
    print("❌", e)

# Test Advanced Endpoints
adv = [
    "/helpers/trips",
    "/helpers/guides",
    "/helpers/routes",
    "/helpers/poi",
    "/helpers/regions",
    "/stats",
    "/upcoming-trips",
    "/guides-by-region",
    "/recent-events",
    "/queries"
]

print("\nTesting advanced endpoints:")
for a in adv:
    try:
        res = requests.get(f"{BASE_URL}{a}")
        if res.status_code == 200:
            print("✅", a)
        else:
            print("❌", a, res.status_code, res.text)
    except Exception as e:
        print("❌", a, "Exception:", str(e))
