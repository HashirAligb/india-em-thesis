"""
Agent pipeline for the Assumption Auditor section.

Pipeline: data_engine -> layer2 -> assumption_audit -> verdict_agents -> app.
Takes the AuditResult from assumption_audit.py, has Gemini explain it in plain
English, then fact-checks that text in Python. app.py calls run_pipeline()
when the user clicks "Generate narrative".

Architecture: each agent is a plain function -- same signature, chained in a
list so adding a third agent is one more list entry, not a rewrite.

  Agent signature:  (audit_result: AuditResult, prior_text: str = "") -> str
  Validator:        (audit_result, analysis_text) -> ValidationResult  [pure Python]

LLM provider is isolated in _llm_call().  Swap the provider by editing only
that function.  Current provider: Google Gemini via google-genai.
API key read from the GEMINI_API_KEY environment variable (a local .env file,
or Streamlit secrets when deployed). Never hardcoded.

Rules that cannot break:
  - Python computes every number in AuditResult.  Agents only explain it.
  - If any agent call fails, the deterministic verdict is unchanged.
  - The validator is pure Python, no LLM.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Callable, TypedDict

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.assumption_audit import AuditResult


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

AgentFn = Callable[[AuditResult, str], str]


class ValidationResult(TypedDict):
    passed: bool
    failures: list[str]
    warnings: list[str]


# ---------------------------------------------------------------------------
# Provider wrapper -- swap provider here only
# ---------------------------------------------------------------------------

def _llm_call(system: str, user: str, max_tokens: int = 600) -> str:
    """System and user prompts in, Gemini's reply text out.
    The only code that knows the LLM provider, so swapping providers means editing just this.
    Called by both agents; raises if GEMINI_API_KEY is missing, and run_pipeline() catches it."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Add it to your .env file: GEMINI_API_KEY=your_key"
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text.strip()


# ---------------------------------------------------------------------------
# Agent 1 -- Analysis
# ---------------------------------------------------------------------------

def agent_analysis(audit: AuditResult, prior_text: str = "") -> str:
    """Audit result in, a 3-4 paragraph plain-English explanation from Gemini out.
    The prompt passes only Python-computed facts and forbids new numbers or forecasts.
    First agent in run_pipeline(); its text is then fact-checked by validate_analysis()."""
    d = audit["nearest_downgrade"]
    blockers = audit["upgrade_blockers"]
    ps = audit["profile_stability"]

    system = (
        "You are an analyst explaining a quantitative framework result to a thesis reader. "
        "Explain only what the Python scoring model found -- do not add your own view. "
        "Write in plain English. "
        "Do not use em dashes. "
        "Do not add numbers, indicators, or claims not in the audit result you receive. "
        "Do not make investment recommendations. "
        "Do not say the downgrade scenario is likely or imminent -- "
        "it is a model boundary, not a forecast."
    )

    user = f"""Explain this assumption audit result in 3-4 short paragraphs for a thesis appendix.

AUDIT RESULT (Python-computed, authoritative):
- Current rung: {audit['current_rung']} ({audit['current_rung_label']})
- Derivation: {audit['current_derivation']}

Indicator scores:
{chr(10).join(f'  {k}: {v}' for k, v in audit['indicator_scores'].items())}

Upgrade blockers (why Rung 2 and 1 are unreachable via threshold changes):
1. Governance: {blockers[0]['why_threshold_cant_fix']}
2. Digital adoption: {blockers[1]['why_threshold_cant_fix']}

Nearest downgrade (data milestone, not a forecast):
  Current P/E premium: {d['current_value_pct']}%
  Declared severe gate opens at: {d['trigger_value_pct']}%
  Gap: {d['gap_pp']} percentage points ({d['gap_relative_pct']}% increase relative to current)
  Plausibility: {d['plausibility_label']}
  Note: {d['boundary_note']}

Profile stability: {ps['note']}

Key constraint to mention: the governance and digital adoption favorable conditions
are fixed model assumptions declared before scoring began, not proven facts.

Framing requirements:
  - Headline: Rung 3 is stable within the declared framework.
  - Use the exact gap number {d['gap_pp']}pp when describing the downgrade boundary.
  - Frame the boundary as a model boundary, not something the market is approaching.
  - Do not use the phrase "nearly double" or "tripwire".
"""

    return _llm_call(system, user, max_tokens=600)


# ---------------------------------------------------------------------------
# Python fact-validator (no LLM)
# ---------------------------------------------------------------------------

