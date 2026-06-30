import requests

def extract_github(username):
    """Calls the public GitHub API and returns raw profile data."""
    if not username:
        return None
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Warning: GitHub user '{username}' not found (status {response.status_code}).")
            return None
        data = response.json()
        repos_resp = requests.get(data.get("repos_url", ""), timeout=5)
        languages = set()
        if repos_resp.status_code == 200:
            for repo in repos_resp.json():
                if repo.get("language"):
                    languages.add(repo["language"])
        return {
            "name": data.get("name"),
            "bio": data.get("bio"),
            "github_url": data.get("html_url"),
            "languages": list(languages),
            "_source": "github"
        }
    except requests.exceptions.RequestException as e:
        print(f"Warning: GitHub API call failed ({e}), skipping.")
        return None