# main.py — Entry point. CLI loop only; the actual logic resides elsewhere.

from context import maybe_compact
from agent import run_turn


SYSTEM_PROMPT = (
    "You are a friendly English tutor for Persian speakers. "
    "Reply in simple English matched to the learner's level; explain mistakes briefly in Persian. "
    "When the learner wants to remember a word, call save_word. "
    "For a quiz, call get_quiz_words and ask one word at a time. "
    "Do not call tools for ordinary conversation."
)


def main():
    context = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Agent ready. Ctrl-C to quit.\n")

    while True:
        try:
            user_input = input("you › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not user_input:
            continue

        context.append({"role": "user", "content": user_input})
        context = maybe_compact(context)

        answer = run_turn(context)
        print("\n agent ›", answer, "\n")


if __name__ == "__main__":
    main()