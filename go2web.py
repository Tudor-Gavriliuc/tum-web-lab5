import argparse
import os
import json

from http_client import HttpClient
from SetStructure import SetStructure
from find import Find

def main():
    parser = argparse.ArgumentParser(description='A simple web scraping tool')
    parser.add_argument('-u', '--url', help='Fetch the given URL')
    parser.add_argument('-s', '--search', help='Search term to look for')
    parser.add_argument('-link', type=int, help='Link number from search result')
    parser.add_argument("--json", action="store_true", help="Request JSON content")
    parser.add_argument("--html", action="store_true", help="Request HTML content")

    args = parser.parse_args()
    last_results_file = os.path.join(os.path.expanduser("~"), ".go2web_last_results")

    client = HttpClient()
    formatter = SetStructure()
    searcher = Find(client)

    if args.url:
        # Request format
        accept = None
        if args.json:
            accept = "application/json"
        elif args.html:
            accept = "text/html"

        response, headers = client.make_http_request(args.url, accept=accept)

        content_type = headers.get("Content-Type", "")
        if "application/json" in content_type:
            print(formatter.format_json_content(response))
        else:
            links = formatter.format_html_content(response)

            # Save links
            with open(last_results_file, "w") as f:
                json.dump([(text, link) for text, link in links], f)

    elif args.search:
        results = searcher.search(args.search)
        print(f"\n=== Search Results for '{args.search}' ===\n")

        if results:
            for i, (title, url) in enumerate(results):
                print(f"{i + 1}. {title}\n  {url}\n")

            with open(last_results_file, "w") as f:
                json.dump(results, f)
        else:
            print(f"No results for '{args.search}'")
    elif args.link is not None:
        if not os.path.exists(last_results_file):
            print(f"No previous results for '{args.search}'")
            return

        with open(last_results_file, "r") as f:
            results = json.load(f)

        if 1 <= args.link <= len(results):
            title, url = results[args.link - 1]
            print(f"\n=== Results for '{title}' - {url} ===\n")

            accept = None
            if args.json:
                accept = "application/json"
            elif args.html:
                accept = "text/html"

            response, headers = client.make_http_request(url, accept=accept)
            content_type = headers.get("Content-Type", "")
            if "application/json" in content_type:
                print(formatter.format_json_content(response))
            else:
                formatter.format_html_content(response)
        else:
            print(f"Invalid link number. Please choose between 1 and {len(results)}")

    else:
        parser.print_help()



if __name__ == '__main__':
    main()