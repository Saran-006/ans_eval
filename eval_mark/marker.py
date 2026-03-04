import requests
import time 

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

def get_mark():
    return