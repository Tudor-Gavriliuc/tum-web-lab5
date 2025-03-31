from urllib.parse import urlparse
import socket
import ssl
import gzip
import zlib

from cache import Cache


class HttpClient:
    def __init__(self, cache=None):
        self.cache = cache if cache else Cache()

    def make_http_request(self, url, method="GET", headers=None, data=None, follow_redirects=True, accept=None, max_redirects=5):
        cached_response = self._check_cache(url, method, accept)
        if cached_response:
            return cached_response

        parsed_url = self._parse_url(url)
        request_headers = self._prepare_headers(parsed_url, headers, accept)
        request_data = self._build_request(method, parsed_url, request_headers, data)

        try:
            response, response_headers, status_code = self._send_request(parsed_url, request_data)

            if self._should_redirect(follow_redirects, status_code, response_headers, max_redirects):
                return self._handle_redirect(
                    parsed_url, response_headers, method, headers, data,
                    follow_redirects, accept, max_redirects
                )

            decoded_body = self._process_response(response, response_headers)
            # Cache successful GET responses
            if method == "GET" and status_code == 200:
                self._cache_response(url, decoded_body, response_headers, accept)

            return decoded_body, response_headers

        except Exception as e:
            return f"Error occurred: {str(e)}", {}

    def _check_cache(self, url, method, accept):
        """Check if a cached response exists and return it if valid"""
        if method != "GET":
            return None

        if accept:
            cached_response, cached_headers = self.cache.get(url, accept)
        else:
            cached_response, cached_headers = self.cache.get(url)

        if cached_response:
            print("Using cached response")
            return cached_response, cached_headers

        return None

    def _cache_response(self, url, response, headers, content_type=None):
        """Cache the response if it's a GET request"""
        if content_type:
            self.cache.set(url, response, headers, content_type)
        else:
            self.cache.set(url, response, headers)
