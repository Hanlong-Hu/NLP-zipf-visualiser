import requests

def fetch_gutenberg(bookid : int):
    url = f"https://www.gutenberg.org/files/{bookid}/{bookid}-0.txt"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def fetch_wiki(title: str) -> str:
    """Fetch the plain-text extract of a Wikipedia article by title."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    pages = data.get("query", {}).get("pages", {})

    # The API returns pages keyed by page ID; "-1" means not found
    for page_id, page in pages.items():
        if page_id == "-1":
            raise ValueError(f"Wikipedia article not found: '{title}'")
        return page.get("extract", "")

    raise ValueError(f"Wikipedia article not found: '{title}'")
