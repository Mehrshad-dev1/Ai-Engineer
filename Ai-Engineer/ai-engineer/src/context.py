# context.py — manage context window length

from config import CLIENT, MODEL, CONTEXT_WINDOW, COMPACT_THRESHOLD


def estimate_tokens(context: list) -> int:
    ''' about 3.75 charcter = 1 token (approximate)'''
    return int(sum(len(str(i)) for i in context) / 3.75)


def compact(context: list) -> list:
    first, body = context[0], context[1:]
    transcript = "\n\n".join(str(i) for i in body)
    summary = CLIENT.responses.create(
        model=MODEL,
        input="Summarize this conversation, preserving decisions, facts, and open tasks:\n\n" + transcript,
    ).output_text
    return [first, {"role": "user", "content": f"[SUMMARY OF EARLIER CONVERSATION]\n{summary}"}]


def maybe_compact(context: list) -> list:
    if estimate_tokens(context) > CONTEXT_WINDOW * COMPACT_THRESHOLD:
        print(" … context over 80%, compacting")
        return compact(context)
    return context
