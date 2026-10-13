"""Prompt templates and output parsing for each step of the simulation."""

from __future__ import annotations

import re

from .case import CASE_FACTS
from .personas import PERSONAS, PERSONA_ORDER

FIRST_FIELDS = ["Position", "Concern", "Condition for reconsidering", "Next action"]
DISCUSSION_FIELDS = ["Responding to", "Response", "Position now", "Change in position"]
FINAL_FIELDS = FIRST_FIELDS + ["Change since first reaction"]


def system_prompt(pid: str) -> str:
    """Persona system prompt: shared case facts + ONLY this persona's profile."""
    p = PERSONAS[pid]
    return f"""You are role-playing {p['name']} ({p['role']}) in a business-school stakeholder \
simulation about Linden Compute's proposed third data centre.

Rules:
- Stay in character as {p['name']}. Speak in the first person, plainly, as this person would \
in a real meeting with the executive team.
- Base everything on the shared case facts and your own profile. Do not invent new facts \
(numbers, events, agreements, documents). If you rely on something not in the case, say \
briefly that it is your assumption.
- You only know other people through the case facts and what they say in the meeting. You \
have not seen their private profiles.
- Be realistic: you may support, oppose, stay undecided or change your mind, but only for \
reasons that follow from your interests, history and personality.
- Follow the requested output format exactly and respect the word limit.

=== SHARED CASE FACTS ===
{CASE_FACTS}
=== YOUR PROFILE ({p['name']}) ===
{p['profile']}"""


def _format_block(fields: list[str]) -> str:
    return "\n".join(f"{f}: ..." for f in fields)


def first_reaction_prompt(proposal: str) -> str:
    return f"""The executive team presents its proposal for discussion.

=== ORIGINAL PROPOSAL ===
{proposal}
You have NOT seen anyone else's reaction. Give your first reaction in UNDER 100 WORDS in \
total, using exactly these four labelled lines:
{_format_block(FIRST_FIELDS)}

- Position: your overall stance on the proposal as it stands.
- Concern: your single most important concern.
- Condition for reconsidering: what would have to change for you to move your position.
- Next action: what you will most likely do next."""


def label(pid: str) -> str:
    p = PERSONAS[pid]
    return f"{p['name']} ({p['role']})"


def format_round(replies: dict[str, str]) -> str:
    parts = []
    for pid in PERSONA_ORDER:
        if pid in replies and replies[pid]:
            parts.append(f"--- {label(pid)} ---\n{replies[pid].strip()}")
    return "\n\n".join(parts)


def discussion_history(first: dict[str, str], exchanges: list[dict]) -> str:
    text = "=== FIRST REACTIONS (collected independently) ===\n" + format_round(first)
    for i, ex in enumerate(exchanges, start=1):
        text += f"\n\n=== DISCUSSION EXCHANGE {i} ==="
        if ex.get("question"):
            text += f"\nClarifying question from the executive team: {ex['question']}"
        text += "\n" + format_round(ex.get("replies", {}))
    return text


def discussion_prompt(pid: str, proposal: str, first: dict[str, str],
                      previous: list[dict], number: int, question: str = "") -> str:
    name = PERSONAS[pid]["name"]
    q_part = ""
    fields = list(DISCUSSION_FIELDS)
    if question.strip():
        q_part = (f"\nThe executive team also asks everyone a clarifying question (the proposal "
                  f"itself is unchanged): \"{question.strip()}\"\n"
                  f"Answer it briefly in an extra line labelled 'Answer to question'.\n")
        fields.insert(2, "Answer to question")
    return f"""This is discussion exchange {number} of the stakeholder meeting. The proposal is \
UNCHANGED:

=== ORIGINAL PROPOSAL ===
{proposal}
Everything said so far:

{discussion_history(first, previous)}
{q_part}
Now respond as {name} to ONE specific point made by SOMEONE ELSE (not yourself). Name the \
person and the point. You may agree, push back, ask them something, or offer a trade. Then \
state your position now and explain any change since your last statement (or say "No \
change" and why). Keep it UNDER 120 WORDS, using exactly these labelled lines:
{_format_block(fields)}"""


def final_prompt(pid: str, original: str, revised: str, tradeoffs: str,
                 first: dict[str, str], exchanges: list[dict]) -> str:
    return f"""The executive team has listened to the discussion and now presents a REVISED \
proposal. Compare it with the original and with what you said earlier.

=== ORIGINAL PROPOSAL ===
{original}
=== REVISED PROPOSAL ===
{revised.strip()}

=== TRADE-OFFS THE EXECUTIVE TEAM SAYS IT ACCEPTS ===
{tradeoffs.strip() or "(none stated)"}

=== DISCUSSION HISTORY ===
{discussion_history(first, exchanges)}

Give your FINAL reaction to the revised proposal in UNDER 100 WORDS, using exactly these \
labelled lines:
{_format_block(FINAL_FIELDS)}

Be honest: if the revision does not address your concern, say so. Do not accept promises \
that are vague or that the case gives you no reason to trust."""


ANALYST_SYSTEM = """You are a neutral, sceptical teaching assistant reviewing an AI stakeholder \
simulation for a business-school assignment. You are not one of the stakeholders. Be concise \
and concrete. Remember that AI personas can simply echo the assumptions written into their \
profiles; point this out where relevant."""


def analyst_prompt(original: str, revised: str, first: dict[str, str],
                   exchanges: list[dict], final: dict[str, str]) -> str:
    return f"""=== ORIGINAL PROPOSAL ===
{original}
=== REVISED PROPOSAL ===
{revised}

{discussion_history(first, exchanges)}

=== FINAL REACTIONS ===
{format_round(final)}

Compare the final reactions with the first reactions. In under 250 words, using these \
headings:
Shifts: for each persona, one line on how and why the position moved (or did not).
Most influential exchange: which exchange point most changed positions, and why.
Unresolved disagreement: the most important disagreement still open.
Claims to check with real stakeholders: 2-3 claims the simulation relied on that should be \
verified with the real people, noting which ones came from profile assumptions.
Echo risk: where the personas may only be repeating the team's own assumptions."""


def parse_fields(text: str, fields: list[str]) -> dict[str, str]:
    """Extract 'Label: value' fields from a reply. Missing fields -> ''."""
    if not text:
        return {f: "" for f in fields}
    labels = "|".join(re.escape(f) for f in sorted(fields, key=len, reverse=True))
    pattern = re.compile(
        rf"^[\s*_#>-]*(?:\*\*)?({labels})(?:\*\*)?\s*[:\-–]\s*(?:\*\*)?",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    out = {f: "" for f in fields}
    lookup = {f.lower(): f for f in fields}
    for i, m in enumerate(matches):
        key = lookup[m.group(1).lower()]
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        value = text[m.end():end].strip().strip("*").strip()
        if not out[key]:
            out[key] = value
    return out


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text or ""))
