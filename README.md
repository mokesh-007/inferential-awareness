# Inferential Awareness — an AI that decides whether it should answer

Inferential Awareness is an evidence-first safety agent. It pairs **Amazon Bedrock** (the generative response) with **Strands Decider 2B** (a quick, typed decision) to decide whether an AI should:

- answer from supplied trusted context;
- ask for missing evidence rather than hallucinate; or
- give a safe boundary and redirect rather than help with a harmful request.


**Decision pattern:** Guardrails — Evidence-first response gate

## The meaningful decision

Before Bedrock is allowed to generate an answer, Decider 2B reads the user request and the trusted context and answers two typed yes/no questions in one forward pass:

1. Does the trusted context directly support a reliable answer?
2. Does a direct answer need a safety boundary or safer alternative?

Inferential Awareness turns those calibrated probabilities into normal program control flow. It uses a conservative threshold: any uncertainty becomes a clarification, never an invented answer.

```text
request + trusted context
          |
          v
Strands Decider 2B ──> answer / clarify / safe redirect
          |                         |
          | answer                  +--> fixed safe response; Bedrock is not asked to improvise
          v
Amazon Bedrock drafts only from the approved context
```

This is a narrow safety control, not a claim to solve all hallucinations or all AI safety problems. Its purpose is to prevent one very common failure: generating a confident answer when the agent has no evidence for it.

## Reusable asset

[`src/signal_gate/policy.py`](src/signal_gate/policy.py) is the reusable **Evidence-first Response Guardrail**. To apply it to a support bot, policy assistant, RAG app, or internal knowledge agent:

1. Retrieve and pass only approved context.
2. Call `guardrail.decide(user_request, trusted_context)` before the generative step.
3. Only send the request to Bedrock after the `answer` decision.
4. Tune `RESPONSE_CONFIDENCE_MIN` on labelled examples from your own domain.

The decision model never writes policy or chooses how to respond. The application owns the threshold and the three safe actions.

## Run locally

New to Python or PowerShell? Follow the step-by-step [Windows quick start](START_HERE_WINDOWS.md).

```bash
python -m venv .venv
. .venv/bin/activate                    # PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"

# Terminal 1: serve the experimental decision model.
pip install "strands-decider @ git+https://github.com/strands-labs/strands-decider"
strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099

# Terminal 2: AWS credentials with Bedrock access must be available.
python -m signal_gate.app
```

Demo sequence:

```image
<img width="1907" height="561" alt="image" src="https://github.com/user-attachments/assets/7806d7ff-621a-4399-bd6b-f5b1438c923a" />

```

`pytest` runs deterministic policy tests using a fake Decider—no AWS account or model download is needed for those checks.

## Deploy on AWS

Use the Dockerfile to run Inferential Awareness on ECS Fargate or AgentCore Runtime, and run Decider 2B behind a private EC2 GPU endpoint. Amazon Bedrock supplies text generation through the service’s task role. See [`deploy/README.md`](deploy/README.md) for the network and IAM boundaries.

