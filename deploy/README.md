# AWS deployment

```text
Client -> Inferential Awareness (ECS Fargate or AgentCore Runtime)
               |              \
               |               \-> Amazon Bedrock: generative response
               |
               \-> private VPC -> EC2 GPU: Strands Decider 2B :8099
```

Run the Decider service on a GPU EC2 instance in private subnets. Its upstream HTTP server has no authentication, so permit port 8099 only from the Inferential Awareness security group or an internal NLB. Give the Inferential Awareness task/agent role only `bedrock:InvokeModel` for the selected model and configure `STRANDS_DECIDER_URL` with the private endpoint. Persist only redacted decision metrics (`action`, probabilities, latency); protect user content according to your data policy.

