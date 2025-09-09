import urllib.request, urllib.parse, urllib.error
import sqlite3
import json
import time
import sys

# Base URL for OpenStreetMap Nominatim API
serviceurl = "https://nominatim.openstreetmap.org/search?"

# Connect to SQLite database (creates if not exists)
conn = sqlite3.connect("opengeo.sqlite")
cur = conn.cursor()

cur.execute(
    """
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)
"""
)

# Ask for input file name
fname = input("Enter .data file name (default: where.data): ").strip()
if len(fname) < 1:
    fname = "where.data"

try:
    fh = open(fname)
except FileNotFoundError:
    print(f"Error: File '{fname}' not found.")
    sys.exit(1)

count = 0
nofound = 0

for line in fh:
    if count >= 100:
        print("Retrieved 100 locations, restart to retrieve more.")
        break

    address = line.strip()
    if not address:
        continue

    print("")
    cur.execute("SELECT geodata FROM Locations WHERE address = ?", (address,))
    row = cur.fetchone()
    if row is not None:
        print("Found in database:", address)
        continue

    # Query parameters for Nominatim
    parms = {"q": address, "format": "json", "limit": 1}

    url = serviceurl + urllib.parse.urlencode(parms)
    print("Retrieving:", url)

    try:
        uh = urllib.request.urlopen(url)
        data = uh.read().decode()
    except Exception as e:
        print("Error retrieving data:", e)
        continue

    print("Retrieved", len(data), "characters", data[:40].replace("\n", " "))
    count += 1

    try:
        js = json.loads(data)
    except:
        print("Failed to parse JSON:", data)
        continue

    if not js:
        print("==== Download error ===")
        continue

    if len(js) == 0:
        print("==== Object not found ====")
        nofound += 1

    # Insert data into database as plain text
    cur.execute(
        """INSERT INTO Locations (address, geodata)
           VALUES (?, ?)""",
        (address, data),
    )
    conn.commit()

    if count % 10 == 0:
        print("Pausing for a bit...")
        time.sleep(2)

fh.close()

if nofound > 0:
    print("Number of locations not found:", nofound)

print("Run geodump1.py to read the data from the database and generate a JS file.")
