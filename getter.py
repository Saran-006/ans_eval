import qp_rag.separator as qp
import notes_rag.builder as builder
import notes_rag.loader as loader
import helper as hlp
import ans_rag.llm as llm
import eval_mark.marker as parser
import eval_mark.eval_prompt as prompter



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



def get_ans(path):

    ans=llm.get_all_text(path)
    
    return parser.ans_parser(ans)

def get_mark(retrival_dict,ans_text):
    
    prompts = prompter.build_eval_prompt(retrival_dict, ans_text)

    response=llm.call_llm(prompts)

    # print(response)

    # print("----\n",response,"----\n")

    mark=parser.get_score_string(f'{response}')

    print(mark)

