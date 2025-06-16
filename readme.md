# Bangladeshi News Scraper

This is a Python script that scrapes the latest news headlines and URLs from three popular Bangladeshi news websites:

- Prothom Alo
- Jugantor
- Ittefaq

The data is saved in a JSON file (`news_data.json`) and avoids duplicates using a hashed URL-based ID.

---

## Features

- Scrapes headlines and URLs from top Bangladeshi news sites
- Avoids duplicate entries
- Saves data in a readable and structured JSON format
- Easy to run and extend

---

## Requirements

- Python 3.x
- requests
- beautifulsoup4

Install dependencies using:

```bash
pip install requests beautifulsoup4
```

### How to Run

Clone or download this repository.

Run the scraper script:

```bash
python app.py
```

on MacOS or Linux, or:

```bash
python3 app.py
```

## Output

The output will be saved in a file named `news_data.json` in the same directory as the script. The JSON file will contain an array of news articles, each with a unique ID, headline, and URL.


## Example Output
```json
{
  "unique_id": {
    "source": "Prothom Alo",
    "headline": "সরাসরি: ইসরায়েলের তেল আবিবের বাসিন্দাদের অবিলম্বে সরে যেতে বলল ইরান",
    "url": "https://www.prothomalo.com/world/xyz",
    "id": "unique_id",
    "timestamp": "2025-06-16T14:30:00"
  }
}
```