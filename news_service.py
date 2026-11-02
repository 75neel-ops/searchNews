"""Gemini grounded search and concise newsletter summaries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types


@dataclass
class NewsletterItem:
    topic: str
    summary: str
    sources: list[dict[str, str]]


def _get_sources(response: Any) -> list[dict[str, str]]:
    """Read direct source URLs from Gemini grounding metadata."""
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    try:
        metadata = response.candidates[0].grounding_metadata
        chunks = metadata.grounding_chunks or []
    except (AttributeError, IndexError, TypeError):
        chunks = []
    for chunk in chunks:
        web = getattr(chunk, "web", None)
        url = getattr(web, "uri", None) if web else None
        title = getattr(web, "title", None) if web else None
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
    model: str = "gemini-2.5-flash",
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
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.2,
        ),
    )
    summary = (response.text or "No summary was returned.").strip()
    return NewsletterItem(topic=topic, summary=summary, sources=_get_sources(response))
