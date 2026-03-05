# 📰 Vestige

> **A Python library for fetching and parsing issues of the Bulgarian State Gazette (Държавен вестник).**

Vestige gives you a clean, dependency-light Python interface to the official [Държавен вестник](https://dv.parliament.bg/) listing. Scrape issue metadata and download links without wrestling with raw HTML or cryptic JSF form fields ever again.

## ✨ Features

- **📄 Issue Listings**: Fetch paginated lists of State Gazette issues, including issue number, date, year, and type.
- **📥 Download Links**: Automatically resolve the PDF and RTF download URLs for each issue.
- **🔌 Pluggable Architecture**: Swap out the HTTP transport or the HTML parser via simple interfaces — great for testing with mocks.
- **🗂️ Typed Models**: Clean dataclasses (`IssueEntry`, `DownloadFile`, `PageResult`) with `to_dict()` helpers for easy JSON serialisation.
- **⚡ Minimal Dependencies**: Only needs `requests` and `beautifulsoup4`.

## 📥 Installation

```bash
pip install vestige-scraper
```

Or, to install directly from source:

```bash
pip install .
```

## 🚀 Quick Start

```python
from vestige import DVClient

client = DVClient()

# Fetch the first page of issues (with download URLs resolved)
page = client.get_page(1)

print(page)
# PageResult(page=1, total_results=..., total_pages=..., entries=...)

for entry in page.entries:
    print(entry)
    for file in entry.download_urls:
        print(f"  → {file.filename}: {file.url}")
```

### Fetch all pages at once

```python
all_pages = client.get_all_pages(max_pages=5)

for page in all_pages:
    for entry in page.entries:
        print(entry.to_dict())
```

### Skip download URL resolution (faster)

```python
page = client.get_page(1, fetch_downloads=False)
```

## 🗂️ Models

| Class | Description |
|-------|-------------|
| `IssueEntry` | One issue of the State Gazette — number, date, year, type, and download files. |
| `DownloadFile` | A single downloadable file (`url`, `filename`). |
| `PageResult` | One page of results — holds metadata and a list of `IssueEntry` objects. |

## ⚙️ Advanced Usage

### Custom transport / parser (e.g. for testing)

```python
from vestige import DVClient
from vestige.network.transport import RequestsTransport
from vestige.scraping.parsers import IssueParser

client = DVClient(
    transport=MyCustomTransport(),
    parser=MyCustomParser(),
)
```

Both `transport` and `parser` accept any object that satisfies the `PageFetcher` and `PageParser` interfaces defined in `vestige.core.interfaces`.

## 🐍 Requirements

- Python **3.10+**
- `requests >= 2.31`
- `beautifulsoup4 >= 4.12`

## 🤝 Contributing

Issues and pull requests are welcome! Please file an issue if you encounter any problems or have suggestions for improvements.

---
*Built with ❤️ for Bulgaria's open data. MIT Licensed.*
