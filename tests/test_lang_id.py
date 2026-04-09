"""Tests for the language identification module."""

from codemix.lang_id import CharNGramLangID, ScriptDetector, create_default_detector


class TestScriptDetector:
    def test_devanagari(self):
        assert ScriptDetector.detect("नमस्ते") == "hi"

    def test_latin(self):
        assert ScriptDetector.detect("hello") == "latin"

    def test_mixed_prefers_majority(self):
        assert ScriptDetector.detect("हेllo") == "hi"  # 2 devanagari vs 3 latin — depends on chars

    def test_numbers(self):
        assert ScriptDetector.detect("123") == "other"


class TestCharNGramLangID:
    def setup_method(self):
        self.detector = create_default_detector()

    def test_hindi_words(self):
        for word in ["bahut", "accha", "kyunki", "zindagi", "hamesha"]:
            result = self.detector.predict(word)
            assert result.lang == "hi", f"Expected 'hi' for '{word}', got '{result.lang}'"

    def test_english_words(self):
        for word in ["beautiful", "actually", "sometimes", "through", "between"]:
            result = self.detector.predict(word)
            assert result.lang == "en", f"Expected 'en' for '{word}', got '{result.lang}'"

    def test_tag_sentence(self):
        tagged = self.detector.tag_sentence("yaar ye movie bahut amazing thi")
        langs = [tw.lang for tw in tagged]
        # "yaar", "ye", "bahut", "thi" should be Hindi
        # "movie", "amazing" should be English
        assert langs[0] == "hi"  # yaar
        assert langs[4] == "en"  # amazing

    def test_confidence_range(self):
        result = self.detector.predict("hello")
        assert 0.0 <= result.confidence <= 1.0

    def test_save_load(self, tmp_path):
        path = str(tmp_path / "model.json")
        self.detector.save(path)

        loaded = CharNGramLangID()
        loaded.load(path)

        original = self.detector.predict("bahut")
        from_loaded = loaded.predict("bahut")
        assert original.lang == from_loaded.lang
