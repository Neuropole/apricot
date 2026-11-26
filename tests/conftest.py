import os

# The Groq client is created at import time; tests never call the real API.
os.environ.setdefault("GROQ_API_KEY", "test-key")
