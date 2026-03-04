import qp_rag.separator as qp
import notes_rag.builder as builder
import notes_rag.loader as loader
import helper as hlp
import sys


questions=hlp.extract_questions(qp.get_question_from_pdf(sys.argv[1]))

builder.build_vector_db(sys.argv[2],sys.argv[3])

def extract_ans_key(questions):
    key_ans=dict()

    for question in questions:
        retrivals=loader.query_vector_db(question)
        key_ans[question]=retrivals

    return key_ans



