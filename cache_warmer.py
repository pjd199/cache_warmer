"""Cache Warmer."""
from time import perf_counter_ns

from bs4 import BeautifulSoup, SoupStrainer
from requests import get, head


def main() -> None:
    """Download the root page, then downloads the linked pages."""
    root = "https://www.life-baptist.org.uk"
    headers = {
        "User-Agent": "Cache-Warmer",
    }

    response = get(root, headers=headers)
    if response.status_code == 200:
        print(f"Parsing links for {root}")
        soup = BeautifulSoup(response.text, "html.parser", parse_only=SoupStrainer("a"))
        links = {
            link.attrs["href"]
            for link in soup.find_all("a")
            if "href" in link.attrs and link["href"].startswith(root)
        }
        for link in sorted(links):
            start = perf_counter_ns()
            response = head(link, headers=headers)
            elapsed = (perf_counter_ns() - start) // 1000000
            text = (
                f"{link.replace(root,'')}"
                f" - status {response.status_code}"
                f", time {elapsed:,}ms"
            )
            if "x-origin-cache-status" in response.headers:
                text += f", cache: {response.headers['x-origin-cache-status']}"
            if "x-cdn-cache-status" in response.headers:
                text += f", cdn: {response.headers['x-cdn-cache-status']}"
            if elapsed >= 1000:
                text += ", ****** SLOW *****"
            print(text)
    else:
        print(f"Unable to download {root}")


if __name__ == "__main__":
    main()