def validate_analysis(audit: AuditResult, analysis_text: str) -> ValidationResult:
    """Checks the agent's text names Rung 3 and both blockers, and flags numbers not in the audit.
    Plain Python with no LLM, so the checker itself can't make things up.
    Called by run_pipeline() right after agent_analysis(); app.py shows the pass/fail badge."""
    d = audit["nearest_downgrade"]
    text = analysis_text.lower()
    failures: list[str] = []
    warnings: list[str] = []

    if "rung 3" not in text:
        failures.append("Text does not name Rung 3.")

    if "governance" not in text:
        failures.append("Text does not mention the governance blocker.")

    if "digital" not in text:
        failures.append("Text does not mention the digital adoption blocker.")

    # If the gap is mentioned it must be the correct value
    gap_str       = str(d["gap_pp"])               # "16.1"
    trigger_str   = str(int(d["trigger_value_pct"]))  # "40"
    current_str   = str(d["current_value_pct"])       # "23.9"
    relative_str  = str(d["gap_relative_pct"])         # "67.4"

    allowed: set[str] = {
        str(audit["current_rung"]),   # "3"
        current_str,   # "23.9"
        trigger_str,   # "40"
        gap_str,       # "16.1"
        relative_str,  # "67.4"
        "1", "2", "4", "5", "6",
        "48", "71", "23",        # digital adoption figures in audit
        "10",                    # old-age dep india (in WGI context)
        "35",                    # minimum severe-band floor (atrisk+5pp) in boundary note
    }

    def _canon(s: str) -> str:
        """Normalize a number string so "40.0" and "0.40" both match "40" in the allowed set.
        Stops harmless formatting differences being flagged as invented numbers.
        Used only inside validate_analysis()."""
        try:
            f = float(s)
            if 0 < f < 1:          # fraction -> percentage
                f = round(f * 100, 1)
            if f == int(f):
                return str(int(f))  # drop trailing .0
            return s
        except ValueError:
            return s

    # Require digits after a decimal so "3." (sentence end) -> "3" not "3.",
    # and "16.1pp" -> "16.1" not split into "16" + "1".
    invented = [
        n for n in re.findall(r"\d+(?:\.\d+)?", analysis_text)
        if _canon(n) not in allowed and n not in allowed
    ]
    if invented:
        warnings.append(
            f"Numbers in text not confirmed in audit: {invented}. Verify these are not invented."
        )

    imminence = ["imminent", "likely to reach", "approaching", "on track", "trending toward"]
    for phrase in imminence:
        if phrase in text:
            warnings.append(
                f"'{phrase}' near the downgrade scenario may overstate likelihood."
            )

    return ValidationResult(passed=len(failures) == 0, failures=failures, warnings=warnings)


# ---------------------------------------------------------------------------
# Agent 2 -- Overreach check
# ---------------------------------------------------------------------------

def agent_overreach_check(audit: AuditResult, prior_text: str = "") -> str:
    """Analysis text in, "No overreach detected." or a bullet list of problems out.
    Catches soft issues a Python check can't, like forecast-style wording or investment advice.
    Second agent in run_pipeline(); it receives agent_analysis()'s text as prior_text."""
    if not prior_text.strip():
        return "No prior text to check."

    d = audit["nearest_downgrade"]

    system = (
        "You are a quality-checker for an academic thesis. "
        "You will receive an analyst's explanation of a quantitative model result. "
        "Flag only soft overreach: exaggeration, presenting a math scenario as a forecast "
        "or likely event, investment recommendations, false certainty, or causal claims "
        "the model does not support. "
        "Do not re-check numbers. Do not suggest tone improvements. "
        "If nothing is wrong, respond with exactly: No overreach detected. "
        "If issues exist, list them as short bullet points starting with '-'. "
        "Be conservative: flag only clear issues."
    )

    user = f"""Check this analyst explanation for overreach.

Context: academic thesis. The model placed India at Rung 3 of a 4-rung confidence ladder.
The nearest downgrade boundary is {d['gap_pp']} percentage points away and is a model
boundary, not a market forecast.

Text to check:
{prior_text}

Flag only: exaggeration, forecast-framing of a math scenario, investment recommendations,
unsupported causal claims, false certainty.
If none found, respond with exactly: No overreach detected.
"""

    return _llm_call(system, user, max_tokens=300)


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(audit: AuditResult) -> dict:
    """Audit result in, a dict with the analysis, its validation and the overreach check out.
    Agents are a list, so adding one is one new entry; each failure is caught so the page still loads.
    Called by app.py when the user clicks "Generate narrative"."""
    chain: list[tuple[str, AgentFn]] = [
        ("analysis",        agent_analysis),
        ("overreach_check", agent_overreach_check),
    ]

    outputs: dict = {}
    prior = ""

    for name, fn in chain:
        try:
            result = fn(audit, prior)
            outputs[name] = result
            if name == "analysis":
                outputs["validation"] = validate_analysis(audit, result)
                prior = result
        except Exception as exc:  # noqa: BLE001
            outputs[name] = f"[Agent unavailable: {exc}]"
            if name == "analysis":
                outputs["validation"] = ValidationResult(
                    passed=False,
                    failures=[f"Analysis agent failed: {exc}"],
                    warnings=[],
                )

    return outputs


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    from src.assumption_audit import run_assumption_audit, _FULL_DEFAULTS

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "layer2_indicators.json")
    with open(data_path) as f:
        data = json.load(f)

    audit = run_assumption_audit(data, _FULL_DEFAULTS)

    print("=== Running agent pipeline ===\n")
    outputs = run_pipeline(audit)

    print("--- Analysis ---")
    print(outputs.get("analysis", "[not run]"))
    print()

    print("--- Python validation ---")
    val = outputs.get("validation", {})
    print(f"  passed={val.get('passed')}")
    for f in val.get("failures", []):
        print(f"  FAIL: {f}")
    for w in val.get("warnings", []):
        print(f"  WARN: {w}")
    print()

    print("--- Overreach check ---")
    print(outputs.get("overreach_check", "[not run]"))
