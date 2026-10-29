"""OpenAI-compatible chat client with bounded retries and usage accounting."""
from __future__ import annotations

import json
import os
import random
import re
import threading
import time

import httpx

from .judges import Profile

TRANSIENT = {408, 409, 425, 429, 500, 502, 503, 504, 529}


def parse_grade(text: str) -> tuple[bool | None, str]:
    """(criteria_met, explanation). None when the output has no boolean verdict.

    Unlike some pipelines, an unparsable reply is never turned into a verdict:
    it is retried, and if it stays unparsable it is reported as missing.
    """
    s = (text or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    start, end = s.find("{"), s.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(s[start : end + 1])
            met = obj.get("criteria_met")
            if isinstance(met, bool):
                return met, str(obj.get("explanation", ""))
        except json.JSONDecodeError:
            pass
    return None, ""


class Client:
    def __init__(self, profile: Profile, base_url: str | None = None, model: str | None = None, api_key: str | None = None, timeout: float = 180.0):
        self.p = profile
        self.base_url = (base_url or profile.base_url).rstrip("/")
        self.model = model or profile.model
        self.api_key = api_key or next((os.environ[k] for k in profile.api_key_env if os.environ.get(k)), "")
        self.http = httpx.Client(timeout=timeout)
        self.lock = threading.Lock()
        self.usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "transient_retries": 0}

    def _body(self, prompt: str) -> dict:
        msgs = ([{"role": "system", "content": self.p.system}] if self.p.system else []) + [{"role": "user", "content": prompt}]
        body = {"model": self.model, "messages": msgs}
        if self.model.startswith(("gpt-5", "o3", "o4")):
            body["max_completion_tokens"] = self.p.max_tokens
        else:
            body["max_tokens"] = self.p.max_tokens
            if self.p.temperature is not None:
                body["temperature"] = self.p.temperature
        if self.p.reasoning_effort:
            body["reasoning_effort"] = self.p.reasoning_effort
        body.update(self.p.extra)
        return body

    def complete(self, prompt: str, max_transient_retries: int = 6) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        last = None
        for attempt in range(max_transient_retries + 1):
            try:
                r = self.http.post(f"{self.base_url}/chat/completions", headers=headers, json=self._body(prompt))
                if r.status_code in TRANSIENT:
                    raise RuntimeError(f"HTTP {r.status_code}")
                r.raise_for_status()
                data = r.json()
                u = data.get("usage") or {}
                with self.lock:
                    self.usage["calls"] += 1
                    self.usage["prompt_tokens"] += int(u.get("prompt_tokens") or 0)
                    self.usage["completion_tokens"] += int(u.get("completion_tokens") or 0)
                return data["choices"][0]["message"].get("content") or ""
            except httpx.HTTPStatusError:
                raise
            except Exception as e:  # noqa: BLE001 (transient: network, 429, 5xx)
                last = e
                with self.lock:
                    self.usage["transient_retries"] += 1
                time.sleep(min(30.0, 1.5 * 2**attempt) * (1 + 0.3 * random.random()))
        raise RuntimeError(f"giving up after {max_transient_retries} transient retries: {last}")

    def grade(self, prompt: str, max_attempts: int = 5) -> tuple[bool | None, str, int]:
        """Retry unparsable replies up to max_attempts; returns (met, explanation, attempts)."""
        for attempt in range(1, max_attempts + 1):
            met, expl = parse_grade(self.complete(prompt))
            if met is not None:
                return met, expl, attempt
        return None, "", max_attempts
