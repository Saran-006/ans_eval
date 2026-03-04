def extract_questions(question_paper):
    list=[]
    print(question_paper)
    for i,j in enumerate(question_paper):
        list.extend(question_paper[j])
    print(f'\n\n\n{list}\n\n\n')
    return list