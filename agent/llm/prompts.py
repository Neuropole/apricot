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