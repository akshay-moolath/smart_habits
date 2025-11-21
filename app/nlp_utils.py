def compute_sentiment_simple(text: str) -> float:
    text = text.lower()
    positive = sum(1 for w in ("good","happy","great","love","nice","awesome","energized") if w in text)
    negative = sum(1 for w in ("sad","bad","angry","hate","tired","stressed","lonely") if w in text)
    total = positive + negative
    if total == 0:
        return 0.0
    return (positive - negative) / total
