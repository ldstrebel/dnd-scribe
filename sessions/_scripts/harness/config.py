"""Configuration and registry loader for the Editorial Harness.

Dynamically loads campaign configuration, canonical characters, locations,
player registries, deny-lists, and stylistic thresholds from campaign-config.json.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Set


def get_repo_root() -> Path:
    """Returns repository root directory."""
    return Path(__file__).resolve().parent.parent.parent.parent


def get_sessions_dir() -> Path:
    return get_repo_root() / "sessions"


def get_campaign_config_path() -> Path:
    """Locates campaign-config.json."""
    return get_sessions_dir() / "config" / "campaign-config.json"


def load_campaign_config() -> Dict[str, Any]:
    """Loads the central campaign-config.json."""
    config_path = get_campaign_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading campaign-config.json: {e}")
    return {}


_CAMPAIGN_CONFIG = load_campaign_config()

# Deny-lists loaded from campaign-config.json with safe fallbacks
DENY_LIST_PLAYERS: Set[str] = set(_CAMPAIGN_CONFIG.get("deny_list_players", [
    "luke strebel", "luke s", "luke f", "luke foreman",
    "sophie foreman", "sophie noone", "sophie foreman noone",
    "kristina strebel", "kristina", "christina",
    "john hagey", "hagey", "holly strebel",
    "luke", "sophie", "john", "holly"
]))

DENY_LIST_MECHANICS: Set[str] = set(_CAMPAIGN_CONFIG.get("deny_list_mechanics", [
    "roll20", "roll 20", "d12", "d20", "d6", "d8", "d4", "d10", "d100",
    "armor slot", "armor slots", "agility roll", "stress slot", "stress slots",
    "hope point", "hope points", "fear point", "fear points",
    "character sheet", "character sheets", "roll for", "saving throw",
    "saving throws", "critical hit", "critical fail", "hit points",
    "difficulty class", "action token", "action tracker", "spell slot",
    "spell slots", "daggerheart", "roll with hope", "roll with fear"
]))

DENY_LIST_OOC_REALIA: Set[str] = set(_CAMPAIGN_CONFIG.get("deny_list_realia", [
    "wi-fi", "wifi", "got disconnected", "was disconnected", "player disconnected",
    "disconnecting from the call", "lagging out",
    "mic check", "mute yourself", "you're muted", "unmute", "push to talk",
    "discord call", "discord server", "on discord", "zoom call", "google meet",
    "gas bill", "headset", "html file", "browser tab", "screen share", "screenshare"
]))

# Phonetic replacements
PHONETIC_REPLACEMENTS: Dict[str, str] = _CAMPAIGN_CONFIG.get("phonetic_replacements", {
    "pair-ey": "Paris",
    "pair-ee": "Paris",
    "perry": "Pierre",
    "pier": "Pierre",
    "ukules": "Eusacles",
    "usacles": "Eusacles",
    "draven": "Dravin",
    "nancy": "Nincy",
    "nanci": "Nincy",
    "teddie": "Teddy",
    "ted": "Teddy"
})

# Filter words / crutches that dilute active prose
FILTER_WORDS = [
    r"\bfelt like\b",
    r"\bseemed to\b",
    r"\bcould hear\b",
    r"\bcould see\b",
    r"\bnoticed that\b",
    r"\bappeared as if\b",
    r"\bsuddenly\b",
    r"\ball of a sudden\b",
    r"\bstarted to\b",
    r"\bbegan to\b",
    r"\bin that moment\b"
]

# Sensory registers to monitor for balanced sensory prose
SENSORY_KEYWORDS = {
    "visual": ["glint", "shadow", "gleam", "pale", "dark", "crimson", "azure", "emerald", "silhouette", "glow", "mist", "flash"],
    "auditory": ["hum", "crack", "thud", "roar", "echo", "whisper", "creak", "crackle", "clang", "rattle", "whistle", "shout", "buzz"],
    "olfactory_gustatory": ["ozone", "sulfur", "brine", "copper", "damp", "smoke", "char", "musty", "bitter", "salt", "pine", "ash"],
    "tactile_kinetic": ["vibrate", "chill", "searing", "rough", "slick", "grime", "heft", "drag", "pulse", "stumble", "friction", "splinter"],
    "arcanatech_energy": ["resonance", "embodied energy", "current", "conduit", "frequency", "copper", "harmonic", "circuit", "lavsidian", "steam"]
}


def load_canonical_entities(repo_root: Path = None) -> Dict[str, List[str]]:
    """Loads canonical entities from campaign config or directory scan."""
    config_entities = _CAMPAIGN_CONFIG.get("canonical_entities", {})
    if config_entities and config_entities.get("pcs"):
        return {
            "pcs": sorted(config_entities.get("pcs", [])),
            "npcs": sorted(config_entities.get("npcs", [])),
            "locations": sorted(config_entities.get("locations", []))
        }

    root = repo_root or get_repo_root()
    pcs = set()
    npcs = set()
    locations = set()

    pc_dir = root / "campaign" / "characters" / "pcs"
    if pc_dir.exists():
        for f in pc_dir.glob("*.md"):
            if not f.name.startswith("."):
                pcs.add(f.stem.replace("-", " ").title())
    pcs.update({"Pierre", "Prof. Edward Dravin", "Edward Dravin", "Dravin", "Eusacles", "Alfie"})

    npc_dir = root / "campaign" / "characters" / "npcs"
    if npc_dir.exists():
        for f in npc_dir.glob("*.md"):
            if not f.name.startswith("."):
                npcs.add(f.stem.replace("-", " ").title())
    npcs.update({"Naomi", "Theodore", "Rosa", "Mike", "The Three Fates", "Anna Smith", "Ally", "Nincy", "Thomas", "Gordon", "Dr. Aris Thorne", "Shadow Beast", "News Anchor", "Bus Passenger", "Museum Attendant"})

    world_dir = root / "campaign" / "world"
    if world_dir.exists():
        for f in world_dir.glob("*.md"):
            if not f.name.startswith("."):
                locations.add(f.stem.replace("-", " ").title())
    locations.update({"The Margin", "The Lost Roads", "Library Of The Fates", "North Carolina Museum Of History", "Stanford University", "Las Vegas", "Greyhound Bus", "Asylum"})

    return {
        "pcs": sorted(list(pcs)),
        "npcs": sorted(list(npcs)),
        "locations": sorted(list(locations))
    }


def get_character_anchors() -> Dict[str, Any]:
    """Returns character anchors from campaign-config.json or default."""
    return _CAMPAIGN_CONFIG.get("character_anchors", {})
