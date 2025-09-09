import sqlite3
import json
import codecs

# Connect to the database
conn = sqlite3.connect("opengeo.sqlite")
cur = conn.cursor()

cur.execute("SELECT * FROM Locations")

# Ask for output filename
fname = input("Enter output JS file name (default: where.js): ").strip()
if len(fname) < 1:
    fname = "where.js"

try:
    fhand = codecs.open(fname, "w", "utf-8")
    fhand.write("myData = [\n")
except FileNotFoundError:
    print(f"Error: Could not create file '{fname}'.")
    quit()

count = 0
for row in cur:
    data = row[1]
    if not data:
        continue

    try:
        js = json.loads(data)
    except:
        continue

    if len(js) == 0:
        continue

    try:
        lat = js[0]["lat"]
        lng = js[0]["lon"]
        where = js[0]["display_name"].replace("'", "")
    except Exception as e:
        print("Unexpected format:", e)
        continue

    try:
        print(where, lat, lng)
        count += 1
        if count > 1:
            fhand.write(",\n")
        output = "[" + str(lat) + "," + str(lng) + ", '" + where + "']"
        fhand.write(output)
    except:
        continue

# Always close the array
fhand.write("\n];\n")

cur.close()
fhand.close()

print(f"{count} records written to {fname}")
if count == 0:
    print(f"No data found in database — generated empty file: {fname}")
print("Open where.html to view the data in a browser.")
