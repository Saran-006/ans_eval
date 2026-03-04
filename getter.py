import qp_rag.separator as qp
import notes_rag.builder as builder
import notes_rag.loader as loader
import helper as hlp
import ans_rag.llm as llm



def build_db(notes_pdf,db):

    db=builder.build_vector_db(notes_pdf,db)

    return db



def load_db(path):
    
    return loader.load_db(path)



def get_question(qp_pdf):

    questions=hlp.extract_questions(qp.get_question_from_pdf(qp_pdf))

    return questions



def get_ans_key(questions,db):

    key_ans=dict()

    for question in questions:
        retrivals=loader.query_vector_db(question,db)
        key_ans[question]=retrivals

    return key_ans



def get_anstxt(path):

    ans=llm.get_all_text(path)
    
    return ans 






