# frontend/utils/api_client.py

import os
from typing import Any, Optional

import requests
import streamlit as st


def _base_url() -> str:
    in_docker = os.path.exists("/.dockerenv")
    for key in ("ERP_API_BASE_URL", "API_BASE_URL"):
        url = os.environ.get(key)
        if not url:
            continue
        if in_docker and ("localhost" in url or "127.0.0.1" in url):
            continue
        return url.rstrip("/")
    if in_docker:
        return "http://api:8000"
    try:
        secret = st.secrets.get("API_BASE_URL")
        if secret:
            return str(secret).rstrip("/")
    except Exception:
        pass
    return "http://127.0.0.1:8000"


def _headers() -> dict[str, str]:
    token = st.session_state.get("token", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _handle(resp: requests.Response) -> Any:
    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Non-JSON response: {resp.text}") from exc

    if resp.status_code >= 400:
        detail = data.get("detail", "Unknown error")
        st.toast(f"Error: {detail}")
        raise RuntimeError(detail)

    return data


def login(username: str, password: str) -> dict[str, Any]:
    resp = requests.post(
        f"{_base_url()}/api/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    return _handle(resp)


def get(path: str, params: Optional[dict] = None) -> Any:
    resp = requests.get(
        f"{_base_url()}{path}",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    return _handle(resp)


def post(path: str, data: dict) -> Any:
    resp = requests.post(
        f"{_base_url()}{path}",
        headers=_headers(),
        json=data,
        timeout=30,
    )
    return _handle(resp)
