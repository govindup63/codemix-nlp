"""
Text normalization for code-mixed Hindi-English text.

Handles common patterns in informal code-mixed writing:
- Repeated characters ("sooo goood" → "so good")
- Common abbreviations and slang
- Mixed-script normalization
"""

import re
import unicodedata


# Common abbreviations/slang → normalized form
_SLANG_MAP = {
    "u": "you",
    "ur": "your",
    "r": "are",
    "n": "and",
    "b4": "before",
    "2day": "today",
    "2morrow": "tomorrow",
    "2mrw": "tomorrow",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "thnx": "thanks",
    "msg": "message",
    "pic": "picture",
    "pics": "pictures",
    "govt": "government",
    "yr": "year",
    "yrs": "years",
    "info": "information",
    "abt": "about",
    "srsly": "seriously",
    "tbh": "to be honest",
    "imo": "in my opinion",
    "idk": "i don't know",
    "lol": "lol",
    "brb": "be right back",
    "btw": "by the way",
    # Hindi slang normalizations
    "h": "hai",
    "hh": "haha",
    "hmm": "hmm",
    "acha": "accha",
    "thnku": "thank you",
    "tnx": "thanks",
}

# Max allowed consecutive identical characters
_MAX_REPEAT = 2


def reduce_lengthening(word: str) -> str:
    """Reduce character repetitions to at most 2 (e.g., 'sooo' → 'soo')."""
    return re.sub(r"(.)\1{2,}", r"\1\1", word)


def expand_slang(word: str) -> str:
    """Replace known slang/abbreviations with full forms."""
    return _SLANG_MAP.get(word.lower(), word)


def strip_accents(text: str) -> str:
    """Remove diacritics from Latin characters."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace into single space and strip."""
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str, expand_slang_words: bool = True, reduce_repeats: bool = True) -> str:
    """
    Apply full normalization pipeline to code-mixed text.

    Args:
        text: Input text (may contain Hindi and English)
        expand_slang_words: Replace slang with full forms
        reduce_repeats: Reduce repeated characters
    """
    text = normalize_whitespace(text)

    words = text.split()
    normalized = []
    for w in words:
        if reduce_repeats:
            w = reduce_lengthening(w)
        if expand_slang_words:
            w = expand_slang(w)
        normalized.append(w)

    return " ".join(normalized)
