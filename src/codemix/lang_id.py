"""
Word-level language identification for Hindi-English code-mixed text.

Implements two approaches:
1. ScriptDetector — Unicode range based (Devanagari vs Latin)
2. CharNGramLangID — Character n-gram frequency profiles for distinguishing
   Romanized Hindi from English, based on the Cavnar & Trenkle (1994) approach
   adapted for code-mixed scenarios.
"""

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


DEVANAGARI_START = 0x0900
DEVANAGARI_END = 0x097F


@dataclass
class TaggedWord:
    word: str
    lang: str  # "hi", "en", "other"
    confidence: float


class ScriptDetector:
    """Detect language based on Unicode script of characters."""

    @staticmethod
    def detect(word: str) -> str:
        dev = sum(1 for c in word if DEVANAGARI_START <= ord(c) <= DEVANAGARI_END)
        lat = sum(1 for c in word if c.isascii() and c.isalpha())
        if dev > lat:
            return "hi"
        if lat > dev:
            return "latin"
        return "other"


class CharNGramLangID:
    """
    Character n-gram language identifier.

    Builds frequency profiles from labeled word lists and classifies new words
    by cosine similarity against each profile. This is effective for distinguishing
    Romanized Hindi from English because they differ in character distribution
    (e.g., Hindi uses more 'aa', 'bh', 'kh' clusters while English favours 'th',
    'tion', 'ing').
    """

    def __init__(self, n_range: tuple[int, int] = (2, 5), top_k: int = 800):
        self.n_range = n_range
        self.top_k = top_k
        self.profiles: dict[str, dict[str, float]] = {}
        self._trained = False

    def _ngrams(self, word: str) -> Counter:
        padded = f"^{word.lower()}$"
        counts: Counter = Counter()
        for n in range(self.n_range[0], self.n_range[1] + 1):
            for i in range(len(padded) - n + 1):
                counts[padded[i : i + n]] += 1
        return counts

    def train(self, words_by_lang: dict[str, list[str]]) -> None:
        """Build n-gram frequency profiles from labeled word lists."""
        for lang, words in words_by_lang.items():
            merged: Counter = Counter()
            for w in words:
                merged.update(self._ngrams(w))
            total = sum(merged.values()) or 1
            self.profiles[lang] = {
                ng: count / total for ng, count in merged.most_common(self.top_k)
            }
        self._trained = True

    def predict(self, word: str) -> TaggedWord:
        """Classify a single word and return (lang, confidence)."""
        if not self._trained:
            raise RuntimeError("Call train() before predict()")

        wng = self._ngrams(word)
        total = sum(wng.values()) or 1
        word_vec = {ng: c / total for ng, c in wng.items()}

        best_lang, best_score = "other", 0.0
        for lang, profile in self.profiles.items():
            keys = set(word_vec) | set(profile)
            dot = sum(word_vec.get(k, 0) * profile.get(k, 0) for k in keys)
            n1 = math.sqrt(sum(v * v for v in word_vec.values()))
            n2 = math.sqrt(sum(v * v for v in profile.values()))
            score = dot / (n1 * n2) if n1 and n2 else 0.0
            if score > best_score:
                best_lang, best_score = lang, score

        return TaggedWord(word=word, lang=best_lang, confidence=round(best_score, 4))

    def tag_sentence(self, text: str) -> list[TaggedWord]:
        """Tag each word in a sentence with its language."""
        tokens = re.findall(r"\w+|[^\w\s]", text)
        results = []
        for tok in tokens:
            if not any(c.isalpha() for c in tok):
                results.append(TaggedWord(word=tok, lang="other", confidence=1.0))
                continue

            script = ScriptDetector.detect(tok)
            if script == "hi":
                # Already in Devanagari — no ambiguity
                results.append(TaggedWord(word=tok, lang="hi", confidence=1.0))
            elif script == "latin":
                results.append(self.predict(tok))
            else:
                results.append(TaggedWord(word=tok, lang="other", confidence=0.0))
        return results

    def save(self, path: str) -> None:
        data = {"n_range": list(self.n_range), "top_k": self.top_k, "profiles": self.profiles}
        Path(path).write_text(json.dumps(data, indent=2))

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text())
        self.n_range = tuple(data["n_range"])
        self.top_k = data["top_k"]
        self.profiles = data["profiles"]
        self._trained = True


