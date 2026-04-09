"""Command-line interface for codemix-nlp."""

import argparse
import json
import sys

from codemix.pipeline import CodeMixPipeline


def main():
    parser = argparse.ArgumentParser(
        prog="codemix",
        description="Analyze Hindi-English code-mixed text",
    )
    parser.add_argument("text", nargs="?", help="Text to analyze (or use --stdin)")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--transformer",
        action="store_true",
        help="Use transformer model for sentiment (requires download)",
    )
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read().strip()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    pipeline = CodeMixPipeline(use_transformer_sentiment=args.transformer)
    result = pipeline.analyze(text)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        _print_result(result)


def _print_result(result):
    print(f"\n  Input:      {result.original}")
    print(f"  Normalized: {result.normalized}")
    print()

    # Language tags
    print("  Word-level language tags:")
    for tw in result.tagged_words:
        tag = f"[{tw.lang}]"
        print(f"    {tw.word:15s} {tag:8s} (conf: {tw.confidence:.2f})")
    print()

    # Sentiment
    s = result.sentiment
    print(f"  Sentiment:  {s.label.value} (score: {s.score:+.2f})")
    print()

    # Transliterations
    if result.transliterations:
        print("  Hindi words → Devanagari:")
        for tr in result.transliterations:
            print(f"    {tr.original:15s} → {tr.devanagari}")
        print()

    # Stats
    st = result.stats
    print(f"  Stats: {st['hindi_words']} Hindi, {st['english_words']} English, "
          f"{st['other']} other | CMI: {st['code_mixing_index']:.2f}")
    print()


if __name__ == "__main__":
    main()
