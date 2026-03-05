import requests
import time 
import ans_rag.new_ocr as ocr
import ans_rag.get_img as imager

OPENROUTER_KEY = "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"


MODEL = "openai/gpt-3.5-turbo"

def call_llm(prompt, retries=3, max_tokens=2000):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "OCR Fixer"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens  # Use the parameter passed in
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

            elif response.status_code == 401:
                print(f"[LLM ERROR] Invalid API key", flush=True)
                raise Exception("Invalid API key")

            elif response.status_code in (429, 500, 502, 503):
                print(f"[LLM RETRY] Status {response.status_code}, retrying...", flush=True)
                time.sleep(2)
                continue

            else:
                print(f"[LLM ERROR] Status {response.status_code}: {response.text[:200]}", flush=True)
                raise Exception(f"API Error {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print(f"[LLM ERROR] Request timeout on attempt {attempt+1}", flush=True)
            if attempt == retries - 1:
                raise Exception("Request timeout after retries")
            time.sleep(2)
            
        except Exception as e:
            print(f"[LLM ERROR] Attempt {attempt+1}: {str(e)[:100]}", flush=True)
            if attempt == retries - 1:
                raise e
            time.sleep(2)

    return None


def fix_text(ocr_text):

    prompt = f"""You are an OCR correction tool used for processing exam answer sheets.

Your task is to fix character-level OCR mistakes while keeping the original text intact.

Important behavior:

• Many lines may contain random or meaningless text.
• Do NOT try to make sentences meaningful.
• Do NOT rewrite sentences.
• Do NOT expand phrases.
• Only fix clear OCR character mistakes.

Rules:

1. Correct obvious OCR character errors only.
   Example:
   Wwho → Who
   o(n → on
   Pyphou → Python

2. Prefer minimal edits. Change the smallest number of characters possible.

3. Never add new words.

4. Never rewrite the sentence.

5. Never guess missing words.

6. Do NOT fix grammar.

7. Question numbers may appear at the beginning of lines.

A line should be treated as numbered ONLY if it starts with something similar to:

[number][.)]

Examples:
1)
2.
15)

8. Some numbers may be malformed OCR characters:
! → 1
I → 1
S → 5
O → 0

Only fix these when they appear at the start of the line before a bracket or dot.

9. If a line does not match a numbered pattern, keep it unchanged except for clear OCR mistakes.

10. Preserve page markers like "[page]" exactly.

Return the corrected text with the same number of lines and the same structure.

11. OCR may sometimes merge a malformed question number with the first word
because the separator was lost.

Example OCR mistakes:
STytsyk → 5) Tytsyk
ITest → 1) Test
!Hello → 1) Hello

Explanation:
The number-like character (S, I, !, O) was originally a question number,
and the separator like ")" or "." and the space were lost by OCR.

If the very first character of the line resembles a malformed number and
it is directly attached to the first word, treat it as a question number
and reconstruct it.

Correction rule:
[number-like][Word] → [correct number])[space][Word]

Examples:
STytsyk → 5) Tytsyk
ITest → 1) Test
!Answer → 1) Answer

Apply this rule ONLY when:
• The number-like character appears at the very beginning of the line.
• It is immediately attached to the first word.
• It clearly resembles a malformed number.

Do NOT apply this rule if the word is clearly a normal word such as:
System, Some, Simple, Solution.

strip/remove the line if there is only some garbage texts like the 

and if its a question number then it like x) so we can easy detect them 

In those cases, keep the word unchanged.

OCR TEXT:
{ocr_text}
"""

    try:
        # Use very low max_tokens for OCR fixing to save credits (500 tokens)
        corrected = call_llm(prompt, max_tokens=500)
        if corrected:
            return corrected
    except Exception as e:
        print(f"[OCR FIX] Warning: OCR correction failed ({str(e)[:50]}), using raw text", flush=True)
    
    # If OCR fixing fails, return the original text as-is
    # Better to use raw OCR than to fail completely
    return ocr_text




def get_all_text(path):
    images=imager.extract_img(path)
    full_text=""
    for i in images:
        full_text+="[page]\n"+ocr.do_ocr(i)+"\n"

    # print("raw ocr :\n\n\n",full_text,"\n\n\n")

    return fix_text(full_text)




if __name__ == "__main__":
    get_all_text("../samples/t7.pdf")