import os

def search_files():
    search_dir = r"C:\Users\shire\.gemini\antigravity\scratch\TripsManager\Phase5\static"
    for filename in os.listdir(search_dir):
        if filename.endswith(".js") or filename.endswith(".html"):
            path = os.path.join(search_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "locations" in line.lower():
                        print(f"{filename}:{i+1}: {line.strip()}")

search_files()
