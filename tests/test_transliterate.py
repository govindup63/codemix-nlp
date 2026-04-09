"""Tests for the transliteration module."""

from codemix.transliterate import Transliterator


class TestTransliterator:
    def setup_method(self):
        self.t = Transliterator()

    def test_simple_word(self):
        result = self.t.transliterate("namaste")
        assert result.devanagari == "नमस्ते"

    def test_aspirated_consonants(self):
        result = self.t.transliterate("khaana")
        assert "ख" in result.devanagari

    def test_vowel_matras(self):
        result = self.t.transliterate("ki")
        assert "कि" == result.devanagari

    def test_multi_word(self):
        result = self.t.transliterate("kaise ho")
        assert " " in result.devanagari  # Two words preserved
        assert "कै" in result.devanagari

    def test_preserves_original(self):
        result = self.t.transliterate("bahut accha")
        assert result.original == "bahut accha"

    def test_empty_string(self):
        result = self.t.transliterate("")
        assert result.devanagari == ""

    def test_batch(self):
        results = self.t.transliterate_words(["pyaar", "dost"])
        assert len(results) == 2
        assert "प्य" in results[0].devanagari or "प" in results[0].devanagari
