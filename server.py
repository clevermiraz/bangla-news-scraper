from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

# Import the existing scraper logic
from app import main as run_scraper, OUTPUT_FILE

app = FastAPI(title="Bangla News Scraper API")


@app.get("/", response_class=HTMLResponse)
def home_page() -> str:
    return (
        """
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>Bangla News Scraper</title>
            <style>
                body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'; margin: 0; padding: 0; background: #0f172a; color: #e2e8f0; }
                .container { max-width: 720px; margin: 64px auto; padding: 24px; }
                .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
                h1 { margin: 0 0 12px; font-size: 24px; }
                p { margin: 0 0 20px; color: #9ca3af; }
                .actions { display: flex; gap: 12px; }
                .btn { appearance: none; border: none; border-radius: 10px; padding: 12px 16px; font-weight: 600; cursor: pointer; }
                .btn.primary { background: #22c55e; color: #052e16; }
                .btn.secondary { background: #374151; color: #e5e7eb; }
                .btn:active { transform: translateY(1px); }
                a { color: #60a5fa; text-decoration: none; }
                .hint { margin-top: 16px; font-size: 14px; color: #94a3b8; }
            </style>
            <script>
                async function generateAndDownload() {
                    try {
                        const response = await fetch('/download');
                        if (!response.ok) {
                            const text = await response.text();
                            alert('Failed to generate file: ' + text);
                            return;
                        }
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'news_data.json';
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        window.URL.revokeObjectURL(url);
                    } catch (err) {
                        alert('Error: ' + err);
                    }
                }
            </script>
        </head>
        <body>
            <div class=\"container\">
                <div class=\"card\">
                    <h1>Bangla News Scraper</h1>
                    <p>Click the button to scrape latest headlines and download <code>news_data.json</code>.</p>
                    <div class=\"actions\">
                        <button class=\"btn primary\" onclick=\"generateAndDownload()\">Generate & Download</button>
                        <a class=\"btn secondary\" href=\"/file\" download>Download Last File</a>
                    </div>
                    <div class=\"hint\">Server must have internet access to scrape news sites.</div>
                </div>
            </div>
        </body>
        </html>
        """
    )


@app.get("/download")
def generate_and_download():
    # Run the scraper to regenerate the JSON file
    run_scraper()
    output_path = Path(OUTPUT_FILE).resolve()
    if not output_path.exists():
        return JSONResponse({"error": "Failed to generate output file"}, status_code=500)
    return FileResponse(
        path=str(output_path),
        media_type="application/json",
        filename=output_path.name,
    )


@app.get("/file")
def download_last_file():
    output_path = Path(OUTPUT_FILE).resolve()
    if not output_path.exists():
        return JSONResponse({"error": "File not found. Click 'Generate & Download' first."}, status_code=404)
    return FileResponse(
        path=str(output_path),
        media_type="application/json",
        filename=output_path.name,
    )
