"""Safe failure summaries that never include prompts, responses, or credentials."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Failure:
    category: str
    message: str
    status_code: int | None = None
    retryable: bool = False


def describe_failure(error: Exception) -> Failure:
    """Inspect structured status codes, including errors wrapped by LangChain."""
    current = error
    seen = set()
    timed_out = False
    code = None
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        timed_out |= isinstance(current, TimeoutError) or type(current).__name__ in {
            "ReadTimeout", "ConnectTimeout", "WriteTimeout", "PoolTimeout",
        }
        for attribute in ("status_code", "code"):
            value = getattr(current, attribute, None)
            if isinstance(value, int) and 400 <= value <= 599:
                code = value
                break
        if code is not None:
            break
        current = current.__cause__ or current.__context__

    if code in {500, 502, 503, 504}:
        return Failure("provider_unavailable", "The AI service is temporarily unavailable. Please try again shortly.", code, True)
    if code == 429:
        return Failure("rate_limit", "The AI service has reached its request limit. Please wait before trying again.", code)
    if code in {401, 403}:
        return Failure("access_denied", "The AI service rejected this app's credentials or access permissions. The app owner needs to check its configuration.", code)
    if code in {400, 404}:
        return Failure("request_rejected", "The AI service rejected the request. The app owner needs to check the configured model and API settings.", code)
    if timed_out:
        return Failure("timeout", "The AI service took too long to respond. Please try again shortly.", retryable=True)
    return Failure("analysis_failed", "Check the report format or try again later.", code)
