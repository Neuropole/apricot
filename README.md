# apricot
apricot is a self-hostable code agent , unlike tools that only look at diffs, apricot understands your entire codebase — reviews PR, write testcases
# repo structure
```
ai-code-agent/
│
├── .github/
│   └── workflows/
│       └── agent.yml              # GitHub Actions pipeline
│
├── agent/                         # Core agent logic
│   ├── __init__.py
│   ├── main.py                    # Entry point (called by CI)
│   │
│   ├── config.py                  # API keys, configs
│   │
│   ├── llm/
│   │   ├── groq_client.py         # Groq API wrapper
│   │   └── prompts.py             # All prompts (centralized 🔥)
│   │
│   ├── indexing/
│   │   ├── parser.py              # tree-sitter parsing
│   │   ├── chunker.py             # split code into chunks
│   │   ├── embedder.py            # embeddings logic
│   │   └── vector_store.py        # ChromaDB wrapper
│   │
│   ├── retrieval/
│   │   └── retriever.py           # top-k context fetch
│   │
│   ├── intent/
│   │   └── infer.py               # 🔥 intent + property inference
│   │
│   ├── testgen/
│   │   ├── generator.py           # test generation
│   │   └── style_matcher.py       # detect pytest/jest etc.
│   │
│   ├── execution/
│   │   ├── runner.py              # run tests (pytest etc.)
│   │   └── coverage.py            # coverage analysis
│   │
│   ├── feedback/
│   │   └── loop.py                # refine tests (self-improve 🔥)
│   │
│   └── github/
│       ├── commenter.py           # PR comments
│       └── committer.py           # push test files
│
├── scripts/
│   ├── setup.sh
│   └── run_local.py               # run agent locally (debugging)
│
├── .agent/                        # persistent memory (IMPORTANT)
│   ├── context.md                 # codebase summary
│   ├── embeddings/                # cached embeddings
│   └── intent_cache.json          # inferred properties
│
├── tests/                         # agent’s own tests
│
├── requirements.txt
├── README.md
└── .gitignore

```
# end to end flow
```
PR opened →
GitHub Actions triggered →
    ↓
1. Clone repo
2. Load cached embeddings (.agent/)
3. Parse changed files (diff)
4. Embed only changed/new files
5. Retrieve relevant context (RAG)
6. Infer intent + properties 🔥
7. Detect test framework
8. Generate tests
9. Run tests (pytest)
10. Collect failures + coverage
11. Feedback loop (optional refine) 🔥
12. Commit tests OR comment on PR
```