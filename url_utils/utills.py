from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def update_url(
    url: str,
    scheme: Optional[str] = None,
    host: Optional[str] = None,
    path: Optional[str] = None,
    fragment: Optional[str] = None,
    query_params: Optional[dict] = None,
) -> str:
    """
    Update different parts of a URL in a clean and controlled way.

    Args:
        url (str)        : Original URL string
        scheme (str)     : New scheme (e.g. 'https', 'http')
        host (str)       : New host/domain (e.g. 'example.com')
        path (str)       : New path (e.g. '/api/v2')
        fragment (str)   : New fragment (e.g. 'section1')
        query_params (dict): Dictionary of query parameters to update/add

    Returns:
        str : Updated URL string
    """
    parsed = urlparse(url)

    # Parse existing query string into dict
    query = parse_qs(parsed.query)

    # Update query parameters if provided
    if query_params:
        for k, v in query_params.items():
            query[k] = [str(v)]

    # Rebuild query string
    new_query = urlencode(query, doseq=True)

    # Replace parts with new values if provided
    updated = parsed._replace(
        scheme=scheme or parsed.scheme,
        netloc=host or parsed.netloc,
        path=path or parsed.path,
        fragment=fragment or parsed.fragment,
        query=new_query
    )

    return urlunparse(updated)
