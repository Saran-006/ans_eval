# import re
# import numpy as np
# from doctr.io import DocumentFile
# from doctr.models import ocr_predictor

# CONF_THRESHOLD = 0.5


# def do_ocr(path):

#     doc = DocumentFile.from_images(path)
#     model = ocr_predictor(pretrained=True)
#     result = model(doc)

#     words = []

#     # -------------------------
#     # Extract words
#     # -------------------------
#     for page in result.pages:
#         height, width = page.dimensions

#         for block in page.blocks:
#             for line in block.lines:
#                 for word in line.words:

#                     if word.confidence < CONF_THRESHOLD:
#                         continue

#                     text = word.value.strip()
#                     if not text:
#                         continue

#                     (x_min, y_min), (x_max, y_max) = word.geometry

#                     words.append({
#                         "text": text,
#                         "x_min": x_min * width,
#                         "x_max": x_max * width,
#                         "y_center": ((y_min + y_max) / 2) * height,
#                         "height": (y_max - y_min) * height
#                     })

#     if not words:
#         return ""

#     # -------------------------
#     # Sort by vertical center
#     # -------------------------
#     words = sorted(words, key=lambda w: w["y_center"])

#     # -------------------------
#     # Adaptive line threshold
#     # -------------------------
#     heights = [w["height"] for w in words]
#     avg_height = np.median(heights)

#     LINE_THRESHOLD = avg_height * 0.8   # tighter vertical clustering

#     # -------------------------
#     # Group words into lines
#     # -------------------------
#     lines = []
#     current_line = [words[0]]

#     for i in range(1, len(words)):
#         prev = words[i - 1]
#         curr = words[i]

#         if abs(curr["y_center"] - prev["y_center"]) <= LINE_THRESHOLD:
#             current_line.append(curr)
#         else:
#             lines.append(current_line)
#             current_line = [curr]

#     lines.append(current_line)

#     # -------------------------
#     # Merge left margin numbers
#     # -------------------------
#     merged_lines = []

#     for line in lines:
#         line = sorted(line, key=lambda w: w["x_min"])

#         # Detect if line is just a number like "1" or "1)"
#         if len(line) == 1 and re.match(r"^\d+\)?$", line[0]["text"]):
#             # attach to next line if exists
#             if merged_lines:
#                 merged_lines[-1].insert(0, line[0])
#             else:
#                 merged_lines.append(line)
#         else:
#             merged_lines.append(line)

#     # -------------------------
#     # Reconstruct clean text
#     # -------------------------
#     final_text = ""

#     for line in merged_lines:
#         line = sorted(line, key=lambda w: w["x_min"])

#         sentence = ""
#         prev = None

#         for word in line:
#             if prev is None:
#                 sentence += word["text"]
#             else:
#                 gap = word["x_min"] - prev["x_max"]

#                 # Adaptive spacing
#                 if gap < avg_height * 0.3:
#                     sentence += word["text"]
#                 else:
#                     sentence += " " + word["text"]

#             prev = word

#         sentence = re.sub(r"\s+", " ", sentence).strip()

#         if sentence:
#             final_text += sentence + "\n"

#     return final_text.strip()


# if __name__ == "__main__":
#     print(do_ocr("../samples/img6.jpeg"))











#working version..||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# import re
# import numpy as np
# from doctr.io import DocumentFile
# from doctr.models import ocr_predictor

# CONF_THRESHOLD = 0.3  # lowered to avoid missing words


# def vertical_overlap(w1, w2):
#     top1 = w1["y_min"]
#     bottom1 = w1["y_max"]
#     top2 = w2["y_min"]
#     bottom2 = w2["y_max"]

#     overlap = max(0, min(bottom1, bottom2) - max(top1, top2))
#     height = min(bottom1 - top1, bottom2 - top2)

#     if height == 0:
#         return 0

#     return overlap / height


# def do_ocr(path):

#     doc = DocumentFile.from_images(path)
#     model = ocr_predictor(pretrained=True)
#     result = model(doc)

#     words = []

#     for page in result.pages:
#         height, width = page.dimensions

#         for block in page.blocks:
#             for line in block.lines:
#                 for word in line.words:

#                     if word.confidence < CONF_THRESHOLD:
#                         continue

#                     text = word.value.strip()
#                     if not text:
#                         continue

#                     (x_min, y_min), (x_max, y_max) = word.geometry

#                     words.append({
#                         "text": text,
#                         "x_min": x_min * width,
#                         "x_max": x_max * width,
#                         "y_min": y_min * height,
#                         "y_max": y_max * height,
#                     })

#     if not words:
#         return ""

#     # Sort by top position
#     words = sorted(words, key=lambda w: w["y_min"])

#     # -------------------------
#     # Group by vertical overlap (better than center threshold)
#     # -------------------------
#     lines = []
#     current_line = [words[0]]

#     for i in range(1, len(words)):
#         prev = words[i - 1]
#         curr = words[i]

#         if vertical_overlap(prev, curr) > 0.4:
#             current_line.append(curr)
#         else:
#             lines.append(current_line)
#             current_line = [curr]

#     lines.append(current_line)

#     # -------------------------
#     # Sort words left-to-right inside each line
#     # -------------------------
#     final_text = ""

#     for line in lines:
#         line = sorted(line, key=lambda w: w["x_min"])

#         sentence = ""
#         prev = None

#         for word in line:
#             if prev is None:
#                 sentence += word["text"]
#             else:
#                 gap = word["x_min"] - prev["x_max"]

#                 # adaptive gap rule
#                 if gap < 5:
#                     sentence += word["text"]
#                 else:
#                     sentence += " " + word["text"]

#             prev = word

#         sentence = re.sub(r"\s+", " ", sentence).strip()

#         if sentence:
#             final_text += sentence + "\n"

#     return final_text.strip()


# if __name__ == "__main__":
#     print(do_ocr("../samples/img6.jpeg"))








