"""GitHub App Authentication and Critique Sync Engine.

Authenticates as the GitHub App (dnd-scribe-bot) using the RSA private key in .secrets,
fetches open critique PRs, and bridges review feedback directly to the agent harness.
"""

import os
import sys
import time
import json
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
import jwt
import requests

# Root Paths
SCRIPT_DIR = Path(__file__).resolve().parent
HARNESS_DIR = SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
SECRETS_DIR = REPO_ROOT / ".secrets"
CONFIG_FILE = SECRETS_DIR / "app_config.json"


def find_private_key() -> Path:
    """Finds the .pem private key in the .secrets directory."""
    pem_files = list(SECRETS_DIR.glob("*.pem"))
    if not pem_files:
        raise FileNotFoundError(f"No .pem private key found in {SECRETS_DIR}")
    return pem_files[0]


def get_app_config() -> Dict[str, Any]:
    """Loads App ID and optional Installation ID from config or environment."""
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: could not read {CONFIG_FILE}: {e}")

    app_id = os.environ.get("GITHUB_APP_ID") or config.get("app_id")
    installation_id = os.environ.get("GITHUB_INSTALLATION_ID") or config.get("installation_id")

    return {
        "app_id": app_id,
        "installation_id": installation_id,
        "owner": config.get("owner", "ldstrebel"),
        "repo": config.get("repo", "dnd-scribe")
    }


def save_app_config(app_id: Optional[str] = None, installation_id: Optional[str] = None):
    """Saves App configuration to .secrets/app_config.json."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    existing = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    if app_id:
        existing["app_id"] = str(app_id)
    if installation_id:
        existing["installation_id"] = str(installation_id)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


class GitHubBotClient:
    def __init__(self, app_id: Optional[str] = None, pem_path: Optional[Path] = None):
        cfg = get_app_config()
        self.app_id = app_id or cfg.get("app_id")
        self.pem_path = pem_path or find_private_key()
        self.owner = cfg.get("owner", "ldstrebel")
        self.repo = cfg.get("repo", "dnd-scribe")
        self.installation_id = cfg.get("installation_id")
        self._installation_token: Optional[str] = None
        self._token_expiry: float = 0

        with open(self.pem_path, "r", encoding="utf-8") as f:
            self.private_key_content = f.read()

    def generate_jwt(self) -> str:
        """Generates a RS256 signed JWT for GitHub App authentication (valid for 9 minutes)."""
        if not self.app_id:
            raise ValueError("App ID is required. Pass it to GitHubBotClient or set in .secrets/app_config.json")

        now = int(time.time())
        payload = {
            "iat": now - 60,  # 60s in the past for clock drift
            "exp": now + (9 * 60),  # 9 minutes in the future
            "iss": str(self.app_id)
        }
        encoded_jwt = jwt.encode(payload, self.private_key_content, algorithm="RS256")
        return encoded_jwt

    def get_installations(self) -> List[Dict[str, Any]]:
        """Queries GitHub for all installations of this App."""
        app_jwt = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        res = requests.get("https://api.github.com/app/installations", headers=headers)
        if not res.ok:
            raise RuntimeError(f"Failed to fetch installations: {res.status_code} - {res.text}")
        return res.json()

    def get_installation_token(self, force_refresh: bool = False) -> str:
        """Retrieves or refreshes an installation access token (valid for 1 hour)."""
        now = time.time()
        if not force_refresh and self._installation_token and now < (self._token_expiry - 120):
            return self._installation_token

        # Auto-discover installation ID if not set
        if not self.installation_id:
            installations = self.get_installations()
            if not installations:
                raise RuntimeError(
                    f"No installations found for App ID {self.app_id}. "
                    "Did you install the app on your account in GitHub App settings?"
                )
            self.installation_id = str(installations[0]["id"])
            save_app_config(self.app_id, self.installation_id)
            print(f"[OK] Discovered and saved Installation ID: {self.installation_id}")

        app_jwt = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        res = requests.post(url, headers=headers)
        if not res.ok:
            raise RuntimeError(f"Failed to create installation access token: {res.status_code} - {res.text}")

        data = res.json()
        self._installation_token = data["token"]
        self._token_expiry = now + 3600
        return self._installation_token

    def list_open_critique_prs(self, repo_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all open PRs in the repository matching critique review branches."""
        token = self.get_installation_token()
        repo = repo_name or self.repo
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls?state=open"
        res = requests.get(url, headers=headers)
        if not res.ok:
            raise RuntimeError(f"Failed to fetch PRs: {res.status_code} - {res.text}")

        prs = res.json()
        critique_prs = []
        for pr in prs:
            branch = pr.get("head", {}).get("ref", "")
            title = pr.get("title", "").lower()
            if branch.startswith("critique/") or "critique" in title or "review:" in title:
                critique_prs.append(pr)
        return critique_prs

    def fetch_critique_payload_from_pr(self, pr_number: int, repo_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extracts critique JSON from PR files or embedded description block."""
        token = self.get_installation_token()
        repo = repo_name or self.repo
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # Check PR files for sessions/data/critiques/*.json
        files_url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls/{pr_number}/files"
        res = requests.get(files_url, headers=headers)
        if res.ok:
            files = res.json()
            for f in files:
                if f.get("filename", "").endswith(".json") and "critique" in f.get("filename", ""):
                    raw_url = f.get("raw_url")
                    raw_res = requests.get(raw_url, headers=headers)
                    if raw_res.ok:
                        try:
                            return raw_res.json()
                        except Exception:
                            pass

        # Fallback: Parse json from PR body markdown codeblock
        pr_url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls/{pr_number}"
        pr_res = requests.get(pr_url, headers=headers)
        if pr_res.ok:
            body = pr_res.json().get("body", "")
            if "```json" in body:
                try:
                    start = body.find("```json") + 7
                    end = body.find("```", start)
                    json_text = body[start:end].strip()
                    return json.loads(json_text)
                except Exception:
                    pass

        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Bot Authentication & Critique Engine")
    parser.add_argument("--set-app-id", type=str, help="Set and save GitHub App ID")
    parser.add_argument("--set-installation-id", type=str, help="Set and save Installation ID")
    parser.add_argument("--check-prs", action="store_true", help="List all open critique PRs")
    parser.add_argument("--generate-token", action="store_true", help="Generate and print a 1-hour Installation Token")
    args = parser.parse_args()

    if args.set_app_id or args.set_installation_id:
        save_app_config(app_id=args.set_app_id, installation_id=args.set_installation_id)
        print(f"[OK] Saved configuration: App ID={args.set_app_id}, Installation ID={args.set_installation_id}")

    bot = GitHubBotClient()

    if args.generate_token:
        try:
            token = bot.get_installation_token()
            print("\n[KEY] Generated 1-Hour GitHub App Token:")
            print(token)
        except Exception as e:
            print(f"[ERROR] Error generating token: {e}")

    if args.check_prs:
        try:
            prs = bot.list_open_critique_prs()
            print(f"\n[INFO] Found {len(prs)} open critique PR(s) in {bot.owner}/{bot.repo}:")
            for pr in prs:
                print(f"  * #{pr['number']}: {pr['title']} (branch: {pr['head']['ref']})")
                print(f"    URL: {pr['html_url']}")
        except Exception as e:
            print(f"[ERROR] Error listing PRs: {e}")
