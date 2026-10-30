import sqlite3

conn = sqlite3.connect('data/vista_flare.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
print("Tables in vista_flare.db:")
for t in sorted(tables):
    cursor.execute(f"SELECT count(*) FROM {t}")
    c = cursor.fetchone()[0]
    print(f"  {t}: {c}")

cursor.execute("SELECT source, count(*) FROM jobs GROUP BY source;")
print("\nJobs by source:")
for s, c in cursor.fetchall():
    print(f"  {s}: {c}")

conn.close()

