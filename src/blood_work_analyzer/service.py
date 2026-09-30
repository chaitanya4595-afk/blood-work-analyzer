import os

from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts import DIET_PROMPT, EXTRACTION_PROMPT, SECTION_SEPARATOR


def build_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        timeout=30, max_retries=0, max_output_tokens=2048,
    )


def analyze_blood_work(blood_report: str, llm=None) -> tuple[str, str]:
    """Run extraction first, then interpretation, and return summary + diet."""
    if not blood_report.strip():
        raise ValueError("Blood work report cannot be empty.")

    llm = llm or build_llm()

    extracted = llm.invoke(
        EXTRACTION_PROMPT.format(blood_report=blood_report)
    ).text

    if not extracted or not extracted.strip():
        raise ValueError("Model returned no extracted values.")

    response = llm.invoke(
        DIET_PROMPT.format(
            extracted_values=extracted,
            separator=SECTION_SEPARATOR,
        )
    ).text

    summary, separator, diet = response.partition(SECTION_SEPARATOR)
    if not separator:
        raise ValueError("Model response did not contain the expected section separator.")

    return summary.strip(), diet.strip()
