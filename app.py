import qp_rag.separator as qp
import notes_rag.builder as builder
import notes_rag.loader as loader
import sys

questions=qp.get_question_from_pdf(sys.argv[1])

builder.build_vector_db(sys.argv[2])

question=""
loader.query_vector_db(question)

