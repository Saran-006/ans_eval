# ── LLM ──────────────────────────────────────────────
# Get a free API key from https://openrouter.ai/keys
OPENROUTER_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-3.5-turbo"
LLM_RETRIES = 3
LLM_MAX_TOKENS_DEFAULT = 2000
LLM_MAX_TOKENS_OCR = 500       # low to save credits on OCR fixing
LLM_MAX_TOKENS_EVAL = 3000     # higher for full JSON eval response

# ── Embedding ────────────────────────────────────────
EMBEDDING_MODEL = "BAAI/bge-small-en"

# ── Chunker ──────────────────────────────────────────
CHUNK_SPLIT_THRESHOLD = 300    # chars; chunks larger than this get split

# ── Retrieval ────────────────────────────────────────
RETRIEVAL_TOP_K = 3

# ── Server ───────────────────────────────────────────
EVAL_SUBPROCESS_TIMEOUT = 300  # seconds
OUTPUT_DELIMITER = "||||||||||"
