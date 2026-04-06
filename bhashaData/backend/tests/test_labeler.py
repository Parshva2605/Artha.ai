try:
    from backend.config.languages import get_config_by_code
    from backend.pipeline.labeler import (
        LabelResult,
        build_prompt,
        label_text,
        parse_llm_response,
        run_labeling_pipeline,
    )
except ModuleNotFoundError:
    from config.languages import get_config_by_code
    from pipeline.labeler import (
        LabelResult,
        build_prompt,
        label_text,
        parse_llm_response,
        run_labeling_pipeline,
    )


LABELER_MODULE = label_text.__module__


def test_build_prompt_fills_text_and_language_name() -> None:
    prompt = build_prompt("sentiment", "test text", "Hindi")
    assert "test text" in prompt
    assert "Hindi" in prompt
    assert "positive" in prompt


def test_build_prompt_raises_value_error_for_unknown_type() -> None:
    try:
        build_prompt("unknown_type", "text", "Hindi")
        assert False, "Should have raised"
    except ValueError:
        pass


def test_parse_llm_response_parses_valid_sentiment_json() -> None:
    response = '{"label": "positive", "confidence": 0.92, "reason": "Positive tone"}'
    result = parse_llm_response(response, "sentiment")
    assert result is not None
    assert result.label == "positive"
    assert result.confidence == 0.92


def test_parse_llm_response_returns_none_for_invalid_label() -> None:
    response = '{"label": "happy", "confidence": 0.92, "reason": "test"}'
    result = parse_llm_response(response, "sentiment")
    assert result is None


def test_parse_llm_response_returns_none_for_missing_field() -> None:
    response = '{"label": "positive"}'
    result = parse_llm_response(response, "sentiment")
    assert result is None


def test_parse_llm_response_strips_markdown_fences() -> None:
    response = '```json\n{"label": "negative", "confidence": 0.88, "reason": "test"}\n```'
    result = parse_llm_response(response, "sentiment")
    assert result is not None
    assert result.label == "negative"


def test_label_text_always_returns_label_result_never_none(monkeypatch) -> None:
    def fail_claude(_text: str, _label_type: str, _language_name: str):
        raise RuntimeError("Claude down")

    def fail_openai(_text: str, _label_type: str, _language_name: str):
        raise RuntimeError("OpenAI down")

    monkeypatch.setattr(f"{LABELER_MODULE}.label_with_claude", fail_claude)
    monkeypatch.setattr(f"{LABELER_MODULE}.label_with_openai", fail_openai)

    result = label_text("some text", "sentiment", "Hindi")
    assert result is not None
    assert result.needs_review is True
    assert result.llm_used == "needs_review"


def test_labeling_result_totals_are_consistent(monkeypatch) -> None:
    config = get_config_by_code("hi")
    rows = [
        {
            "text_original": "यह एक परीक्षण पंक्ति है",
            "text_clean": "यह एक परीक्षण पंक्ति है",
            "source": "reddit",
            "source_url": None,
            "source_subreddit": "hindi",
            "language_code": "hi",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
        {
            "text_original": "यह दूसरी परीक्षण पंक्ति है",
            "text_clean": "यह दूसरी परीक्षण पंक्ति है",
            "source": "reddit",
            "source_url": None,
            "source_subreddit": "hindi",
            "language_code": "hi",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
        {
            "text_original": "यह तीसरी परीक्षण पंक्ति है",
            "text_clean": "यह तीसरी परीक्षण पंक्ति है",
            "source": "reddit",
            "source_url": None,
            "source_subreddit": "hindi",
            "language_code": "hi",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
    ]

    call_state = {"count": 0}

    def fake_label_text(_text: str, _label_type: str, _language_name: str) -> LabelResult:
        call_state["count"] += 1
        if call_state["count"] == 1:
            return LabelResult(
                label="positive",
                confidence=0.92,
                reason="good",
                llm_used="claude",
                needs_review=False,
                label_type="sentiment",
                raw_response='{"label":"positive"}',
            )
        if call_state["count"] == 2:
            return LabelResult(
                label="neutral",
                confidence=0.78,
                reason="low confidence",
                llm_used="openai",
                needs_review=False,
                label_type="sentiment",
                raw_response='{"label":"neutral"}',
            )
        return LabelResult(
            label="unknown",
            confidence=0.0,
            reason="Both LLMs failed or returned low confidence",
            llm_used="needs_review",
            needs_review=True,
            label_type="sentiment",
            raw_response="",
        )

    monkeypatch.setattr(f"{LABELER_MODULE}.label_text", fake_label_text)

    result = run_labeling_pipeline(rows=rows, label_type="sentiment", language_config=config)

    assert (
        result.total_output + result.rejected_low_confidence + result.needs_review_count
        == result.total_input
    )
