"""Pinned judge profiles.

A profile fixes everything that changes a grade: model id, endpoint type,
system message, temperature, reasoning effort, token budget, and the
rubric-item rendering. Changing any of these is a new profile with a new
name, never an edit. The validation status of each profile (agreement with
physicians, delta replication, self-preference, missing grades, polarity) is
in VALIDATION.md; profiles marked "unvalidated" are tooling, not results.
"""
from __future__ import annotations

from dataclasses import dataclass, field

GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
OPENAI_BASE = "https://api.openai.com/v1"


@dataclass(frozen=True)
class Profile:
    name: str
    model: str
    base_url: str
    api_key_env: tuple[str, ...]
    temperature: float | None = 0.0
    system: str | None = None
    reasoning_effort: str | None = None
    max_tokens: int = 2048
    show_points: bool = True  # simple-evals renders the rubric item as "[points] criterion"
    status: str = "unvalidated"
    notes: str = ""
    extra: dict = field(default_factory=dict)


PROFILES: dict[str, Profile] = {
    # Low-cost hosted judge (Google AI Studio or any OpenAI-compatible proxy).
    "flashlite-v1": Profile(
        name="flashlite-v1",
        model="gemini-3.1-flash-lite",
        base_url=GEMINI_OPENAI_BASE,
        api_key_env=("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        temperature=0.0,
        max_tokens=800,
        status="passed 2026-10-28 (screening and sensitivity; see VALIDATION.md)",
        notes="Google Gemini 3.1 Flash-Lite, provider-default thinking.",
    ),
    # Open-weight judge served locally (vLLM, SGLang, Ollama, llama.cpp server) or by any host.
    "oss120b-v1": Profile(
        name="oss120b-v1",
        model="gpt-oss-120b",
        base_url="http://localhost:8000/v1",
        api_key_env=("HBJUDGE_LOCAL_API_KEY",),
        temperature=0.0,
        reasoning_effort="low",
        max_tokens=800,
        status="not passed alone 2026-10-28 (professional holdout, polarity); validated as a panel member with flashlite-v1",
        notes="openai/gpt-oss-120b (Apache-2.0 weights), reasoning effort low. Set --base-url and --model to your server's values.",
    ),
    "oss20b-v1": Profile(
        name="oss20b-v1",
        model="gpt-oss-20b",
        base_url="http://localhost:8000/v1",
        api_key_env=("HBJUDGE_LOCAL_API_KEY",),
        temperature=0.0,
        reasoning_effort="low",
        notes="openai/gpt-oss-20b, fits a single 16-24 GB GPU.",
    ),
    # Reference grader with the exact simple-evals call settings, for calibration runs.
    "gpt41-reference": Profile(
        name="gpt41-reference",
        model="gpt-4.1-2025-04-14",
        base_url=OPENAI_BASE,
        api_key_env=("OPENAI_API_KEY",),
        temperature=0.5,
        system="You are a helpful assistant.",
        max_tokens=2048,
        status="reference",
        notes="HealthBench's official grader with simple-evals settings (system message, temperature 0.5).",
    ),
}
