# import re

# def extract_qno(question):
#     m = re.match(r'\s*(\d+)', question)
#     return m.group(1) if m else None


# def extract_marks(question):
#     m = re.search(r'\((\d+)\)', question)
#     return m.group(1) if m else "1"


# def build_eval_prompt(retrieval_dict, ans_dict):

#     # Debug: Show what we received
#     print(f"[EVAL_PROMPT] Received {len(ans_dict)} answers, {len(retrieval_dict)} questions", flush=True)
#     print(f"[EVAL_PROMPT] Answer keys BEFORE dedup: {list(ans_dict.keys())}", flush=True)
    
#     # Deduplicate and normalize answer keys
#     # Multiple formats of the same question (e.g., '3)' and '3 ') should be merged
#     normalized_ans_dict = {}
#     for key, value in ans_dict.items():
#         # Extract the leading number from the key
#         match = re.match(r'^(\d+)', key.strip())
#         if match:
#             qno = match.group(1)
#             # Only store if we haven't seen this question number, OR
#             # if current value is non-empty and previous value is empty
#             if qno not in normalized_ans_dict:
#                 normalized_ans_dict[qno] = value
#             elif value.strip() and not normalized_ans_dict[qno].strip():
#                 # Replace empty answer with non-empty one
#                 normalized_ans_dict[qno] = value
#         else:
#             # Key doesn't start with a number - shouldn't happen, but keep it
#             if key not in normalized_ans_dict:
#                 normalized_ans_dict[key] = value
    
#     ans_dict = normalized_ans_dict  # Use deduplicated dict
    
#     print(f"[EVAL_PROMPT] After dedup - final ans_dict has {len(ans_dict)} keys: {list(ans_dict.keys())}", flush=True)

#     prompt = """Answer length expectation depends on the marks for the question.

#     go very liberally i want you to correct in optimistic manner that students feels happy

#     which means i want you check only few keypoints

#     and if the answer is missing then in feed back only "No answer provided" should be placed 
#     dont use custom feed if the answer is missing in other cases you can use your feedbacks

#     Evaluation strictness depends on the marks of the question.

#     Sometimes the notes maybe incorrect in that case uses anyother source for correcting 
#     and if reference material is wrong then in that case you should focus on giving more mark
#     since its out of syllabus and they wrote something

# If max_marks == 1:
# • Only check if the key concept appears.
# • Ignore grammar errors, spelling mistakes, or small OCR errors.
# • Do not require the full textbook definition.
# • If the main idea is present, award full marks.
# • If the idea is partially correct, award 0.5 marks instead of 0.
# for one mark even if a single point gets related then give it more marks 0.5-1
# which means for 1 mark you should check only context dont try to match detailed answers

# If max_marks == 2:
# • Expect one or two correct points.
# • If only one point is correct or the answer is partially correct, award partial marks such as 0.5 or 1.0 instead of giving 0.

# If max_marks >= 5:
# • Expect multiple correct points or a proper explanation.
# • Award marks proportionally based on the number of correct ideas.
# • If the answer is partially correct, give intermediate marks such as 2.5, 3.5, etc., instead of only whole numbers.

# General marking rule:
# • Prefer partial marking instead of strict zero when the student shows some correct understanding.
# • Minor grammar, spelling, or OCR mistakes should not reduce marks if the concept is correct.
# • Marks may be integers or half-step values such as 0.5, 1.5, 2.5, 3.5 depending on correctness.

# If the question carries 1 mark:
# - Accept very short answers.
# - If the key concept or correct keyword appears, award full marks.
# - Do not expect full definitions or detailed explanations.
# -try to give full mark in many cases if they got atleast small keypoint

# If the question carries 2 marks:
# - Expect one or two correct points or a short explanation.

# If the question carries 5 marks or more:
# - Expect multiple correct points or a detailed explanation.
# - Partial marks should be awarded based on the number of correct ideas present."""

#     prompt += """
# You are an exam evaluator.

# Evaluate each student answer using the provided reference material.

# Rules:
# - Compare the student answer with the reference material.
# - Award marks according to the maximum marks for the question.
# - Partial marks are allowed.
# - If the answer is blank or shows "[BLANK - NO ANSWER PROVIDED]", award 0 marks and set feedback to exactly "No answer provided"
# - If the answer is incorrect give 0.
# - Do not invent information outside the reference material.

# Return result in JSON format:
# {
#  "question_number": int,
#  "max_marks": int,
#  "awarded_marks": int,
#  "feedback": "short explanation"
# }

# ----------------------------------------
# """

#     for question, chunks in retrieval_dict.items():

#         qno = extract_qno(question)
#         marks = extract_marks(question)

#         if not qno:
#             continue

#         # Normalize the question number
#         qno_norm = qno.strip()
        
#         # After deduplication, ans_dict keys are just question numbers
#         student_answer = ans_dict.get(qno_norm, "")

#         # print(chunks)

