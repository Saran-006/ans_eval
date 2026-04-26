def extract_questions(question_paper):
    
    list=[]

    for i,j in enumerate(question_paper):
        list.extend(question_paper[j])
        
    return list