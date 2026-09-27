# Blood Work Analyzer

> A two-stage LLM application that first extracts and classifies blood-work
> values, then turns the structured results into a plain-language summary and
> practical Indian diet guidance.

The core design choice is separation of concerns. Instead of asking one model
call to parse numbers and write advice at the same time, Stage 1 creates a
structured interpretation of the report and Stage 2 operates on that cleaner
intermediate representation.

## Key features

- Editable blood-work report input
- Extraction of all reported test values
- HIGH / LOW / NORMAL classification against supplied reference ranges
- Two-stage LLM orchestration
- Separate health-summary and diet-plan outputs
- Preloaded example report for demonstration
- Error handling for malformed responses
- Testable service layer with injected model dependency

## Example workflow

```text
Blood-work report
       │
       ▼
extract values + reference ranges
       │
       ▼
HIGH / LOW / NORMAL classifications
       │
       ▼
interpret structured result
       │
       ├── health summary
       └── Indian diet guidance
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the staged pipeline, component
responsibilities, error handling, and test boundary.

## Technology stack

| Technology | Role |
| --- | --- |
| Python 3.12 | Application language |
| LangChain | Model integration |
| Gemini API | Model serving |
| Gemma | Extraction and interpretation model |
| Streamlit | Interactive UI |
| pytest | Pipeline tests |
| uv | Dependency and environment management |

## Project structure

```text
.
├── app.py
├── src/blood_work_analyzer/
│   ├── __init__.py
│   ├── prompts.py
│   └── service.py
├── tests/
│   └── test_service.py
├── sample_data/
│   └── blood_work.txt
├── notebooks/
│   └── prototype.ipynb
├── .env.example
├── ARCHITECTURE.md
├── pyproject.toml
└── requirements.txt
```

## Local setup

```bash
git clone https://github.com/chaitanya4595-afk/blood-work-analyzer.git
cd blood-work-analyzer
uv sync --extra dev
cp .env.example .env
```

Add your Google API key to `.env`, then run:

```bash
uv run streamlit run app.py
```

Run tests with:

```bash
uv run pytest
```

## Limitations

- Model-generated interpretation can be wrong.
- Report formats are not yet normalized into a typed schema.
- The application does not currently parse uploaded PDF laboratory reports.
- It does not include clinical validation or measured accuracy.
- Model latency can be noticeable on the current provider/model combination.

## Future improvements

- Add typed structured output for extracted lab values
- Add PDF upload and deterministic report parsing
- Validate units and reference ranges before interpretation
- Add an evaluation dataset for extraction accuracy
- Add latency and error telemetry
- Add a faster production model after evaluation

> This project is a technical demonstration and is not a medical diagnosis or
> substitute for professional medical advice.
