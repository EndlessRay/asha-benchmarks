"""Polarity-flip audit for omission criteria.

HealthBench penalty criteria are often phrased as omissions ("Fails to mention
X"). A judge that finds X in the answer must answer "not met"; a flip is the
judge marking the criterion met while its own explanation says X is present,
which deducts points for content the answer contains. Detected by a keyword
reading of the explanation; on a hand-checked sample the detector's
precision was about 0.80 to 0.88 (DNAi nonmaleficence study, 2026-10).
"""
from __future__ import annotations

import re

OMISSION_LEAD = re.compile(r"^(does not|doesn't|fails? to|omits?|lacks?|neglects?|no mention|never|did not)", re.I)
AFFIRMS = re.compile(
    r"(explicitly (mentions|states|recommends|includes|addresses|advises|notes|discusses)|"
    r"does (mention|include|address|provide|recommend|state|discuss|advise|note|emphasi[sz]e)|"
    r"fulfills|satisfies|meets the (requirement|criterion)|which (fulfills|addresses|satisfies)|"
    r"is (mentioned|included|addressed|recommended|stated)|clearly (mentions|states|recommends|includes|addresses))",
    re.I,
)
DENIES = re.compile(
    r"(does not|doesn't|fails? to|omits|lacks|no mention|neither|without mentioning|is not mentioned|"
    r"not (explicitly )?(mention|includ|address|provid|recommend|stat|discuss|emphasi)|but (does not|fails|omits|never)|only (mentions|briefly))",
    re.I,
)


def is_omission(criterion: str) -> bool:
    return bool(OMISSION_LEAD.match(criterion.strip()))


def is_flip(criterion: str, met: bool | None, explanation: str) -> bool:
    if not met or not is_omission(criterion):
        return False
    e = explanation or ""
    return bool(AFFIRMS.search(e)) and not DENIES.search(e)
