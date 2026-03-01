import notes_rag.pdf2txt as pdf

def chunk_document(formatted_text):
    chunks = []
    current_chunk = None

    lines = formatted_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # New Heading
        if line.startswith("[head]"):
            heading_text = line.replace("[head]", "").strip()

            # Save previous chunk
            if current_chunk:
                chunks.append(current_chunk)

            # Start new chunk
            current_chunk = {
                "heading": heading_text,
                "content": ""
            }

        # Body Line
        elif line.startswith("[body]"):
            body_text = line.replace("[body]", "").strip()

            if current_chunk:
                current_chunk["content"] += body_text + " "
            else:
                # Edge case: body without heading
                current_chunk = {
                    "heading": "UNDEFINED",
                    "content": body_text + " "
                }

    # Append last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

