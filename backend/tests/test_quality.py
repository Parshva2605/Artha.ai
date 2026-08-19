try:
    from backend.pipeline.quality import (
        BenchmarkComparison,
        BalanceResult,
        calculate_quality_score,
        check_label_balance,
        check_low_quality,
        check_shortfall,
        generate_quality_report,
        get_benchmark_comparison,
    )
    from backend.pipeline.labeler import LabelingResult
except ModuleNotFoundError:
    from pipeline.quality import (
        BenchmarkComparison,
        BalanceResult,
        calculate_quality_score,
        check_label_balance,
        check_low_quality,
        check_shortfall,
        generate_quality_report,
        get_benchmark_comparison,
    )
    from pipeline.labeler import LabelingResult


def test_calculate_quality_score_returns_correct_value() -> None:
    rows = [
        {"confidence": 0.90},
        {"confidence": 0.85},
        {"confidence": 0.95},
    ]
    score = calculate_quality_score(rows)
    assert score == 90.0


def test_calculate_quality_score_returns_zero_for_empty_list() -> None:
    assert calculate_quality_score([]) == 0.0


def test_check_label_balance_detects_imbalance() -> None:
    distribution = {
        "positive": 700,
        "negative": 200,
        "neutral": 100,
    }
    result = check_label_balance(distribution, 1000)
    assert result.is_balanced is False
    assert result.dominant_label == "positive"
    assert result.dominant_percentage == 70.0


def test_check_label_balance_passes_for_balanced_data() -> None:
    distribution = {
        "positive": 350,
        "negative": 350,
        "neutral": 300,
    }
    result = check_label_balance(distribution, 1000)
    assert result.is_balanced is True
    assert result.dominant_label is None


def test_get_benchmark_comparison_calculates_differences_correctly() -> None:
    per_language_quality = {
        "en": 94.0,
        "hi": 88.0,
        "gu": 85.0,
    }
    result = get_benchmark_comparison(per_language_quality)
    assert result.english_score == 94.0
    assert result.differences["hi"] == -6.0
    assert result.differences["gu"] == -9.0


def test_check_shortfall_detects_shortfall() -> None:
    delivered = {"hi": 350, "gu": 480}
    requested = {"hi": 500, "gu": 500}
    warnings = check_shortfall(delivered, requested)
    assert len(warnings) == 1
    assert "hi" in warnings[0].lower()


def test_check_shortfall_returns_empty_for_no_shortfall() -> None:
    delivered = {"hi": 450, "gu": 480}
    requested = {"hi": 500, "gu": 500}
    warnings = check_shortfall(delivered, requested)
    assert len(warnings) == 0


def test_check_low_quality_returns_warning_below_78() -> None:
    warning = check_low_quality(75.5)
    assert warning is not None
    assert "75.5" in warning


def test_check_low_quality_returns_none_above_78() -> None:
    assert check_low_quality(85.0) is None
    assert check_low_quality(78.0) is None
