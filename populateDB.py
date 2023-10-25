import sqlite3
import json

# Open the JSON file and load the data
with open('staticresources/city_data.json', 'r', encoding='utf-8') as json_file:
    city_data = json.load(json_file)

# Create a connection to the SQLite database
conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

# Clear (delete all data from) the 'cities' table
cursor.execute("DROP TABLE cities")

# Create a table to store city data if it doesn't exist
cursor.execute('''
    CREATE TABLE cities (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT
    )
''')

# Iterate through the JSON data and insert it into the database
# Iterate through the JSON data and insert it into the database
for city in city_data:
    id = city['id']
    name = city['name']
    country = city['country']

    # Insert the city data into the 'cities' table
    cursor.execute("INSERT INTO cities (id, name, country) VALUES (?, ?, ?)", (id, name, country))


# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Database populated with city data.")
