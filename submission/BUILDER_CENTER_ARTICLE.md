# The most important thing my AI does is decide not to answer yet

Generative AI is very good at making an answer sound complete. That is also the problem: a user can ask a question outside the agent’s knowledge, and the model may turn missing facts into confident prose.

I built **Inferential Awareness**, an evidence-first response-safety agent. It uses Amazon Bedrock to generate useful answers and Strands Decider 2B to decide, before that generation happens, whether the AI should answer, ask for evidence, or give a safe redirect.

## The decision I gave to Decider 2B

For every request, Inferential Awareness assembles a small state containing the user’s request and retrieved, approved context. Decider 2B answers two narrow typed yes/no questions:

1. Does the trusted context directly support the requested answer?
2. Would directly answering need a safety boundary or safer alternative?

The model returns probabilities—not text, policy, or a jailbreakable explanation. My application code applies the policy:

```python
if safety >= 0.80:
    return "safe_redirect"
if evidence >= 0.80 and safety <= 0.20:
    return "answer"
return "clarify"
```

The conservative default is intentional. An uncertain decision is not permission to invent an answer; it is a prompt to ask for the missing evidence.

## What happens in the demo

First I ask, “What is our refund policy?” and give the agent no trusted context. Instead of turning a generic internet-like answer into company policy, Inferential Awareness asks for an approved source.

Then I supply a short approved policy excerpt. Decider 2B allows the response. Only then does Amazon Bedrock generate an answer, instructed to stay within that excerpt.

Finally I submit a request that needs a safety boundary. Inferential Awareness does not route it to a free-form answer. It returns a safe redirect that offers harm-preventing alternatives or appropriate official support.

## Why a decision model belongs here

The decision is repeated at a natural boundary: immediately before every generative response. It needs a closed answer, not an essay. Decider 2B supplies a fast, calibrated score that normal program logic can audit and enforce. Bedrock remains responsible for language; the decision model establishes when language generation is appropriate.

## Reusable pattern: Evidence-first Response Guardrail

This project demonstrates the **#guardrails** decision pattern. The public repository includes the exact typed questions, a dependency-light Decider HTTP client, confidence-driven policy, deterministic tests, and AWS deployment guidance. Builders can drop it in front of a RAG assistant, HR policy bot, healthcare education app, or operations assistant by replacing the trusted-context provider and tuning their evaluation threshold.

Inferential Awareness is not a production safety guarantee and it does not solve every hallucination. It makes a smaller promise I can show in a demo: the agent will not use its fluent voice to fill a gap in evidence.

**Tags:** `#strands-decider-2b` `#guardrails`

