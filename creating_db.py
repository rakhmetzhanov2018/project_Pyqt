import sqlite3

con = sqlite3.connect('my.db')
cur = con.cursor()
cur.execute("""CREATE TABLE words (
   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
   name TEXT,
   part_of_speech TEXT,
   normal_form TEXT,
   characteristics TEXT
   );
""")
con.commit()
