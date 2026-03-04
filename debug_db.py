import sqlite3
conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute("SELECT id,subject_id,student_name,score,answer_path,result_text,created_at FROM evaluation ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()
print('EVALS:')
for r in rows:
    print(r)
cur.execute("SELECT id,name,notes_path,question_path,vector_db_path FROM subject")
print('\nSUBJECTS:')
for r in cur.fetchall():
    print(r)
conn.close()
