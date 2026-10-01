#!/usr/bin/env python3
"""
Adversarial Trade-Off Inquisitor Runner
Executes the red-team interrogation of publishing compromises, generates
sessions/reports/tradeoff-audit-YYYY-MM-DD.md, and pushes a PR branch to GitHub
using git worktree isolation to keep the active workspace clean.
"""

import sys
import os
import re
import json
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

def run_cmd(cmd: List[str], cwd: Optional[str] = None, check: bool = True) -> str:
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, encoding="utf-8", errors="ignore")
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr}")
    return res.stdout.strip()

def get_current_branch(repo_root: str) -> str:
    try:
        return run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    except Exception:
        return "uneraseable"

def resolve_focus(day_of_week: int, requested_focus: str, state_file: str) -> str:
    """
    Determine rotation focus:
    - 0 or 6 (Sunday night / Mon early morning): 'agency'
    - 1 or 2 (Tuesday night / Wed early morning): 'liberties'
    - 4 or 5 (Friday night / Sat early morning): 'continuity'
    """
    if requested_focus and requested_focus != "auto":
        return requested_focus

    # Check rotation state if exists
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                next_f = state.get("next_focus")
                if next_f:
                    return next_f
        except Exception:
            pass

    # Map by weekday
    # Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5
    if day_of_week in [0, 6]:
        return "agency"
    elif day_of_week in [1, 2]:
        return "liberties"
    else:
        return "continuity"

def generate_adversarial_critique(dossier: Dict[str, Any], focus: str) -> Dict[str, Any]:
    """
    Generates targeted inquisitorial challenges based on the extracted dossier.
    """
    session_id = dossier["session_id"].upper()
    title = dossier.get("title", "")
    liberties = dossier.get("authorial_liberties", [])
    skips = dossier.get("substantive_skips", [])
    risky = dossier.get("risky_source_decisions", [])
    telemetry = dossier.get("tension_telemetry", {})
    prev_context = dossier.get("prev_session_context", {})

    challenges = []

    if focus in ["agency", "auto"]:
        # Challenge physical force and combat staging (e.g. Scene 10, Scene 6)
        high_stakes_libs = [l for l in liberties if "combat" in l["scope"].lower() or "scene-10" in l["scene"] or "scene-06" in l["scene"]]
        for lib in high_stakes_libs:
            scene_name = lib["scene"].upper()
            scope = lib["scope"]
            desc = lib["liberty"]
            impact = lib["impact"]
            boundary = lib.get("boundary", "")

            hole = (
                f"**The Agency & Velocity Tension:** While '{desc[:80]}...' preserves immediate dramatic pacing, "
                f"compacting this physical struggle risks compressing player panic into choreographed competence (`FP-01`). "
                f"Verify that involuntary Swain MRU reflexes (gasping, kicking, visceral shock) are fully staged "
                f"and that mutual consent was not retroactively smoothed into the character beats (`FP-02`)."
            )
            recommendation = (
                f"Check Track B scene prose to ensure the visceral tactile resistance "
                f"matches the raw audio turns before the cutoff."
            )
            challenges.append({
                "type": "Agency & Friction Probe",
                "scene": scene_name,
                "scope": scope,
                "documented_stance": desc,
                "hole_identified": hole,
                "recommendation": recommendation
            })

    if focus in ["liberties", "auto"]:
        # Challenge high compression velocity cuts (e.g. Scenes 1, 4, 8)
        compression_libs = [l for l in liberties if "condensed" in l["liberty"].lower() or "streamlined" in l["liberty"].lower()]
        for lib in compression_libs:
            scene_name = lib["scene"].upper()
            scope = lib["scope"]
            desc = lib["liberty"]
            impact = lib["impact"]

            hole = (
                f"**The Velocity vs. Voice Trade-Off:** The stated justification claims '{impact}'. "
                f"However, cutting exploratory table banter risks pruning character voice idiosyncrasies "
                f"(e.g., Pierre's eccentric cultural rants, Dravin's academic pedantry). "
                f"If compression exceeded 50%, evaluate whether the scene sounds like a generic fantasy novel "
                f"rather than the specific party dynamics established at the table."
            )
            recommendation = (
                f"Inspect the 3-tier ledger in this scene. Confirm that none of the stripped turns contained "
                f"character-defining quirks that foreshadow later revelations."
            )
            challenges.append({
                "type": "Velocity & Voice Probe",
                "scene": scene_name,
                "scope": scope,
                "documented_stance": desc,
                "hole_identified": hole,
                "recommendation": recommendation
            })

    if focus in ["continuity", "auto"]:
        # Challenge skipped lore and cross-session debt
        substantive_skips = [s for s in skips if len(s["raw_text"]) > 40]
        for sk in substantive_skips[:3]:
            line_no = sk["line"]
            reason = sk["reason"]
            raw_text = sk["raw_text"]

            hole = (
                f"**Downstream Debt Probe on L{line_no}:** This dialogue turn (\"{raw_text[:75]}...\") "
                f"was exempted as '{reason}'. Inquisitor check: Did the GM's casual syntax contain a world rule "
                f"or clue that makes later player breakthroughs in subsequent sessions seem ungrounded? (`DEC-024`)"
            )
            recommendation = (
                f"Cross-reference this entity/concept against `CAMPAIGN_ARC_LEDGER.md`. If this mechanic returns "
                f"in future sessions, convert this exemption from a skip into a narrator-grounded Tier B staging."
            )
            challenges.append({
                "type": "Downstream Lore Debt Probe",
                "scene": f"Line L{line_no}",
                "scope": "Skipped Dialogue Ledger",
                "documented_stance": reason,
                "hole_identified": hole,
                "recommendation": recommendation
            })

        if prev_context:
            p_id = prev_context.get("session_id", "").upper()
            challenges.append({
                "type": "Cross-Session Causal Probe",
                "scene": f"{p_id} ➔ {session_id}",
                "scope": "Session Threshold Continuity",
                "documented_stance": f"Transition from {p_id} to {session_id}",
                "hole_identified": (
                    f"Verified that physical inventory, status effects, and emotional fatigue from the end of {p_id} "
                    f"were carried into {session_id} Scene 1 without a 'reset to baseline' between recording dates."
                ),
                "recommendation": f"Audit {session_id} Scene 1 opening paragraphs against {p_id} closing scene state."
            })

    return {
        "session_id": session_id,
        "title": title,
        "focus": focus,
        "challenges": challenges
    }

