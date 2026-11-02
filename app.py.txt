"""NilanjanC's personalized Bengali and English news brief."""
from __future__ import annotations

import os
from datetime import date

import streamlit as st

from news_service import summarize_topic
from source_catalog import BENGALI_NEWSPAPERS, ENGLISH_NEWSPAPERS, SOCIAL_PLATFORMS, TOPICS


def configured_api_key() -> str:
    """Read the key from Streamlit secrets when configured, else the environment."""
    try:
        secret = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret = ""
    return secret or os.getenv("GEMINI_API_KEY", "")


st.set_page_config(page_title="NilanjanC | News Brief", page_icon="🗞️", layout="wide")
st.markdown("<style>.block-container{max-width:1050px;padding-top:2rem}.brand{color:#526477;font-size:.95rem;letter-spacing:.08em;text-transform:uppercase}.stButton button[kind=primary]{background:#173b57;border-color:#173b57}</style>", unsafe_allow_html=True)
st.markdown('<div class="brand">A personal news digest by NilanjanC</div>', unsafe_allow_html=True)
st.title("Your news, briefly.")
st.caption("A focused overview of current reporting and public social conversations, with links to the originals.")

with st.sidebar:
    st.header("Build your brief")
    api_key = st.text_input("Gemini API key", type="password", value=configured_api_key(), help="Stored in this browser session only unless you configure Streamlit secrets.")
    language = st.selectbox("Summary language", ["English", "Bengali"])
    timeframe_mode = st.radio("News timeframe", ["Latest", "Specific year"])
    timeframe = "latest available news" if timeframe_mode == "Latest" else str(st.number_input("Year", min_value=1900, max_value=date.today().year, value=date.today().year, step=1))
    st.divider()
    st.caption("Choose any combination of sources. Selected publications guide the search; results depend on public web indexing.")
    bengali_all = st.checkbox("All Bengali newspapers")
    bengali = st.multiselect("Bengali newspapers", list(BENGALI_NEWSPAPERS), disabled=bengali_all)
    english_all = st.checkbox("All English newspapers")
    english = st.multiselect("English newspapers", list(ENGLISH_NEWSPAPERS), disabled=english_all)
    social_all = st.checkbox("All social platforms")
    social = st.multiselect("Social media", list(SOCIAL_PLATFORMS), disabled=social_all)
    st.caption("Social results are public, searchable pages and posts only. Private feeds and login-only content are not accessed.")

picked_topics = st.multiselect("What do you want to follow?", TOPICS, default=["Top headlines", "Politics", "Sports", "Science"])
custom_topics = st.text_input("Add custom topics", placeholder="e.g., Kolkata transport, climate research (comma-separated)")
all_topics = list(dict.fromkeys(picked_topics + [topic.strip() for topic in custom_topics.split(",") if topic.strip()]))

if st.button("Generate my newsletter", type="primary", use_container_width=True):
    if not api_key:
        st.error("Add your Gemini API key in the sidebar or configure GEMINI_API_KEY in Streamlit secrets.")
    elif not all_topics:
        st.error("Choose at least one topic or enter a custom topic.")
    else:
        selected_bengali = list(BENGALI_NEWSPAPERS) if bengali_all else bengali
        selected_english = list(ENGLISH_NEWSPAPERS) if english_all else english
        selected_social = list(SOCIAL_PLATFORMS) if social_all else social
        newspaper_queries = [BENGALI_NEWSPAPERS[name] for name in selected_bengali] + [ENGLISH_NEWSPAPERS[name] for name in selected_english]
        social_queries = [SOCIAL_PLATFORMS[name] for name in selected_social]
        st.subheader("Your newsletter")
        st.caption(f"Prepared for NilanjanC · {timeframe.title()} · {date.today().strftime('%B %d, %Y')}")
        for topic in all_topics:
            with st.spinner(f"Searching and summarizing: {topic}"):
                try:
                    item = summarize_topic(api_key, topic, timeframe, newspaper_queries, social_queries, language)
                except Exception as exc:
                    st.error(f"Could not generate the {topic} brief: {exc}")
                    continue
            with st.container(border=True):
                st.markdown(f"#### {topic}")
                st.write(item.summary)
                if item.sources:
                    st.markdown("**Read more**")
                    for source in item.sources:
                        st.markdown(f"- [{source['title']}]({source['url']})")
                else:
                    st.caption("No direct source link was returned for this topic. Try again or broaden the selected sources.")
        st.caption("Summaries are AI-generated from public web search results. Follow source links for full context and corrections.")

st.divider()
st.caption("© NilanjanC · Personalized news brief")
