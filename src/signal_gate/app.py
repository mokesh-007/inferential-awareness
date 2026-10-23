"""Interactive Inferential Awareness agent: Decider chooses whether Bedrock should answer."""
from __future__ import annotations

import os

from strands import Agent
from strands.models.bedrock import BedrockModel

from .decider import DeciderClient
from .policy import EvidenceFirstResponseGuardrail

SYSTEM_PROMPT = """You are Inferential Awareness, an evidence-grounded assistant. Answer only from the
TRUSTED CONTEXT provided in the user message. Do not add unstated facts or professional,
medical, legal, financial, or emergency certainty. State what the context says, name gaps,
and encourage official or qualified help when the context says it is needed."""


def build_agent() -> Agent:
    api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    if api_key and (api_key.lstrip().lower().startswith("set ") or "aws_bearer_token_bedrock=" in api_key.lower()):
        raise RuntimeError(
            "The Bedrock key contains a Windows shell command. Set the variable again and paste only "
            "the key value, not 'set AWS_BEARER_TOKEN_BEDROCK=...'."
        )
    return Agent(
        model=BedrockModel(
            model_id=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
            # Passing the temporary Bedrock bearer key explicitly keeps local setup simple.
            # When unset, BedrockModel falls back to the normal AWS credential chain/IAM role.
            api_key=api_key,
        ),
        system_prompt=SYSTEM_PROMPT,
    )


def reply(agent: Agent, guardrail: EvidenceFirstResponseGuardrail, request: str, trusted_context: str) -> str:
    decision = guardrail.decide(request, trusted_context)
    audit = f"[Decider: {decision.action}; evidence={decision.evidence_probability:.2f}; safety={decision.safety_probability:.2f}; confidence={decision.confidence:.2f}]"
    if decision.action == "clarify":
        return f"I don't have enough trusted evidence to answer that reliably. Please provide an approved source or clarify the missing detail.\n{audit}"
    if decision.action == "safe_redirect":
        return f"I can't help directly with that request. I can help with a safer, harm-preventing alternative or point you to appropriate official support.\n{audit}"
    prompt = f"TRUSTED CONTEXT:\n{trusted_context}\n\nUSER REQUEST:\n{request}\n\nAnswer concisely using only the trusted context."
    return f"{agent(prompt)}\n{audit}"


def main() -> None:
    try:
        agent = build_agent()
    except RuntimeError as exc:
        print(f"Inferential Awareness setup error: {exc}")
        return
    guardrail = EvidenceFirstResponseGuardrail(DeciderClient())
    print("Inferential Awareness: enter a request, then paste trusted context (blank line ends context). Type 'quit' to exit.")
    while (request := input("\nRequest> ").strip()) not in {"quit", "exit"}:
        if not request:
            continue
        print("Trusted context> ")
        lines: list[str] = []
        while (line := input()).strip():
            lines.append(line)
        try:
            print("\nInferential Awareness> " + reply(agent, guardrail, request, "\n".join(lines)))
        except Exception as exc:
            message = str(exc)
            if "Invalid API Key format" in message:
                message = (
                    "Bedrock rejected the key format. Reset the exposed key in the Bedrock API keys page, "
                    "then paste only the new key value when PowerShell prompts—do not paste the 'set ...' command."
                )
            elif "explicit deny in a service control policy" in message:
                message = (
                    "AWS Organizations is blocking Bedrock API-key use for this account. "
                    "Ask the organization administrator or AWS Support to remove that denial."
                )
            print(f"\nInferential Awareness> Could not complete the request: {message}")


if __name__ == "__main__":
    main()

