# Inferential Awareness demo — 2:20 target

**0:00–0:15:** “This agent makes one safety decision before it generates text: should it answer, ask for evidence, or safely redirect?” Show the architecture.

**0:15–0:35:** Highlight the two typed Decider questions in `policy.py`. “Bedrock writes language. Decider 2B checks evidence sufficiency and safety need; code owns the threshold.”

**0:35–1:00:** Live run: request “What is our refund policy?” with blank trusted context. Show the `clarify` decision and no Bedrock answer.

**1:00–1:30:** Repeat with an approved policy excerpt. Show `answer`, then the concise Bedrock response. “This time it is allowed to speak, and only from the source.”

**1:30–1:50:** Submit a request requiring a safety boundary. Show `safe_redirect`. “The free-form model never gets a chance to improvise a risky answer.”

**1:50–2:20:** Show the reusable pattern and AWS topology. “Run Decider 2B privately next to an AWS Bedrock agent. This small decision makes an evidence gap visible and actionable.”

