# import qp_rag.separator as qp
# import notes_rag.builder as builder
# import notes_rag.loader as loader
# import helper as hlp
# import sys

# questions=hlp.extract_questions(qp.get_question_from_pdf(sys.argv[1]))

# builder.build_vector_db(sys.argv[2])


# for question in questions:
#     retrivals=loader.query_vector_db(question)
#     print()
#     print(question)
#     print(retrivals)

import ans_rag.llm as llm

llm.get_all_text("samples/test_pgs.pdf")
