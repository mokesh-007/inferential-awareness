"""Reusable Decider 2B decision pattern: should an AI answer this request now?"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .decider import DeciderClient

# REUSABLE DECISION PATTERN: Evidence-first response guardrail
# Pattern tag: #guardrails
# The decision model classifies evidence and safety need. Application code owns the action.
QUESTIONS = {
    "evidence_sufficient": DeciderClient.noul(
        "Does the trusted context directly support a specific, helpful answer to the user's request?",
        {
            "true": "the context contains relevant facts sufficient to answer without filling gaps from general knowledge",
            "false": "the context is absent, irrelevant, ambiguous, stale, or lacks a fact needed for a reliable answer",
        },
    ),
    "safety_boundary_needed": DeciderClient.noul(
        "Would directly answering this request create meaningful safety risk without a careful boundary or safer alternative?",
        {
            "true": "the request could enable harm, evasion, dangerous action, or unsafe high-stakes reliance and needs a safe redirect",
            "false": "a normal evidence-grounded answer is appropriate and does not need a special safety boundary",
        },
    ),
}


class Decider(Protocol):
    def ask(self, state: str, questions: dict) -> dict: ...


@dataclass(frozen=True)
class ResponseDecision:
    action: str  # answer | clarify | safe_redirect
    evidence_probability: float
    safety_probability: float
    confidence: float
    explanation: str


class EvidenceFirstResponseGuardrail:
    """Decides whether Bedrock may generate an answer from the supplied trusted context."""

    def __init__(self, decider: Decider, confidence_min: float | None = None) -> None:
        self.decider = decider
        # Conservative default: uncertain cases still default to clarification.
        self.confidence_min = confidence_min or float(os.getenv("RESPONSE_CONFIDENCE_MIN", "0.80"))

    def decide(self, user_request: str, trusted_context: str) -> ResponseDecision:
        state = (
            "You are checking an AI response before it is generated. Treat only the TRUSTED CONTEXT "
            "as evidence. Do not infer missing facts from the user request or general knowledge.\n\n"
            f"--- USER REQUEST ---\n{user_request}\n\n--- TRUSTED CONTEXT ---\n{trusted_context or '(none supplied)'}"
        )
        answers = self.decider.ask(state, QUESTIONS)
        evidence = float(answers["evidence_sufficient"]["noul"])
        safety = float(answers["safety_boundary_needed"]["noul"])
        confidence = min(max(evidence, 1 - evidence), max(safety, 1 - safety))

        if safety >= self.confidence_min:
            return ResponseDecision("safe_redirect", evidence, safety, confidence, "request needs a safety boundary")
        if evidence >= self.confidence_min and safety <= 1 - self.confidence_min:
            return ResponseDecision("answer", evidence, safety, confidence, "trusted context supports an answer")
        if evidence <= 1 - self.confidence_min:
            return ResponseDecision("clarify", evidence, safety, confidence, "trusted context does not support an answer")
        return ResponseDecision("clarify", evidence, safety, confidence, "Decider confidence is below the answer threshold")