# ---------------------------------------------------------------------------
# Default training data — common words in casual Romanized Hindi and English
# ---------------------------------------------------------------------------

_HINDI_WORDS = [
    "hai", "ka", "ki", "ke", "ko", "se", "mein", "ye", "wo", "kya",
    "nahi", "aur", "par", "bhi", "tha", "thi", "hum", "tum", "mera",
    "tera", "uska", "iska", "kuch", "bahut", "accha", "bura", "chal",
    "bol", "sun", "dekh", "jaa", "aa", "kha", "pi", "le", "de",
    "kar", "ho", "raha", "rahi", "wala", "wali", "yaar", "bhai",
    "didi", "sab", "log", "kaam", "ghar", "paisa", "dost", "pyaar",
    "zindagi", "duniya", "samajh", "padhai", "khana", "pani", "raat",
    "din", "subah", "shaam", "abhi", "baad", "pehle", "saath", "andar",
    "bahar", "upar", "niche", "idhar", "udhar", "kahin", "kabhi",
    "hamesha", "bilkul", "sachchi", "jhootha", "pagal", "chalo", "aaja",
    "jaane", "milke", "bolna", "sunna", "dekhna", "karna", "hona",
    "rehna", "mujhe", "tujhe", "humko", "tumko", "unko", "kisko",
    "kyun", "kaise", "kahan", "kab", "kitna", "kaun", "konsa", "lekin",
    "magar", "isliye", "kyunki", "agar", "toh", "warna", "shayad",
    "zaroor", "pakka", "sach", "theek", "galat", "acha", "zyada",
    "thoda", "bohot", "sochna", "likhna", "padhna", "samjhna", "milna",
    "banana", "todna", "kholna", "bandh", "shuru", "khatam", "matlab",
    "waise", "jaise", "chaiye", "chahiye", "sakta", "sakti", "sakte",
    "wala", "waala", "pata", "lagta", "dikhta", "sunta", "bolta",
    "khelta", "sota", "jaata", "aata", "deta", "leta", "marta",
    "hasna", "rona", "gaana", "nachna", "bhagna", "girna", "uthna",
]

_ENGLISH_WORDS = [
    "the", "is", "are", "was", "were", "have", "has", "had", "been",
    "will", "would", "could", "should", "can", "may", "might", "must",
    "do", "does", "did", "not", "and", "but", "or", "so", "yet",
    "for", "nor", "at", "by", "to", "in", "on", "of", "with", "from",
    "up", "out", "off", "over", "into", "about", "after", "before",
    "during", "between", "through", "this", "that", "these", "those",
    "here", "there", "where", "when", "how", "what", "which", "who",
    "why", "all", "each", "every", "both", "few", "more", "most",
    "some", "any", "no", "other", "such", "only", "same", "than",
    "very", "just", "also", "now", "then", "still", "already", "always",
    "never", "often", "sometimes", "usually", "really", "actually",
    "good", "great", "nice", "bad", "new", "old", "big", "small",
    "long", "short", "high", "low", "right", "wrong", "true", "false",
    "think", "know", "want", "need", "like", "love", "hate", "feel",
    "see", "look", "watch", "hear", "tell", "say", "ask", "give",
    "take", "make", "come", "go", "get", "put", "run", "work", "call",
    "try", "use", "find", "help", "show", "play", "move", "start",
    "stop", "open", "close", "turn", "keep", "set", "leave", "change",
    "point", "read", "write", "learn", "build", "because", "thing",
    "time", "people", "world", "school", "place", "system", "number",
]


def create_default_detector() -> CharNGramLangID:
    """Return a detector pre-trained on common Hindi/English words."""
    det = CharNGramLangID()
    det.train({"hi": _HINDI_WORDS, "en": _ENGLISH_WORDS})
    return det
