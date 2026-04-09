"""
Rule-based transliteration from Romanized Hindi to Devanagari.

Handles casual Romanized Hindi as commonly typed in social media and messaging
(e.g., "namaste" → "नमस्ते", "kaise ho" → "कैसे हो").

The approach uses a longest-match-first strategy over a phoneme mapping table,
with special handling for:
- Aspirated consonants (kh, gh, ch, jh, th, dh, ph, bh)
- Vowel matras (dependent vowel signs after consonants)
- Implicit schwa deletion at word boundaries
- Common spelling variations in informal Romanized Hindi
"""

from dataclasses import dataclass


@dataclass
class TranslitResult:
    original: str
    devanagari: str


# Consonant mappings — ordered longest-first for greedy matching
_CONSONANTS: list[tuple[str, str]] = [
    ("shh", "ष"),
    ("sh", "श"),
    ("chh", "छ"),
    ("ch", "च"),
    ("th", "थ"),  # dental aspirated
    ("dh", "ध"),  # dental aspirated
    ("ph", "फ"),
    ("bh", "भ"),
    ("kh", "ख"),
    ("gh", "घ"),
    ("jh", "झ"),
    ("ng", "ङ"),
    ("nn", "ण"),
    ("tr", "त्र"),
    ("gn", "ज्ञ"),
    ("gy", "ज्ञ"),
    ("ksh", "क्ष"),
    ("t", "त"),
    ("d", "द"),
    ("n", "न"),
    ("p", "प"),
    ("b", "ब"),
    ("m", "म"),
    ("y", "य"),
    ("r", "र"),
    ("l", "ल"),
    ("v", "व"),
    ("w", "व"),
    ("s", "स"),
    ("h", "ह"),
    ("k", "क"),
    ("g", "ग"),
    ("j", "ज"),
    ("z", "ज़"),
    ("f", "फ़"),
    ("q", "क़"),
    ("x", "क्स"),
]

# Independent vowels (used at word start or after another vowel)
_VOWELS_INDEPENDENT: list[tuple[str, str]] = [
    ("aa", "आ"),
    ("ai", "ऐ"),
    ("au", "औ"),
    ("ee", "ई"),
    ("oo", "ऊ"),
    ("ou", "औ"),
    ("a", "अ"),
    ("i", "इ"),
    ("u", "उ"),
    ("e", "ए"),
    ("o", "ओ"),
]

# Dependent vowel signs (matras, used after consonants)
_VOWELS_MATRA: list[tuple[str, str]] = [
    ("aa", "ा"),
    ("ai", "ै"),
    ("au", "ौ"),
    ("ee", "ी"),
    ("oo", "ू"),
    ("ou", "ौ"),
    ("a", ""),  # inherent 'a' — no matra needed
    ("i", "ि"),
    ("u", "ु"),
    ("e", "े"),
    ("o", "ो"),
]

# Virama (halant) — suppresses the inherent vowel
_HALANT = "्"


def _match_consonant(text: str, pos: int) -> tuple[str, int] | None:
    """Try to match a consonant at position pos, longest first."""
    for roman, dev in _CONSONANTS:
        end = pos + len(roman)
        if text[pos:end].lower() == roman:
            return dev, end
    return None


def _match_vowel(text: str, pos: int, as_matra: bool) -> tuple[str, int] | None:
    """Try to match a vowel at position pos."""
    table = _VOWELS_MATRA if as_matra else _VOWELS_INDEPENDENT
    for roman, dev in table:
        end = pos + len(roman)
        if text[pos:end].lower() == roman:
            return dev, end
    return None


def _transliterate_word(word: str) -> str:
    """Transliterate a single Romanized Hindi word to Devanagari."""
    if not word:
        return word

    result = []
    i = 0
    after_consonant = False

    while i < len(word):
        ch = word[i]

        # Skip non-alpha characters
        if not ch.isalpha():
            result.append(ch)
            after_consonant = False
            i += 1
            continue

        # Try consonant match
        cons = _match_consonant(word, i)
        if cons is not None:
            dev_cons, new_i = cons

            # If previous char was also a consonant, insert halant
            if after_consonant:
                result.append(_HALANT)

            result.append(dev_cons)
            after_consonant = True
            i = new_i

            # Check for a following vowel (matra)
            if i < len(word):
                vowel = _match_vowel(word, i, as_matra=True)
                if vowel is not None:
                    dev_v, new_i = vowel
                    if dev_v:  # non-empty matra (not inherent 'a')
                        result.append(dev_v)
                    after_consonant = False
                    i = new_i
            continue

        # Try vowel match (independent)
        vowel = _match_vowel(word, i, as_matra=after_consonant)
        if vowel is not None:
            dev_v, new_i = vowel
            if after_consonant and dev_v:
                result.append(dev_v)
            elif not after_consonant:
                result.append(dev_v)
            after_consonant = False
            i = new_i
            continue

        # Fallback — keep character as-is
        result.append(ch)
        after_consonant = False
        i += 1

    # If word ends on a consonant, the inherent 'a' is typically silent
    # in Hindi — no halant needed (schwa deletion)
    return "".join(result)


class Transliterator:
    """Transliterate Romanized Hindi text to Devanagari script."""

    def transliterate(self, text: str) -> TranslitResult:
        words = text.split()
        converted = [_transliterate_word(w) for w in words]
        return TranslitResult(original=text, devanagari=" ".join(converted))

    def transliterate_words(self, words: list[str]) -> list[TranslitResult]:
        return [self.transliterate(w) for w in words]
