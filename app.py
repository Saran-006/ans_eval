import getter as gt
import sys


try:
    notes=sys.argv[2]
    db=sys.argv[3]
    ans=sys.argv[4]
    qp=sys.argv[5]
    if sys.argv[1]=="1":
        gt.build_db(notes,db)
except:
    notes="samples/bn1.pdf"
    db="vector_db/t1.pkl"
    ans="samples/ans1.pdf"
    qp="samples/qp1.pdf"



ans_txt=gt.get_ans(ans)

ldb=gt.load_db(db)

ak=gt.get_ans_key(gt.get_question(qp),ldb)

# print(ans_txt)

print(gt.get_mark(ak,ans_txt))

