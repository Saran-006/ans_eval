import getter as gt
import sys

notes="samples/bn1.pdf"
db="vector_db/t1.pkl"
ans="samples/ans1.pdf"
qp="samples/qp1.pdf"

if sys.argv[1]=="1":
    gt.build_db(notes,db)

ans_txt=gt.get_anstxt(ans)

ldb=gt.load_db(db)

ak=gt.get_ans_key(gt.get_question(qp),ldb)

print(ak)
print("\n\n\n","-"*20,"\n\n\n")
print(ans_txt)