"""Small standard-library client for the Strands Decider HTTP protocol."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any


class DeciderUnavailable(RuntimeError):
    pass


class DeciderClient:
    def __init__(self, url: str | None = None, timeout_seconds: float | None = None) -> None:
        self.url = (url or os.getenv("STRANDS_DECIDER_URL", "http://127.0.0.1:8099")).rstrip("/")
        self.timeout_seconds = timeout_seconds or float(os.getenv("STRANDS_DECIDER_TIMEOUT_SECONDS", "180"))
        self.last_latency_ms: float | None = None

    @staticmethod
    def noul(instructions: str, criteria: Mapping[str, str]) -> dict[str, Any]:
        return {"type": "noul", "instructions": instructions, "criteria": dict(criteria)}

    def ask(self, state: str, questions: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.url}/v1/systemone",
            data=json.dumps({"state": state, "model": "signal-gate", "questions": dict(questions)}).encode(),
            headers={"content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read())
        except TimeoutError as exc:
            raise DeciderUnavailable(
                f"Decider 2B did not respond within {self.timeout_seconds:g} seconds. "
                "Check that its server is still running in the other PowerShell window. "
                "You can allow more time by setting STRANDS_DECIDER_TIMEOUT_SECONDS."
            ) from exc
        except urllib.error.URLError as exc:
            raise DeciderUnavailable(
                "Start Decider 2B with: strands-decider serve "
                "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099"
            ) from exc
        self.last_latency_ms = payload.get("latency_ms")
        return payload["answers"]

