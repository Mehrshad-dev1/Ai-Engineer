import json
import pathlib
import random

VOCAB_FILE = pathlib.Path("vocab.json")


def _load() -> list:
    if VOCAB_FILE.exists():
        return json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    return []


def save_word(word: str, meaning: str, example: str = "") -> str:
    """Save a new vocabulary word for the learner."""
    words = _load()
    if any(w["word"].lower() == word.lower() for w in words):
        return f"'{word}' is already saved."
    words.append({"word": word, "meaning": meaning, "example": example})
    VOCAB_FILE.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"Saved '{word}'."


def list_words() -> str:
    """List all saved vocabulary words."""
    words = _load()
    if not words:
        return "Vocabulary list is empty."
    return "\n".join(f"{w['word']}: {w['meaning']}" for w in words)


def get_quiz_words(n: int = 3) -> str:
    """Pick random saved words for a quiz."""
    words = _load()
    if not words:
        return "No words saved yet."
    return json.dumps(random.sample(words, min(n, len(words))), ensure_ascii=False)