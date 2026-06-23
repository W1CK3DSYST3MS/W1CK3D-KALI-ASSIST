"""Beginner glossary (Blueprint §9). Terms surfaced inline on first use.

Modules contribute terms; the registry merges them. The front-end asks the
glossary whether a term has been shown yet (first-use surfacing).
"""

from __future__ import annotations

from .models import GlossaryTerm


class Glossary:
    def __init__(self) -> None:
        self._terms: dict[str, str] = {}
        self._seen: set[str] = set()

    def add(self, term: str, definition: str) -> None:
        self._terms[term] = definition

    def add_many(self, terms: list[GlossaryTerm]) -> None:
        for t in terms:
            self._terms[t.term] = t.definition

    def define(self, term: str) -> str | None:
        return self._terms.get(term)

    def first_use(self, term: str) -> str | None:
        """Return the definition the FIRST time a term is requested, else None."""
        if term in self._seen:
            return None
        self._seen.add(term)
        return self._terms.get(term)

    def reset_seen(self) -> None:
        self._seen.clear()

    def __contains__(self, term: str) -> bool:
        return term in self._terms

    def __len__(self) -> int:
        return len(self._terms)
