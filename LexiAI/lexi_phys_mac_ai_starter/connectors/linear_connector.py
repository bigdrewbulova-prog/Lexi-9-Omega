import os
import requests

LINEAR_ENDPOINT = "https://api.linear.app/graphql"

def linear_query(query, variables=None):
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise RuntimeError("Missing LINEAR_API_KEY in .env")
    r = requests.post(
        LINEAR_ENDPOINT,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()
