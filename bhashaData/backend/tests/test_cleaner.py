try:
    from backend.config.languages import get_config_by_code
    from backend.pipeline.cleaner import Deduplicator, clean_text, run_cleaning_pipeline
except ModuleNotFoundError:
    from config.languages import get_config_by_code
    from pipeline.cleaner import Deduplicator, clean_text, run_cleaning_pipeline


def test_clean_text_removes_urls() -> None:
    input_text = "Check this https://example.com great site"
    result = clean_text(input_text)
    assert result is not None
    assert "http" not in result


def test_clean_text_removes_mentions() -> None:
    input_text = "Hello @username how are you doing today"
    result = clean_text(input_text)
    assert result is not None
    assert "@username" not in result


def test_clean_text_returns_none_for_too_short_text() -> None:
    input_text = "hi ok"
    result = clean_text(input_text, min_word_count=4)
    assert result is None


def test_clean_text_returns_none_for_emoji_heavy_text() -> None:
    input_text = "👍👍👍👍👍👍👍👍👍👍"
    result = clean_text(input_text)
    assert result is None


def test_deduplicator_catches_duplicates() -> None:
    deduplicator = Deduplicator()
    assert deduplicator.is_duplicate("hello world this is text") is False
    assert deduplicator.is_duplicate("hello world this is text") is True


def test_deduplicator_is_case_insensitive() -> None:
    deduplicator = Deduplicator()
    assert deduplicator.is_duplicate("Hello World Test Text") is False
    assert deduplicator.is_duplicate("hello world test text") is True


def test_run_cleaning_pipeline_rejects_wrong_language() -> None:
    rows = [
        {
            "text_original": "This is an English social media sample with enough words for filtering",
            "source": "reddit",
            "source_url": "https://reddit.com/sample/1",
            "source_subreddit": "india",
            "language_code": "gu",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
        {
            "text_original": "Another English sample row that should be rejected by Gujarati language detection",
            "source": "reddit",
            "source_url": "https://reddit.com/sample/2",
            "source_subreddit": "india",
            "language_code": "gu",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
        {
            "text_original": "આ ગુજરાતી વાક્ય પરીક્ષણ માટે પૂરતા શબ્દો સાથે લખાયેલું છે",
            "source": "reddit",
            "source_url": "https://reddit.com/sample/3",
            "source_subreddit": "gujarat",
            "language_code": "gu",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
    ]
    config = get_config_by_code("gu")
    deduplicator = Deduplicator()

    result = run_cleaning_pipeline(rows=rows, language_config=config, deduplicator=deduplicator)
    assert result.rejected_language >= 1


def test_run_cleaning_pipeline_preserves_text_original() -> None:
    input_text = "यह फिल्म बहुत अच्छी थी देखें https://example.com और इसे जरूर देखना चाहिए आज"
    row = {
        "text_original": input_text,
        "source": "reddit",
        "source_url": "https://reddit.com/sample/4",
        "source_subreddit": "hindi",
        "language_code": "hi",
        "domain": "social_media",
        "scraped_at": "2026-04-06T00:00:00+00:00",
    }

    cleaned_text = clean_text(input_text, min_word_count=5)
    assert cleaned_text is not None
    assert "https" not in cleaned_text
    assert "https://example.com" in row["text_original"]

    config = get_config_by_code("hi")
    deduplicator = Deduplicator()

    result = run_cleaning_pipeline(rows=[row], language_config=config, deduplicator=deduplicator)
    assert result.total_output > 0
    cleaned_row = result.clean_rows[0]
    assert "https://example.com" in cleaned_row["text_original"]
    assert "https://example.com" not in cleaned_row["text_clean"]


def test_cleaning_result_totals_add_up() -> None:
    rows = [
        {
            "text_original": "This is an English row that will not match Hindi language detection",
            "source": "reddit",
            "source_url": "https://reddit.com/sample/5",
            "source_subreddit": "india",
            "language_code": "hi",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
        {
            "text_original": "यह एक सही हिंदी पाठ पंक्ति है जो परीक्षण के लिए उपयोग की गई है",
            "source": "reddit",
            "source_url": "https://reddit.com/sample/6",
            "source_subreddit": "hindi",
            "language_code": "hi",
            "domain": "social_media",
            "scraped_at": "2026-04-06T00:00:00+00:00",
        },
    ]
    config = get_config_by_code("hi")
    deduplicator = Deduplicator()

    result = run_cleaning_pipeline(rows=rows, language_config=config, deduplicator=deduplicator)

    rejected_total = (
        result.rejected_language
        + result.rejected_too_short
        + result.rejected_high_noise
        + result.rejected_duplicate
    )
    assert result.total_input == (result.total_output + rejected_total)
