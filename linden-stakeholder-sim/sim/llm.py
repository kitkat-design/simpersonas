"""Minimal OpenRouter client.

Every persona reply is its own HTTP request with its own system prompt, so no
persona can see another persona's profile or (in Step 2) another reply.
"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, api_key: str | None, model: str, *, demo: bool = False,
                 temperature: float | None = None, max_tokens: int = 4000,
                 timeout: int = 180, app_url: str = "https://streamlit.io"):
        self.api_key = api_key
        self.model = model
        self.demo = demo
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.app_url = app_url

    # ------------------------------------------------------------------ calls
    def chat(self, system: str, user: str) -> str:
        if self.demo:
            return _demo_reply(system, user)
        if not self.api_key:
            raise LLMError("No OpenRouter API key. Add OPENROUTER_API_KEY to the app's secrets "
                           "or paste a key in the sidebar.")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": self.max_tokens,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_url,
            "X-Title": "Linden Compute Stakeholder Simulation",
        }
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                r = requests.post(OPENROUTER_URL, json=payload, headers=headers,
                                  timeout=self.timeout)
            except requests.RequestException as e:  # network problem: retry
                last_err = e
                time.sleep(2 * (attempt + 1))
                continue
            if r.status_code in (429, 500, 502, 503, 504):
                last_err = LLMError(f"OpenRouter returned {r.status_code}: {r.text[:300]}")
                time.sleep(3 * (attempt + 1))
                continue
            if r.status_code != 200:
                raise LLMError(f"OpenRouter returned {r.status_code}: {r.text[:500]}")
            data = r.json()
            if "error" in data:
                raise LLMError(f"OpenRouter error: {data['error']}")
            try:
                content = data["choices"][0]["message"]["content"] or ""
            except (KeyError, IndexError, TypeError):
                raise LLMError(f"Unexpected response: {str(data)[:500]}")
            content = content.strip()
            if not content:
                last_err = LLMError("The model returned an empty reply (it may have used its "
                                    "whole token budget on reasoning).")
                continue
            return content
        raise LLMError(str(last_err) if last_err else "Request failed.")

    def map(self, jobs: dict[str, tuple[str, str]]) -> dict[str, str | Exception]:
        """Run independent (system, user) jobs in parallel. Returns key -> text or Exception."""
        results: dict[str, str | Exception] = {}

        def run(key: str):
            system, user = jobs[key]
            try:
                return key, self.chat(system, user)
            except Exception as e:  # noqa: BLE001 - surface per-persona errors in the UI
                return key, e

        with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
            for key, value in pool.map(run, list(jobs)):
                results[key] = value
        return results


# --------------------------------------------------------------------- demo
def _demo_reply(system: str, user: str) -> str:
    """Offline placeholder so the whole flow can be tried without an API key."""
    m = re.search(r"role-playing (.+?) \(", system)
    who = m.group(1) if m else "Analyst"
    fields = re.findall(r"^([A-Z][A-Za-z ]+): \.\.\.$", user, re.MULTILINE)
    if not fields:
        return (f"[Demo mode] {who}: placeholder analysis. Switch off demo mode and add an "
                f"OpenRouter key to get real output.")
    return "\n".join(f"{f}: [demo] {who} - placeholder text for '{f.lower()}'."
                     for f in fields)
