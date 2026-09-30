import logging
import os
import time

from langchain_google_genai import ChatGoogleGenerativeAI

from .errors import describe_failure
from .prompts import DIET_PROMPT, EXTRACTION_PROMPT, SECTION_SEPARATOR


def build_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        timeout=20, max_retries=0, max_output_tokens=2048,
    )


def _invoke_stage(llm, prompt: str, stage: str):
    """Retry only the failed stage once for a transient server error or timeout."""
    for attempt in range(2):
        try:
            return llm.invoke(prompt)
        except Exception as exc:
            failure = describe_failure(exc)
            logging.getLogger(__name__).warning(
                "Model request failed: stage=%s attempt=%s category=%s http_status=%s error_type=%s",
                stage, attempt + 1, failure.category, failure.status_code, type(exc).__name__,
            )
            if not failure.retryable or attempt == 1:
                raise
            time.sleep(1)


def analyze_blood_work(blood_report: str, llm=None) -> tuple[str, str]:
    """Run extraction first, then interpretation, and return summary + diet."""
    if not blood_report.strip():
        raise ValueError("Blood work report cannot be empty.")

    llm = llm or build_llm()

    extracted = _invoke_stage(
        llm, EXTRACTION_PROMPT.format(blood_report=blood_report), "extraction"
    ).text

    if not extracted or not extracted.strip():
        raise ValueError("Model returned no extracted values.")

    response = _invoke_stage(
        llm, DIET_PROMPT.format(
            extracted_values=extracted,
            separator=SECTION_SEPARATOR,
        ), "interpretation"
    ).text

    summary, separator, diet = response.partition(SECTION_SEPARATOR)
    if not separator:
        raise ValueError("Model response did not contain the expected section separator.")

    return summary.strip(), diet.strip()
