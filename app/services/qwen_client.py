from __future__ import annotations

from typing import List, Optional, Dict, Any

from app.core.config import get_settings


class QwenChatClient:
    """Thin wrapper around OpenAI-compatible Chat Completions API for DashScope/Qwen."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        s = get_settings()
        self.api_key = api_key or s.dashscope_api_key
        self.base_url = base_url or s.dashscope_base_url
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not configured")

    def chat_completion(self, model: str, messages: List[dict], stream: bool = False, extra_body: Optional[Dict[str, Any]] = None) -> dict:
        import httpx

        url = self.base_url.rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload: Dict[str, Any] = {
            'model': model,
            'messages': messages,
            'stream': stream,
        }
        if extra_body:
            payload.update(extra_body)

        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()


def get_qwen_client() -> QwenChatClient:
    return QwenChatClient()