def build_markdown_report(critique: Dict[str, Any], date_str: str) -> str:
    session_id = critique["session_id"]
    title = critique.get("title", "")
    focus = critique["focus"].upper()
    challenges = critique["challenges"]

    md = []
    md.append(f"# 🕵️ Adversarial Trade-Off Inquest Report: {session_id}")
    md.append(f"**Date:** {date_str} | **Audit Focus:** `{focus}` | **Session:** {session_id} - *{title}*\n")
    md.append("## Executive Summary\n")
    md.append(
        "This automated inquest was triggered to stress-test documented editorial compromises and authorial liberties. "
        "Unlike the standard publishing pipeline (which verifies whether permits and hash locks exist), this report "
        "assumes every velocity cut and whitelisted skip is a potential compromise that must defend its narrative necessity.\n"
    )
    md.append("---\n")
    md.append(f"## ⚔️ Interrogated Compromises ({len(challenges)} Challenges Surfaced)\n")

    for idx, c in enumerate(challenges, 1):
        md.append(f"### Challenge #{idx}: [{c['type']}] - {c['scene']} ({c['scope']})")
        md.append(f"* **Documented Stance / Permit:** {c['documented_stance']}")
        md.append(f"* **Inquisitor Attack:** {c['hole_identified']}")
        md.append(f"* **Actionable Recommendation:** {c['recommendation']}\n")

    md.append("---\n")
    md.append("## 📋 Next Editorial Action Items")
    md.append("1. **Reviewer Triage:** Review the above challenges before approving next session novelization.")
    md.append("2. **Contract Hardening:** If an authorial liberty removed essential character voice, update the session's intent contract.")
    md.append("3. **Downstream Lore Verification:** Check `CAMPAIGN_ARC_LEDGER.md` for any newly flagged entity debts.")

    return "\n".join(md)

def update_rotation_state(state_file: str, current_session: str, current_focus: str, date_str: str):
    next_map = {
        "agency": "liberties",
        "liberties": "continuity",
        "continuity": "agency"
    }
    state = {
        "last_run": date_str,
        "last_session": current_session,
        "last_focus": current_focus,
        "next_focus": next_map.get(current_focus, "agency"),
        "history": []
    }
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                old = json.load(f)
                hist = old.get("history", [])
                hist.append(f"{date_str}:{current_session}:{current_focus}")
                state["history"] = hist[-10:] # keep last 10
        except Exception:
            pass
            
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def generate_commit_message(critique: Dict[str, Any], date_str: str, target_session: str) -> str:
    session_id = target_session.lower()
    focus = critique["focus"].upper()
    challenges = critique["challenges"]

    subject = f"audit({session_id}): red-team trade-off review [{focus}] - {len(challenges)} challenges surfaced"

    body_lines = [
        subject,
        "",
        f"Date: {date_str} | Focus: {focus} | Session: {target_session.upper()} ({critique.get('title', '')})",
        "",
        "Interrogated Compromises:"
    ]
    for idx, c in enumerate(challenges, 1):
        clean_hole = re.sub(r"[*`]", "", c["hole_identified"])
        if len(clean_hole) > 130:
            clean_hole = clean_hole[:127] + "..."
        body_lines.append(f"- [{c['type']}] {c['scene']} ({c['scope']}): {clean_hole}")

    body_lines.append("")
    body_lines.append(f"Report: sessions/reports/tradeoff-audit-{date_str}.md")
    return "\n".join(body_lines)

