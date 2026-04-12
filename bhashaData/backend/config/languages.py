from __future__ import annotations

from typing import Any

REQUIRED_LANGUAGE_KEYS = {
    "code",
    "name",
    "script",
    "subreddits",
    "youtube_search_terms",
    "news_sites",
    "play_store_lang_code",
    "llm_prompt_instruction",
    "min_word_count",
    "quality_threshold",
    "is_benchmark_language",
}

LANGUAGE_CONFIGS: dict[str, dict[str, Any]] = {
    "en": {
        "code": "en",
        "name": "English",
        "script": "latin",
        "subreddits": [],
        "youtube_search_terms": [
            "india news english",
            "indian tech review",
            "india entertainment",
            "app review english",
            "product review",
            "technology review",
            "movie review english",
            "food review india",
            "cricket highlights",
        ],
        "news_sites": [
            "timesofindia.com",
            "hindustantimes.com",
            "thehindu.com",
            "ndtv.com",
        ],
        "play_store_lang_code": "en_IN",
        "llm_prompt_instruction": "Label this English text only using the allowed label set and return strict JSON with label, confidence, and reason.",
        "min_word_count": 6,
        "quality_threshold": 0.80,
        "is_benchmark_language": True,
    },
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "script": "devanagari",
        "subreddits": [],
        "youtube_search_terms": [
            "hindi news",
            "bollywood latest",
            "cricket hindi commentary",
            "hindi entertainment",
            "bollywood news",
            "cricket hindi",
            "hindi comedy",
            "india news hindi",
            "hindi movie review",
            "hindi technology",
        ],
        "news_sites": ["bhaskar.com", "aajtak.in", "ndtv.in", "jagran.com", "amarujala.com"],
        "play_store_lang_code": "hi",
        "llm_prompt_instruction": "Label this Hindi text (Devanagari) only using the allowed label set and return strict JSON with label, confidence, and reason.",
        "min_word_count": 5,
        "quality_threshold": 0.80,
        "is_benchmark_language": False,
    },
    "gu": {
        "code": "gu",
        "name": "Gujarati",
        "script": "gujarati",
        "subreddits": [],
        "youtube_search_terms": [
            "gujarati news",
            "vtv gujarati",
            "sandesh news gujarati",
            "gujarat samachar",
            "gujarati comedy",
            "gujarat news today",
            "gujarati serial",
            "ahmedabad vlog",
            "gujarat news",
            "gujarati natak",
            "gujarati song",
        ],
        "news_sites": [
            "divyabhaskar.co.in",
            "sandesh.com",
            "gujaratsamachar.com",
            "abhiyaan.com",
            "gujaratmirror.com",
            "bombaysamachar.com",
        ],
        "play_store_lang_code": "gu",
        "llm_prompt_instruction": "Label this Gujarati text only using the allowed label set and return strict JSON with label, confidence, and reason.",
        "min_word_count": 3,
        "quality_threshold": 0.75,
        "is_benchmark_language": False,
    },
    "mr": {
        "code": "mr",
        "name": "Marathi",
        "script": "devanagari",
        "subreddits": [],
        "youtube_search_terms": ["marathi news", "tv9 marathi", "zee 24 taas", "marathi entertainment"],
        "news_sites": [
            "loksatta.com",
            "maharashtratimes.com",
            "divyamarathi.bhaskar.com",
            "esakal.com",
        ],
        "play_store_lang_code": "mr",
        "llm_prompt_instruction": "Label this Marathi text (Devanagari) only using the allowed label set and return strict JSON with label, confidence, and reason.",
        "min_word_count": 4,
        "quality_threshold": 0.80,
        "is_benchmark_language": False,
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "script": "tamil",
        "subreddits": [],
        "youtube_search_terms": [
            "tamil news",
            "puthiya thalaimurai",
            "sun news tamil",
            "kollywood latest",
        ],
        "news_sites": ["dinamalar.com", "dinamani.com", "puthiyathalaimurai.tv", "vikatan.com"],
        "play_store_lang_code": "ta",
        "llm_prompt_instruction": "Label this Tamil text only using the allowed label set and return strict JSON with label, confidence, and reason.",
        "min_word_count": 4,
        "quality_threshold": 0.82,
        "is_benchmark_language": False,
    },
}


def validate_all_configs() -> None:
    benchmark_count = 0

    for language_key, config in LANGUAGE_CONFIGS.items():
        missing_keys = REQUIRED_LANGUAGE_KEYS - set(config.keys())
        if missing_keys:
            raise ValueError(
                f"Language '{language_key}' missing required fields: {sorted(missing_keys)}"
            )

        code = config["code"]
        if not isinstance(code, str) or not code.strip():
            raise ValueError(f"Language '{language_key}' has invalid field 'code': must be a non-empty string")

        if not isinstance(config["subreddits"], list):
            raise ValueError(f"Language '{language_key}' has invalid field 'subreddits': must be a list")

        if not isinstance(config["news_sites"], list) or len(config["news_sites"]) == 0:
            raise ValueError(f"Language '{language_key}' has invalid field 'news_sites': must be a non-empty list")

        if not isinstance(config["youtube_search_terms"], list) or len(config["youtube_search_terms"]) == 0:
            raise ValueError(
                f"Language '{language_key}' has invalid field 'youtube_search_terms': must be a non-empty list"
            )

        quality_threshold = config["quality_threshold"]
        if not isinstance(quality_threshold, float) or not (0.0 <= quality_threshold <= 1.0):
            raise ValueError(
                f"Language '{language_key}' has invalid field 'quality_threshold': must be a float between 0.0 and 1.0"
            )

        min_word_count = config["min_word_count"]
        if not isinstance(min_word_count, int) or min_word_count <= 0:
            raise ValueError(
                f"Language '{language_key}' has invalid field 'min_word_count': must be an integer greater than 0"
            )

        is_benchmark = config["is_benchmark_language"]
        if not isinstance(is_benchmark, bool):
            raise ValueError(
                f"Language '{language_key}' has invalid field 'is_benchmark_language': must be a boolean"
            )
        if is_benchmark:
            benchmark_count += 1

    if benchmark_count != 1:
        raise ValueError(
            "Invalid benchmark configuration: exactly one language must have is_benchmark_language=True"
        )


def get_config_by_code(lang_code: str) -> dict[str, Any]:
    normalized_code = (lang_code or "").strip().lower()
    if normalized_code in LANGUAGE_CONFIGS:
        return LANGUAGE_CONFIGS[normalized_code]
    raise ValueError(f"Unsupported language code: '{lang_code}'")


def get_all_language_codes() -> list[str]:
    return list(LANGUAGE_CONFIGS.keys())


def get_benchmark_language() -> dict[str, Any]:
    for config in LANGUAGE_CONFIGS.values():
        if config["is_benchmark_language"]:
            return config
    raise ValueError("No benchmark language configured")


def is_supported_language(lang_code: str) -> bool:
    normalized_code = (lang_code or "").strip().lower()
    return normalized_code in LANGUAGE_CONFIGS


validate_all_configs()
