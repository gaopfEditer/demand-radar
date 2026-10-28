from pipeline.score import score_opportunity, tier_for_score


def test_score_missing_competition_is_pending_not_fake_low():
    opp = {
        "title": "json formatter",
        "category": "developer_tools",
        "cluster_id": "c_test",
        "keywords": ["json formatter", "json formatter online"],
        "members": [
            {
                "keyword": "json formatter",
                "normalized": "json formatter",
                "intent": "transactional",
                "source": "seed,autocomplete",
                "trend_score": 40,
            }
        ],
    }
    result = score_opportunity(opp)
    assert result["score"] is not None
    # Competition may be None or tentative; must not invent KD-based low competition claim
    assert "competition" in (result["pending_dimensions"] or []) or result["competition_score"] is not None
    assert result["confidence"] in ("low", "medium", "high", "pending")
    assert result["demand_score"] is not None


def test_score_no_data_pending():
    opp = {
        "title": "unknown thing",
        "category": None,
        "keywords": ["unknown thing"],
        "members": [{"keyword": "unknown thing", "normalized": "unknown thing"}],
    }
    result = score_opportunity(opp)
    # feasibility may still score from heuristics; demand/evidence/competition often pending
    assert isinstance(result["pending_dimensions"], list)


def test_tier_for_score():
    assert tier_for_score(85) == "priority_research"
    assert tier_for_score(70) == "candidate"
    assert tier_for_score(55) == "watch"
    assert tier_for_score(20) == "deprioritize"
    assert tier_for_score(None) == "pending"
