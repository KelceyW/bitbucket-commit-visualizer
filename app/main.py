import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from core.config import Settings

settings = Settings()
BITBUCKET_USERNAME = settings.bitbucket_username
BITBUCKET_APP_PASSWORD = settings.bitbucket_app_password
BITBUCKET_WORKSPACE = settings.bitbucket_workspace

API_BASE = 'https://api.bitbucket.org/2.0'
headers = {"Content-Type": "application/json"}


def fetch_repositories():
    print("Fetching repositories...")
    repos = []
    url = f"{API_BASE}/repositories/{BITBUCKET_WORKSPACE}"
    while url:
        resp = requests.get(url, auth=(
            BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        resp.raise_for_status()
        data = resp.json()
        repos.extend(data.get('values', []))
        url = data.get('next')
    return [repo['slug'] for repo in repos]


def fetch_commits(repo_slug):
    print(f"Fetching commits for repo: {repo_slug}")
    commits = []
    url = f"{API_BASE}/repositories/{BITBUCKET_WORKSPACE}/{repo_slug}/commits"
    while url:
        resp = requests.get(url, auth=(
            BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))
        resp.raise_for_status()
        data = resp.json()
        commits.extend(data.get('values', []))
        url = data.get('next')
    return commits


def collect_user_commits(repos):
    commit_dates = []
    for repo in repos:
        try:
            commits = fetch_commits(repo)
            for commit in commits:
                author = commit.get('author', {}).get('user', {}).get('display_name', {})
                if author == settings.bitbucket_display_name:
                    date_str = commit['date']
                    date_obj = datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S')
                    commit_dates.append(date_obj)
        except Exception as e:
            print(f"Failed to fetch from {repo}: {e}")
    return commit_dates


def plot_commits(dates, by='month'):
    df = pd.DataFrame({'date': dates})
    df['date'] = pd.to_datetime(df['date'])
    if by == 'month':
        df['period'] = df['date'].dt.to_period('M').astype(str)
    else:
        df['period'] = df['date'].dt.to_period('W').astype(str)

    commits_by_period = df['period'].value_counts().sort_index()

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.barplot(x=commits_by_period.index, y=commits_by_period.values, palette="viridis")
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Period')
    plt.ylabel('Number of Commits')
    plt.title(f"Your Bitbucket Contributions by {by.capitalize()}")
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    repos = fetch_repositories()
    commit_dates = collect_user_commits(repos)
    if commit_dates:
        period = input("View contributions by 'month' or 'week'? (default is month): ").strip().lower() or 'month'
        plot_commits(commit_dates, by=period)
    else:
        print("No contributions found.")
