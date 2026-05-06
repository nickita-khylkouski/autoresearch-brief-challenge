from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RATE_LIMIT_PATTERNS = (
    "rate limit",
    "too many requests",
    "status code: 429",
    "error 429",
    "resource exhausted",
    "quota",
)


def mask_secret(text: str) -> str:
    masked = text
    masked = re.sub(r"sk[-_][A-Za-z0-9_\-]{8,}", "***MASKED_KEY***", masked)
    masked = re.sub(r"Bearer\s+[A-Za-z0-9_\-.]+", "Bearer ***MASKED***", masked)
    return masked


class SecretRedactor:
    def __init__(self, secrets: list[str]) -> None:
        self.secrets = sorted({secret for secret in secrets if secret}, key=len, reverse=True)

    def redact(self, text: str) -> str:
        redacted = mask_secret(text)
        for secret in self.secrets:
            redacted = redacted.replace(secret, "***MASKED_KEY***")
        return redacted


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def split_key_blob(raw: str) -> list[str]:
    keys: list[str] = []
    for piece in re.split(r"[\n,]+", raw or ""):
        key = piece.strip().strip("'\"")
        if key and key not in keys:
            keys.append(key)
    return keys


@dataclass
class MiniMaxSettings:
    keys: list[str]
    api_host: str = "https://api.minimaxi.chat"
    model: str = "MiniMax-M2.7"
    group_id: str = ""
    mode: str = "text_chatcompletion_v2"
    env_file: Path | None = None


