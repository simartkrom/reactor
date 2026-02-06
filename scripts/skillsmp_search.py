#!/usr/bin/env python3
"""SkillsMP Search Script

Provides keyword and AI semantic search for the SkillsMP skills marketplace.

Usage:
    python skillsmp_search.py keyword <query> [page] [limit] [sort]
    python skillsmp_search.py ai <query>

Examples:
    python skillsmp_search.py keyword "web scraper" 1 20 stars
    python skillsmp_search.py ai "How to extract data from PDFs"
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://skillsmp.com/api/v1"


def get_api_key():
    """Retrieve the SkillsMP API key from environment variables."""
    api_key = os.environ.get("SKILLSMP_API_KEY")
    if not api_key:
        print("Error: SKILLSMP_API_KEY environment variable is not set.")
        print("Visit https://skillsmp.com/docs/api to generate an API key.")
        sys.exit(1)
    return api_key


def make_request(endpoint, params=None):
    """Make an authenticated GET request to the SkillsMP API."""
    api_key = get_api_key()
    url = f"{BASE_URL}{endpoint}"

    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.readable() else ""
        try:
            error_data = json.loads(error_body)
        except json.JSONDecodeError:
            error_data = {"message": error_body or str(e)}
        return {"success": False, "error": {"status": e.code, "message": error_data}}
    except urllib.error.URLError as e:
        return {"success": False, "error": {"status": 0, "message": f"Network error: {e.reason}"}}
    except Exception as e:
        return {"success": False, "error": {"status": 0, "message": str(e)}}


def keyword_search(query, page=1, limit=20, sort_by="stars"):
    """Execute a keyword-based search on the SkillsMP marketplace.

    Args:
        query: Search term.
        page: Page number (default: 1).
        limit: Results per page (default: 20, max: 100).
        sort_by: Sort order - 'stars' or 'recent' (default: 'stars').

    Returns:
        dict: API response with search results.
    """
    params = {
        "q": query,
        "page": page,
        "limit": min(limit, 100),
        "sort": sort_by,
    }
    return make_request("/skills/search", params)


def ai_search(query):
    """Execute an AI-powered semantic search on the SkillsMP marketplace.

    Args:
        query: Natural language question or description.

    Returns:
        dict: API response with search results.
    """
    params = {"q": query}
    return make_request("/skills/ai-search", params)


def format_results(results):
    """Format search results for display."""
    if not results.get("success", True):
        error = results.get("error", {})
        print(f"Error: {error.get('message', 'Unknown error')}")
        return

    skills = results.get("data", results.get("skills", []))
    total = results.get("total", len(skills))

    if not skills:
        print("No skills found matching your query.")
        return

    print(f"Found {total} skill(s):\n")

    for i, skill in enumerate(skills, 1):
        name = skill.get("name", "Unknown")
        description = skill.get("description", "No description")
        stars = skill.get("stars", 0)
        url = skill.get("url", "")

        print(f"  {i}. {name}")
        print(f"     {description}")
        print(f"     Stars: {stars}")
        if url:
            print(f"     URL: {url}")
        print()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    search_type = sys.argv[1].lower()
    query = sys.argv[2]

    if search_type == "keyword":
        page = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        sort_by = sys.argv[5] if len(sys.argv) > 5 else "stars"

        print(f"Keyword search: \"{query}\" (page={page}, limit={limit}, sort={sort_by})\n")
        results = keyword_search(query, page, limit, sort_by)

    elif search_type == "ai":
        print(f"AI search: \"{query}\"\n")
        results = ai_search(query)

    else:
        print(f"Unknown search type: {search_type}")
        print("Use 'keyword' or 'ai'.")
        sys.exit(1)

    format_results(results)


if __name__ == "__main__":
    main()
