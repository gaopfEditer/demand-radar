from pipeline.deduplicate import deduplicate_keywords


def test_deduplicate_merges_sources():
    records = [
        {"keyword": "JSON Formatter", "normalized": "json formatter", "source": "seed"},
        {"keyword": "json formatter", "normalized": "json formatter", "source": "autocomplete"},
        {"keyword": "Webhook Tester", "normalized": "webhook tester", "source": "seed"},
    ]
    out = deduplicate_keywords(records)
    assert len(out) == 2
    jf = next(r for r in out if r["normalized"] == "json formatter")
    assert "seed" in jf["source"]
    assert "autocomplete" in jf["source"]


def test_deduplicate_skips_empty():
    assert deduplicate_keywords([{"keyword": "", "normalized": ""}]) == []
