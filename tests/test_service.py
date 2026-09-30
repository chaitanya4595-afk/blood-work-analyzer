from dataclasses import dataclass

import pytest

from blood_work_analyzer.service import analyze_blood_work


@dataclass
class FakeResponse:
    text: str


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def invoke(self, _prompt):
        self.calls += 1
        if self.calls == 1:
            return FakeResponse(
                "- LDL: 162 mg/dL | Status: HIGH | Reference: <100"
            )
        return FakeResponse(
            "LDL is above the supplied reference range.\n"
            "===DIET PLAN===\n"
            "**Foods to avoid**\n- Fried foods\n\n"
            "**Foods to eat more of**\n- Oats"
        )


class MalformedSecondStageLLM:
    def __init__(self):
        self.calls = 0

    def invoke(self, _prompt):
        self.calls += 1
        if self.calls == 1:
            return FakeResponse(
                "- LDL: 162 mg/dL | Status: HIGH | Reference: <100"
            )
        return FakeResponse("Summary returned without the required separator")


def test_two_stage_pipeline_splits_summary_and_diet():
    llm = FakeLLM()
    summary, diet = analyze_blood_work("LDL: 162", llm=llm)

    assert llm.calls == 2
    assert "LDL" in summary
    assert "Foods to avoid" in diet


def test_empty_report_is_rejected_before_model_call():
    llm = FakeLLM()

    with pytest.raises(ValueError):
        analyze_blood_work("   ", llm=llm)

    assert llm.calls == 0


def test_malformed_second_stage_output_is_rejected():
    with pytest.raises(ValueError, match="expected section separator"):
        analyze_blood_work("LDL: 162", llm=MalformedSecondStageLLM())


def test_empty_extraction_does_not_start_interpretation():
    class EmptyLLM(FakeLLM):
        def invoke(self, _prompt):
            self.calls += 1
            return FakeResponse("")
    llm = EmptyLLM()
    with pytest.raises(ValueError, match="no extracted values"):
        analyze_blood_work("Synthetic test values", llm=llm)
    assert llm.calls == 1


def test_server_failure_retries_only_interpretation(monkeypatch, caplog):
    from unittest.mock import Mock
    from langchain_google_genai.chat_models import GoogleAPIError
    from blood_work_analyzer import service

    failure = GoogleAPIError(503, {"error": {"message": "PRIVATE_REPORT SECRET_KEY", "status": "UNAVAILABLE"}})
    llm = Mock()
    llm.invoke.side_effect = [FakeResponse("Extracted synthetic values"), failure, FakeResponse("Summary===DIET PLAN===Diet")]
    sleep = Mock()
    monkeypatch.setattr(service.time, "sleep", sleep)
    assert analyze_blood_work("Synthetic input", llm=llm) == ("Summary", "Diet")
    assert llm.invoke.call_count == 3
    assert llm.invoke.call_args_list[1] == llm.invoke.call_args_list[2]
    sleep.assert_called_once_with(1)
    assert "http_status=503" in caplog.text
    assert "PRIVATE_REPORT" not in caplog.text
    assert "SECRET_KEY" not in caplog.text


@pytest.mark.parametrize("code", [400, 401, 403, 404, 429])
def test_client_failure_is_not_retried(code, monkeypatch):
    from unittest.mock import Mock
    from google.genai.errors import ClientError
    from blood_work_analyzer import service

    failure = RuntimeError("Wrapped client error")
    failure.__cause__ = ClientError(code, {"error": {"message": "private details"}})
    llm = Mock()
    llm.invoke.side_effect = failure
    sleep = Mock()
    monkeypatch.setattr(service.time, "sleep", sleep)
    with pytest.raises(RuntimeError):
        analyze_blood_work("Synthetic input", llm=llm)
    assert llm.invoke.call_count == 1
    sleep.assert_not_called()


def test_timeout_retry_is_bounded(monkeypatch):
    from unittest.mock import Mock
    import httpx
    from blood_work_analyzer import service

    llm = Mock()
    llm.invoke.side_effect = httpx.ReadTimeout("private request contents")
    sleep = Mock()
    monkeypatch.setattr(service.time, "sleep", sleep)
    with pytest.raises(httpx.ReadTimeout):
        analyze_blood_work("Synthetic input", llm=llm)
    assert llm.invoke.call_count == 2
    sleep.assert_called_once_with(1)
