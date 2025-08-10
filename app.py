import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Iterable, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Legacy default output (kept for CLI compatibility)
OUTPUT_FILE = "news_data.json"


def load_existing_data():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data_to_path(data: Dict[str, dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_data(data: Dict[str, dict]) -> None:
    """Backward compatible save to legacy OUTPUT_FILE."""
    save_data_to_path(data, OUTPUT_FILE)


def generate_id(url):
    return hashlib.md5(url.encode()).hexdigest()


# ✅ Prothom Alo


def scrape_prothom_alo():
    url = "https://www.prothomalo.com"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    headlines = []
    links = soup.select("a.title-link")
    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")
        if text and href:
            full_url = urljoin(url, href)
            headlines.append(
                {
                    "source": "Prothom Alo",
                    "headline": text,
                    "url": full_url,
                    "id": generate_id(full_url),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    return headlines


# ✅ Jugantor


def scrape_jugantor():
    url = "https://www.jugantor.com"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    headlines = []
    articles = soup.select("div.desktopSectionLead")
    for article in articles:
        h3 = article.select_one("h3.title11")
        a = article.select_one("a.linkOverlay")
        if h3 and a:
            text = h3.get_text(strip=True)
            href = a.get("href")
            if text and href:
                full_url = urljoin(url, href)
                headlines.append(
                    {
                        "source": "Jugantor",
                        "headline": text,
                        "url": full_url,
                        "id": generate_id(full_url),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
    return headlines


# ✅ Ittefaq


def scrape_ittefaq():
    url = "https://www.ittefaq.com.bd"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    headlines = []
    links = soup.select("a.link_overlay")
    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")
        if text and href:
            full_url = urljoin(url, href)
            headlines.append(
                {
                    "source": "Ittefaq",
                    "headline": text,
                    "url": full_url,
                    "id": generate_id(full_url),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    return headlines


# -------- Details extraction and summarization -------- #


def extract_article_text_generic(url: str) -> str:
    """Fetch article URL and extract readable text with simple heuristics."""
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(res.text, "html.parser")

    containers: List[BeautifulSoup] = []
    article_tag = soup.find("article")
    if article_tag:
        containers.append(article_tag)

    for selector in [
        '[itemprop="articleBody"]',
        ".article-body",
        ".story",
        ".story-body",
        ".details",
        ".detail-body",
        ".content",
        "#content",
        ".news-content",
    ]:
        found = soup.select_one(selector)
        if found and found not in containers:
            containers.append(found)

    if not containers:
        containers = [soup.body] if soup.body else []

    paragraphs: List[str] = []
    for container in containers:
        for p in container.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 40:
                paragraphs.append(text)
        if paragraphs:
            break

    if not paragraphs:
        texts: List[str] = [
            el.get_text(strip=True) for el in soup.select("div,section")
        ]
        texts = [t for t in texts if len(t) > 60]
        paragraphs = texts[:8]

    return "\n".join(paragraphs[:20])


def summarize_text_with_gemini(title: str, content: str) -> str:
    """Summarize article content using Gemini (new SDK only); fallback if missing."""
    if not content:
        return ""

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai as genai_new  # type: ignore

            client = genai_new.Client(api_key=api_key)
            model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            prompt = (
                "আপনি একজন সংবাদ সহকারী। নিচের খবরের সারমর্ম ২-৩ বাক্যে বাংলায় সংক্ষেপে লিখুন। "
                "কোনো মতামত বা অলংকার যোগ করবেন না, কেবল মূল তথ্য দিন।\n\n"
                f"শিরোনাম: {title}\n\n"
                f"বিবরণ: {content[:6000]}\n"
            )
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = (
                getattr(response, "output_text", None)
                or getattr(response, "text", None)
                or ""
            )
            if not text:
                try:
                    text = response.candidates[0].content.parts[0].text  # type: ignore[attr-defined]
                except Exception:
                    text = ""
            if text:
                return text[:800]
        except Exception:
            pass

    # Fallback when API/key unavailable
    text = content.strip()
    if not text:
        return ""
    for sep in ["।", ".", "!", "?"]:
        parts = text.split(sep)
        if len(parts) > 1:
            summary = sep.join(parts[:2]).strip()
            if not summary.endswith(sep):
                summary += sep
            return summary[:500]
    return text[:500]


def enrich_with_details_and_summary(articles: Iterable[dict]) -> List[dict]:
    enriched: List[dict] = []
    for article in articles:
        content = extract_article_text_generic(article["url"])
        summary = summarize_text_with_gemini(article["headline"], content)
        enriched.append({**article, "content": content, "summary": summary})
    return enriched


def scrape_all() -> List[dict]:
    """Scrape all sources, deduplicate, and return as a list."""
    existing_data = load_existing_data()
    all_by_id: Dict[str, dict] = {item["id"]: item for item in existing_data.values()}

    for scraper in [scrape_prothom_alo, scrape_jugantor, scrape_ittefaq]:
        try:
            for article in scraper():
                if article["id"] not in all_by_id:
                    all_by_id[article["id"]] = article
        except Exception as e:
            print(f"Error in scraper {scraper.__name__}: {e}")

    items = list(all_by_id.values())
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return items


def generate_json_bytes_with_summaries() -> bytes:
    """Full pipeline: scrape -> fetch details -> summarize -> JSON bytes."""
    base_articles = scrape_all()
    enriched = enrich_with_details_and_summary(base_articles)
    return json.dumps(enriched, ensure_ascii=False, indent=2).encode("utf-8")


# ✅ Main Function


def main():
    """CLI behavior: generate fresh enriched data to a timestamped file."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = f"news_data_{timestamp}.json"
    json_bytes = generate_json_bytes_with_summaries()
    # Store pretty JSON to timestamped file
    save_data_to_path(json.loads(json_bytes.decode("utf-8")), output_file)
    print(f"✅ Generated fresh data with summaries. Saved to '{output_file}'.")


if __name__ == "__main__":
    main()