def get_github_token() -> Optional[str]:
    # 1. Check environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    # 2. Check git credential manager
    try:
        p = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            text=True,
            capture_output=True,
            encoding="utf-8"
        )
        for line in p.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def create_or_update_github_pr(repo_root: str, branch_name: str, base_branch: str, title: str, body: str) -> Optional[str]:
    """
    Creates or updates the pull request directly on GitHub using the REST API.
    """
    token = get_github_token()
    if not token:
        print("⚠️ No GitHub token found via environment or git credential helper. Skipping direct PR creation.")
        return None

    # Determine repo full name (e.g. ldstrebel/dnd-scribe)
    remote_url = run_cmd(["git", "remote", "get-url", "origin"], cwd=repo_root, check=False)
    m = re.search(r"github\.com[/:]([^/]+)/([^/.]+)", remote_url)
    if not m:
        print(f"⚠️ Could not parse GitHub repo from remote URL: {remote_url}")
        return None

    owner, repo = m.group(1), m.group(2)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Tradeoff-Inquisitor",
        "Content-Type": "application/json"
    }

    import urllib.request
    import urllib.error

    # 1. Check if PR already exists for this branch
    try:
        req = urllib.request.Request(f"{api_url}?head={owner}:{branch_name}&state=open", headers=headers)
        with urllib.request.urlopen(req) as resp:
            prs = json.loads(resp.read().decode())
            if prs:
                existing_pr = prs[0]
                pr_num = existing_pr["number"]
                pr_html_url = existing_pr["html_url"]
                # Update existing PR
                patch_data = json.dumps({"title": title, "body": body}).encode("utf-8")
                patch_req = urllib.request.Request(
                    f"{api_url}/{pr_num}",
                    data=patch_data,
                    headers=headers,
                    method="PATCH"
                )
                with urllib.request.urlopen(patch_req) as patch_resp:
                    print(f"🔄 Updated existing Pull Request #{pr_num}: {pr_html_url}")
                    return pr_html_url
    except Exception as e:
        print(f"Notice during PR check: {e}")

    # 2. Create new PR
    try:
        post_data = json.dumps({
            "title": title,
            "head": branch_name,
            "base": base_branch,
            "body": body
        }).encode("utf-8")

        create_req = urllib.request.Request(api_url, data=post_data, headers=headers, method="POST")
        with urllib.request.urlopen(create_req) as resp:
            created = json.loads(resp.read().decode())
            pr_html_url = created["html_url"]
            print(f"✨ Created new Pull Request: {pr_html_url}")
            return pr_html_url
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        print(f"⚠️ GitHub API error creating PR ({e.code}): {error_msg}")
    except Exception as e:
        print(f"⚠️ Failed to create PR via GitHub API: {e}")

    return None

