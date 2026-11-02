# NilanjanC News Brief

A modular Streamlit app that creates short, topic-based Bengali/English news briefs and links back to the public source pages. Gemini Google Search grounding provides live web search and citation metadata; the app does not scrape or reproduce full articles.

## Run locally

1. Use Python 3.10 or newer.
2. From this folder, install dependencies:

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set your key in `.streamlit/secrets.toml` (recommended):

   ```toml
   GEMINI_API_KEY = "your-paid-gemini-api-key"
   ```

   Or set the `GEMINI_API_KEY` environment variable. Do not commit the key.
4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Use

Select newspapers, social platforms, one or more topics, or add comma-separated custom topics. Choose Latest or a specific year and English or Bengali summaries. Select “All” for the newspaper groups and social platforms.

## Source coverage

The outlet and platform choices guide Gemini's Google Search grounding; they are search preferences, not a guarantee that each selected site will appear in every result. Social sources are limited to publicly indexed posts/pages, not private or login-only feeds. Google Search grounding availability, quota, and pricing depend on your Gemini API project and model. The default model is `gemini-3.8-flash` and can be changed in `news_service.py`. The app uses the Gemini Interactions API with Google Search grounding.

The source catalog is in `source_catalog.py`; Gemini integration and citation extraction are in `news_service.py`; the Streamlit interface is in `app.py`.

