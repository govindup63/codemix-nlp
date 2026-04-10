"""
Example: Analyzing Hindi-English code-mixed text with codemix-nlp.

Run: python examples/analyze_text.py
"""

from codemix.pipeline import CodeMixPipeline


def main():
    pipeline = CodeMixPipeline()

    # Iconic Bollywood Hinglish dialogues - perfect test cases for code-mixing
    samples = [
        # 3 Idiots
        "Life is a race, if you don't run fast, you will be like a broken undaa",
        "Ajeeb desh hai hamara, pizza tees minute mein pahuchne ki guarantee hai, lekin ambulance?",
        # Yeh Jawaani Hai Deewani
        "Shaadi is dal chawal for pachaas saal till you die, arre life mein thoda bahut keema pav bhi hona chahiye nah",
        # General code-mixed examples
        "bhai aaj ka match dekha? India ne bahut accha khela",
        "coding seekh raha hoon, Python bahut interesting language hai",
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