class MiniMaxClient:
    def __init__(self, settings: MiniMaxSettings, *, mock: bool = False) -> None:
        self.settings = settings
        self.mock = mock
        self.cooldowns: dict[int, float] = {}
        self.mock_index = 0
        self.redactor = SecretRedactor(settings.keys)

    @classmethod
    def from_environment(cls, *, mock: bool = False) -> "MiniMaxClient":
        env_file_raw = os.environ.get("MINIMAX_ENV_FILE", "").strip()
        if env_file_raw:
            env_file = Path(env_file_raw).expanduser()
        else:
            from .config import ROOT

            env_file = ROOT / ".env"
        values = read_env_file(env_file)
        merged = dict(values)
        for key, value in os.environ.items():
            if key.startswith("MINIMAX_"):
                merged[key] = value

        keys: list[str] = []
        keys.extend(split_key_blob(merged.get("MINIMAX_API_KEYS", "")))
        indexed = sorted(name for name in merged if re.fullmatch(r"MINIMAX_API_KEY_\d+", name))
        for name in indexed:
            keys.extend(split_key_blob(merged.get(name, "")))
        keys.extend(split_key_blob(merged.get("MINIMAX_API_KEY", "")))
        unique_keys: list[str] = []
        for key in keys:
            if key and key not in unique_keys:
                unique_keys.append(key)

        settings = MiniMaxSettings(
            keys=unique_keys,
            api_host=merged.get("MINIMAX_API_HOST", "https://api.minimaxi.chat").rstrip("/"),
            model=merged.get("MINIMAX_MODEL", "MiniMax-M2.7"),
            group_id=merged.get("MINIMAX_GROUP_ID", ""),
            mode=merged.get("MINIMAX_API_MODE", "text_chatcompletion_v2"),
            env_file=env_file,
        )
        return cls(settings, mock=mock)

    def propose_patch(self, prompt: str) -> tuple[str, dict[str, Any]]:
        if self.mock:
            return self._mock_patch(prompt), {"provider": "mock-minimax", "model": self.settings.model}
        if not self.settings.keys:
            raise RuntimeError("Missing MiniMax API key. Set MINIMAX_API_KEY or MINIMAX_ENV_FILE.")
        last_error = ""
        for index, key in enumerate(self.settings.keys):
            if self.cooldowns.get(index, 0) > time.time():
                continue
            try:
                return self._call_minimax(key, prompt), {
                    "provider": "minimax",
                    "model": self.settings.model,
                    "key_index": index,
                }
            except RuntimeError as exc:
                message = str(exc)
                last_error = message
                if is_rate_limit(message):
                    self.mark_key_cooldown(index, message)
                    continue
                raise
        raise RuntimeError(self.redactor.redact(last_error or "All MiniMax API keys are on cooldown."))

    def mark_key_cooldown(self, index: int, reason: str, seconds: int = 60) -> None:
        self.cooldowns[index] = time.time() + seconds
        if not self.settings.env_file:
            return
        path = self.settings.env_file.with_name("minimax_key_health.json")
        try:
            payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"keys": {}}
        except Exception:
            payload = {"keys": {}}
        keys = payload.setdefault("keys", {})
        keys[str(index)] = {
            "cooldown_until_epoch": self.cooldowns[index],
            "reason": self.redactor.redact(reason)[:500],
            "updated_at_epoch": time.time(),
        }
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    def _call_minimax(self, key: str, prompt: str) -> str:
        if self.settings.mode == "openai":
            url = f"{self.settings.api_host}/v1/chat/completions"
            body = {
                "model": self.settings.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
        else:
            url = f"{self.settings.api_host}/v1/text/chatcompletion_v2"
            body = {
                "model": self.settings.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }
        if self.settings.group_id:
            headers["GroupId"] = self.settings.group_id
            headers["group-id"] = self.settings.group_id
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(mask_secret(f"MiniMax HTTP {exc.code}: {body_text}")) from exc
        except Exception as exc:
            raise RuntimeError(mask_secret(f"MiniMax request failed: {exc}")) from exc

        base_resp = payload.get("base_resp")
        if isinstance(base_resp, dict) and int(base_resp.get("status_code", 0) or 0) != 0:
            raise RuntimeError(mask_secret(f"MiniMax API error: {base_resp}"))
        text = extract_text(payload)
        if not text:
            raise RuntimeError(mask_secret(f"MiniMax response had no patch text: {payload}"))
        return strip_code_fence(text)

    def _mock_patch(self, prompt: str) -> str:
        if "SEARCH_DEPTH = 1" in prompt:
            return """diff --git a/bot/config.py b/bot/config.py
--- a/bot/config.py
+++ b/bot/config.py
@@ -1,6 +1,6 @@
-SEARCH_DEPTH = 1
+SEARCH_DEPTH = 2
 MATERIAL_WEIGHT = 1.0
-MOBILITY_WEIGHT = 0.0
+MOBILITY_WEIGHT = 2.0
 KING_SAFETY_WEIGHT = 0.0
-USE_PIECE_SQUARES = False
+USE_PIECE_SQUARES = True
 CAPTURE_FIRST = True
"""
        if "KING_SAFETY_WEIGHT = 0.0" in prompt and "SEARCH_DEPTH = 2" in prompt:
            return """diff --git a/bot/config.py b/bot/config.py
--- a/bot/config.py
+++ b/bot/config.py
@@ -1,6 +1,6 @@
 SEARCH_DEPTH = 2
 MATERIAL_WEIGHT = 1.0
 MOBILITY_WEIGHT = 2.0
-KING_SAFETY_WEIGHT = 0.0
+KING_SAFETY_WEIGHT = 1.0
 USE_PIECE_SQUARES = True
 CAPTURE_FIRST = True
"""
        if "score += 150" in prompt:
            return ""
        return """diff --git a/bot/move_ordering.py b/bot/move_ordering.py
--- a/bot/move_ordering.py
+++ b/bot/move_ordering.py
@@ -21,4 +21,6 @@ def move_score(board: chess.Board, move: chess.Move) -> int:
     if board.gives_check(move):
-        score += 75
+        score += 150
+    if move.to_square in {chess.D4, chess.E4, chess.D5, chess.E5}:
+        score += 20
     if not config.CAPTURE_FIRST:
         score = -score
"""


def is_rate_limit(text: str) -> bool:
    hay = text.lower()
    return any(pattern in hay for pattern in RATE_LIMIT_PATTERNS)


def extract_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        choice = choices[0]
        if isinstance(choice, dict) and isinstance(choice.get("message"), dict):
            message = choice["message"]
            if isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(message.get("content"), list):
                parts = []
                for item in message["content"]:
                    if isinstance(item, dict):
                        parts.append(str(item.get("text", "")))
                return "".join(parts)
        if isinstance(choice, dict):
            return str(choice.get("text", ""))
    if isinstance(payload.get("reply"), str):
        return str(payload["reply"])
    if isinstance(payload.get("output"), str):
        return str(payload["output"])
    if isinstance(payload.get("text"), str):
        return str(payload["text"])
    return ""


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip() + "\n"
    lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
    cleaned = "\n".join(lines).strip()
    return cleaned + ("\n" if cleaned else "")
