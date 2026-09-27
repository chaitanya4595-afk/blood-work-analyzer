# Architecture

## Overview

Blood Work Analyzer deliberately separates factual extraction from narrative
interpretation. This avoids asking one prompt to simultaneously parse every
number, classify it, explain it, and create dietary guidance.

```text
Blood-work report
       │
       ▼
Stage 1: extraction prompt
       │
       ▼
test value + reference range + HIGH/LOW/NORMAL
       │
       ▼
Stage 2: interpretation prompt
       │
       ├────────► plain-language health summary
       │
       └────────► practical Indian diet guidance
```

## Components

### Streamlit application

`app.py` provides an editable input report and independent output panels for the
summary and diet plan. A sample report is loaded from `sample_data/`.

### Prompt layer

`src/blood_work_analyzer/prompts.py` owns the extraction and interpretation
contracts. The second stage receives the first stage's structured output rather
than the original raw report.

### Service layer

`src/blood_work_analyzer/service.py` orchestrates the two model calls. It
validates non-empty input and requires the expected separator before returning
the two user-facing outputs.

### Model provider

Gemma is accessed through the Gemini API using LangChain's Google GenAI
integration. Credentials remain outside the repository.

## Failure handling

- Blank reports are rejected before any API call.
- Missing or invalid credentials surface as application errors.
- A malformed second-stage response without the expected separator is rejected
  instead of silently rendering an incomplete result.
- The Streamlit layer catches failures and displays an error rather than losing
  the page state.

## Testing boundary

The service accepts an injected LLM. Tests use a fake model, so the pipeline
contract can be verified without external API calls or credits.

## Scope

This is a technical demonstration of staged LLM orchestration. It does not
provide medical diagnosis and should not be used for consequential medical
decisions.
