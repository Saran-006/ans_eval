import qp2txt as qp
import re

def get_question_from_pdf(path):
    content=qp.get_content_from_pdf(path)

    lines=content.split('\n')

    section_points=[]

    for i in range(len(lines)):

        if re.match(r'^(PART|SECTION|UNIT)\b[\s:–—-]*[A-Z0-9]{1,4}\b',lines[i].upper()):#return its a section point
            section_points.append(i)


    question_points=[]

    for i in range(len(section_points)-1):

        for j in range(section_points[i],section_points[i+1]):
            
            if re.match(r'^[(\[{)]?[0-9]{1,3}[\]})\.\s]',lines[j]):
                question_points.append(j)


    for j in range(section_points[-1],len(lines)):
        
        if re.match(r'^[(\[{)]?[0-9]{1,3}[\]})\.\s]',lines[j]):
            question_points.append(j)

        
    end_of_qp=-1
    for i in range(len(lines)):
        if re.match(r'^\s*(END\s+OF\s+QUESTION\s+PAPER|END\s+OF\s+QP|ALL\s+THE\s+BEST|BEST\s+OF\s+LUCK|GOOD\s+LUCK|THANK\s+YOU)\s*\.?\s*$',lines[i].upper()):
            end_of_qp=i
            break

    questions=[]
    for i in range(len(question_points)-1):
        temp=""
        for j in range(question_points[i],question_points[i+1]):
            if j in section_points:break
            temp+=lines[j]
        questions.append(temp)

    temp=""
    for i in range(question_points[-1],end_of_qp):
        if j in section_points:break
        temp+=lines[i]
    questions.append(temp)

    # for i in questions:print(i)

    sectionq=[]

    for i in range(len(section_points)-1):

        temp=0

        section=range(section_points[i],section_points[i+1])
            
        for j in question_points:
            if j in section:temp+=1

        sectionq.append(temp)
    temp=0
    section=range(section_points[-1],end_of_qp)
            
    for j in question_points:
        if j in section:temp+=1

    sectionq.append(temp)

    question_set=[]
    x=0
    limit=0
    for i in sectionq:
        temp=[]
        limit+=i
        for j in questions:
            if x==limit:break
            temp.append(questions[x])
            x+=1
        question_set.append(temp)


    # print(question_set)
    question_paper=dict()

    for i in range(len(question_set)):
        question_paper[lines[section_points[i]]]=question_set[i]

    return question_paper

if __name__=='__main__':
    question_paper=get_question_from_pdf('../samples/qp1.pdf')
    for i,j in enumerate(question_paper):print(j,":",question_paper[j])