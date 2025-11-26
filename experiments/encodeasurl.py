#!/usr/bin/env python3
import sys
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.strip())

    # Parse query string into key-value pairs
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)

    # Re-encode query parameters (spaces -> +, special chars -> %xx)
    encoded_query = urlencode(query_pairs, doseq=True)

    # Rebuild the URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        encoded_query,
        parsed.fragment
    ))
    return normalized

if __name__ == "__main__":
    # Read raw URL from stdin
    raw_url = sys.stdin.read().strip()
    safe_url = normalize_url(raw_url)

    # Print with quotes so it can be pasted directly into curl
    print(f'"{safe_url}"')
