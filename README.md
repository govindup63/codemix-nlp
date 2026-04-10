<p align="center">
  <img src="assets/logo.svg" alt="codemix-nlp" width="480" />
</p>

<p align="center">
  <a href="https://github.com/govindup63/codemix-nlp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <img src="https://img.shields.io/badge/accuracy-87%25-brightgreen.svg" alt="Accuracy 87%">
  <img src="https://img.shields.io/badge/tests-26%20passed-brightgreen.svg" alt="Tests 26 passed">
</p>

<p align="center">
  NLP toolkit for analyzing Hindi-English code-mixed text. Handles the unique challenges of <strong>code-switching</strong> - where speakers alternate between Hindi (often Romanized) and English within a sentence, as commonly seen in Indian social media, messaging, and spoken language.
</p>

---

## Features

- **Word-level Language Identification** - Character n-gram frequency profiles distinguish Romanized Hindi from English (based on Cavnar & Trenkle, 1994)
- **Romanized Hindi → Devanagari Transliteration** - Rule-based phonetic mapping with support for aspirated consonants, vowel matras, and schwa deletion
- **Bilingual Sentiment Analysis** - Lexicon-based (lightweight) and transformer-based (XLM-RoBERTa) approaches
- **Text Normalization** - Handles character repetition, slang expansion, and mixed-script cleanup
- **Code-Mixing Index (CMI)** - Quantifies the degree of language mixing in a sentence
- **REST API** - FastAPI server for all features
- **CLI** - Command-line tool for quick analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/govindup63/codemix-nlp.git
cd codemix-nlp

# Install with uv (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from codemix.pipeline import CodeMixPipeline

pipeline = CodeMixPipeline()
result = pipeline.analyze("Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?")

print(result.sentiment.label)      # neutral
print(result.stats)                # {'hindi_words': 7, 'english_words': 7, ...}
for tw in result.tagged_words:
    print(f"{tw.word:15s} [{tw.lang}] ({tw.confidence:.2f})")
```

### CLI

```bash
codemix "Life is a race, if you don't run fast, you will be like a broken undaa"
codemix --json "Shaadi is dal chawal for pachaas saal till you die, arre life mein thoda bahut keema pav bhi hona chahiye nah"
echo "Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai" | codemix --stdin
```

### REST API

```bash
uvicorn codemix.api:app --reload

# Analyze text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?"}'

# Language detection only
curl -X POST http://localhost:8000/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "Shaadi is dal chawal for pachaas saal till you die"}'
```

## CLI Examples

> Examples use iconic Bollywood Hinglish dialogues - perfect test cases for code-mixing analysis.

**3 Idiots** - "Life is a race..."
```bash
$ codemix "Life is a race, if you don't run fast, you will be like a broken undaa"

  Input:      Life is a race, if you don't run fast, you will be like a broken undaa
  Normalized: Life is a race, if you don't run fast, you will be like a broken undaa

  Word-level language tags:
    Life            [en]     (conf: 0.12)
    is              [en]     (conf: 0.07)
    race            [en]     (conf: 0.13)
    you             [en]     (conf: 0.02)
    run             [en]     (conf: 0.06)
    fast            [en]     (conf: 0.12)
    broken          [en]     (conf: 0.10)
    undaa           [hi]     (conf: 0.20)

  Sentiment:  negative (score: -1.00)

  Hindi words -> Devanagari:
    undaa           -> उन्दा

  Stats: 3 Hindi, 14 English, 3 other | CMI: 0.18
```

**3 Idiots** - "Ajeeb desh hai hamara..."
```bash
$ codemix "Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?"

  Input:      Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?
  Normalized: Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?

  Word-level language tags:
    Ajeeb           [en]     (conf: 0.05)
    desh            [hi]     (conf: 0.07)
    hai             [hi]     (conf: 0.19)
    hamara          [hi]     (conf: 0.24)
    pizza           [hi]     (conf: 0.15)
    tees            [en]     (conf: 0.12)
    minute          [en]     (conf: 0.14)
    pahuchne        [hi]     (conf: 0.13)
    ki              [hi]     (conf: 0.18)
    guarantee       [en]     (conf: 0.12)
    hai             [hi]     (conf: 0.19)
    lekin           [en]     (conf: 0.08)
    ambulance       [en]     (conf: 0.12)

  Sentiment:  neutral (score: +0.00)

  Hindi words -> Devanagari:
    desh -> देश  hai -> है  hamara -> हमर  pahuchne -> पहुच्ने  ki -> कि

  Stats: 7 Hindi, 7 English, 3 other | CMI: 0.50
