from datetime import date
from unittest.mock import patch

import pytest

from agent_tools import check_sla_status, get_complaint, find_similar_complaints

FIXED_TODAY = date(2026, 10, 16)

@pytest.fixture(autouse=True)
def freeze_date():
    with patch("agent_tools.date") as mock_date:
        mock_date.today.return_value = FIXED_TODAY
        mock_date.fromisoformat.side_effect = date.fromisoformat
        yield

def test_days_elapsed_is_correct():
      assert check_sla_status(6)["days_elapsed"] == 36

def test_ack_breached_when_past_3_days():
    assert check_sla_status(6)["ack_breached"] is True

def test_response_not_breached_at_36_days():
    assert check_sla_status(6)["response_breached"] is False

def test_response_breached_past_56_days():
    assert check_sla_status(2)["response_breached"] is True

def test_days_until_deadline_is_correct():
    assert check_sla_status(6)["days_until_response_deadline"] == 20

def test_unknown_complaint_id_returns_error():
    assert check_sla_status(999)["error"] == "unknown_complaint_id"


# --- get_complaint ---
def test_get_complaint_returns_full_record():
    result = get_complaint(1)
    assert result["id"] == 1
    assert result["product"] == "credit_card"
    assert result["customer"]["name"] == "Ada Owens"
    assert result["customer"]["vulnerability_flag"] is False

def test_get_complaint_unknown_id_returns_error():
    assert get_complaint(999)["error"] == "unknown_complaint_id"


# --- find_similar_complaints ---

def test_find_similar_by_product_returns_matches():
    result = find_similar_complaints(product="mortgage")
    assert result["count"] >= 1
    assert all(r["product"] == "mortgage" for r in result["results"])

def test_find_similar_by_theme_keyword():
    result = find_similar_complaints(theme="bereavement")
    assert result["count"] >= 1
    assert all("bereavement" in r["summary"].lower() for r in result["results"])

def test_find_similar_vulnerable_only_filter():
    result = find_similar_complaints(product="mortgage", vulnerable_only=True)
    assert all(r["vulnerable"] is True for r in result["results"])

def test_find_similar_missing_both_filters_returns_error():
    result = find_similar_complaints()
    assert result["error"] == "missing_filter"

def test_find_similar_invalid_product_returns_error():
    result = find_similar_complaints(product="spaceship")
    assert result["error"] == "unknown_product"

def test_find_similar_limit_is_respected():
    result = find_similar_complaints(product="credit_card", limit=1)
    assert len(result["results"]) <= 1

def test_find_similar_results_sorted_newest_first():
    result = find_similar_complaints(product="mortgage")
    dates = [r["opened_date"] for r in result["results"]]
    assert dates == sorted(dates, reverse=True)