from graph.db import Neo4JDB
import sys
import os

db = Neo4JDB(os.environ["NEO_DB_URL"], os.environ["NEO_DB_USER"], os.environ["NEO_DB_PASS"])
db.clear_db()
file_name = "test.csv"
if len(sys.argv) > 0:
	file_name = sys.argv[1]
print("Loading "+file_name + "...")
db.load_csv(file_name)
db.close()