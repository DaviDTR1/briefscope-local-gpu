"""
Token counting using tiktoken (cl100k_base — good approximation for all providers).
"""
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_enc.encode(text, disallowed_special=()))


def count_messages_tokens(messages: list[dict]) -> int:
    """Approximate token count for a list of {role, content} dicts."""
    total = 0
    for m in messages:
        total += 4  # per-message overhead
        total += count_tokens(m.get("content", ""))
    return total
