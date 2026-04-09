"""
Example: Analyzing Hindi-English code-mixed text with codemix-nlp.

Run: python examples/analyze_text.py
"""

from codemix.pipeline import CodeMixPipeline


def main():
    pipeline = CodeMixPipeline()

    samples = [
        "yaar ye movie bahut amazing thi",
        "kya bakwas hai ye, totally waste of time",
        "bhai aaj ka match dekha? India ne bahut accha khela",
        "mera new phone ka camera quality shandar hai, love it",
        "traffic itna horrible hai ki har roz late ho jaata hoon",
    ]

    for text in samples:
        result = pipeline.analyze(text)

        print(f"Input: {text}")
        print(f"Sentiment: {result.sentiment.label.value} ({result.sentiment.score:+.2f})")
        print(f"Hindi: {result.stats['hindi_words']}, English: {result.stats['english_words']}, "
              f"CMI: {result.stats['code_mixing_index']:.2f}")

        if result.transliterations:
            hindi_parts = " | ".join(
                f"{t.original} → {t.devanagari}" for t in result.transliterations[:5]
            )
            print(f"Transliterations: {hindi_parts}")

        print("-" * 60)


if __name__ == "__main__":
    main()
