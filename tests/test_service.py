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
