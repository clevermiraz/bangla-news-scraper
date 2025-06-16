import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import hashlib
from urllib.parse import urljoin

OUTPUT_FILE = 'news_data.json'


def load_existing_data():
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def generate_id(url):
    return hashlib.md5(url.encode()).hexdigest()

# ✅ Prothom Alo


def scrape_prothom_alo():
    url = 'https://www.prothomalo.com'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    headlines = []
    links = soup.select('a.title-link')
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href')
        if text and href:
            full_url = urljoin(url, href)
            headlines.append({
                'source': 'Prothom Alo',
                'headline': text,
                'url': full_url,
                'id': generate_id(full_url),
                'timestamp': datetime.utcnow().isoformat()
            })
    return headlines

# ✅ Jugantor


def scrape_jugantor():
    url = 'https://www.jugantor.com'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    headlines = []
    articles = soup.select('div.desktopSectionLead')
    for article in articles:
        h3 = article.select_one('h3.title11')
        a = article.select_one('a.linkOverlay')
        if h3 and a:
            text = h3.get_text(strip=True)
            href = a.get('href')
            if text and href:
                full_url = urljoin(url, href)
                headlines.append({
                    'source': 'Jugantor',
                    'headline': text,
                    'url': full_url,
                    'id': generate_id(full_url),
                    'timestamp': datetime.utcnow().isoformat()
                })
    return headlines

# ✅ Ittefaq


def scrape_ittefaq():
    url = 'https://www.ittefaq.com.bd'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    headlines = []
    links = soup.select('a.link_overlay')
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href')
        if text and href:
            full_url = urljoin(url, href)
            headlines.append({
                'source': 'Ittefaq',
                'headline': text,
                'url': full_url,
                'id': generate_id(full_url),
                'timestamp': datetime.utcnow().isoformat()
            })
    return headlines

# ✅ Main Function


def main():
    existing_data = load_existing_data()
    all_data = {item['id']: item for item in existing_data.values()}

    for scraper in [scrape_prothom_alo, scrape_jugantor, scrape_ittefaq]:
        try:
            articles = scraper()
            for article in articles:
                if article['id'] not in all_data:
                    all_data[article['id']] = article
        except Exception as e:
            print(f"Error in scraper {scraper.__name__}: {e}")

    save_data(all_data)
    print(
        f"✅ Scraped {len(all_data)} unique headlines. Saved to '{OUTPUT_FILE}'.")


if __name__ == '__main__':
    main()
