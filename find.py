from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from http_client import HttpClient


class Find:
    def __init__(self, http_client=None):
        """Initialize the Search class with an optional HttpClient instance"""
        self.http_client = http_client if http_client else HttpClient()

    def search(self, term, search_engine="duckduckgo", max_results=10):
        """Search for a term using the specified search engine"""
        if search_engine == "duckduckgo":
            return self._search_duckduckgo(term, max_results)
        else:
            print(f"Search engine '{search_engine}' not supported")
            return []

    def _search_duckduckgo(self, term, max_results=10):
        """Perform a search using DuckDuckGo"""
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(term)}"
        print(f"Searching for: {search_url}")

        response, headers = self.http_client.make_http_request(search_url)

        return self._parse_duckduckgo_results(response, max_results)

    def _parse_duckduckgo_results(self, html_content, max_results=10):
        """Parse search results from DuckDuckGo HTML response"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        for result in soup.find_all('div', class_='result__body'):
            a_tag = result.find('a', class_='result__a')
            if a_tag and 'href' in a_tag.attrs:
                link = a_tag['href']
                if link.startswith("//duckduckgo.com/l/?uddg="):
                    actual_url = link.split("uddg=")[1].split("&")[0]
                    actual_url = actual_url.replace("%3A", ":").replace("%2F", "/")
                    links.append((a_tag.get_text(), actual_url))
                    if len(links) >= max_results:
                        break

        return links


# For backward compatibility
def search(term, search_engine="duckduckgo", http_client=None, max_results=10):
    searcher = Find(http_client)
    return searcher.search(term, search_engine, max_results)