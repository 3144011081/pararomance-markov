"""
markov_model.py
----------------
A small, dependency-free, word-level Markov chain text generator.

Concept (matches the notebook's intro to Markov chains):
- We build a "transition table": for every sequence of N previous words
  (the "state", where N = order), we record which words followed it in
  the training data, and how often.
- To generate new text, we start from a random valid starting state and
  repeatedly pick a "next word" at random, weighted by how often it
  followed that state in the training data, until we hit an end-of-title
  marker.

BEGIN and END are special sentinel tokens so the chain knows how titles
really start and end (instead of drifting into the middle of a title).
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

BEGIN = "___BEGIN___"
END = "___END___"


def clean_title(raw: str) -> str:
    """Normalize one raw dataset line into a clean title string."""
    title = raw.strip()
    # The scraped dataset truncates long titles with a trailing "..."
    # (and sometimes a dangling partial word before it). Strip that off
    # so we don't train the model to think titles end mid-word.
    title = re.sub(r"\.\.\.$", "", title).strip()
    # Collapse internal whitespace.
    title = re.sub(r"\s+", " ", title)
    return title


def load_titles(path: str | Path) -> list[str]:
    path = Path(path)
    titles = []
    for line in path.read_text(encoding="utf-8").splitlines():
        title = clean_title(line)
        if title:
            titles.append(title)
    return titles


class MarkovChain:
    """Word-level Markov chain of a given order (state size)."""

    def __init__(self, order: int = 2):
        if order < 1:
            raise ValueError("order must be >= 1")
        self.order = order
        # state (tuple of `order` words) -> {next_word: count}
        self.table: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # ---------- training ----------

    def fit(self, texts: list[str]) -> "MarkovChain":
        for text in texts:
            words = text.split(" ")
            if not words:
                continue
            padded = [BEGIN] * self.order + words + [END]
            for i in range(len(padded) - self.order):
                state = tuple(padded[i : i + self.order])
                nxt = padded[i + self.order]
                self.table[state][nxt] += 1
        return self

    # ---------- generation ----------

    def _weighted_choice(self, options: dict[str, int]) -> str:
        words = list(options.keys())
        weights = list(options.values())
        return random.choices(words, weights=weights, k=1)[0]

    def generate(self, max_words: int = 25, tries: int = 50) -> str | None:
        """Generate one title. Returns None if it fails after `tries` attempts
        (can happen with very high order + small datasets)."""
        start_states = [s for s in self.table if s[0] == BEGIN or BEGIN in s]
        # Prefer true sentence-start states (all BEGIN tokens).
        true_starts = [s for s in self.table if all(tok == BEGIN for tok in s)]
        candidates = true_starts or start_states or list(self.table.keys())
        if not candidates:
            return None

        for _ in range(tries):
            state = random.choice(candidates)
            words: list[str] = [w for w in state if w != BEGIN]
            for _ in range(max_words):
                options = self.table.get(state)
                if not options:
                    break
                nxt = self._weighted_choice(options)
                if nxt == END:
                    if words:
                        return " ".join(words)
                    break
                words.append(nxt)
                state = tuple((*state[1:], nxt))
            # ran out of max_words without hitting END; still usable
            if words:
                return " ".join(words)
        return None

    def generate_many(self, n: int, max_words: int = 25, unique: bool = True) -> list[str]:
        results: list[str] = []
        seen = set()
        attempts = 0
        max_attempts = n * 20 + 50
        while len(results) < n and attempts < max_attempts:
            attempts += 1
            title = self.generate(max_words=max_words)
            if not title:
                continue
            if unique and title.lower() in seen:
                continue
            seen.add(title.lower())
            results.append(title)
        return results

    # ---------- persistence ----------

    def to_json(self) -> str:
        serializable = {
            "order": self.order,
            "table": {
                " | ".join(state): dict(counts) for state, counts in self.table.items()
            },
        }
        return json.dumps(serializable)

    @classmethod
    def from_json(cls, data: str) -> "MarkovChain":
        obj = json.loads(data)
        chain = cls(order=obj["order"])
        for state_key, counts in obj["table"].items():
            state = tuple(state_key.split(" | "))
            chain.table[state] = defaultdict(int, counts)
        return chain

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "MarkovChain":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))
