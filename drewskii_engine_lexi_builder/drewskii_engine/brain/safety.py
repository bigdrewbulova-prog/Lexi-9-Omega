"""Safety boundaries for Drewskii.Engine CLI."""
from __future__ import annotations

BLOCKED_TERMS = [
    "steal password",
    "get password",
    "collect password",
    "password dump",
    "hack account",
    "account takeover",
    "bypass login",
    "bypass security",
    "security bypass",
    "spy on",
    "keylogger",
    "malware",
    "phishing",
    "hidden persistence",
    "background surveillance",
    "systemui implant",
    "kernel exploit",
    "baseband",
    "secure enclave provisioning",
    "identity information without consent",
    "state id number for someone",
    "root the phone",
    "wipe system",
]


def is_blocked(text: str) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in BLOCKED_TERMS)


def blocked_reason(text: str) -> str | None:
    lowered = (text or "").lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            return term
    return None
