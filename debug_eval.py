import sqlite3,os,sys
eid = int(sys.argv[1]) if len(sys.argv)>1 else 2
conn=sqlite3.connect('data.db')
cur=conn.cursor()
cur.execute("SELECT id, subject_id, student_name, score, answer_path, result_text, created_at FROM evaluation WHERE id=?",(eid,))
ev=cur.fetchone()
print('EVAL:', ev)
cur.execute('SELECT id,name,notes_path,question_path,vector_db_path FROM subject WHERE id=?',(ev[1],))
sub=cur.fetchone()
print('SUBJECT:', sub)
conn.close()
up=os.path.join(os.getcwd(),'uploads')
dbdir=os.path.join(os.getcwd(),'vector_db')
ans=os.path.join(up, ev[4]) if ev and ev[4] else None
qp=os.path.join(up, sub[3]) if sub and sub[3] else None
vdb=os.path.join(dbdir, sub[4]) if sub and sub[4] else None
print('paths:')
print('answer:', ans, 'exists=', os.path.exists(ans) if ans else None)
print('question:', qp, 'exists=', os.path.exists(qp) if qp else None)
print('vectordb:', vdb, 'exists=', os.path.exists(vdb) if vdb else None)
