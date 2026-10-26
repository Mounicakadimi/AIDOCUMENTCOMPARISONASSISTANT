
import os
import difflib
from dotenv import load_dotenv

load_dotenv()

MAX_CHARS = 30000


def create_summary(text, title):
    text = " ".join(text.split())

    if len(text) > 900:
        text = text[:900].rsplit(" ", 1)[0] + "..."

    return f"{title} summary:\n{text}"


def compare_documents(text_a, text_b):
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    common_words = sorted(words_a & words_b)
    unique_a = sorted(words_a - words_b)
    unique_b = sorted(words_b - words_a)

    all_words = words_a | words_b

    overlap = (
        len(words_a & words_b) / len(all_words) * 100
        if all_words else 0
    )

    similarity = (
        difflib.SequenceMatcher(
            None,
            text_a.lower(),
            text_b.lower(),
            autojunk=False
        ).ratio() * 100
    )

    differences = "\n".join(
        list(difflib.unified_diff(
            text_a.splitlines(),
            text_b.splitlines(),
            fromfile="Document A",
            tofile="Document B",
            lineterm=""
        ))[:250]
    ) or "No line-by-line differences found."

    summary_a = create_summary(text_a, "Document A")
    summary_b = create_summary(text_b, "Document B")

    comparison = (
        f"Text similarity: {similarity:.2f}%.\n"
        f"Shared unique words: {len(common_words)}.\n"
        f"Words unique to Document A: {len(unique_a)}.\n"
        f"Words unique to Document B: {len(unique_b)}.\n"
        "Check the line differences for changed dates, "
        "names, numbers, and other details."
    )

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai

            if max(len(text_a), len(text_b)) > MAX_CHARS:
                raise ValueError(
                    "Documents exceed the 30,000-character AI "
                    "limit. Use shorter documents or add chunking."
                )

            client = genai.Client(api_key=api_key)
            model = os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            )

            prompt = f"""
Compare the two documents carefully.

Return these sections:
SUMMARY_A:
SUMMARY_B:
COMPARISON:

Summarize each document separately.
Identify important similarities and differences.
Pay special attention to dates, names, and numbers.
Do not invent differences.
If the content is identical, say so.

DOCUMENT A:
{text_a}

DOCUMENT B:
{text_b}
"""

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            answer = (response.text or "").strip()

            if not answer:
                raise RuntimeError(
                    "The AI provider returned an empty response."
                )

            upper = answer.upper()

            if all(section in upper for section in [
                "SUMMARY_A:", "SUMMARY_B:", "COMPARISON:"
            ]):
                def get_section(start, end):
                    first = upper.find(start)
                    last = upper.find(end, first + len(start))

                    if first < 0 or last < 0:
                        return ""

                    return answer[
                        first + len(start):last
                    ].strip()

                summary_a = (
                    get_section("SUMMARY_A:", "SUMMARY_B:")
                    or summary_a
                )

                summary_b = (
                    get_section("SUMMARY_B:", "COMPARISON:")
                    or summary_b
                )

                comparison_start = upper.find("COMPARISON:")

                comparison = answer[
                    comparison_start + len("COMPARISON:"):
                ].strip() or comparison

            else:
                comparison = answer

        except Exception as error:
            comparison += (
                "\n\nAI analysis failed. Local comparison "
                "is still available. Check your API key and "
                f"network, then retry. Details: {error}"
            )

    return {
        "similarity": round(similarity, 2),
        "overlap": round(overlap, 2),
        "common_words": common_words[:120],
        "unique_a": unique_a[:120],
        "unique_b": unique_b[:120],
        "differences": differences,
        "summary_a": summary_a,
        "summary_b": summary_b,
        "comparison": comparison
    }
