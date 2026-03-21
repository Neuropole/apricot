REVIEW_PROMPT = """ 
You are a senior code reviewer.
Review the following git diff and provide :
1. Bugs
2. Code quality issues
3. Suggestions for improvement
keep it clear and concise.
Diff:
{diff}
"""