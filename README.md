# GradeRAG

Built this to fix how RAG systems fetch context — instead of grabbing random chunks, this one reads the document structure first (headings → sections → content) and builds a hierarchy before retrieval. The LLM gets short, relevant, structured context instead of a blob of random text.

Learned what RAG was on day 1. Had a working system by day 3. UI on day 4 (Copilot handled that part, not going to lie).

---

## Why It Exists

Most RAG implementations chunk by token count. That breaks document structure — a heading ends up separated from its content, a definition gets split mid-sentence. This system reads heading hierarchy first, then chunks within that structure. The LLM gets cleaner input, the answers are more accurate.

---

## What It Does

Upload a question paper, reference notes, and a student answer sheet. It reads the answer, retrieves the relevant parts of the notes, and returns marks with feedback. No manual checking.

```
Question Paper + Notes + Answer Sheet
              ↓
       RAG Pipeline
              ↓
      Marks + Feedback
```

---

## The Hard Part

Reusing the vector DB when the same subject comes up again without rebuilding it from scratch. Sounds simple. Took a full day of head-crumbling to get right — and no AI was used for that part.

---

## Structure

```
src/
├── qp_rag/          question paper parsing
├── ans_rag/         OCR + answer extraction  
├── notes_rag/       chunker.py — the core of this project
├── eval_mark/       LLM prompt + marks parser
└── utils/           Pipeline helper

app.py               background eval worker
config.py            all tunables (API key, model, thresholds)
server.py            Flask server
data.db              SQLite results
vector_db/           per-subject embeddings (pickle)
uploads/             all files uploaded (questions, notes, answers)
```

All tunables (API key, model name, chunk size, retrieval top-k, token limits) live in `config.py` — change anything there without touching the pipeline code.

---

## Internals

### PDF → Structured Text (`notes_rag/pdf2txt.py`)

Uses `pdfplumber` to extract every word along with its font metadata — fontname, size, and `(x0, top)` position. Headers/footers are stripped using a 2%/98% page-height threshold.

For each page, it builds a font-size frequency histogram. The most common size = body text. The largest size = heading. Then it classifies each line:

```
Bold font?           → [head]
Matches "word: " pattern? → [head]
Font size ≈ body?    → [body]
Font size ≈ heading? → [head]
Else                 → [body]
```

As a second pass, any `[body]` line containing `:` gets promoted to `[head]`. Output is a tagged document like:

```
[Page]
[head]1. PRIMARY SECTION :
[head]1.1 Subsection :
[body]This paragraph contains the actual content...
```

### Heading-Aware Chunker (`notes_rag/chunker.py`)

This is the core of the project. Instead of splitting by token count, it reads the heading structure first.

**Step 1 — Find heading clusters.** Consecutive `[head]` lines form a cluster. Example: `[head]Chapter 1` followed by `[head]Section 1.1` followed by `[head]Definition` = one cluster of 3 headings.

**Step 2 — Build heading maps.** For each chunk, it stores the full heading breadcrumb. If content sits under `Chapter 1 > Section 1.1 > Definition`, the chunk title becomes `Chapter 1 | Section 1.1 | Definition`.

**Step 3 — Extract body.** All `[body]` lines between two heading clusters form one chunk's content.

**Step 4 — Split large chunks.** If content exceeds 300 characters, it's split into sub-chunks (each inheriting the same heading trail).

**Step 5 — Token counting.** Each chunk gets a token count via the `BAAI/bge-small-en` tokenizer for downstream awareness.

Output is a list of dicts:
```python
{ "id": 0, "title": "Chapter 1 | Section 1.1", "content": "...", "token": 87 }
```

### Vector DB Build & Reuse (`notes_rag/vectorDB_builder.py`, `vectorDB_loader.py`)

