# Start here on Windows

Inferential Awareness is a small chat program that runs in PowerShell. You already have Decider 2B running locally. To get real generated answers, you need an AWS account and Amazon Bedrock access. You do not need to rent an EC2 server for this first demo: Bedrock runs in AWS while Inferential Awareness and Decider run on your computer.

## Set up AWS and Bedrock

If you do not have an AWS account, create one at [aws.amazon.com](https://aws.amazon.com/). AWS asks for billing details. Turn on multi-factor authentication (MFA) for the account owner/root sign-in, and do not create or use root access keys for the app. AWS recommends using a separate administrative identity for normal work.

Before running the app, set a small AWS Budget email alert in Billing and Cost Management. A budget sends an alert; it is not a hard spending cap. Bedrock model calls can incur charges, so try short prompts and check your account's current pricing.

For a first local experiment, a short-term Bedrock API key avoids configuring long-lived access keys:

1. Sign in to the AWS Console with an identity permitted to use Bedrock.
2. Open **Amazon Bedrock** and select **US East (N. Virginia) / `us-east-1`** in the region menu. The region must match the app setting below.
3. Open **API keys** in the Bedrock navigation and create a **short-term API key**. If you cannot see that option, your identity needs permission to use Bedrock and create/use the key; ask the account administrator to grant it.
4. Keep the key private. Do not send it in chat, put it in a source file, or commit it to GitHub. A short-term key expires (AWS says up to 12 hours), so you may need to create another later.

The app's default model is Amazon Nova Lite (`amazon.nova-lite-v1:0`). If Bedrock reports that the model is unavailable, check the selected region and the model's availability/access in the Bedrock Model catalog. Commercial Bedrock model access often activates on first use, subject to account permissions and model requirements.

## First: open the project folder

Open PowerShell, then paste this command and press Enter:

```powershell
cd "$HOME\Documents\Codex\2026-10-19\build-a-working-agent-on-aws\outputs\signal-gate-response-safety"
```

If that path does not exist on your computer, open the `signal-gate-response-safety` folder in File Explorer, click the address bar, type `powershell`, and press Enter.

## Install the app once

You need Python 3.10 or newer. Then paste these commands one at a time in PowerShell:

```powershell
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
```

This creates a private Python setup inside this folder and installs the app. It needs an internet connection the first time.

## Start Decider 2B (PowerShell window 1)

Keep this window open while you use the app. Install and start the decision model:

```powershell
& .\.venv\Scripts\python.exe -m pip install "strands-decider @ git+https://github.com/strands-labs/strands-decider"
strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099
```

The first start downloads several gigabytes of model files and can take a while. Wait until it says it is serving on port `8099`. The model runs on your computer; CPU-only machines may take longer to answer.

## Start Inferential Awareness (PowerShell window 2)

Open a second PowerShell window and go to the same folder using the `cd` command above. Set the region, then paste the short-term key when PowerShell prompts for it. The key is kept only in this window's environment for this session:

```powershell
$env:AWS_REGION = "us-east-1"
$env:AWS_BEARER_TOKEN_BEDROCK = Read-Host "Paste your short-term Bedrock API key"
& .\.venv\Scripts\python.exe -m signal_gate.app
```

The API key expires; after expiration, generate a fresh one and restart the app in a new PowerShell session. For a longer-term deployment, use AWS IAM roles or temporary IAM Identity Center credentials instead of a long-lived key. See [AWS Bedrock API key guidance](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) and the [Strands Bedrock setup guide](https://strandsagents.com/docs/user-guide/sdk/model-providers/amazon-bedrock/).

## Try these examples

At `Request>`, type only the question, then press Enter:

```text
What is our refund policy?
```

At `Trusted context>`, paste the approved policy text, then press Enter on a blank line to finish it. Inferential Awareness should allow Bedrock to answer using that context. If you leave the context blank, Inferential Awareness should ask for evidence instead.

Example interaction:

```text
Request> What is our refund policy?
Trusted context>
Approved policy: customers may request a refund within 30 days of purchase.

Inferential Awareness> [answer from Bedrock]
[Decider: answer; evidence=...; safety=...; confidence=...]
```

Do not type the policy at `Request>`; that field is for the question. At the end of each answer you will see a `[Decider: ...]` line showing the decision and probabilities.

To stop the app, type `quit` at `Request>`. Stop the Decider server with Ctrl+C in window 1.

## If you do not have AWS set up yet

The real chat needs Bedrock credentials. You can still see the decision rules without AWS by running the included policy checks:

```powershell
& .\.venv\Scripts\python.exe -m pip install pytest
& .\.venv\Scripts\python.exe -m pytest -q
```





## Common problems

- **`py` is not recognized:** install Python from python.org and select the option to add Python to PATH, then reopen PowerShell.
- **`strands-decider` is not recognized:** close and reopen PowerShell after the install, or run `& .\.venv\Scripts\strands-decider.exe serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099`.
- **AWS credentials or model access error:** configure AWS credentials and ask your account administrator to enable the Bedrock model in the selected region.
- **Computer runs out of memory or the model is too slow:** stop here rather than repeatedly retrying. The practical alternative is hosting Decider 2B on a private GPU EC2 instance; that uses paid AWS resources.

