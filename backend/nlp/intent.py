import spacy

_nlp = None

QUESTION_WORDS = {"what", "why", "how", "when", "where", "who", "which"}
EXPLAIN_KEYWORDS = {"explain", "describe", "elaborate", "tell me about"}
QUIZ_KEYWORDS = {"quiz", "test", "question me", "mcq", "practice"}
EVALUATE_KEYWORDS = {"check", "evaluate", "is this right", "my answer is"}


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def classify_intent(message: str) -> str:
    text = message.lower().strip()

    if any(keyword in text for keyword in EVALUATE_KEYWORDS):
        return "EVALUATE"
    if any(keyword in text for keyword in QUIZ_KEYWORDS):
        return "QUIZ"
    if any(keyword in text for keyword in EXPLAIN_KEYWORDS):
        return "EXPLAIN"

    nlp = get_nlp()
    doc = nlp(text)
    first_token = doc[0].text.lower() if len(doc) > 0 else ""
    if first_token in QUESTION_WORDS or text.endswith("?"):
        return "ASK"

    if any(text.startswith(word) for word in QUESTION_WORDS):
        return "ASK"

    return "ASK"
