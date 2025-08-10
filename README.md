## Bangla News Scraper

A small Python app that scrapes top headlines from leading Bangla news sites, enriches each article with extracted body text, and generates short Bangla summaries using Google's Gemini API (with an offline fallback when the API/key is unavailable). You can run it as a simple CLI to produce a JSON file or as a FastAPI server that lets you download a freshly generated dataset from a minimal web UI.

### Supported sources
- `https://www.prothomalo.com` (Prothom Alo)
- `https://www.jugantor.com` (Jugantor)
- `https://www.ittefaq.com.bd` (Ittefaq)

---

### Features
- **Headline scraping**: Pulls latest headlines and canonical links from the homepages above
- **Deduplication**: Uses an MD5 of the article URL as a stable `id`
- **Article text extraction**: Grabs readable content with light heuristics across common containers
- **Summarization**: Generates 2–3 sentence Bangla summaries via Gemini; falls back to a simple heuristic if the API/key is missing
- **Two ways to run**:
  - CLI: writes a timestamped JSON file
  - FastAPI server: one-click generate-and-download via web UI or `curl`

---

### How it works (architecture)
- `app.py`
  - Per-site scrapers: `scrape_prothom_alo`, `scrape_jugantor`, `scrape_ittefaq`
  - `extract_article_text_generic(url)`: fetches the article page and collects paragraphs from common content containers
  - `summarize_text_with_gemini(title, content)`: uses `GEMINI_API_KEY` via `google-genai` if available; otherwise falls back to a brief first-sentences summary
  - `scrape_all()`: runs all scrapers, deduplicates by URL-based MD5, sorts by timestamp
  - `generate_json_bytes_with_summaries()`: full pipeline (scrape → enrich → summarize) returning pretty JSON bytes
  - CLI `main()`: writes `news_data_YYYYMMDD_HHMMSS.json`
- `server.py`
  - FastAPI app with two routes:
    - `GET /` – a minimal HTML page with a button to generate and download the latest dataset
    - `GET /download` – generates fresh JSON and streams it back with a timestamped filename

Notes on deduplication:
- If a `news_data.json` file exists in the project root, it will be loaded to help deduplicate with past runs. Otherwise, deduplication occurs only within the current scrape.

---

### Requirements
- Python 3.10+
- A network connection from the machine running the app
- Optional: a Google Gemini API key for higher-quality summaries

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Configuration (optional)
Create a `.env` file in the project root to enable Gemini summaries:

```bash
GEMINI_API_KEY=your_api_key_here
# Optional (default: gemini-1.5-flash)
GEMINI_MODEL=gemini-1.5-flash
```

If `GEMINI_API_KEY` is missing, the app uses a simple local fallback summarizer.

---

### Run as CLI
Generate a new timestamped dataset with summaries:

```bash
python app.py
```

Output example: `news_data_20250101_120000.json`

---

### Run the FastAPI server
Start the server:

```bash
uvicorn server:app --reload --port 8000
```

- Visit `http://localhost:8000/` for a minimal UI. Click "Generate & Download" to get a fresh JSON file.
- Or use `curl`:

```bash
curl -L "http://localhost:8000/download" -o news_data.json
```

---

### Data format
Each item includes source metadata, URL, a stable `id`, extracted `content`, and a Bangla `summary`:

```json
{
  "source": "Prothom Alo",
  "headline": "শিরোনাম...",
  "url": "https://www.prothomalo.com/...",
  "id": "b1946ac92492d2347c6235b4d2611184",
  "timestamp": "2025-01-01T12:00:00.000000",
  "content": "পূর্ণ নিবন্ধের টেক্সট...",
  "summary": "২–৩ বাক্যে বাংলায় সারসংক্ষেপ..."
}
```

---

### Extending
- To add a new source:
  1. Create a new `scrape_<site>()` in `app.py`
  2. Parse the homepage, collect headline text and absolute URLs
  3. Return a list of dicts with the same shape used by existing scrapers
  4. Add your scraper to the list in `scrape_all()`
- The generic article extractor should work for many sites, but you can add site-specific extraction rules if needed.

---

### Operational notes and caveats
- Respect target sites' Terms of Service and robots.txt
- CSS selectors can change; if a site updates its layout, update the corresponding scraper
- Network, geo-blocking, or rate-limiting issues can cause partial data; try again later
- Summaries depend on the article text quality and API availability

---

### Troubleshooting
- No summaries? Ensure `.env` has a valid `GEMINI_API_KEY` and that outbound network access is permitted
- Empty `content`? The extractor may not match the site's structure; consider improving selectors or adding site-specific rules
- Server fails to start? Verify dependencies and Python version, then re-install packages
