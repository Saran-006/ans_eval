import pdfplumber
from statistics import median

pdf_path = "sample.pdf"

RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RESET = "\x1b[0m"


def group_into_lines(words, y_tol=3):
    lines = []
    current = []
    current_y = None

    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        if current_y is None:
            current_y = w["top"]

        if abs(w["top"] - current_y) <= y_tol:
            current.append(w)
        else:
            lines.append(current)
            current = [w]
            current_y = w["top"]

    if current:
        lines.append(current)

    return lines


def symbol_ratio(text):
    symbols = "{}();:=<>#[]"
    count = sum(text.count(s) for s in symbols)
    return count / max(len(text), 1)


with pdfplumber.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):

        print(f"\n--- Page {page_number} ---")

        page_height = page.height
        header_limit = page_height * 0.08
        footer_limit = page_height * 0.92

        words = page.extract_words(extra_attrs=["fontname", "size"])

        # Remove header/footer
        words = [
            w for w in words
            if header_limit < w["top"] < footer_limit
        ]

        if not words:
            continue

        sizes = [w["size"] for w in words]
        median_size = median(sizes)

        lines = group_into_lines(words)

        in_code_block = False
        brace_balance = 0

        for line in lines:
            line = sorted(line, key=lambda x: x["x0"])
            text = " ".join(w["text"] for w in line).strip()
            avg_size = sum(w["size"] for w in line) / len(line)
            word_count = len(line)
            indent = min(w["x0"] for w in line)
            sym_ratio = symbol_ratio(text)

            # ---- Code Detection ----
            if "{" in text:
                brace_balance += text.count("{")
                in_code_block = True

            if "}" in text:
                brace_balance -= text.count("}")
                if brace_balance <= 0:
                    in_code_block = False
                    brace_balance = 0

            looks_like_code = (
                sym_ratio > 0.15 or
                indent > 100 or
                any(k in text for k in ["#include", "public:", "private:", "int ", "void ", "def ", "return"])
            )

            if looks_like_code or in_code_block:
                print(GREEN + text + RESET)
                continue

            # ---- Heading Scoring ----
            score = 0

            if avg_size > median_size:
                score += 2

            if word_count <= 8:
                score += 1

            if text.endswith(":"):
                score += 1

            if text.isupper():
                score += 1

            if sym_ratio < 0.05:
                score += 1

            # ---- Classification ----
            if score >= 4:
                print(RED + text + RESET)
            elif score >= 2:
                print(YELLOW + text + RESET)
            else:
                print(GREEN + text + RESET)