import src.qp_rag.qpBuilder as qp
import src.notes_rag.vectorDB_builder as vectorDB_builder
import src.notes_rag.vectorDB_loader as vectorDB_loader
import src.utils.helper as hlp
import src.ans_rag.llm as llm
import src.eval_mark.marker as parser
import src.eval_mark.eval_prompt as prompter
import config



def build_db(notes_pdf,db):

    db=vectorDB_builder.build_vector_db(notes_pdf,db)

    return db



def load_db(path):
    
    return vectorDB_loader.load_db(path)



def get_question(qp_pdf):

    questions=hlp.extract_questions(qp.get_question_from_pdf(qp_pdf))

    return questions



def get_ans_key(questions,db):

    key_ans=dict()

    for question in questions:
        retrivals=vectorDB_loader.query_vector_db(question,db)
        key_ans[question]=retrivals

    return key_ans



def get_ans(path):

    ans=llm.get_all_text(path)

    # print(ans)
    
    return parser.ans_parser(ans)

def get_mark(retrival_dict,ans_text):
    
    prompts = prompter.build_eval_prompt(retrival_dict, ans_text)

    # Use higher max_tokens for evaluation (need more tokens for full JSON response)
    response=llm.call_llm(prompts, max_tokens=config.LLM_MAX_TOKENS_EVAL)

    # print(prompts,"\n\n\n\n")

    print(ans_text,config.OUTPUT_DELIMITER)

    print(response,config.OUTPUT_DELIMITER)

    mark=parser.get_score_string(f'{response}')

    print(mark)

