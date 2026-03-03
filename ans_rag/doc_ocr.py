from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import cv2
import numpy as np
import re

def do_ocr(path):
    IMAGE_PATH = path
    ".jpeg"
    CONF_THRESHOLD = 0.5

    doc = DocumentFile.from_images(IMAGE_PATH)
    model = ocr_predictor(pretrained=True)

    result = model(doc)

    img = cv2.imread(IMAGE_PATH)
    height, width = img.shape[:2]

    words = []

    # -------------------------
    # Extract words with confidence filtering
    # -------------------------
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    if word.confidence < CONF_THRESHOLD:
                        continue

                    text = word.value.strip()

                    if len(text) <= 1 and not text.isdigit():
                        continue

                    (x_min, y_min), (x_max, y_max) = word.geometry

                    words.append({
                        "text": text,
                        "x_min": x_min * width,
                        "x_max": x_max * width,
                        "y_center": ((y_min + y_max) / 2) * height
                    })

    # -------------------------
    # Sort by vertical center
    # -------------------------
    words = sorted(words, key=lambda w: w["y_center"])

    # -------------------------
    # Compute adaptive line gap
    # -------------------------
    y_values = [w["y_center"] for w in words]
    y_diffs = np.diff(sorted(y_values))

    if len(y_diffs) > 0:
        avg_gap = np.median(y_diffs)
    else:
        avg_gap = 10

    LINE_THRESHOLD = avg_gap * 1.5

    # -------------------------
    # Group into lines
    # -------------------------
    lines = []
    current_line = [words[0]]

    for i in range(1, len(words)):
        if abs(words[i]["y_center"] - words[i-1]["y_center"]) < LINE_THRESHOLD:
            current_line.append(words[i])
        else:
            lines.append(current_line)
            current_line = [words[i]]

    lines.append(current_line)

    # -------------------------
    # Sort each line left to right
    # -------------------------
    final_text = ""

    for line in lines:
        line = sorted(line, key=lambda w: w["x_min"])

        sentence = ""
        prev = None

        for word in line:
            if prev is None:
                sentence += word["text"]
            else:
                gap = word["x_min"] - prev["x_max"]

                if gap < width * 0.02:
                    sentence += word["text"]
                else:
                    sentence += " " + word["text"]

            prev = word

        sentence = re.sub(r"\s+", " ", sentence).strip()

        if sentence:
            final_text += sentence + "\n"

    return final_text

if __name__=='__main__':
    print(do_ocr("../samples/img6"))
