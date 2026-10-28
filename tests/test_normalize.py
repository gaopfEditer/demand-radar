from pipeline.normalize import detect_intent, normalize_keyword, normalize_record


def test_normalize_keyword_basic():
    assert normalize_keyword("  JSON Formatter  ") == "json formatter"
    assert normalize_keyword("API!!!") == "api"


def test_detect_intent_commercial():
    assert detect_intent("best webhook tester alternative") == "commercial_investigation"


def test_detect_intent_transactional():
    assert detect_intent("free pdf compressor online") == "transactional"


def test_normalize_record():
    rec = normalize_record("AI Coding Agent", category="ai_development", source="seed")
    assert rec["normalized"] == "ai coding agent"
    assert rec["category"] == "ai_development"
    assert rec["source"] == "seed"
    assert "intent" in rec
