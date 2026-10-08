"""resolve_s6_critiques.py

Updates s6-source-decisions.json (both config and index) with concrete resolution notes
and marks all 33 human critique items as 'resolved' (DEC-031, DEC-036).
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = REPO_ROOT / "sessions" / "config" / "s6-source-decisions.json"
INDEX_FILE = REPO_ROOT / "sessions" / "data" / "index" / "s6-source-decisions.json"

RESOLUTIONS = {
    "rev-s6-strebs-01": (
        "Resolved in `s6-scene-01-alt.md` (L0259). Staged the Transformed Woman's predatory intent clearly: "
        "she specifically demands Pierre's memories of the lost road gatehouse, runic sigils, and pathway geometry, "
        "establishing her lore objective before attempting extraction."
    ),
    "rev-s6-strebs-02": (
        "Resolved in `s6-scene-01-alt.md` (L0260). Restored and smoothed Pierre's parley lines, "
        "cleaning up dialogue flow and establishing clear spatial blocking across the tiered lecture rows."
    ),
    "rev-s6-strebs-03": (
        "Resolved in `s6-scene-01-alt.md` (opening paragraphs). Staged the architectural layout of the lecture hall—"
        "the raked seating, oak benches, high clerestory windows, acoustic baffles, and podium—"
        "providing spatial anchoring for the panicked student stampede and incursion."
    ),
    "rev-s6-strebs-04": (
        "Resolved in `s6-scene-02-alt.md` (L0382). Corrected Alfie's dialogue to 'I do not know what this does, "
        "but I suppose I will just hit it,' showing Alfie slamming the iron rod against the mahogany blotter to trigger "
        "the static barrier, then nodding in contentment."
    ),
    "rev-s6-strebs-05": (
        "Resolved in `s6-scene-02-alt.md` (L0411). Paced the transition smoothly from the static barrier's detonation "
        "to Eusacles clicking on his cassette Walkman pop tunes, followed by Pierre's exasperated reaction."
    ),
    "rev-s6-strebs-06": (
        "Resolved in `s6-scene-02-alt.md` (L0446). Preserved Dravin's unawakened state: Dravin points and calls out "
        "'You there! I see you—' with scholarly fixation, superimposing a lunar sliver over the ceiling tiles that beams down "
        "like a spotlight without him realizing he is casting magic."
    ),
    "rev-s6-strebs-07": (
        "Resolved in `s6-scene-02-alt.md` (L0448). Pierre standing at the moonbeam's border feels celestial radiance "
        "strip obscuring glamers, releasing a pulse of physical energy that invigorates and strengthens him and his allies."
    ),
    "rev-s6-strebs-08": (
        "Resolved in `s6-scene-03-alt.md` (L0516). Staged Eusacles unclipping the brass pocket watch from his denim loop "
        "and flicking his wrist so it unfurls and expands into the spiked iron morningstar."
    ),
    "rev-s6-strebs-09": (
        "Resolved in `s6-scene-03-alt.md` (L0516-L0530). Staged the Divine Smite detonation; Eusacles grins in satisfaction "
        "upon seeing radiant golden flames erupt against fiendish flesh, confirming his hunch that the beast is a fiend."
    ),
    "rev-s6-strebs-10": (
        "Resolved in `s6-scene-03-alt.md` (L0530-L0560). Staged the setup properly: the sprinkler deluge soaking the hall, "
        "charged water pooling in the aisles, and electrical coils whipping through the spray before Pierre engages."
    ),
    "rev-s6-strebs-11": (
        "Resolved in `s6-scene-03-alt.md` (L0579). Excised vocalized spellcasting ('Hold Person'); Pierre engages with somatic focus "
        "and verbal taunting while avoiding direct eye contact with the adversary's serpent coils."
    ),
    "rev-s6-strebs-12": (
        "Resolved in `s6-scene-03-alt.md` (L0595). Allowed the feline vision beat to breathe: Pierre taunts the woman, "
        "experiences a sudden splitting ocular headache, sees infrared heat signatures shimmering across the room, panics that he "
        "might turn Alfie to stone, and checks his reflection in his bronze spearhead to discover his luminous vertical slit pupils."
    ),
    "rev-s6-strebs-13": (
        "Resolved in `s6-scene-04-alt.md` (L0627). Removed all ungrounded references to 'Medusa', replacing them with descriptive "
        "terms: 'the paralyzed adversary' and 'the transformed woman'."
    ),
    "rev-s6-strebs-14": (
        "Resolved in `s6-scene-04-alt.md`. Purged pseudo-intellectual buzzwords, purple jargon ('viscous cadence', 'tapestry of violence'), "
        "and synthetic filler, replacing them with grounded, visceral combat prose."
    ),
    "rev-s6-strebs-15": (
        "Resolved in `s6-scene-04-alt.md` (L0712). Restored Professor Dravin's authentic voice: measured, pragmatic, and academic, "
        "removing nonsensical jargon."
    ),
    "rev-s6-strebs-16": (
        "Resolved in `s6-scene-04-alt.md` (L0749). Confirmed and enforced the adversary descriptor as 'the paralyzed woman / creature', "
        "completely omitting the word 'Medusa'."
    ),
    "rev-s6-strebs-17": (
        "Resolved in `s6-scene-05-alt.md` (L0768). Reworked the entire sequence: Dravin uses a compact mirror to sight over his shoulder "
        "without making direct eye contact, fires the pneumatic dart, watches it dissolve harmlessly into her skin, groans in academic "
        "frustration, and refocuses his vision so the lunar beam pins her down while keeping Pierre safely outside its border."
    ),
    "rev-s6-strebs-18": (
        "Resolved in `s6-scene-05-alt.md` (L0803). Fixed all single-asterisk markdown formatting to ensure clean, consistent italics rendering "
        "on web and e-readers."
    ),
    "rev-s6-strebs-19": (
        "Resolved in `s6-scene-05-alt.md` (L0895). Replaced the out-of-character 'primal outrage' scream with a hissed spasm of genuine physical "
        "pain and thwarted arrogance as Pierre's spear snaps against her tendrils."
    ),
    "rev-s6-strebs-20": (
        "Resolved in `s6-scene-06-alt.md` (L0932). Dravin notices the moonlight tracks his eye movements, sweeps the beam across the auditorium "
        "floor to scorch the satyr advancing up the center aisle and intercept the second circling Alfie's ward, blistering their flesh as "
        "they crash into the balustrade."
    ),
    "rev-s6-strebs-21": (
        "Resolved in `s6-scene-06-alt.md`. Gave the memory siphon moment full narrative room to breathe: the tactile horror of siphoning tendrils, "
        "the visceral tearing of Eusacles's memories, and the condensation of a full year into a tangible motorcycle gear shift."
    ),
    "rev-s6-strebs-22": (
        "Resolved in `s6-scene-06-alt.md` (L1007). Corrected the sequence: the woman realizes the rift is collapsing under the weight of the "
        "extraction and snaps 'We will just have to do it here!', commanding her thralls with urgent desperation."
    ),
    "rev-s6-strebs-23": (
        "Resolved in `s6-scene-07-alt.md` (L1087). Alfie sees Pierre attempting hair treatment, shouts 'Mage Band!', manifesting an elastic glowing "
        "lavender scrunchie to bind the tendrils; Pierre corrals the whipping coils and suffers 12 points of psychic blowback."
    ),
    "rev-s6-strebs-24": (
        "Resolved in `s6-scene-07-alt.md` (L1113). Grounded the memory loss beat in emotional reality: Pierre mourns the loss of his genuine romantic "
        "memory of courting Janette in the Loire Valley chateau courtyard, treating the stolen memory with poignant weight rather than internet slapstick."
    ),
    "rev-s6-strebs-25": (
        "Resolved in `s6-scene-08-alt.md` (L1285). Paced the combat encounter in clean chronological sequence: Dravin's spiritual encyclopedia "
        "bludgeons both beasts, a satyr charges Alfie and wedges its horns into the desk, the second satyr mauls Pierre down to 2 HP, Pierre hacks "
        "at bound tendrils with a scalpel, Alfie drives an upholstery needle into the satyr's eye, and Dravin notes all combatants are bloodied."
    ),
    "rev-s6-strebs-26": (
        "Resolved in `s6-scene-09-alt.md` (L1343). Paced and staged Spore the Dying accurately: Dravin announces that the wounded are near death "
        "and he feels inspired to 'let fester what you have begun'; Alfie sees Pierre is bloodied and twists the runic letter from 'SPARE' to "
        "'SPORE THEM DYING', preventing Pierre from suffering the rot."
    ),
    "rev-s6-strebs-27": (
        "Resolved in `s6-scene-09-alt.md` (L1358). Staged the climax with clear causality: Pierre maintains a death-grip on the hair coils bound "
        "in Alfie's Mage Band, preventing the transformed woman from diving into the collapsing rift with the fleeing satyrs, leaving her pinned "
        "for Dravin's decisive strike."
    ),
    "rev-s6-strebs-28": (
        "Resolved in `s6-scene-09-alt.md` (L1360). Replaced generic 'luminescence sputtered' with physical description: the whipping, electrified "
        "tendrils bound in Alfie's Mage Band droop into limp, dim gray threads as Dravin's encyclopedia knocks her unconscious."
    ),
    "rev-s6-strebs-29": (
        "Resolved in `s6-scene-09-alt.md` (L1428). Pierre surveys the wreckage, hears approaching sirens, and devises the escape plan: concealing "
        "the unconscious woman in a rolling janitor cart to wheel her to the architecture studio for interrogation."
    ),
    "rev-s6-strebs-30": (
        "Resolved in `s6-scene-10-alt.md` (L1444). Restored Dr. Thorne's spoken dialogue where she stammers in shock and asks if Alfie is a talking "
        "doll, providing direct conversational context for Alfie's indignant response."
    ),
    "rev-s6-strebs-31": (
        "Resolved in `s6-scene-10-alt.md` (L1460). Kept Dravin's dialogue in authentic character: 'I do not entirely understand how this resonance "
        "works, but I gather I can keep her alive, or cause deadly fungal spores to sprout from her flesh.'"
    ),
    "rev-s6-strebs-32": (
        "Resolved in `s6-scene-10-alt.md` (L1500). Staged the team convincing Dr. Thorne that she is the central figure in a vast occult conspiracy "
        "as playful revenge for calling Alfie a doll, driving Thorne into manic fringe research as she flees."
    ),
    "rev-s6-strebs-33": (
        "Resolved in `s6-scene-10-alt.md` (L1538) & Pipeline Telemetry. Cleaned up scene wrap-up prose and overhauled the publishing pipeline telemetry "
        "to eliminate canned letter grade inflation (A's and B+'s for all) and multi-colored dashboard bloat, reporting honest word-level compliance "
        "and real parity metrics."
    ),
}

def update_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    critiques = data.get("critiques", [])
    resolved_count = 0
    for c in critiques:
        cid = c.get("id")
        if cid in RESOLUTIONS:
            c["status"] = "resolved"
            c["resolution_notes"] = RESOLUTIONS[cid]
            resolved_count += 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {resolved_count} critique items in {path}")

def main():
    update_file(CONFIG_FILE)
    update_file(INDEX_FILE)

if __name__ == "__main__":
    main()
