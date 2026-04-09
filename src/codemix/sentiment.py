"""
Sentiment analysis for Hindi-English code-mixed text.

Two approaches:
1. LexiconSentiment — Lightweight, no model download. Uses bilingual
   sentiment lexicons (positive/negative word lists in both Hindi Romanized
   and English) with aggregation.
2. TransformerSentiment — Uses a pre-trained multilingual transformer
   (XLM-RoBERTa) via HuggingFace for higher accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Label(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    label: Label
    score: float  # -1.0 (most negative) to +1.0 (most positive)
    details: dict


# ---------------------------------------------------------------------------
# Bilingual sentiment lexicons (curated for code-mixed social media)
# ---------------------------------------------------------------------------

_POS_HI = {
    "accha", "acha", "badiya", "badhiya", "zabardast", "shandar", "mast",
    "khushi", "pyaar", "dost", "achha", "sundar", "mazaa", "kamaal",
    "sahi", "theek", "pasand", "dil", "jeet", "umeed", "sapna", "hasna",
    "muskurahat", "dhanyavaad", "shukriya", "badhai", "shubh", "anand",
    "safal", "tarakki", "mehnat", "vishwas", "himmat", "jazba", "garv",
    "izzat", "bharosa", "khubsurat", "sachha", "pakka", "behtareen",
}

_NEG_HI = {
    "bura", "kharab", "ganda", "bekar", "bakwas", "wahiyat", "ghatiya",
    "dukh", "takleef", "pareshani", "gussa", "nafrat", "darr", "rona",
    "haar", "galat", "jhootha", "dhoka", "chori", "maar", "gaali",
    "pagal", "bewakoof", "nalayak", "kamina", "harami", "chor",
    "mushkil", "kathin", "toot", "barbaad", "tabahi", "failur", "dard",
}

_POS_EN = {
    "good", "great", "awesome", "amazing", "excellent", "fantastic",
    "wonderful", "brilliant", "love", "happy", "best", "perfect",
    "beautiful", "nice", "super", "cool", "incredible", "outstanding",
    "terrific", "fabulous", "enjoy", "glad", "pleased", "thankful",
    "grateful", "delighted", "excited", "cheerful", "optimistic",
    "successful", "win", "achieve", "appreciate", "admire", "proud",
}

_NEG_EN = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "ugly",
    "stupid", "dumb", "idiot", "fool", "disgusting", "pathetic",
    "useless", "failure", "sad", "angry", "annoyed", "frustrated",
    "disappointed", "depressed", "miserable", "tragic", "painful",
    "boring", "lame", "trash", "garbage", "rubbish", "nonsense",
    "wrong", "broken", "waste", "sucks", "poor", "weak", "sick",
}

# Negation words that flip sentiment
_NEGATORS = {"not", "no", "nahi", "nah", "na", "never", "kabhi", "neither", "nor", "mat"}

# Intensifiers
_INTENSIFIERS = {"very", "bahut", "bohot", "really", "so", "extremely", "zyada", "bilkul"}


class LexiconSentiment:
    """Lightweight bilingual lexicon-based sentiment analyzer."""

    def __init__(self):
        self._pos = _POS_HI | _POS_EN
        self._neg = _NEG_HI | _NEG_EN

    def analyze(self, text: str) -> SentimentResult:
        words = text.lower().split()
        pos_score = 0.0
        neg_score = 0.0
        negated = False
        intensifier = 1.0
        matched: list[dict] = []

        for w in words:
            clean = "".join(c for c in w if c.isalnum())
            if not clean:
                continue

            if clean in _NEGATORS:
                negated = True
                continue

            if clean in _INTENSIFIERS:
                intensifier = 1.5
                continue

            weight = intensifier
            if clean in self._pos:
                if negated:
                    neg_score += weight
                    matched.append({"word": clean, "base": "positive", "negated": True})
                else:
                    pos_score += weight
                    matched.append({"word": clean, "base": "positive", "negated": False})
                negated = False
                intensifier = 1.0
            elif clean in self._neg:
                if negated:
                    pos_score += weight
                    matched.append({"word": clean, "base": "negative", "negated": True})
                else:
                    neg_score += weight
                    matched.append({"word": clean, "base": "negative", "negated": False})
                negated = False
                intensifier = 1.0
            else:
                # Reset negation after a non-sentiment word
                if negated:
                    negated = False

        total = pos_score + neg_score
        if total == 0:
            return SentimentResult(label=Label.NEUTRAL, score=0.0, details={"matched": matched})

        normalized = (pos_score - neg_score) / total  # [-1, 1]

        if normalized > 0.1:
            label = Label.POSITIVE
        elif normalized < -0.1:
            label = Label.NEGATIVE
        else:
            label = Label.NEUTRAL

        return SentimentResult(
            label=label,
            score=round(normalized, 4),
            details={"positive_score": pos_score, "negative_score": neg_score, "matched": matched},
        )


class TransformerSentiment:
    """
    Transformer-based sentiment analysis using a multilingual model.

    Uses XLM-RoBERTa fine-tuned on multilingual sentiment data.
    Requires ~1GB download on first use.
    """

    def __init__(self, model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual"):
        self._model_name = model_name
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            from transformers import pipeline
            self._pipeline = pipeline("sentiment-analysis", model=self._model_name)

    def analyze(self, text: str) -> SentimentResult:
        self._load()
        result = self._pipeline(text, truncation=True, max_length=512)[0]

        label_map = {
            "positive": Label.POSITIVE,
            "negative": Label.NEGATIVE,
            "neutral": Label.NEUTRAL,
        }
        label = label_map.get(result["label"].lower(), Label.NEUTRAL)
        raw_score = result["score"]

        if label == Label.NEGATIVE:
            score = -raw_score
        elif label == Label.POSITIVE:
            score = raw_score
        else:
            score = 0.0

        return SentimentResult(
            label=label,
            score=round(score, 4),
            details={"model": self._model_name, "raw_label": result["label"], "raw_score": raw_score},
        )
