import json

import re

def ans_parser(text):

    ansd = {}
    num = None
    ans = ""

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        m = re.match(r'^([0-9]+[)\]}\s])\s*(.*)', line)

        if m:
            if num is not None:
                ansd[num] = ans.strip()

            num = m.group(1)
            ans = m.group(2)

        else:
            ans += " " + line

    # store last answer
    if num is not None:
        ansd[num] = ans.strip()

    return ansd



import json
import re

def get_score_string(llm_json):

    data = json.loads(llm_json)

    scored = sum(q.get("awarded_marks", 0) for q in data)
    total = sum(q.get("max_marks", 0) for q in data)

    return f"{scored}/{total}"