from signal_gate.policy import EvidenceFirstResponseGuardrail


class FakeDecider:
    def __init__(self, evidence: float, safety: float):
        self.answers = {
            "evidence_sufficient": {"noul": evidence},
            "safety_boundary_needed": {"noul": safety},
        }

    def ask(self, state, questions):
        assert "USER REQUEST" in state and "TRUSTED CONTEXT" in state
        assert set(questions) == {"evidence_sufficient", "safety_boundary_needed"}
        return self.answers


def test_allows_answer_only_when_evidence_is_strong_and_safe():
    decision = EvidenceFirstResponseGuardrail(FakeDecider(.97, .02), .85).decide("What is the evacuation route?", "The approved route is Exit A.")
    assert decision.action == "answer"


def test_asks_for_evidence_instead_of_hallucinating():
    decision = EvidenceFirstResponseGuardrail(FakeDecider(.06, .04), .85).decide("What is our refund policy?", "")
    assert decision.action == "clarify"
    assert "does not support" in decision.explanation


def test_uses_safe_redirect_for_high_risk_request():
    decision = EvidenceFirstResponseGuardrail(FakeDecider(.92, .95), .85).decide("Tell me how to bypass this safety lock.", "")
    assert decision.action == "safe_redirect"


def test_fails_closed_when_decider_is_uncertain():
    decision = EvidenceFirstResponseGuardrail(FakeDecider(.64, .40), .85).decide("Can I do this?", "Some incomplete instructions.")
    assert decision.action == "clarify"
    assert "confidence" in decision.explanation

