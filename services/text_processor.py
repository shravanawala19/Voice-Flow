from __future__ import annotations

import re


PUNCTUATION_PHRASES: dict[tuple[str, ...], str] = {
    ("question", "mark"): "?",
    ("exclamation", "mark"): "!",
    ("exclamation", "point"): "!",
    ("period",): ".",
    ("full", "stop"): ".",
    ("comma",): ",",
    ("colon",): ":",
    ("semicolon",): ";",
    ("dash",): "-",
    ("hyphen",): "-",
    ("open", "parenthesis"): "(",
    ("close", "parenthesis"): ")",
    ("new", "line"): "\n",
    ("new", "paragraph"): "\n\n",
}

QUESTION_STARTS = {
    "who",
    "what",
    "when",
    "where",
    "why",
    "how",
    "can",
    "could",
    "would",
    "should",
    "is",
    "are",
    "do",
    "does",
    "did",
}

GREETINGS = {"hello", "hi", "hey"}


class TextProcessor:
    def process(self, text: str, auto_punctuation: bool = True) -> str:
        text = " ".join(text.strip().split())
        if not text:
            return ""

        text = self._replace_spoken_punctuation(text)
        text = self._fix_spacing(text)
        if auto_punctuation:
            text = self._add_light_punctuation(text)
        return self._capitalize_sentences(text)

    def contains_wake_word(self, text: str, wake_word: str) -> bool:
        return wake_word.lower() in text.lower()

    def remove_wake_word(self, text: str, wake_word: str) -> str:
        pattern = re.compile(re.escape(wake_word), flags=re.IGNORECASE)
        return pattern.sub("", text, count=1).strip(" ,.")

    def _replace_spoken_punctuation(self, text: str) -> str:
        words = text.split()
        output: list[str] = []
        i = 0
        phrases = sorted(PUNCTUATION_PHRASES.items(), key=lambda item: len(item[0]), reverse=True)
        while i < len(words):
            lower_remaining = [word.lower().strip(".,?!") for word in words[i:]]
            matched = False
            for phrase, mark in phrases:
                if tuple(lower_remaining[: len(phrase)]) == phrase:
                    output.append(mark)
                    i += len(phrase)
                    matched = True
                    break
            if not matched:
                output.append(words[i])
                i += 1
        return " ".join(output)

    def _add_light_punctuation(self, text: str) -> str:
        words = text.split()
        if not words:
            return text
        lower_words = [word.lower().strip(".,?!") for word in words]

        if lower_words[0] in GREETINGS and len(words) > 3:
            words[0] = words[0].rstrip(",") + ","
            text = " ".join(words)

        if text[-1] not in ".?!":
            if lower_words[0] in QUESTION_STARTS:
                text += "?"
            else:
                text += "."
        return text

    def _capitalize_sentences(self, text: str) -> str:
        result: list[str] = []
        capitalize_next = True
        for char in text:
            if capitalize_next and char.isalpha():
                result.append(char.upper())
                capitalize_next = False
            else:
                result.append(char)
            if char in ".?!\n":
                capitalize_next = True
        return "".join(result)

    def _fix_spacing(self, text: str) -> str:
        text = re.sub(r"\s+([,.;:?!])", r"\1", text)
        text = re.sub(r"([(])\s+", r"\1", text)
        text = re.sub(r"\s+([)])", r"\1", text)
        text = re.sub(r"([,.;:?!])([^\s\n])", r"\1 \2", text)
        text = re.sub(r"\s+\n", "\n", text)
        text = re.sub(r"\n\s+", "\n", text)
        return text.strip()
