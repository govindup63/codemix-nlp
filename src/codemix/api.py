"""
FastAPI REST API for the codemix-nlp toolkit.

Endpoints:
    POST /analyze         — Full pipeline analysis
    POST /detect-language  — Language identification only
    POST /transliterate    — Romanized Hindi to Devanagari
    POST /sentiment        — Sentiment analysis only
"""

from fastapi import FastAPI
from pydantic import BaseModel

from codemix.lang_id import create_default_detector
from codemix.pipeline import CodeMixPipeline
from codemix.sentiment import LexiconSentiment
from codemix.transliterate import Transliterator

app = FastAPI(
    title="CodeMix NLP API",
    description="NLP toolkit for analyzing Hindi-English code-mixed text",
    version="0.1.0",
)

pipeline = CodeMixPipeline()
detector = create_default_detector()
transliterator = Transliterator()
sentiment = LexiconSentiment()


class TextInput(BaseModel):
    text: str

class BatchInput(BaseModel):
    texts: list[str]


@app.post("/analyze")
def analyze(body: TextInput):
    """Run full analysis pipeline on code-mixed text."""
    result = pipeline.analyze(body.text)
    return result.to_dict()


@app.post("/analyze/batch")
def analyze_batch(body: BatchInput):
    """Analyze multiple texts in one request."""
    results = pipeline.analyze_batch(body.texts)
    return [r.to_dict() for r in results]


@app.post("/detect-language")
def detect_language(body: TextInput):
    """Identify language of each word in the input."""
    tagged = detector.tag_sentence(body.text)
    return {
        "words": [
            {"word": tw.word, "lang": tw.lang, "confidence": tw.confidence}
            for tw in tagged
        ]
    }


@app.post("/transliterate")
def transliterate(body: TextInput):
    """Transliterate Romanized Hindi to Devanagari."""
    result = transliterator.transliterate(body.text)
    return {"original": result.original, "devanagari": result.devanagari}


@app.post("/sentiment")
def analyze_sentiment(body: TextInput):
    """Analyze sentiment of code-mixed text."""
    result = sentiment.analyze(body.text)
    return {
        "label": result.label.value,
        "score": result.score,
        "details": result.details,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
