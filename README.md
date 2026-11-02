# AI Learning Workspace

Yeh workspace AI aur agent concepts ko examples ke zariye seekhne aur revise karne ke liye hai. Topic ka README kholo, example dekho, phir apne alfaaz mein concept samjha kar chhoti variation try karo.

## Learning path

### 1. LLM basics

- [Chat and messages](learning/01-llm-basics/README.md)

### 2. Tool calling

- [First tool](learning/02-tool-calling/01-first-tool/README.md)
- [Tool arguments](learning/02-tool-calling/02-tool-arguments/README.md)
- [Multiple tools](learning/02-tool-calling/03-multiple-tools/README.md)
- [Tool loop](learning/02-tool-calling/04-tool-loop/README.md)
- [Safe tool execution](learning/02-tool-calling/05-safe-tool-execution/README.md)

### 3. APIs and data

- [Weather API](learning/03-api-and-data/01-weather-api/README.md)
- [Retry and backoff](learning/03-api-and-data/02-retry-and-backoff/README.md)
- [Pydantic validation](learning/03-api-and-data/03-pydantic-validation/README.md)
- [Community search](learning/03-api-and-data/04-community-search/README.md)

### 4. Digital twin

- [Digital twin example](learning/04-digital-twin/README.md)

### 5. OpenAI Agents SDK

- [Agent execution and tools](learning/05-openai/01-agent-execution-and-tools/README.md)
- [Email and notifications](learning/05-openai/02-email-and-notifications/README.md)
- [LLM orchestration](learning/05-openai/orchestration-with-llm/Readme.md)

## Projects

- [Checklist agent](projects/checklist-agent/README.md)
- [Digital twin app](projects/digital-twin/README.md)

## Workspace folders

- `learning/` — chhote topic-wise lessons aur examples.
- `projects/` — mukammal practice applications.
- `resources/` — shared reference documents, jaise digital twin ka profile.

## Revision routine

1. Lesson README se concept ka overview lo.
2. `example.py` parho aur samjho ke har step kya karta hai.
3. Apne alfaaz mein short notes likho.
4. Code mein chhoti tabdeeli karke dekho ke behavior kaise badalta hai.

## Run examples

Commands workspace root se chalao, misaal ke taur par:

```bash
.venv/bin/python learning/02-tool-calling/01-first-tool/example.py
```

Kuch examples ko root `.env` mein API credentials chahiye. Digital twin ke shared files `resources/` mein hain.
