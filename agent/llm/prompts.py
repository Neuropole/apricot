REVIEW_PROMPT = """
Analyze the code changes using the provided DIFF and CONTEXT.

Return output STRICTLY in this format:

### Bugs
- List any bugs (or write "None")

### Improvements
- Code quality improvements

### Suggestions
- Best practices or optimizations

Rules:
- Be concise
- Do NOT repeat the diff
- Use context if helpful
- If everything looks good, say: "Code looks good ✅"
"""
INTENT_PROMPT = """
Your are a senior software engineer.

Analyze the given code diff and extract:

1. Purpose of the code
2. Key properties (invariants)
3. Edge cases

STRICT RULES:
- Output only in JSON
- No explanations text
- Keep it concise

FORMAT:
{"purpose": "...",
  "properties": ["...", "..."],
  "edge_cases": ["...", "..."]
}

---DIFF---
{diff}
"""