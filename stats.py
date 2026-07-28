import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

token = os.getenv("TOKEN") or os.getenv("GITHUB_TOKEN") or ""
username = "mathis1M"



def require_token():
    if not token:
        raise RuntimeError("TOKEN or GITHUB_TOKEN is required")


def get_repositories():
    require_token()
    repositories = []
    page = 1

    while True:
        query = urlencode({
            "affiliation": "owner",
            "per_page": 100,
            "page": page,
            "visibility": "all",
        })
        request = Request(
            f"https://api.github.com/user/repos?{query}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "stats.py",
            },
        )

        with urlopen(request) as response:
            repositories.extend(json.load(response))

        if len(repositories) < page * 100:
            break
        page += 1

    return repositories


def getpublicandprivate():
    private = 0
    public = 0

    for repository in get_repositories():
        if repository["private"]:
            private += 1
        else:
            public += 1

    return private, public


def get_most_starred_and_forked():
    repositories = get_repositories()
    most_starred = max(
        repositories,
        key=lambda repository: repository["stargazers_count"],
        default=None,
    )
    most_forked = max(
        repositories,
        key=lambda repository: repository["forks_count"],
        default=None,
    )

    return most_starred, most_forked


def get_followers_and_following():
    require_token()
    request = Request(
        "https://api.github.com/user",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "stats.py",
        },
    )

    with urlopen(request) as response:
        user = json.load(response)

    return user["followers"], user["following"]


def get_total_commits():
    require_token()
    query = urlencode({"q": f"author:{username}", "per_page": 1})
    request = Request(
        f"https://api.github.com/search/commits?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "stats.py",
        },
    )

    with urlopen(request) as response:
        return json.load(response)["total_count"]


def get_language_percentages():
    totals = {}

    for repository in get_repositories():
        request = Request(
            repository["languages_url"],
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "stats.py",
            },
        )
        with urlopen(request) as response:
            languages = json.load(response)
        for language, amount in languages.items():
            totals[language] = totals.get(language, 0) + amount

    total = sum(totals.values())
    if not total:
        return []
    return [
        (language, round(amount / total * 100, 1))
        for language, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)[:3]
    ]


if __name__ == "__main__":
    private, public = getpublicandprivate()
    json_data = {
        "private_repos": private,
        "public_repos": public,
    }
    print(json.dumps(json_data, indent=4))
