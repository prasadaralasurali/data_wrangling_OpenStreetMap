import sqlite3
import csv
from pprint import pprint

sqlite_file = 'openstreet.db'
    
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS ways''')
conn.commit()

cur.execute('''
CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
) 
''')

conn.commit()

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['user'].decode("utf-8"),i['uid'], i['version'],i['changeset'],i['timestamp']) for i in dr]
    
cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
conn.commit()

conn.close()

#####################################################
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()
cur.execute('''DROP TABLE IF EXISTS ways_tags''')
conn.commit()

cur.execute('''
CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
)  
''')

conn.commit()

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['key'],i['value'].decode("utf-8"), i['type']) for i in dr]
    
cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()
conn.close()

#####################################################
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()
cur.execute('''DROP TABLE IF EXISTS ways_nodes''')
conn.commit()

cur.execute('''
CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
)  
''')

conn.commit()

with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['node_id'],i['position']) for i in dr]
    
cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
conn.commit()
conn.close()