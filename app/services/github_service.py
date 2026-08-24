"""
Thin wrapper around PyGithub for the operations this app needs:
fetching a PR's diff and posting a review comment back.
"""
from github import Github


def get_pr_diff(access_token: str, repo_full_name: str, pr_number: int) -> str:
    gh = Github(access_token)
    repo = gh.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    files = pr.get_files()
    diff_parts = []
    for f in files:
        diff_parts.append(f"--- {f.filename} ---\n{f.patch or '(binary or too large to diff)'}")

    return "\n\n".join(diff_parts)


def post_review_comment(access_token: str, repo_full_name: str, pr_number: int, body: str):
    gh = Github(access_token)
    repo = gh.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)


def register_webhook(access_token: str, repo_full_name: str, callback_url: str, secret: str) -> str:
    gh = Github(access_token)
    repo = gh.get_repo(repo_full_name)
    hook = repo.create_hook(
        name="web",
        config={
            "url": callback_url,
            "content_type": "json",
            "secret": secret,
        },
        events=["pull_request"],
        active=True,
    )
    return str(hook.id)
