"""Link publication authors to visible team profiles without changing their names.

Names are compared after removing accents and punctuation. A publication may
abbreviate given names to initials, but every remaining name token must agree.
Use a member's optional ``authorNames`` list for alternate full names or omitted
surnames; the renderer never guesses those. Ambiguous matches remain plain text.
"""

from __future__ import annotations

from html import escape
import re
import unicodedata


_HONORIFICS = {"dr", "dra", "prof", "professor"}


def name_tokens(name: str) -> tuple[str, ...]:
    """Normalize accents, case, punctuation and common academic prefixes."""
    normalized = unicodedata.normalize("NFKD", name.casefold())
    plain = "".join(character for character in normalized
                    if not unicodedata.combining(character))
    tokens = re.findall(r"[a-z]+", plain)
    while tokens and tokens[0] in _HONORIFICS:
        tokens.pop(0)
    return tuple(tokens)


def _matches(author: tuple[str, ...], name: tuple[str, ...]) -> bool:
    """Require a complete surname and exact words, allowing author initials."""
    if not author or len(author) != len(name):
        return False
    # A lone name or an all-initial name does not establish an identity.
    if len(author) < 2 or len(author[-1]) == 1:
        return False
    return all(candidate == source or
               (len(candidate) == 1 and source.startswith(candidate))
               for candidate, source in zip(author, name))


def _member_names(team: dict) -> list[tuple[dict, tuple[tuple[str, ...], ...]]]:
    return [
        (member, tuple(name_tokens(name) for name in
                       [member["name"], *member.get("authorNames", [])]))
        for member in team.get("members", [])
        if member.get("visible", True)
    ]


def _matched_authors(authors: list[str], team: dict) -> list[dict | None]:
    """Share conservative identity resolution between display and validation."""
    members = _member_names(team)
    matches = []
    for author in authors:
        tokens = name_tokens(author)
        candidates = [member for member, names in members
                      if any(_matches(tokens, name) for name in names)]
        matches.append(candidates[0] if len(candidates) == 1 else None)
    return matches


def team_member_ids(authors: list[str], team: dict) -> set[str]:
    """Return distinct, unambiguously matched visible team member IDs.

    Repeating an author or using multiple byline variants for the same person
    counts once. Matching is identical to the linked author display, including
    editable aliases, ambiguity handling and the exclusion of invisible members.
    """
    return {member["id"] for member in _matched_authors(authors, team)
            if member is not None}


def authored_names(authors: list[str], team: dict) -> str:
    """Return comma-separated authors, linking uniquely matched team members.

    Source authors are never rewritten or reordered, and ``team`` is not mutated.
    ``authorNames`` aliases use the same normalization and initial matching as
    member names. Invisible profiles and ambiguous identities are not linked.
    """
    rendered = []
    for author, member in zip(authors, _matched_authors(authors, team)):
        label = escape(author, quote=True)
        if member is not None:
            target = escape(member["id"], quote=True)
            label = f'<a class="team-author" href="team.html#{target}">{label}</a>'
        rendered.append(label)
    return ", ".join(rendered)
