import easyocr
import numpy as np

def do_ocr(path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(path)

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
    final_text=""
    for line in lines:
        final_text+=line+"\n"
    
    return final_text

if __name__=="__main__":
    print(do_ocr("../samples/img4.jpeg"))
