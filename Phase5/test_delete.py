import urllib.request
try:
    req = urllib.request.Request('http://127.0.0.1:5000/api/locations/500', method='DELETE')
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read())
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Body:", e.read())
