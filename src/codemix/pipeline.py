"""
Unified analysis pipeline for code-mixed text.

Combines language identification, transliteration, sentiment analysis,
and text normalization into a single pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from codemix.lang_id import CharNGramLangID, TaggedWord, create_default_detector
from codemix.normalize import normalize
from codemix.sentiment import Label, LexiconSentiment, SentimentResult, TransformerSentiment
from codemix.transliterate import TranslitResult, Transliterator


@dataclass
class AnalysisResult:
    """Complete analysis of a code-mixed text input."""

    original: str
    normalized: str
    tagged_words: list[TaggedWord]
    sentiment: SentimentResult
    transliterations: list[TranslitResult]
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "normalized": self.normalized,
            "tagged_words": [
                {"word": tw.word, "lang": tw.lang, "confidence": tw.confidence}
                for tw in self.tagged_words
            ],
            "sentiment": {
                "label": self.sentiment.label.value,
                "score": self.sentiment.score,
            },
            "transliterations": [
                {"original": tr.original, "devanagari": tr.devanagari}
                for tr in self.transliterations
            ],
            "stats": self.stats,
        }


class CodeMixPipeline:
    """
    End-to-end pipeline for code-mixed Hindi-English text analysis.

    Usage:
        pipeline = CodeMixPipeline()
        result = pipeline.analyze("yaar ye movie bahut amazing thi")
    """

    def __init__(self, use_transformer_sentiment: bool = False):
        self._lang_id = create_default_detector()
        self._transliterator = Transliterator()
        self._sentiment: LexiconSentiment | TransformerSentiment
        if use_transformer_sentiment:
            self._sentiment = TransformerSentiment()
        else:
            self._sentiment = LexiconSentiment()

    @property
    def lang_detector(self) -> CharNGramLangID:
        return self._lang_id

    def analyze(self, text: str) -> AnalysisResult:
        """Run full analysis pipeline on input text."""
        # 1. Normalize
        norm = normalize(text)

        # 2. Language identification
        tagged = self._lang_id.tag_sentence(norm)

        # 3. Sentiment analysis
        sentiment = self._sentiment.analyze(norm)

        # 4. Transliterate Hindi words to Devanagari
        transliterations = []
        for tw in tagged:
            if tw.lang == "hi":
                result = self._transliterator.transliterate(tw.word)
                transliterations.append(result)

        # 5. Compute stats
        hi_count = sum(1 for tw in tagged if tw.lang == "hi")
        en_count = sum(1 for tw in tagged if tw.lang == "en")
        total = hi_count + en_count or 1
        cmi = 1 - (max(hi_count, en_count) / total) if total > 0 else 0.0

        stats = {
            "total_words": len(tagged),
            "hindi_words": hi_count,
            "english_words": en_count,
            "other": sum(1 for tw in tagged if tw.lang == "other"),
            "code_mixing_index": round(cmi, 4),
        }

        return AnalysisResult(
            original=text,
            normalized=norm,
            tagged_words=tagged,
            sentiment=sentiment,
            transliterations=transliterations,
            stats=stats,
        )

    def analyze_batch(self, texts: list[str]) -> list[AnalysisResult]:
        """Analyze multiple texts."""
        return [self.analyze(t) for t in texts]
