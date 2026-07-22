import os

def get_github_client():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing GITHUB_TOKEN in .env")
    from github import Github
    return Github(token)

def list_repos(limit=20):
    gh = get_github_client()
    repos = []
    for repo in gh.get_user().get_repos():
        repos.append(repo.full_name)
        if len(repos) >= limit:
            break
    return repos
