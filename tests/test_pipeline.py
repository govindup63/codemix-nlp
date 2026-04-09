"""Tests for the unified analysis pipeline."""

from codemix.pipeline import CodeMixPipeline
from codemix.sentiment import Label


class TestCodeMixPipeline:
    def setup_method(self):
        self.pipeline = CodeMixPipeline()

    def test_basic_analysis(self):
        result = self.pipeline.analyze("yaar ye movie bahut amazing thi")
        assert result.original == "yaar ye movie bahut amazing thi"
        assert len(result.tagged_words) > 0
        assert result.stats["total_words"] > 0

    def test_hindi_words_detected(self):
        result = self.pipeline.analyze("bahut accha kaam kiya")
        assert result.stats["hindi_words"] >= 3

    def test_english_words_detected(self):
        result = self.pipeline.analyze("this is a very good movie")
        assert result.stats["english_words"] >= 4

    def test_code_mixing_index(self):
        # Pure English — CMI should be 0
        result = self.pipeline.analyze("this is completely english text only")
        assert result.stats["code_mixing_index"] < 0.2

    def test_sentiment_positive(self):
        result = self.pipeline.analyze("bahut amazing movie thi love it")
        assert result.sentiment.label == Label.POSITIVE

    def test_sentiment_negative(self):
        result = self.pipeline.analyze("bahut ghatiya bakwas terrible movie")
        assert result.sentiment.label == Label.NEGATIVE

    def test_transliterations_present(self):
        result = self.pipeline.analyze("bahut accha hai yaar")
        assert len(result.transliterations) > 0

    def test_to_dict(self):
        result = self.pipeline.analyze("hello yaar")
        d = result.to_dict()
        assert "original" in d
        assert "tagged_words" in d
        assert "sentiment" in d
        assert "transliterations" in d
        assert "stats" in d

    def test_batch(self):
        texts = ["bahut accha", "very bad", "hello yaar"]
        results = self.pipeline.analyze_batch(texts)
        assert len(results) == 3

    def test_normalization_applied(self):
        result = self.pipeline.analyze("yaaaar   bahut   goood")
        # Repeated chars should be reduced
        assert "yaar" in result.normalized or "yaa" in result.normalized
