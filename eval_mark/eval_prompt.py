import re

def extract_qno(question):
    m = re.match(r'\s*(\d+)', question)
    return m.group(1) if m else None


def extract_marks(question):
    m = re.search(r'\((\d+)\)', question)
    return m.group(1) if m else "1"


def build_eval_prompt(retrieval_dict, ans_dict):

    prompt = """Answer length expectation depends on the marks for the question.

    go very liberally i want you to correct in optimistic manner that students feels happy

    which means i want you check only few keypoints

    Evaluation strictness depends on the marks of the question.

If max_marks == 1:
• Only check if the key concept appears.
• Ignore grammar errors, spelling mistakes, or small OCR errors.
• Do not require the full textbook definition.
• If the main idea is present, award full marks.
• If the idea is partially correct, award 0.5 marks instead of 0.

If max_marks == 2:
• Expect one or two correct points.
• If only one point is correct or the answer is partially correct, award partial marks such as 0.5 or 1.0 instead of giving 0.

If max_marks >= 5:
• Expect multiple correct points or a proper explanation.
• Award marks proportionally based on the number of correct ideas.
• If the answer is partially correct, give intermediate marks such as 2.5, 3.5, etc., instead of only whole numbers.

General marking rule:
• Prefer partial marking instead of strict zero when the student shows some correct understanding.
• Minor grammar, spelling, or OCR mistakes should not reduce marks if the concept is correct.
• Marks may be integers or half-step values such as 0.5, 1.5, 2.5, 3.5 depending on correctness.

If the question carries 1 mark:
- Accept very short answers.
- If the key concept or correct keyword appears, award full marks.
- Do not expect full definitions or detailed explanations.
-try to give full mark in many cases if they got atleast small keypoint

If the question carries 2 marks:
- Expect one or two correct points or a short explanation.

If the question carries 5 marks or more:
- Expect multiple correct points or a detailed explanation.
- Partial marks should be awarded based on the number of correct ideas present."""

    prompt += """
You are an exam evaluator.

Evaluate each student answer using the provided reference material.

Rules:
- Compare the student answer with the reference material.
- Award marks according to the maximum marks for the question.
- Partial marks are allowed.
- If the answer is incorrect give 0.
- Do not invent information outside the reference material.

Return result in JSON format:
{
 "question_number": int,
 "max_marks": int,
 "awarded_marks": int,
 "feedback": "short explanation"
}

----------------------------------------
"""

    for question, chunks in retrieval_dict.items():

        qno = extract_qno(question)
        marks = extract_marks(question)

        if not qno:
            continue

        student_answer = ans_dict.get(f"{qno})", "")

        context = ""
        for c in chunks:
            txt = c.get("content", "").strip()
            if txt:
                context += txt + "\n"

        prompt += f"""
QUESTION {qno} ({marks} marks)
{question}

REFERENCE MATERIAL
{context}

STUDENT ANSWER
{student_answer}

----------------------------------------
"""
    return prompt+""" Return the evaluation as a SINGLE JSON array containing all question objects.

Example format:

[
 { "question_number":1, "max_marks":1, "awarded_marks":1, "feedback":"..." },
 { "question_number":2, "max_marks":1, "awarded_marks":0, "feedback":"..." }
]"""