**Build:** Takes the chunks from the chunker, prepends `"Represent this sentence for retrieval: "` (BGE's required query prefix), encodes with `BAAI/bge-small-en` (384-dim, normalized), and pickles the chunks + embeddings to a `.pkl` file.

**Load:** Deserializes the pickle and wraps it in a `db_container` object (chunks, embeddings, model reference).

**Reuse logic:** The server checks if the `.pkl` file already exists before calling `app.py`. If it exists → flag `0` (skip build). If not → flag `1` (build from notes). This means the expensive embedding step only happens once per subject, no matter how many students are evaluated.

**Retrieval:** `query_vector_db()` encodes the query with the same BGE model, computes cosine similarity via `np.dot` (embeddings are already L2-normalized), takes the top-k results.

### Question Paper Parser (`qp_rag/qp2txt.py`, `qpBuilder.py`)

**`qp2txt.py`** — Same font-analysis approach as the notes parser, but simpler. Extracts raw text line-by-line since question papers don't need heading hierarchy.

**`qpBuilder.py`** — Regex-based structural parser. Detects:
- Section boundaries (`PART A`, `SECTION B`, `UNIT 1`, etc.)
- Question numbers (`1.`, `2)`, `[3]`, etc.)
- End-of-paper markers (`END OF QUESTION PAPER`, `ALL THE BEST`, etc.)

Groups questions under their sections and returns a dict: `{ "PART A": ["1. What is...", "2. Define..."], "PART B": [...] }`

### OCR Pipeline for Answer Sheets (`ans_rag/`)

Answer sheets are handwritten PDFs — can't use pdfplumber. Multi-stage pipeline:

**1. Image Extraction (`imgExtractor.py`)** — Uses PyMuPDF (`fitz`) to extract embedded images from each PDF page. Saves them to `static_img/`.

**2. OCR (`ocrModel.py`)** — Uses `doctr` (not Tesseract) for handwriting recognition:
   - Adds 80px white padding to each image (prevents edge-clipping)
   - Runs `ocr_predictor` with lowered detection threshold (0.1)
   - Filters words below 0.25 confidence
   - Reconstructs lines from word bounding boxes using vertical overlap (>40% overlap = same line)
   - Handles a common OCR artifact: standalone number tokens get merged with the next line (e.g., `"5"` on its own line + `"Tytsyk"` → `"5) Tytsyk"`)

**3. LLM Post-Correction (`llm.py`)** — Sends raw OCR text to GPT-3.5 (via OpenRouter) with a carefully scoped prompt:
   - Fix character-level mistakes only (`Wwho → Who`, `o(n → on`)
   - Don't rewrite sentences or add words
   - Detect malformed question numbers at line starts (`STytsyk → 5) Tytsyk`, `!Hello → 1) Hello`)
   - Preserve `[page]` markers
   - Strip garbage-only lines
   - Uses only 500 max_tokens to save API costs

### Evaluation & Marking (`eval_mark/`)

**Answer Parser (`marker.py`)** — Splits the corrected OCR text by question-number patterns (`1)`, `2.`, `3-`, etc.) into a dict: `{ "1)": "answer text...", "2)": "..." }`.

**Prompt Builder (`eval_prompt.py`)** — For each question:
1. Normalizes answer keys (handles OCR duplicate keys like `3)` and `3 `)
2. Cleans OCR garbage (page tags, stray numbers, common substitutions like `6o → to`)
3. Retrieves top-3 chunks from the vector DB as reference material
4. Builds a per-question evaluation block with marks-aware rubric:
   - 1 mark → check key concept only, partial = 0.5
   - 2 marks → expect 1–2 points, partial = 0.5 or 1
   - 5 marks → proportional marking (2.5, 3.5, etc.)
5. Instructs the LLM to return a JSON array of `{ question_number, max_marks, awarded_marks, feedback }`

**Score Parser** — Extracts `awarded_marks` and `max_marks` from the JSON response, sums them, returns `"X/Y"` format. Only counts `max_marks` for questions where the student actually wrote an answer (skips "No answer provided").

### Server Orchestration (`server.py`)

Flask app with SQLite (via Flask-SQLAlchemy). Two models: `Subject` and `Evaluation`.

**Subject creation:** Upload notes PDF + question paper PDF, name a vector DB file. Server stores file paths, creates DB record.

**Evaluation flow:**
1. Upload answer sheet PDF → creates `Evaluation` record with `score=None`
2. Server calls `app.py` as a subprocess: `python app.py [build_flag] [notes] [db] [answer] [qp]`
3. `app.py` runs the full pipeline: build/load vector DB → parse questions → OCR answers → retrieve context → build eval prompt → call LLM → parse score
4. Output is parsed from stdout using `||||||||||` delimiters: `answer_parsing || markings || score`
5. Score, answer parsing, and detailed markings are stored in the DB

**Re-evaluation:** Same answer sheet can be re-evaluated (e.g., after updating notes/question paper). Each attempt is stored in `eval_history` as JSON. Display shows the highest score.

**Auto-migration:** Server handles schema changes at startup — adds new columns (`question_path`, `eval_history`, `answer_parsing`, `markings`) and migrates `score` column type from INTEGER to TEXT.

---

## Stack

Flask · SQLite · Custom heading-aware chunker · Pickle vector store · OCR pipeline (doctr + LLM correction) · BGE-small-en embeddings · OpenRouter API (GPT-3.5)

---

## Results

Tested on biology answer sheets. Worked better than expected for a 3-day build. Not perfect — retrieval quality depends on how well the notes are structured — but accurate enough to be useful.

---

## Known Gaps

- No reranking, pure cosine similarity
- Chunk quality drops with poorly formatted notes
- Vector store is file-based, not production-scale

---

[github.com/Saran-006](https://github.com/Saran-006)
