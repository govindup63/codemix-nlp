"""
Evaluate language identification accuracy on labeled data.

Uses a small hand-labeled evaluation set to compute precision, recall,
and F1-score for the character n-gram language identifier.
"""

from codemix.lang_id import create_default_detector

# Hand-labeled evaluation data: (word, true_lang)
EVAL_DATA = [
    # Hindi words (Romanized)
    ("bahut", "hi"), ("accha", "hi"), ("kaam", "hi"), ("zindagi", "hi"),
    ("duniya", "hi"), ("padhai", "hi"), ("khana", "hi"), ("hamesha", "hi"),
    ("isliye", "hi"), ("kyunki", "hi"), ("shayad", "hi"), ("zaroor", "hi"),
    ("samajh", "hi"), ("pareshani", "hi"), ("mushkil", "hi"),
    ("raha", "hi"), ("wala", "hi"), ("chahiye", "hi"), ("sakta", "hi"),
    ("matlab", "hi"),
    # English words
    ("beautiful", "en"), ("actually", "en"), ("sometimes", "en"),
    ("through", "en"), ("between", "en"), ("because", "en"),
    ("people", "en"), ("system", "en"), ("amazing", "en"),
    ("terrible", "en"), ("wonderful", "en"), ("fantastic", "en"),
    ("interesting", "en"), ("different", "en"), ("important", "en"),
    ("problem", "en"), ("solution", "en"), ("computer", "en"),
    ("together", "en"), ("understand", "en"),
    # Ambiguous / harder cases
    ("time", "en"), ("film", "en"), ("bus", "en"),
    ("log", "hi"), ("bas", "hi"), ("dil", "hi"),
]


def evaluate():
    detector = create_default_detector()

    correct = 0
    total = len(EVAL_DATA)
    tp = {"hi": 0, "en": 0}
    fp = {"hi": 0, "en": 0}
    fn = {"hi": 0, "en": 0}

    errors = []
    for word, true_lang in EVAL_DATA:
        pred = detector.predict(word)
        if pred.lang == true_lang:
            correct += 1
            tp[true_lang] += 1
        else:
            errors.append((word, true_lang, pred.lang, pred.confidence))
            fp[pred.lang] = fp.get(pred.lang, 0) + 1
            fn[true_lang] = fn.get(true_lang, 0) + 1

    accuracy = correct / total

    print(f"Language Identification Evaluation")
    print(f"{'=' * 45}")
    print(f"Total: {total} | Correct: {correct} | Accuracy: {accuracy:.1%}")
    print()

    for lang in ["hi", "en"]:
        precision = tp[lang] / (tp[lang] + fp[lang]) if (tp[lang] + fp[lang]) else 0
        recall = tp[lang] / (tp[lang] + fn[lang]) if (tp[lang] + fn[lang]) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
        print(f"  {lang.upper():>3s}: P={precision:.2f}  R={recall:.2f}  F1={f1:.2f}")

    if errors:
        print(f"\nMisclassified ({len(errors)}):")
        for word, true, pred, conf in errors:
            print(f"  {word:20s}  true={true}  pred={pred}  conf={conf:.3f}")


if __name__ == "__main__":
    evaluate()
