import sys
import re
import json
from bs4 import BeautifulSoup

class SetStructure:
    @staticmethod
    def format_html_content(content):
        soup = BeautifulSoup(content, 'html.parser')

        title = soup.title.string if soup.title else "No title"
        print(f"\n=== {title} ===\n")

        # Print the content with minimal formatting
        visible_text = []
        for text in soup.stripped_strings:
            visible_text.append(text)

        formatted_text = "\n".join(visible_text)
        # Remove excessive newlines
        formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)

        # Handle encoding errors when printing
        try:
            print(formatted_text)
        except UnicodeEncodeError:
            # Replace characters that can't be encoded with a question mark
            print(formatted_text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

        print("\n=== Links ===\n")
        links = []
        for i, a in enumerate(soup.find_all('a', href=True)):
            link_text = a.get_text()
            # Handle encoding errors for link text too
            try:
                print(f"{i + 1}. {link_text}: {a['href']}")
            except UnicodeEncodeError:
                safe_text = link_text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                print(f"{i + 1}. {safe_text}: {a['href']}")
            links.append((link_text, a['href']))

        return links

    @staticmethod
    def format_json_content(content):
        try:
            json_data = json.loads(content)
            return json.dumps(json_data, indent=2)
        except:
            return content