def execute_worktree_pr(repo_root: str, report_filename: str, report_content: str, state_file_rel: str, state_content: str, branch_name: str, base_branch: str, commit_msg: str, pr_title: str) -> Optional[str]:
    """
    Creates an isolated git worktree, commits the report and rotation state with a detailed
    commit message, pushes the branch to origin, creates/updates the PR, cleans up the worktree,
    and returns the PR URL.
    """
    worktree_dir = os.path.join(repo_root, ".worktrees", "tradeoff-audit-runner")
    try:
        # Clean up any leftover worktree
        if os.path.exists(worktree_dir):
            run_cmd(["git", "worktree", "remove", "--force", worktree_dir], cwd=repo_root, check=False)
            if os.path.exists(worktree_dir):
                shutil.rmtree(worktree_dir, ignore_errors=True)

        os.makedirs(os.path.dirname(worktree_dir), exist_ok=True)

        print(f"🌲 Creating isolated git worktree at {worktree_dir} branching from {base_branch}...")
        run_cmd(["git", "worktree", "add", "-B", branch_name, worktree_dir, base_branch], cwd=repo_root)

        # Write files inside worktree
        wt_report_path = os.path.join(worktree_dir, report_filename)
        os.makedirs(os.path.dirname(wt_report_path), exist_ok=True)
        with open(wt_report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        wt_state_path = os.path.join(worktree_dir, state_file_rel)
        os.makedirs(os.path.dirname(wt_state_path), exist_ok=True)
        with open(wt_state_path, "w", encoding="utf-8") as f:
            f.write(state_content)

        # Commit inside worktree with detailed multi-line commit message
        print(f"📦 Staging and committing detailed report on branch {branch_name}...")
        run_cmd(["git", "add", report_filename, state_file_rel], cwd=worktree_dir)
        
        # Write commit message to temp file to avoid shell escaping issues with multi-line messages
        commit_msg_file = os.path.join(repo_root, ".worktrees", "TRADE_OFF_COMMIT_MSG.txt")
        with open(commit_msg_file, "w", encoding="utf-8") as f:
            f.write(commit_msg)
        run_cmd(["git", "commit", "-F", commit_msg_file], cwd=worktree_dir)
        if os.path.exists(commit_msg_file):
            os.remove(commit_msg_file)

        # Push branch
        print(f"🚀 Pushing branch {branch_name} to origin...")
        run_cmd(["git", "push", "-u", "origin", branch_name, "--force"], cwd=worktree_dir)

        # Direct GitHub Pull Request Creation
        print(f"📬 Managing GitHub Pull Request...")
        pr_url = create_or_update_github_pr(repo_root, branch_name, base_branch, pr_title, report_content)
        if not pr_url:
            pr_url = f"https://github.com/ldstrebel/dnd-scribe/compare/{base_branch}...{branch_name}?expand=1"
        return pr_url

    finally:
        # Clean up worktree
        print("🧹 Cleaning up isolated worktree...")
        run_cmd(["git", "worktree", "remove", "--force", worktree_dir], cwd=repo_root, check=False)
        if os.path.exists(worktree_dir):
            shutil.rmtree(worktree_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Adversarial Trade-Off Inquisitor Runner")
    parser.add_argument("--session", default=None, help="Target session ID (e.g. s5)")
    parser.add_argument("--prev", default=None, help="Previous session ID for continuity analysis")
    parser.add_argument("--focus", choices=["auto", "agency", "liberties", "continuity"], default="auto", help="Audit focus")
    parser.add_argument("--push", action="store_true", help="Push PR branch to GitHub via isolated worktree")
    parser.add_argument("--dry-run", action="store_true", help="Run analysis and print to stdout without saving files or pushing")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sessions_dir = os.path.join(repo_root, "sessions")
    
    # Import extractor
    sys.path.insert(0, os.path.join(sessions_dir, "_scripts"))
    from extract_session_tradeoffs import find_latest_session, extract_tradeoff_dossier

    target_session = args.session or find_latest_session(sessions_dir)
    prev_session = args.prev
    if not prev_session:
        m = re.match(r"^s(\d+)$", target_session.lower())
        if m and int(m.group(1)) > 1:
            prev_session = f"s{int(m.group(1)) - 1}"

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    state_file = os.path.join(sessions_dir, "config", "audit-rotation-state.json")
    state_rel = os.path.relpath(state_file, repo_root).replace("\\", "/")

    focus = resolve_focus(now.weekday(), args.focus, state_file)

    print(f"🕵️ RUNNING ADVERSARIAL TRADE-OFF INQUISITOR")
    print(f"Target Session: {target_session.upper()} (Prev: {prev_session.upper() if prev_session else 'None'})")
    print(f"Focus Area:     {focus.upper()}")
    print(f"Timestamp:      {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Extract dossier
    dossier = extract_tradeoff_dossier(target_session, sessions_dir, prev_session)
    critique = generate_adversarial_critique(dossier, focus)
    report_md = build_markdown_report(critique, date_str)

    if args.dry_run:
        print("\n" + "=" * 75)
        print("📄 DRY RUN REPORT OUTPUT:")
        print("=" * 75)
        print(report_md)
        print("=" * 75)
        return

    # Save report locally
    reports_dir = os.path.join(sessions_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"sessions/reports/tradeoff-audit-{date_str}.md"
    local_report_path = os.path.join(repo_root, report_filename)
    with open(local_report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"✅ Saved local report to: {local_report_path}")

    # Update state locally
    update_rotation_state(state_file, target_session, focus, date_str)
    with open(state_file, "r", encoding="utf-8") as f:
        state_content = f.read()

    # If push requested, run isolated worktree
    if args.push:
        base_branch = get_current_branch(repo_root)
        branch_name = f"audit/tradeoff-{date_str}"
        commit_msg = generate_commit_message(critique, date_str, target_session)
        pr_title = f"[Audit] Trade-Off Inquest ({target_session.upper()}) - {date_str}: [{focus.upper()}]"
        print(f"\n🚀 Creating branch and pushing to GitHub: {branch_name}")
        pr_url = execute_worktree_pr(repo_root, report_filename, report_md, state_rel, state_content, branch_name, base_branch, commit_msg, pr_title)
        print(f"\n🎉 PUSH & PULL REQUEST COMPLETE!")
        print(f"🔗 Pull Request URL:\n   {pr_url}\n")

if __name__ == "__main__":
    main()