#         # Limit context to first 3-5 chunks to keep prompt reasonable size
#         context = ""
#         for i, c in enumerate(chunks):
#             if i >= 3:  # Only use first 3 chunks
#                 break
#             txt = c['content'].strip()
#             if txt:
#                 context += txt + "\n"

#         prompt += f"""
# QUESTION {qno} ({marks} marks)
# {question}

# REFERENCE MATERIAL
# {context}

# STUDENT ANSWER
# {student_answer if student_answer.strip() else "[BLANK - NO ANSWER PROVIDED]"}

# ----------------------------------------
# """
#     return prompt+""" Return the evaluation as a SINGLE JSON array containing all question objects.

# Example format:

# [
#  { "question_number":1, "max_marks":1, "awarded_marks":1, "feedback":"..." },
#  { "question_number":2, "max_marks":1, "awarded_marks":0, "feedback":"..." }
# ]"""



import re


MAX_QUESTION = 50   # safety cap


# -----------------------------
# Question number extraction
# -----------------------------
def normalize_qno(key):
    """
    Extract question number safely from OCR keys.
    Handles:
    1) , 1. , 1 : , 1- , ' 1)' , '10 '
    """

    if not key:
        return None

    match = re.match(r'^\s*(\d{1,2})', str(key))

    if not match:
        return None

    qno = int(match.group(1))

    if qno <= MAX_QUESTION:
        return str(qno)

    return None


# -----------------------------
# Clean OCR garbage
# -----------------------------
def clean_answer(text):

    if not text:
        return ""

    text = str(text)

    # Remove page tags
    text = re.sub(r'\[.*?\]', '', text)

    # Remove Part-I, Part II etc
    text = re.sub(r'Part\s*[- ]?\s*\w+', '', text, flags=re.I)

    # Remove stray single numbers (OCR noise)
    text = re.sub(r'\b\d\b', '', text)

    # Fix common OCR mistakes
    text = text.replace("6o", "to")
    text = text.replace("0f", "of")

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -----------------------------
# Normalize OCR answers
# -----------------------------
def normalize_answers(ans_dict):

    normalized = {}

    for key, value in ans_dict.items():

        qno = normalize_qno(key)

        if not qno:
            continue

        answer = clean_answer(value)

        # Keep first answer unless it is blank
        if qno not in normalized:
            normalized[qno] = answer

        elif not normalized[qno] and answer:
            normalized[qno] = answer

    return normalized


# -----------------------------
# Extract question number
# -----------------------------
def extract_qno(question):

    m = re.match(r'^\s*(\d+)', question)

    if m:
        return m.group(1)

    return None


# -----------------------------
# Extract marks
# -----------------------------
def extract_marks(question):

    m = re.search(r'\((\d+)\)', question)

    if m:
        return m.group(1)

    return "1"


# -----------------------------
# Remove duplicate RAG chunks
# -----------------------------
def build_context(chunks, limit=3):

    context = ""
    seen = set()

    for c in chunks:

        txt = c['content'].strip()

        if not txt:
            continue

        if txt in seen:
            continue

        context += txt + "\n"

        seen.add(txt)

        if len(seen) >= limit:
            break

    return context


# -----------------------------
# Main prompt builder
# -----------------------------
def build_eval_prompt(retrieval_dict, ans_dict):

    print("[EVAL_PROMPT] Raw answers:", ans_dict)

    ans_dict = normalize_answers(ans_dict)

    print("[EVAL_PROMPT] Normalized answers:", ans_dict)

    prompt = """
You are an exam evaluator.

Mark answers optimistically.

Evaluation rules:

1 mark questions:
- Accept very short answers
- If the key idea or keyword appears → FULL marks
- If partially correct → 0.5

2 mark questions:
- Expect 1–2 correct points
- Partial understanding → 0.5 or 1

5 mark questions:
- Expect explanation
- Award proportional marks (2.5, 3.5 etc)

Important:
- Ignore grammar mistakes
- Ignore OCR errors
- Do NOT require textbook definitions
- If the student shows correct understanding → reward marks

If the student answer is empty:
feedback MUST be exactly "No answer provided".

Return JSON:

{
 "question_number": int,
 "max_marks": int,
 "awarded_marks": float,
 "feedback": "short explanation"
}

----------------------------------------
"""

    for question, chunks in retrieval_dict.items():

        qno = extract_qno(question)

        if not qno:
            continue

        marks = extract_marks(question)

        student_answer = ans_dict.get(qno, "")

        context = build_context(chunks)

        prompt += f"""
QUESTION {qno} ({marks} marks)
{question}

REFERENCE MATERIAL
{context}

STUDENT ANSWER
{student_answer}

----------------------------------------
"""

    prompt += """
Return the evaluation as a SINGLE JSON array.

Example:

[
 { "question_number":1, "max_marks":1, "awarded_marks":1, "feedback":"Correct idea." },
 { "question_number":2, "max_marks":1, "awarded_marks":0.5, "feedback":"Partial idea." }
]
"""

    return prompt