```

**Yeh Jawaani Hai Deewani** - JSON output:
```bash
$ codemix --json "Shaadi is dal chawal for pachaas saal till you die, arre life mein thoda bahut keema pav bhi hona chahiye nah"
{
  "original": "Shaadi is dal chawal for pachaas saal till you die, ...",
  "tagged_words": [
    {"word": "Shaadi", "lang": "hi", "confidence": 0.1825},
    {"word": "is", "lang": "en", "confidence": 0.0702},
    {"word": "dal", "lang": "en", "confidence": 0.0748},
    {"word": "chawal", "lang": "hi", "confidence": 0.1404},
    {"word": "for", "lang": "en", "confidence": 0.1156},
    {"word": "pachaas", "lang": "hi", "confidence": 0.1582},
    {"word": "saal", "lang": "hi", "confidence": 0.154},
    {"word": "till", "lang": "en", "confidence": 0.1552},
    {"word": "you", "lang": "en", "confidence": 0.0238},
    {"word": "die", "lang": "en", "confidence": 0.136},
    {"word": "thoda", "lang": "hi", "confidence": 0.1902},
    {"word": "bahut", "lang": "hi", "confidence": 0.1145},
    {"word": "hona", "lang": "hi", "confidence": 0.2993},
    {"word": "chahiye", "lang": "hi", "confidence": 0.1857}
  ],
  "sentiment": {"label": "neutral", "score": 0.0},
  "transliterations": [
    {"original": "Shaadi", "devanagari": "शादि"},
    {"original": "chawal", "devanagari": "चवल"},
    {"original": "pachaas", "devanagari": "पचास"},
    {"original": "saal", "devanagari": "साल"},
    {"original": "bahut", "devanagari": "बहुत"},
    {"original": "hona", "devanagari": "होन"},
    {"original": "chahiye", "devanagari": "चहिये"}
  ],
  "stats": {
    "total_words": 22, "hindi_words": 12, "english_words": 9,
    "other": 1, "code_mixing_index": 0.4286
  }
}
```

## Language ID Evaluation

```
$ python scripts/evaluate_lang_id.py

Total: 46 | Correct: 40 | Accuracy: 87.0%

   HI: P=0.95  R=0.78  F1=0.86
   EN: P=0.81  R=0.96  F1=0.88
```

## Modules

### Language Identification (`codemix.lang_id`)

Two-stage approach:
1. **Script detection** - Unicode range checks separate Devanagari from Latin script
2. **N-gram classification** - For Latin-script words, character n-gram frequency profiles distinguish Romanized Hindi from English using cosine similarity

```python
from codemix.lang_id import create_default_detector

detector = create_default_detector()
tagged = detector.tag_sentence("bahut amazing movie thi")
# [TaggedWord(word='bahut', lang='hi', confidence=0.82),
#  TaggedWord(word='amazing', lang='en', confidence=0.76), ...]
```

### Transliteration (`codemix.transliterate`)

Converts Romanized Hindi to Devanagari using phonetic rules with longest-match-first strategy.

```python
from codemix.transliterate import Transliterator

t = Transliterator()
result = t.transliterate("namaste dost kaise ho")
print(result.devanagari)  # नमस्ते दोस्त कैसे हो
```

### Sentiment Analysis (`codemix.sentiment`)

```python
# Lightweight lexicon-based (no download)
from codemix.sentiment import LexiconSentiment
s = LexiconSentiment()
result = s.analyze("bahut amazing movie thi love it")
print(result.label)  # positive

# Transformer-based (higher accuracy, ~1GB download)
from codemix.sentiment import TransformerSentiment
s = TransformerSentiment()
result = s.analyze("kya bakwas movie thi terrible")
print(result.label)  # negative
```

## Running Tests

```bash
pytest -v
```

## Project Structure

```
codemix-nlp/
├── src/codemix/
│   ├── lang_id.py          # Character n-gram language identification
│   ├── transliterate.py    # Romanized Hindi → Devanagari
│   ├── sentiment.py        # Lexicon + transformer sentiment analysis
│   ├── normalize.py        # Text normalization for code-mixed input
│   ├── pipeline.py         # Unified analysis pipeline
│   ├── api.py              # FastAPI REST server
│   └── cli.py              # Command-line interface
├── tests/                  # Unit tests (26 passing)
├── scripts/
│   └── evaluate_lang_id.py # Evaluation with P/R/F1 metrics
├── data/
│   └── samples.json        # Labeled code-mixed sentences
└── examples/
    └── analyze_text.py     # Usage examples
```

## Motivation

Code-mixing is a natural phenomenon in multilingual societies like India, where speakers frequently alternate between Hindi and English. Most NLP tools are designed for monolingual text and perform poorly on code-mixed input. This toolkit addresses that gap with lightweight, practical tools for processing Hindi-English code-mixed text - a step toward better NLP support for Indian languages.

## References

- Cavnar, W. B., & Trenkle, J. M. (1994). *N-gram-based text categorization.*
- Das, A., & Gamback, B. (2014). *Identifying languages at the word level in code-mixed Indian social media text.*
- Khanuja, S., et al. (2020). *GLUECoS: An evaluation benchmark for code-switched NLP.*
- Kakwani, D., et al. (2020). *IndicNLPSuite: Monolingual corpora, evaluation benchmarks and pre-trained models for Indian languages.*

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
