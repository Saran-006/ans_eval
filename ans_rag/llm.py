import requests
import time
# import ocr_model as ocr
# import doc_ocr as ocr
import ans_rag.new_ocr as ocr
import ans_rag.get_img as imager

OPENROUTER_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

def call_llm(prompt, retries=3):

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
        "max_tokens": 150
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

            elif response.status_code == 401:
                raise Exception("Invalid API key")

            elif response.status_code in (429, 500, 502, 503):
                time.sleep(2)  # retry delay
                continue

            else:
                raise Exception(f"API Error {response.status_code}: {response.text}")

        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2)

    return None


def fix_text(ocr_text):

    prompt = fprompt = fprompt = f"""
You are an OCR correction system for evaluating exam answer sheets.

IMPORTANT RULES:

1. You may correct spelling errors.
2. You may correct obvious OCR character mistakes (example: "7T" → "IT").
3. You may fix small grammar mistakes (example: "plants makes" → "plants make").
4. You may replace a word ONLY if it is clearly an OCR mistake.
5. DO NOT add new information.
6. DO NOT introduce new concepts or vocabulary.
7. DO NOT remove repeated answers.
8. DO NOT merge numbered blocks.
9. Preserve all numbering exactly as written.
10. Keep original sentence structure as much as possible.
11. retain question numbers its crucial for marking
12. "[page]" means its a splitter tag added by me dont remove it

If the same answer appears twice, keep both.

Return corrected text in the same numbered block format.

OCR TEXT:
{ocr_text}
"""

    corrected = call_llm(prompt)
    print(corrected)




def get_all_text(path):
    images=imager.extract_img(path)
    full_text=""
    for i in images:
        full_text+="[page]\n"+ocr.do_ocr(i)+"\n"

    return fix_text(full_text)




if __name__ == "__main__":
    get_all_text("../samples/test_pgs.pdf")