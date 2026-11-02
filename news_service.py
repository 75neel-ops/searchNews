"""Gemini grounded search and concise newsletter summaries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google import genai


@dataclass
class NewsletterItem:
    topic: str
    summary: str
    sources: list[dict[str, str]]


def _field(value: Any, name: str, default: Any = None) -> Any:
    """Read a field from either SDK model objects or dictionary responses."""
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def _get_sources(interaction: Any) -> list[dict[str, str]]:
    """Read cited URLs from the Interactions API model output annotations."""
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for step in _field(interaction, "steps", []) or []:
        if _field(step, "type") != "model_output":
            continue
        for block in _field(step, "content", []) or []:
            if _field(block, "type") != "text":
                continue
            for citation in _field(block, "annotations", []) or []:
                if _field(citation, "type") != "url_citation":
                    continue
                url = _field(citation, "url")
                title = _field(citation, "title")
                if url and url.startswith(("https://", "http://")) and url not in seen:
                    seen.add(url)
                    found.append({"title": title or url, "url": url})
    return found[:5]


def summarize_topic(
    api_key: str,
    topic: str,
    timeframe: str,
    newspaper_queries: list[str],
    social_queries: list[str],
    language: str = "English",
    model: str = "gemini-3.8-flash",
) -> NewsletterItem:
    """Search the public web via Gemini and return a brief grounded overview."""
    client = genai.Client(api_key=api_key)
    outlets = ", ".join(newspaper_queries) or "reputable news publishers"
    platforms = ", ".join(social_queries) or "publicly indexed social media"
    prompt = f"""
Create a concise newsletter brief for the topic: {topic}.
Timeframe: {timeframe}.
Prioritize reporting from these selected outlets: {outlets}.
Also look for relevant public posts or discussions on these platforms: {platforms}.
Return 2-4 crisp sentences (maximum 90 words), in {language}. Cover only verifiable developments in the requested timeframe. Distinguish social discussion from verified reporting, and do not present a social post as confirmed fact. If useful results are unavailable, say so plainly. Do not invent facts, dates, quotes, or URLs. Do not reproduce article text.
""".strip()
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        tools=[{"type": "google_search"}],
    )
    summary = (_field(interaction, "output_text", "") or "No summary was returned.").strip()
    return NewsletterItem(topic=topic, summary=summary, sources=_get_sources(interaction))
