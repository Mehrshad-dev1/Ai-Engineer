# main.py — Entry point. CLI loop only; the actual logic resides elsewhere.

from context import maybe_compact
from agent import run_turn


SYSTEM_PROMPT = (
    "You are a capable assistant with tools for math, files, "
    "web search, and the shell. Use them when they help."
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
        print("\nagent ›", answer, "\n")


if __name__ == "__main__":
    main()