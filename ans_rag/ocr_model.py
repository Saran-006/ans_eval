import easyocr
import numpy as np

reader = easyocr.Reader(['en'])
results = reader.readtext("../samples/img5.jpeg")

# Sort top-to-bottom first
results = sorted(results, key=lambda x: x[0][0][1])

lines = []
current_line = []
line_threshold = 15  # adjust if needed

for bbox, text, conf in results:
    y_top = bbox[0][1]

    if not current_line:
        current_line.append((bbox, text))
        current_y = y_top
    else:
        if abs(y_top - current_y) < line_threshold:
            current_line.append((bbox, text))
        else:
            # Sort line left-to-right
            current_line = sorted(current_line, key=lambda x: x[0][0][0])
            line_text = " ".join([t[1] for t in current_line])
            lines.append(line_text)

            current_line = [(bbox, text)]
            current_y = y_top

# Add last line
if current_line:
    current_line = sorted(current_line, key=lambda x: x[0][0][0])
    line_text = " ".join([t[1] for t in current_line])
    lines.append(line_text)

print("\nExtracted Text:\n")
for line in lines:
    print(line)