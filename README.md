# codemix-nlp

NLP toolkit for analyzing Hindi-English code-mixed text. Handles the unique challenges of **code-switching** — where speakers alternate between Hindi (often Romanized) and English within a sentence, as commonly seen in Indian social media, messaging, and spoken language.

## Features

- **Word-level Language Identification** — Character n-gram frequency profiles distinguish Romanized Hindi from English (based on Cavnar & Trenkle, 1994)
- **Romanized Hindi → Devanagari Transliteration** — Rule-based phonetic mapping with support for aspirated consonants, vowel matras, and schwa deletion
- **Bilingual Sentiment Analysis** — Lexicon-based (lightweight) and transformer-based (XLM-RoBERTa) approaches
- **Text Normalization** — Handles character repetition, slang expansion, and mixed-script cleanup
- **Code-Mixing Index (CMI)** — Quantifies the degree of language mixing in a sentence
- **REST API** — FastAPI server for all features
- **CLI** — Command-line tool for quick analysis

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
result = pipeline.analyze("yaar ye movie bahut amazing thi")

print(result.sentiment.label)      # positive
print(result.stats)                # {'hindi_words': 4, 'english_words': 2, ...}
for tw in result.tagged_words:
    print(f"{tw.word:15s} [{tw.lang}] ({tw.confidence:.2f})")
```

### CLI

```bash
codemix "bhai party mein bahut maza aaya, awesome food tha"
codemix --json "aaj ka weather bahut pleasant hai"
echo "bahut accha kaam kiya" | codemix --stdin
```

### REST API

```bash
uvicorn codemix.api:app --reload

# Analyze text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "yaar ye movie bahut amazing thi"}'

# Language detection only
curl -X POST http://localhost:8000/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "bhai aaj ka match dekha? India ne accha khela"}'
```

## Modules

### Language Identification (`codemix.lang_id`)

Two-stage approach:
1. **Script detection** — Unicode range checks separate Devanagari from Latin script
2. **N-gram classification** — For Latin-script words, character n-gram frequency profiles distinguish Romanized Hindi from English using cosine similarity

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

## Evaluation

```bash
python scripts/evaluate_lang_id.py
```

## Running Tests

```bash
pytest
```

## Motivation

Code-mixing is a natural phenomenon in multilingual societies like India, where speakers frequently alternate between Hindi and English. Most NLP tools are designed for monolingual text and perform poorly on code-mixed input. This toolkit addresses that gap with lightweight, practical tools for processing Hindi-English code-mixed text — a step toward better NLP support for Indian languages.

## References

- Cavnar, W. B., & Trenkle, J. M. (1994). N-gram-based text categorization.
- Das, A., & Gambäck, B. (2014). Identifying languages at the word level in code-mixed Indian social media text.
- Khanuja, S., et al. (2020). GLUECoS: An evaluation benchmark for code-switched NLP.
- Kakwani, D., et al. (2020). IndicNLPSuite: Monolingual corpora, evaluation benchmarks and pre-trained models for Indian languages.

## License

MIT
