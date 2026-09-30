from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest
import blood_work_analyzer.service as service


def test_new_failed_request_clears_previous_results(monkeypatch):
    analyze = Mock(return_value=("Synthetic summary", "Synthetic diet"))
    monkeypatch.setattr(service, "analyze_blood_work", analyze)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.text_area[0].set_value("Invented software test data")
    next(button for button in app.button if button.label == "Analyze report").click().run()
    assert app.session_state["summary"] == "Synthetic summary"
    analyze.side_effect = TimeoutError("Simulated provider timeout")
    next(button for button in app.button if button.label == "Analyze report").click().run()
    assert not app.exception
    assert app.error
    assert "summary" not in app.session_state
    assert "diet_plan" not in app.session_state
