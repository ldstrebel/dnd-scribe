#!/usr/bin/env python3
"""
Generate Campaign Codex True Wiki (DEC-037, DEC-038 & DEC-039).

Deterministic generator producing a fully interactive, cross-linked campaign wiki:
- Master Codex Navigation Portal (campaign/codex/README.md)
- Session Chronicles Hub & Pages (campaign/codex/sessions/README.md, s1.md - s7.md)
- Dramatis Personae Hub & Dossiers (campaign/codex/characters/README.md, *.md)
- Factions Hub & Dossiers (campaign/codex/factions/README.md, *.md)
- Active Mysteries & Plot Lines Board (campaign/codex/threads/open-threads.md)
- The Critic & Editorial Reviews Hub & Pages (campaign/codex/critic/README.md, s1-review.md - s7-review.md)

Audience Boundary Standard (DEC-038 / FP-18):
- Zero compiler debug tables, zero raw line indices (L####), zero contributor names.
- Zero internal schema/block tokens.
- 100% in-world lore, deep narrative debriefs, active plot line tracking, and character growth reviews.
"""

import os
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
INDEX_DIR = ROOT_DIR / "sessions" / "data" / "index"
CONFIG_DIR = ROOT_DIR / "sessions" / "config"
CODEX_DIR = ROOT_DIR / "campaign" / "codex"


def load_all_data():
    manifests = {}
    configs = {}
    source_decisions = {}
    for s in range(1, 8):
        m_path = INDEX_DIR / f"s{s}-manifest-v2.json"
        if m_path.exists():
            with open(m_path, "r", encoding="utf-8") as f:
                manifests[s] = json.load(f)
        c_path = CONFIG_DIR / f"s{s}-session-config.json"
        if c_path.exists():
            with open(c_path, "r", encoding="utf-8") as f:
                configs[s] = json.load(f)
        sd_path = CONFIG_DIR / f"s{s}-source-decisions.json"
        if sd_path.exists():
            with open(sd_path, "r", encoding="utf-8") as f:
                source_decisions[s] = json.load(f)

    camp_cfg_path = CONFIG_DIR / "campaign-config.json"
    with open(camp_cfg_path, "r", encoding="utf-8") as f:
        camp_cfg = json.load(f)

    return manifests, configs, source_decisions, camp_cfg


# =====================================================================
# SESSION DATA
# =====================================================================

def get_session_recaps():
    return {
        1: (
            "Displaced from a late-night Las Vegas Greyhound bus into dimensional freefall, "
            "four disparate strangers awaken inside the marble colonnades of the Library of the Fates. "
            "As amorphous ink-beasts tear through the stacks to consume severed timeline threads, the company "
            "rallies with necrotic frost, chained morningstars, and fencing steel alongside Alfie, a newly woven "
            "driftwood duelist. Escaping through a cosmic tapestry rift, the survivors tumble into the Appalachian "
            "foothills, crossing the fog-shrouded threshold of The Margin."
        ),
        2: (
            "Within the timeless mountain refuge of The Margin, Teddy reveals the sanctuary's 1846 surveyor origins "
            "as a crease in reality where calendar decay cannot reach. While Naomi organizes defensive blackout drills "
            "and briefs the company on four scattered timeline Fragments, Pierre inadvertently triggers his ancient "
            "petrifying Gorgon gaze during an encounter at a rural station. Reunited at the compound, the party boards "
            "a vintage farm truck to navigate the uncharted fog of the Lost Roads toward North Carolina."
        ),
        3: (
            "Threading through the dimensional mist of the Lost Roads, the company arrives in downtown Raleigh to "
            "infiltrate the North Carolina Museum of Natural History. Donning academic disguises, Pierre bluffs security "
            "as a visiting Sorbonne intern while Alfie deploys Wordcraft to trigger a spectral sheep distraction in the lobby. "
            "Deep within the Aegean antiquity gallery, the pair inspect the fractured Greek stele anchoring a severed "
            "timeline, setting off museum alarms as hostile forces converge."
        ),
        4: (
            "Ambushed inside the Aegean antiquity wing by serpent-crowned Gorgon Redactors, the company mounts a "
            "desperate defense utilizing improvised baguette explosives, a high-altitude clay urn drop, and salvaged "
            "ancient armor. Touching the fractured stele, Alfie is overwhelmed by a traumatic vision of ancient oarsmen "
            "and a burning coastal port. Grounding the relic's electrical surge, Pierre secures the tablet, and the party "
            "escapes through the Lost Roads back to The Margin."
        ),
        5: (
            "A celestial dispatch delivered by Hermes bears a sealed winter warning from Persephone, alerting the Margin "
            "that planar veils are thinning. Traveling across the Lost Roads to University University in Pennsylvania, "
            "the company infiltrates a chaotic lecture hall amidst student protests over medical historian Dr. Aris Thorne. "
            "Infiltrating the backstage green room, Dravin recovers Thorne's altered 1948 trial binder—where 'STABLE' was "
            "retroactively overwritten to 'STALE' by an unseen hand—just as satyr strike teams smash through the doors."
        ),
        6: (
            "Violent planar combat erupts across the university amphitheater as satyr strike teams and a tendril-grafted "
            "Gorgon operative assault the party. Dravin establishes a defensive sanctuary of moonlight while Eusacles smites "
            "intruders before suffering a cognitive memory siphon. Coordinating with Alfie's chaotic enchantments and Pierre's "
            "corrosive spells, the party paralyzes the primary operative and subdues her with a classical lexicon strike. "
            "Stashing the unconscious captive in a janitor cart, the company escapes through campus architecture tunnels."
        ),
        7: (
            "Interrogating the captive operative reveals a chilling truth: the party members themselves have absorbed anomalous "
            "energy, transforming them into living timeline vessels targeted for erasure. Alfie severs the parasitic tendril, "
            "triggering a purple flare that liberates the woman, Susanna, who is safely escorted along the Lost Roads. "
            "At The Margin, Eusacles receives a nocturnal dream visit from Thanatos, who engraves divine protection onto his "
            "pocket watch, while Naomi prepares the company for an expedition into the Washington, D.C. police evidence locker."
        ),
    }


def get_session_cliffhangers():
    return {
        1: (
            "**Next Objective:** Cross the mist-veiled threshold of the Appalachian forest sanctuary, secure shelter from the cold, "
            "and examine the classical scrolls stolen from the collapsing Library.\n\n"
            "**Unresolved Cliffhanger:** The disoriented survivors stand before the warm lantern light of a mountain porch, "
            "clutching cosmic manuscripts while monstrous ink-beasts prowl the dark periphery beyond the trees."
        ),
        2: (
            "**Next Objective:** Navigate the vintage farm truck through the uncharted dimensional fog of the Lost Roads to reach downtown Raleigh, North Carolina.\n\n"
            "**Unresolved Cliffhanger:** Reeling from the sudden awakening of his petrifying Gorgon glare at a rural service station, Pierre sits gripped by existential dread in the truck cab as reality parts into dense, blinding mist."
        ),
        3: (
            "**Next Objective:** Break through the museum security perimeter, reach the central atrium, and rendezvous with the transport truck.\n\n"
            "**Unresolved Cliffhanger:** Emergency alarms howl across the Aegean antiquity gallery, heavy iron security shutters descend across the exits, and shadowy armed silhouettes sprint down the corridors toward the shattered glass vitrine."
        ),
        4: (
            "**Next Objective:** Decompress at The Margin, process the newly recovered Greek relic, and inspect the salvaged Spartan hoplite armor.\n\n"
            "**Unresolved Cliffhanger:** The company returns to mountain sanctuary with the fractured stele, but Alfie remains deeply shaken by agonizing phantom memories of burning naval ports, unable to sleep without lanterns burning."
        ),
        5: (
            "**Next Objective:** Survive the coordinated satyr assault in the academic corridors, extract Dr. Thorne, and protect the altered clinical trial records.\n\n"
            "**Unresolved Cliffhanger:** Trapped in the backstage green room with Thorne's handwritten binder showing 'STABLE' retroactively overwritten to 'STALE', the party braces as horned satyr strike teams smash through the doors."
        ),
        6: (
            "**Next Objective:** Evacuate campus through maintenance tunnels, reach the Lost Roads pickup point, and safely transport the captive to The Margin.\n\n"
            "**Unresolved Cliffhanger:** With the primary transformed operative knocked unconscious by Dravin's lexicon strike, the party conceals her paralyzed form in a janitor cart and flees into the dark architectural tunnels beneath the university."
        ),
        7: (
            "**Next Objective:** Infiltrate the high-security evidence locker of the Washington, D.C. Metropolitan Police Department to recover the anomalous airline flight artifact.\n\n"
            "**Unresolved Cliffhanger:** Following Eusacles' nocturnal communion with Thanatos and Naomi's Anomaly Board briefing, the company gears up at dawn, knowing that Redactor tracking teams are actively hunting them as living anomaly vessels."
        ),
    }


def get_deep_narrative_debriefs():
    return {
        1: (
            "### Act I: The Shattered Highway & The Celestial Colonnade (Chapters 1–2)\n"
            "A routine midnight Greyhound journey through the Nevada basin shatters when the vehicle plunges through a planar tear. "
            "[Pierre](../characters/pierre.md), [Professor Dravin](../characters/dravin.md), and [Eusacles](../characters/eusacles.md) "
            "awaken not on asphalt, but upon vast flagstones surrounded by colossal marble columns stretching beyond mortal sight: "
            "the extra-dimensional Library of [The Three Fates](../characters/fates.md).\n\n"
            "### Act II: Assault of the Correctors (Chapters 3–5)\n"
            "The cosmic haven is under siege. Predatory ink-beasts known as Correctors pour through reality tears, seeking to devour severed "
            "timeline threads. Professor Dravin anchors an improvised defense with necrotic frost and silver chime vibrations, while Eusacles "
            "unleashes brutal brawling maneuvers with his watch-chain morningstar. In the chaos of the crumbling stacks, Pierre recovers "
            "and conceals ancient classical manuscripts.\n\n"
            "### Act III: The Weaving of Alfie (Chapters 6–9)\n"
            "Desperate for frontline combatants, the Three Fates weave [Alfie](../characters/alfie.md) from weathered driftwood, sea-threads, "
            "and sailcloth. Drawing her needle rapier, the two-foot construct immediately joins the fray, crippling massive horrors with "
            "surgical tendon strikes.\n\n"
            "### Act IV: The Tapestry Rift & Appalachian Sanctuary (Chapters 10–12)\n"
            "As the cosmic Library buckles under the weight of reality fissures, the Three Fates cast a shimmering tapestry net across planar boundaries. "
            "The four disoriented survivors are torn from the collapsing marble halls and cast through cold, dimensional freefall, tumbling into the Appalachian night. "
            "Guiding their steps along an abandoned logging track through dense pine fog, they emerge before a weathered wooden porch glowing with warm kerosene lamplight: "
            "[The Margin](../factions/margin-wardens.md). Displaced from their lives, pursued by ink-beasts, and clutching stolen scrolls, the survivors cross the threshold into the unknown."
        ),
        2: (
            "### Act I: Intake at the Mountain Sanctuary (Chapter 13)\n"
            "Welcomed onto the cedar porch of [The Margin](../factions/margin-wardens.md) by founding caretaker [Teddy](../characters/teddy.md) "
            "and [Rosa](../characters/rosa.md), the survivors learn that the haven exists within a temporal crease where calendar decay cannot "
            "reach. Teddy reveals he has resided there since 1846 following the upstream redaction of his home town.\n\n"
            "### Act II: Naomi's Anomaly Briefing & Blackout Drills (Chapter 14)\n"
            "Eleven-year-old tactical coordinator [Naomi](../characters/naomi.md) introduces the party to the strategic Anomaly Board, "
            "identifying four scattered historical Fragments that anchor severed timelines across North America. To prepare the newcomers, "
            "she institutes rigorous blackout corrector drills.\n\n"
            "### Act III: The Golden Glare & Departure into the Mist (Chapter 15)\n"
            "During a supply run to a nearby rural gas station, [Pierre](../characters/pierre.md) is confronted by an aggressive attendant. "
            "Under acute survival stress, his dormant Gorgon bloodline flares: a flash of golden light erupts from his eyes, petrifying the clerk into stone-like paralysis. "
            "Reeling from the horrifying revelation of his monstrous heritage, Pierre retreats to the compound. With planar predators tracking the disturbance, "
            "[Mike](../characters/mike.md) cranks the ignition of the vintage 1978 farm truck. As the iron lever grinds to part reality, the vehicle plunges into the disorienting, "
            "unmapped dimensional fog of the Lost Roads bound for North Carolina."
        ),
        3: (
            "### Act I: Navigating the Dimensional Fog (Chapter 23)\n"
            "[Mike](../characters/mike.md) navigates the vintage 1978 farm truck through the treacherous, disorienting mist of the Lost Roads, "
            "bypassing mortal geography to deposit the party in downtown Raleigh, North Carolina.\n\n"
            "### Act II: Academic Disguise & The Sheep Stampede (Chapter 24)\n"
            "Infiltrating the North Carolina Museum of Natural History, [Pierre](../characters/pierre.md) bluffs security by posing as a visiting "
            "Sorbonne intern in an oversized lab coat. To draw guards away from the security desk, [Alfie](../characters/alfie.md) executes a "
            "Wordcraft alteration (*Sleep* $\\rightarrow$ *Sheep*), releasing a chaotic flock of spectral livestock into the lobby.\n\n"
            "### Act III: The Aegean Vitrine & The Tripped Alarms (Chapter 25)\n"
            "Deep within the darkened Aegean antiquity wing, [Pierre](../characters/pierre.md) and [Alfie](../characters/alfie.md) reach the glass vitrine "
            "safeguarding the fractured Greek marble stele. As Pierre inspects the severed classical inscription anchoring a broken timeline branch, the delicate security seals trip. "
            "Klaxons howl through the cavernous museum halls, emergency iron shutters begin descending across the exits, and armed shadowy silhouettes move rapidly through "
            "the corridors to intercept the intruders before they can touch the stone."
        ),
        4: (
            "### Act I: The Mezzanine Ambush & Urn Drop (Chapter 26)\n"
            "Serpent-crowned [Redactor](../factions/redactors.md) Gorgons assault the Aegean wing to shatter the relic. The party mounts a "
            "dynamic defense: [Alfie](../characters/alfie.md) topples a heavy ceramic urn from the upper mezzanine while [Pierre](../characters/pierre.md) "
            "deploys an improvised baguette distraction and an extension-cord tripwire.\n\n"
            "### Act II: The Burning Coast Nightmare (Chapter 27)\n"
            "When Alfie physically touches the ancient stele, an agonizing sensory flashback overwhelms her mind: freezing brine, oarsmen rowing "
            "in pitch darkness, and a coastal village put to the torch by an ancient captain.\n\n"
            "### Act III: Grounding the Surge & Flight to the Mountain Haven (Chapter 28)\n"
            "With the severed stele discharging dangerous surges of raw temporal electricity, Pierre grounds the charge through an already-petrified attendant, "
            "salvages a set of ancient Spartan hoplite armor, and bundles the shivering Alfie into his coat. As museum reinforcements close in, the party dives into the spatial fold "
            "of the Lost Roads, fleeing back into the quiet shelter of The Margin. Though the relic is secured, Alfie remains haunted by traumatic phantom memories of burning naval ports, "
            "realizing that touching timeline fragments means absorbing the suffering of slaughtered histories."
        ),
        5: (
            "### Act I: The Hermes Express & Persephone's Dispatch (Chapter 29)\n"
            "Golden-sandaled courier [Hermes](../characters/hermes.md) arrives at The Margin, charging steep transit fees to deliver a sealed "
            "parchment from Persephone. The letter warns that as the goddess descends for the winter solstice, planar boundaries will thin, "
            "exposing the haven to predatory incursions.\n\n"
            "### Act II: Infiltrating University University (Chapter 30)\n"
            "The company travels via the Lost Roads to Pennsylvania, infiltrating a turbulent university campus engulfed in student protests "
            "against guest lecturer [Dr. Aris Thorne](../characters/thorne.md).\n\n"
            "### Act III: The 1948 Trial Notes & Satyr Ambush (Chapter 31)\n"
            "Infiltrating the backstage green room, [Professor Dravin](../characters/dravin.md) and Alfie locate Dr. Thorne's locked research binder. "
            "Examining the handwritten 1948 clinical trial logs, Dravin uncovers chilling physical proof of active historical manipulation: "
            "the diagnostic word 'STABLE' was retroactively overwritten to 'STALE' by an unseen hand. Before the party can formulate an extraction plan, "
            "heavy hooves thunder down the corridor and the green room doors splinter inward as horned satyr Redactor strike units assault the room with drawn weapons."
        ),
        6: (
            "### Act I: Amphitheater Under Siege & Memory Siphon (Chapters 32–34)\n"
            "Horned satyr strike units and a tendril-grafted Gorgon operative assault the stage. [Professor Dravin](../characters/dravin.md) "
            "casts Twilight Sanctuary and Moonbeam to establish a luminous perimeter. [Eusacles](../characters/eusacles.md) crushes an attacker "
            "with his morningstar before an enemy tendril strike drains a portion of his living memories.\n\n"
            "### Act II: Acrobatic Chaos & Acidic Wards (Chapters 35–37)\n"
            "[Alfie](../characters/alfie.md) activates her enchanted Chaos Belt and deploys a spectral mage band, while [Pierre](../characters/pierre.md) "
            "weaves acidic defensive barriers to deny ground to the flanking satyrs.\n\n"
            "### Act III: The Lexicon Strike & Subterranean Extraction (Chapters 38–41)\n"
            "Pierre lands a clutch *Hold Person* spell to immobilize the primary transformed operative mid-stride. Seizing the opening, Professor Dravin brings a "
            "massive, leather-bound classical lexicon down upon her skull, knocking her unconscious. Bloodied and nursing cognitive memory wounds, the party hauls "
            "the captive into a heavy rolling janitor cart and dives into the subterranean campus steam tunnels, fleeing into the Lost Roads just as sirens wail across the university above."
        ),
        7: (
            "### Act I: The Cart Interrogation & Tendril Severing (Chapter 42)\n"
            "Huddled around the janitor cart, the party interrogates the captive operative. She reveals that an entity known as the Master "
            "is systematically editing history to create a curated timeline, and that the party members themselves have absorbed timeline "
            "anomalies, making them living vessels targeted for erasure. When the woman insults [Alfie](../characters/alfie.md) as disposable 'junk', "
            "Alfie severs the parasitic cephalopod tendril with her needle rapier. The severed organism dissolves in an agonizing purple flare, "
            "alerting the Master.\n\n"
            "### Act II: The Campus Stalker & The Rabbit Patronus (Chapters 43–44)\n"
            "A six-fingered, multi-faced [Redactor](../factions/redactors.md) stalker shadows the party across the quad. [Pierre](../characters/pierre.md) "
            "conjures a radiant white rabbit patronus to draw the hunter away while guiding the liberated operative, [Susanna](../characters/susanna.md), "
            "through the Lost Roads to sanctuary.\n\n"
            "### Act III: Rum Pancakes & Four Centuries of Memory (Chapters 45–46)\n"
            "At The Margin, morale is restored by domestic warmth. Over rum-infused griddle pancakes prepared by [Mike](../characters/mike.md), "
            "Alfie reveals that while she has walked the earth for four days, she carries 458 years of accumulated thread memory from drowned sailor cloaks.\n\n"
            "### Act IV: The Nocturnal Dream of Thanatos (Chapters 47–48)\n"
            "[Thanatos](../characters/thanatos.md) visits [Eusacles](../characters/eusacles.md) in a campfire dream, engraving his pocket watch "
            "with divine protective armor (Tier 2 Birthright). When Eusacles asks about Pierre's mother, Thanatos bursts into booming laughter, "
            "calling it 'an epic prank' before vanishing into the mist.\n\n"
            "### Act V: The Washington D.C. Directive & Dawn Preparations (Chapters 49–50)\n"
            "Following Eusacles' nocturnal communion with Thanatos and the morning ritual of rum-griddle pancakes, [Naomi](../characters/naomi.md) pins a series of "
            "reconnaissance photographs to the strategic Anomaly Board. She identifies their next mandatory target: an anomalous artifact recovered from an unrecorded 1980s airline hijacking, "
            "held in the high-security evidence locker of the Washington, D.C. Metropolitan Police Department. As dawn breaks over the mountain ridge, the party straps on salvaged hoplite plates "
            "and readies their gear, bracing to infiltrate the heart of the mortal capital."
        ),
    }


def get_session_lore_discoveries():
    return {
        1: [
            ("The Loom of Time", "The primordial metaphysical tapestry from which all mortal history is woven. Breaches or severed threads cause localized reality tears, spawning predatory ink-beasts."),
            ("The Three Fates", "Clotho, Lachesis, and Atropos—ancient cosmic weavers residing in an extra-dimensional marble library, currently overwhelmed by widespread temporal redactions."),
            ("The Margin", "A timeless sanctuary hidden in an Appalachian crease of reality where calendar decay is halted and displaced timeline survivors find refuge."),
        ],
        2: [
            ("The Lost Roads", "Ancient, fog-shrouded interstitial highways threading through dimensional creases, bridging vast geographic distances without crossing mortal space."),
            ("The Anomaly Board", "Naomi's strategic registry tracking four primary timeline breaches: the Greek Tablet in Raleigh, the Toy Catapult Bolt, the Mad Doctor's Tour, and the DC Plane Incident."),
            ("Echidna's Heritage", "An ancient maternal bloodline carrying dormant petrifying abilities that awaken under severe stress, tracing back to the primordial Mother of Monsters."),
        ],
        3: [
            ("The Greek Inscription Tablet", "An ancient Hellenic marble stele bearing an inscription whose severed letters anchor an alternate timeline branch."),
            ("Wordcraft in Practice", "The supernatural discipline of altering physical reality and spellcraft through subtle single-letter linguistic substitutions."),
        ],
        4: [
            ("The Redactors", "Ruthless planar enforcers dispatched to erase evidence of historical tampering, eliminate living anomalies, and destroy historical epigraphy."),
            ("Relic Sensory Echoes", "Direct physical contact with an active timeline Fragment floods the bearer with vivid, traumatic sensory recollections of alternate historical timelines."),
        ],
        5: [
            ("Active Historical Redaction", "Physical proof that historical documents and medical trial records are being systematically rewritten in real time by an unseen coordinator."),
            ("The 1948 Trial Notes", "A buckram binder recording clinical trials of a historical vaccine, where diagnostic classifications were retroactively overwritten from 'STABLE' to 'STALE'."),
            ("Persephone's Solstice Warning", "As the Underworld sovereign descends for winter, the metaphysical boundaries shielding The Margin thin, heightening vulnerability to planar predators."),
        ],
        6: [
            ("Cognitive Redaction", "The terrifying capability of Redactor operatives to physically drain living memories from combatants during melee engagements."),
            ("Transformed Operatives", "Mortal agents captured and biologically altered by the Redactors, grafted with dark tendrils and deployed as disposable combat assets."),
        ],
        7: [
            ("Living Anomaly Vessels", "The critical revelation that the party members are not merely gathering fragments, but have absorbed timeline energy, making them the primary targets of erasure."),
            ("The Redactor Stalkers", "Elite six-fingered, multi-faced temporal hunters capable of tracking anomaly vessels across mortal university campuses and planar borders."),
            ("The Hermes Express", "An exorbitant celestial transit service operated by the messenger god, connecting disparate planar reaches for exorbitant fees."),
            ("Thanatos' Bureaucracy", "The Greek god of death operates independently from the Fates' clerical apparatus, offering quiet nocturnal guidance and protective armor blessings."),
        ],
    }


def get_session_milestones():
    return {
        1: [
            "A reality rupture aboard a midnight Vegas Greyhound bus propels four disparate strangers into the Library of the Fates.",
            "The Three Fates weave Alfie from driftwood and sea-threads to fight alongside the party.",
            "Professor Dravin and Eusacles coordinate necrotic frost and chained morningstar strikes to repel swarming ink-beasts.",
            "Pierre recovers and conceals ancient classical scrolls from the crumbling library stacks.",
            "The survivors escape through a cosmic tapestry net into the Appalachian foothills, reaching The Margin.",
        ],
        2: [
            "Teddy reveals his 1846 surveyor origins and explains The Margin as a protective 'crease in the map.'",
            "Naomi establishes blackout corrector drills to train newcomers against planar incursions.",
            "Naomi presents the Anomaly Board, identifying the four primary scattered timeline Fragments.",
            "Pierre's latent petrifying gaze flares during an encounter at a rural gas station, temporarily paralyzing an attendant.",
            "The party boards Mike's vintage truck to traverse the Lost Roads bound for North Carolina.",
        ],
        3: [
            "The company navigates the disorienting mist of the Lost Roads into downtown Raleigh.",
            "Pierre disguises himself as an academic intern in an oversized lab coat to bluff museum security.",
            "Alfie uses Wordcraft to manifest a spectral sheep stampede, diverting lobby guards.",
            "Pierre and Alfie breach the Aegean antiquity hall and inspect the fractured Greek stele, triggering gallery alarms.",
        ],
        4: [
            "Serpent-crowned Gorgon Redactors attack the Aegean gallery to shatter the Greek stele.",
            "The company repels the assault using an extension-cord gambit, a mezzanine urn drop, and a baguette distraction.",
            "Alfie touches the stele, experiencing a traumatic sensory vision of ancient naval slaughter.",
            "Pierre grounds the relic's electrical surge, securing the tablet and ancient Spartan hoplite gear.",
            "The party escapes through the Lost Roads back to the mountain sanctuary of The Margin.",
        ],
        5: [
            "Hermes delivers Persephone's sealed solstice warning to The Margin, demanding steep fees for transit.",
            "The party infiltrates University University amidst intense student demonstrations against Dr. Aris Thorne.",
            "Dravin and Alfie recover Thorne's research binder from the green room, discovering the altered 'STABLE' to 'STALE' entry.",
            "Horned satyr Redactors ambush the party in the backstage corridors, smashing through locked doors.",
        ],
        6: [
            "A major pitched battle erupts in the university amphitheater against satyr assault units and a tendril-wielding operative.",
            "Professor Dravin casts Twilight Sanctuary and Moonbeam to establish a fortified defensive perimeter.",
            "Eusacles suffers a disorienting cognitive memory siphon from an enemy tendril strike.",
            "Pierre executes a precision Hold Person spell while Dravin neutralizes the primary operative with a heavy classical lexicon.",
            "The company stashes the unconscious captive inside a rolling janitor cart and flees into campus architecture tunnels.",
        ],
        7: [
            "Interrogating the captive reveals the party's status as living anomaly vessels targeted by the Master.",
            "Alfie severs the parasitic tendril with her needle rapier, triggering an agonizing dissolution into a blinding purple beacon.",
            "Pierre conjures a luminous white rabbit patronus to guide the freed operative, Susanna, through the Lost Roads to sanctuary.",
            "At The Margin, Alfie shares her 458-year thread memory over rum-infused pancakes prepared by Mike.",
            "Thanatos visits Eusacles in a nocturnal dream, engraving his pocket watch with divine defensive armor.",
            "Naomi briefs the company on the Washington, D.C. police evidence locker, launching dawn preparations.",
        ],
    }


def get_session_threads_touched():
    return {
        1: [
            ("TH-01", "Alfie's Origin & Carving", "Opened", "Alfie is woven into being by the Fates; carries naval memories with zero recollection of her carver."),
        ],
        2: [
            ("TH-07", "The Nature of Timeline Fragments", "Opened", "Naomi introduces the Anomaly Board identifying the 4 primary historical Fragments."),
        ],
        3: [
            ("TH-02", "The Naval Nightmare Stele Resonance", "Opened", "The Greek stele is infiltrated in Raleigh; Alfie senses resonance from the vitrine."),
        ],
        4: [
            ("TH-01", "Alfie's Origin & Carving", "Advanced", "Touching the stele triggers vivid memory of ancient burning coast and naval fleet."),
            ("TH-02", "The Naval Nightmare Stele Resonance", "Advanced", "Alfie begins suffering traumatic insomnia requiring lanterns burning through the night."),
        ],
        5: [
            ("TH-03", "1948 Big Pox Clinical Trial Reality", "Opened", "Thorne's altered trial binder recovered; proves 'STABLE' was edited to 'STALE'."),
            ("TH-04", "Persephone's Winter Solstice Warning", "Opened", "Hermes delivers sealed dispatch warning of thinning planar boundaries."),
            ("TH-07", "The Nature of Timeline Fragments", "Advanced", "Party theorizes whether fragments can exist as intangible historical moments."),
        ],
        6: [
            ("TH-03", "1948 Big Pox Clinical Trial Reality", "Advanced", "Trial notes secured amidst violent amphitheater clash against satyr units."),
        ],
        7: [
            ("TH-01", "Alfie's Origin & Carving", "Advanced", "Alfie reveals her 458 years of accumulated thread memory from drowned sailor cloaks."),
            ("TH-05", "The Six-Fingered Redactor Operative", "Opened", "Multi-faced stalker spotted tracking the party across campus quads."),
            ("TH-06", "Washington D.C. Evidence Locker Expedition", "Opened (Active Hook)", "Naomi identifies the D.C. precinct evidence locker as the next target."),
            ("TH-08", "Eusacles' Engraved Watch Resonance", "Confirmed / Resolved", "Thanatos campfire dream confirms watch enchantment and drops lineage hint."),
        ],
    }




# =====================================================================
# CRITIC REVIEWS DATA
# =====================================================================

def get_critic_reviews():
    return {
        1: {
            "score": "8.8 / 10 · High Narrative Momentum",
            "highlights": (
                "The campaign opening achieves immediate high-stakes traction by subverting the traditional tavern trope. "
                "Casting four modern strangers from a mundane Las Vegas Greyhound into cosmic freefall establishes deep vulnerability. "
                "Dravin's patrician intellectual calm contrasts beautifully with Eusacles' casino brawler cynicism, while Pierre's "
                "instinctive theft of ancient scrolls plants an immediate, compelling personal flaw. The emergence of Alfie as a "
                "freshly woven driftwood construct creates an instant table favorite."
            ),
            "threads_audit": (
                "- **Opened:** `TH-01` (Alfie's Origin & Carving) — Established her construct nature and lack of carver memories.\n"
                "- **Pacing Note:** The transition from cosmic horror to the quiet mountain porch of The Margin lands with superb atmospheric relief."
            ),
            "character_cards": {
                "Pierre": "Demonstrated quick-witted survival instincts and academic curiosity, pocketing classical manuscripts under extreme peril. Reluctant combatant.",
                "Alfie": "Instant breakout performance: proud, martial, rejecting construct diminishment, executing lethal low-profile fencing strikes.",
                "Eusacles": "The practical combat anchor; immediately shields companions with improvised chain strikes without hesitation.",
                "Dravin": "Grounds the cosmic terror with scholarly composure, deploying threshold frost magic to enforce tactical spacing."
            },
            "gm_craft": "Masterful pacing of the reality breach; introduced the Fates not as omnipotent overseers, but as frantic weavers overwhelmed by cosmic sabotage.",
            "bets": [
                "Bet #1: Pierre's stolen scrolls contain forbidden knowledge regarding his own ancestry that will cause friction with the party.",
                "Bet #2: Alfie's missing memories stem from an ancient Mediterranean naval battle connected to the Greek stele."
            ]
        },
        2: {
            "score": "8.5 / 10 · Rich Worldbuilding Decompression",
            "highlights": (
                "Session 2 provides necessary narrative breathing room following the cosmic assault. Teddy's introduction as an 1846 surveyor "
                "living in a reality crease grounds the rules of The Margin with rustic elegance. The convenience store supply run brilliantly "
                "demonstrates that ordinary mortal reality is now deeply perilous, culminating in the sudden, shocking manifestation of Pierre's "
                "dormant Gorgon gaze."
            ),
            "threads_audit": (
                "- **Opened:** `TH-07` (The Nature of Timeline Fragments) — Naomi's Anomaly Board establishes the overarching campaign roadmap.\n"
                "- **Pacing Note:** The contrast between quiet domestic pancakes and sudden petrification preserves tension without dragging."
            ),
            "character_cards": {
                "Pierre": "Fleshed out with rich neurotic details; his accidental petrification of the clerk induces genuine guilt and existential terror.",
                "Alfie": "Deepened bonds with the settlement; found a gentle confidante in Rosa while sharpening her needle rapier.",
                "Eusacles": "Showed domestic resourcefulness by rebuilding a damaged cabin and hanging a hammock; the pragmatic skeptic of the group.",
                "Dravin": "Engaged Naomi's anomaly tracking models with academic rigor, helping synthesize the historical significance of the Raleigh stele."
            },
            "gm_craft": "Seamless introduction of the Lost Roads as an atmospheric transit mechanic, turning travel into a tense navigation challenge.",
            "bets": [
                "Bet #1: Pierre's petrification of the rural attendant will leave a breadcrumb trail for Redactor hunters.",
                "Bet #2: Naomi's four Fragments are interconnected parts of an ancient ritual attempting to seal the Underworld."
            ]
        },
        3: {
            "score": "8.7 / 10 · Stellar Comedic Infiltration",
            "highlights": (
                "Session 3 shines with comedic timing and escalating tension. Pierre's portrayal of a nervous French academic intern in an "
                "oversized lab coat creates sublime roleplay friction, while Alfie's Wordcraft conversion of *Sleep* into *Sheep* produces "
                "a hilarious lobby stampede that showcases the creative freedom of the system."
            ),
            "threads_audit": (
                "- **Opened:** `TH-02` (Naval Nightmare Stele Resonance) — The fractured Greek tablet is identified in the Aegean gallery.\n"
                "- **Pacing Note:** The slow, deliberate scouting of the vitrine builds palpable dread before the alarms trip."
            ),
            "character_cards": {
                "Pierre": "Superb social roleplay; turned academic pomposity into an effective infiltration shield.",
                "Alfie": "Brilliant tactical improvisation with Wordcraft; her shoulder-perch dynamic with Pierre reached peak comedic synergy.",
                "Eusacles": "Served as vigilant perimeter lookout, noting anomalous security guard shifts and structural vulnerabilities.",
                "Dravin": "Provided off-site historical decoding of the Aegean catalog, guiding Pierre and Alfie toward the correct exhibit."
            },
            "gm_craft": "Treated the museum as an authentic institutional space rather than a generic dungeon; security protocols felt grounded and real.",
            "bets": [
                "Bet #1: The museum alarms will attract planar strike teams rather than standard Raleigh municipal police.",
                "Bet #2: The stele's broken inscription requires Pierre's epigraphic knowledge to be properly deciphered."
            ]
        },
        4: {
            "score": "9.2 / 10 · Cinematic Action & Dramatic Resonance",
            "highlights": (
                "A tour de force of tabletop action staging. The mezzanine ambush is propulsive, creative, and physically grounded. "
                "Improvising a tripwire with an extension cord, dropping heavy clay urns, and using baguettes as distractions showcase "
                "party ingenuity under lethal pressure. The sudden shift into psychological horror when Alfie touches the tablet lands "
                "with immense emotional weight."
            ),
            "threads_audit": (
                "- **Advanced:** `TH-01` (Alfie's Origin) — Sensory vision of ancient oarsmen and burning coast firmly connects her to antiquity.\n"
                "- **Advanced:** `TH-02` (Naval Nightmare Resonance) — The psychological fallout begins; insomnia and fear of sleep take root."
            ),
            "character_cards": {
                "Pierre": "Heroic turn: overcame his fear of electricity and violence to ground the relic's charge and salvage Spartan hoplite gear.",
                "Alfie": "Outstanding dramatic vulnerability; the comedic bravado cracked to reveal a traumatized soul terrified of ancient fire.",
                "Eusacles": "[NO DATA - ABSENT] (Scouting perimeter trails; character was away on hunting expedition).",
                "Dravin": "Deployed tactical warding to screen the retreat, shielding Alfie while she was incapacitated by sensory overload."
            },
            "gm_craft": "The sensory description of the stele vision—cold brine, salt spray, crackling timber—elevated the narrative from combat to epic literature.",
            "bets": [
                "Bet #1: The Spartan hoplite armor salvaged by Pierre carries latent protective enchantments tied to Ares or Athena.",
                "Bet #2: Alfie's insomnia will lead to cognitive fatigue unless the Margin residents help her process her memories."
            ]
        },
        5: {
            "score": "9.0 / 10 · Paranoid Temporal Mystery",
            "highlights": (
                "Session 5 permanently elevates the campaign stakes from local survival to a war over the historical record itself. "
                "Hermes' arrival is brisk, transactional, and mercenary, setting a fantastic divine tone. Infiltrating the campus amidst "
                "student protests provides vivid modern texture, and the revelation of 'STABLE' altered to 'STALE' in Thorne's handwritten binder "
                "delivers a spine-chilling proof of active reality manipulation."
            ),
            "threads_audit": (
                "- **Opened:** `TH-03` (1948 Big Pox Clinical Trial Reality) — Thorne's altered research binder recovered.\n"
                "- **Opened:** `TH-04` (Persephone's Winter Solstice Warning) — Hermes delivers sealed warning of thinning planar veils.\n"
                "- **Advanced:** `TH-07` (The Nature of Timeline Fragments) — Party realizes timeline edits can target institutional records."
            ),
            "character_cards": {
                "Pierre": "Excellent comedic complaints regarding American collegiate brutalism; served as keen lookout during backstage search.",
                "Alfie": "Demonstrated stealth acumen, darting through ventilation shafts to unlock the green room for Dravin.",
                "Eusacles": "Skeptical anchor; pressed the party on whether Dr. Thorne was a savior or an irresponsible medical charlatan.",
                "Dravin": "Academic MVP: his epigraphic and historical training allowed him to instantly spot the altered ink in the 1948 trial ledger."
            },
            "gm_craft": "Superb atmosphere; captured the chaotic energy of a 1970s academic hall while seamlessly weaving in planar satyr ambushes.",
            "bets": [
                "Bet #1: Dr. Thorne is an unwitting pawn of the Master who does not understand the planar scope of his research.",
                "Bet #2: The satyr strike team was sent specifically to eliminate the trial notes rather than the party."
            ]
        },
        6: {
            "score": "9.3 / 10 · Brutal Tactical Combat & Catharsis",
            "highlights": (
                "A masterclass in tactical combat coordination. The fight in the amphitheater feels desperate, chaotic, and dangerous. "
                "The mechanical and narrative horror of cognitive redaction—tendrils physically siphoning Eusacles' memories—creates genuine terror. "
                "Dravin knocking out the transformed operative with a massive leather-bound classical lexicon is an all-time campaign highlight."
            ),
            "threads_audit": (
                "- **Advanced:** `TH-03` (1948 Big Pox Trial Reality) — Binder successfully secured and extracted from the warzone.\n"
                "- **Pacing Note:** The transition from kinetic auditorium brawl to a frantic janitor-cart extraction maintains high pulse."
            ),
            "character_cards": {
                "Pierre": "Tactical linchpin: deployed acidic barriers and landed a clutch Hold Person on the primary transformed operative.",
                "Alfie": "Wild arcane combatant: triggered her Chaos Belt and anchored herself with a spectral mage band to hold the stage.",
                "Eusacles": "Took the brunt of the assault; suffered a disorienting memory drain while shielding the scholarly party members.",
                "Dravin": "Iconic moment of scholarly violence: channeled Twilight Sanctuary and flattened the paralyzed operative with an ancient lexicon."
            },
            "gm_craft": "Kept the combat dynamic and environmental, utilizing lecture podiums, tiered amphitheater seating, and janitor carts.",
            "bets": [
                "Bet #1: The captured operative can be cured of her Redactor tendrils if treated within The Margin.",
                "Bet #2: Eusacles' lost memories will re-emerge during a future brush with mortal peril or divine communion."
            ]
        },
        7: {
            "score": "9.5 / 10 · Masterful Tonal Balance & Cosmic Payoff",
            "highlights": (
                "Session 7 is arguably the strongest narrative session of the campaign to date. It balances razor-sharp dramatic interrogation "
                "with eerie campus stealth, warm domestic comfort, divine father-son mythic resonance, and propulsive mission preparation. "
                "Alfie's cold, unflinching severing of the tendril ('We don't say the D-word around here') is a triumph of character definition. "
                "The rum pancake breakfast grounds the ensemble beautifully, and Thanatos' dream communion provides divine validation with "
                "sublime dark humor."
            ),
            "threads_audit": (
                "- **Advanced:** `TH-01` (Alfie's Origin) — Alfie reveals 458 years of accumulated thread memory from dead sailors' garments.\n"
                "- **Opened:** `TH-05` (The Six-Fingered Redactor Operative) — Elite multi-faced tracker shadows the party across campus quads.\n"
                "- **Opened (Active Hook):** `TH-06` (Washington D.C. Evidence Locker Expedition) — Naomi identifies the next major target.\n"
                "- **Confirmed / Resolved:** `TH-08` (Eusacles' Engraved Watch) — Thanatos enchants watch and drops cryptic hint on Pierre's mother."
            ),
            "character_cards": {
                "Pierre": "Demonstrated genuine growth from panicked refugee to heroic protector; conjured a radiant rabbit patronus to guide Susanna to safety.",
                "Alfie": "Emotional peak: cold, decisive execution of the parasite, followed by a profound ontological reflection on her four-century thread consciousness.",
                "Eusacles": "Vulnerable and grounded: seeking his divine father's favor, accepting his Tier 2 birthright, and serving as the camp's pragmatic anchor.",
                "Dravin": "[NO DATA - ABSENT] (Conducting independent archival research in university history stacks)."
            },
            "gm_craft": "Thanatos was portrayed with perfection—not an ominous grim reaper, but a tired, amused celestial bureaucrat with genuine love for his son.",
            "bets": [
                "Bet #1: The Washington D.C. evidence locker contains the anomalous black box or passenger manifest from the hijacked plane Fragment.",
                "Bet #2: Pierre's mother is an active celestial or monstrous power who intentionally placed Pierre in the mortal world to hide him."
            ]
        }
    }


# =====================================================================
# CODE GENERATORS
# =====================================================================

def generate_session_pages(manifests, configs, source_decisions, recaps):
    sessions_dir = CODEX_DIR / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    debriefs = get_deep_narrative_debriefs()
    cliffhangers = get_session_cliffhangers()
    lore_map = get_session_lore_discoveries()
    milestones_map = get_session_milestones()
    threads_touched = get_session_threads_touched()

    for s, m in manifests.items():
        cfg = configs.get(s, {})
        title = cfg.get("title", f"Session {s}")
        recap = recaps.get(s, "A chronicle of displaced souls traveling the Lost Roads.")
        debrief = debriefs.get(s, "The party navigates immediate obstacles and uncovers timeline secrets.")
        cliffhanger = cliffhangers.get(s, "The party braces for impending challenges along the Lost Roads.")

        # Chapters count
        blocks = m.get("blocks", [])
        unique_chapters = []
        seen_ch = set()
        for b in blocks:
            sc = b.get("scene")
            if sc and sc not in seen_ch:
                seen_ch.add(sc)
                unique_chapters.append(sc)

        ch_f = unique_chapters[0].split(":")[0].replace("CHAPTER ", "").strip()
        ch_l = unique_chapters[-1].split(":")[0].replace("CHAPTER ", "").strip()

        # Navigation links
        prev_link = f"[⏮️ Session {s-1}](s{s-1}.md)" if s > 1 else "[⏮️ First Session](s1.md)"
        next_link = f"[⏭️ Session {s+1}](s{s+1}.md)" if s < 7 else "[⏭️ Session 8 (Upcoming)]"

        # Active vs Absent
        players = cfg.get("players", {})
        absent = cfg.get("absent_players", {})

        lore_list = lore_map.get(s, [])
        milestones = milestones_map.get(s, [])
        session_threads = threads_touched.get(s, [])

        md = f"""[🏛️ Campaign Codex Home](../README.md) > [📜 Session Chronicles](README.md) > **Session {s}**

# Session {s}: {title}
**Codex Category:** Session Chronicle  
**Novel Chapter Span:** Chapter {ch_f} to Chapter {ch_l} ({len(unique_chapters)} Chapters)  
**Interactive Navigation:** {prev_link} | [📑 All Sessions](README.md) | {next_link} | [🎭 Session {s} Critic Review](../critic/s{s}-review.md)  
**Jump Menu:** [📋 Session Overview](#-session-overview) · [🧭 Next Objective & Cliffhanger](#-next-objective--unresolved-cliffhanger) · [🎬 Narrative Chronicle](#-session-narrative-chronicle) · [👥 Cast & Status](#-dramatis-personae-ensemble-cast) · [🧶 Plot Lines & Threads](#-plot-lines--campaign-threads) · [🏛️ Lore Discoveries](#-in-world-lore--cosmological-discoveries) · [⚔️ Key Story Milestones](#-key-story-milestones--character-turns) · [🎭 Critic Review](../critic/s{s}-review.md)

---

## 📋 Session Overview
{recap}

---

## 🧭 Next Objective & Unresolved Cliffhanger
{cliffhanger}

---

## 🎬 Session Narrative Chronicle
{debrief}
"""


        md += "\n---\n\n## 👥 Dramatis Personae (Ensemble Cast)\n"
        md += "### Active Party Members\n"
        for _, char_name in players.items():
            clean_name = char_name.split("(")[0].strip()
            cid = "dravin" if "dravin" in clean_name.lower() else clean_name.lower()
            md += f"- **[{clean_name}](../characters/{cid}.md)** — Active in-scene, driving party tactical choices and survival.\n"

        if absent:
            md += "\n### Absent Party Members\n"
            for _, char_name in absent.items():
                clean_name = char_name.split("(")[0].strip()
                cid = "dravin" if "dravin" in clean_name.lower() else clean_name.lower()
                md += f"- **[{clean_name}](../characters/{cid}.md)** — Absent from scene (conducting independent archival research or scouting).\n"

        # Recurring Margin Allies vs Guests
        md += "\n### Recurring Margin Allies\n"
        if s >= 2:
            md += "- **[Teddy](../characters/teddy.md)** — Founding Caretaker of The Margin; provides compound guidance and perimeter reports.\n"
            md += "- **[Naomi](../characters/naomi.md)** — Margin Warden & Tactical Coordinator; tracks timeline anomalies on the Anomaly Board.\n"
            md += "- **[Mike](../characters/mike.md)** — Gatekeeper of the Lost Roads; operates the vintage truck and gateway levers.\n"
            md += "- **[Rosa](../characters/rosa.md)** — Cabin Matron & Memory Chronicler; cares for refugees and preserves oral histories.\n"
        else:
            md += "- **[Teddy](../characters/teddy.md)** & **[The Margin Wardens](../factions/margin-wardens.md)** — Displaced sanctuary caretakers awaiting refugees at the forest threshold.\n"

        if s in [1, 2, 5, 6, 7]:
            md += "\n### Notable Guests & Celestial Interventions\n"
            if s == 1:
                md += "- **[The Three Fates](../characters/fates.md)** — Primordial cosmic weavers who weave Alfie and cast the escape net.\n"
            elif s == 5:
                md += "- **[Hermes](../characters/hermes.md)** — Divine messenger who arrives via the Hermes Express with Persephone's solstice dispatch.\n"
                md += "- **[Dr. Aris Thorne](../characters/thorne.md)** — Medical historian lecturing on the controversial 1948 Big Pox clinical trial.\n"
            elif s == 6:
                md += "- **[Dr. Aris Thorne](../characters/thorne.md)** — Flees into campus tunnels as satyr strike teams breach the amphitheater.\n"
            elif s == 7:
                md += "- **[Susanna](../characters/susanna.md)** — Rescued transformed operative freed from Redactor tendril corruption.\n"
                md += "- **[Thanatos](../characters/thanatos.md)** — Greek god of peaceful death who visits Eusacles in a nocturnal dream.\n"

        md += "\n### Adversaries & Threats\n"
        if s in [1]:
            md += "- **Correctors (Ink-Beasts)** — Planar predators tearing through the Library stacks to consume severed threads.\n"
        elif s in [4, 5, 6, 7]:
            md += "- **[The Redactors](../factions/redactors.md)** — Hostile timeline enforcers and stalkers seeking to erase living anomalies.\n"
        else:
            md += "- **Hostile Outpost Attendant** — Aggressive clerk whose confrontation triggers Pierre's latent petrifying glare.\n"

        md += "\n---\n\n## 🧶 Plot Lines & Campaign Threads\n"
        md += "| Thread ID | Core Plot Question | Status This Session | Context & Narrative Development |\n"
        md += "| :--- | :--- | :--- | :--- |\n"
        for tid, tname, tstatus, tcontext in session_threads:
            md += f"| **[{tid}](../threads/open-threads.md#{tid.lower()})** | **{tname}** | `{tstatus}` | {tcontext} |\n"

        if lore_list:
            md += "\n---\n\n## 🏛️ In-World Lore & Cosmological Discoveries\n"
            for term, definition in lore_list:
                md += f"- **{term}:** {definition}\n"

        if milestones:
            md += "\n---\n\n## ⚔️ Key Story Milestones & Character Turns\n"
            for m_item in milestones:
                md += f"- {m_item}\n"

        md += f"""
---

## 🎭 The Critic & Session Review Portal
> **Editorial Review Available:** A deep-dive analysis of narrative pacing, plot line closures, character growth arcs, and predictive bets is documented for this session.  
> 👉 **[Read the Full Session {s} Critic Review & Player Growth Cards →](../critic/s{s}-review.md)**
"""
        out_path = sessions_dir / f"s{s}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)


def generate_sessions_hub():
    hub_md = """[🏛️ Campaign Codex Home](../README.md) > **Session Chronicles Hub**

# 📜 Session Chronicles Portal
**Publication System:** D&D Scribe Publishing Engine  
**Setting:** Mythic Americana / Urban Fantasy  

Welcome to the **Session Chronicles Portal**. Each chronicle contains in-world narrative debriefs, 
chapter-by-chapter breakdowns, character ensemble status, active plot thread tracking, and links to the 
accompanying Critic Editorial Review.

---

## 🗺️ Campaign Acts & Chronicle Directory

### 🌲 Act I: The Shattered Veil & The Margin Sanctuary (Sessions 1–2)
Displaced from ordinary mortal life into dimensional freefall, four strangers awaken in the cosmic Library of the Fates, 
fend off planar ink-beasts, and find refuge in an Appalachian reality crease known as The Margin.
- **[Session 1: The Bus from Vegas & The Library of the Fates](s1.md)** (Chapters 1–12)  
  *The bus rupture, the weaving of Alfie, battle in the stacks, and the tapestry rift to The Margin.*  
  👉 [Read Session 1 Critic Review](../critic/s1-review.md)
- **[Session 2: The Margin, The Fragments & The Lost Roads](s2.md)** (Chapters 13–15)  
  *Intake with Teddy and Rosa, Naomi's Anomaly Board, Pierre's gas station petrifying flare, and gateway departure.*  
  👉 [Read Session 2 Critic Review](../critic/s2-review.md)

---

### 🏛️ Act II: The Raleigh Museum Heist & The Inscription Stele (Sessions 3–4)
Navigating the dimensional mist of the Lost Roads, the company infiltrates the North Carolina Museum of Natural History 
to recover an ancient fractured Greek tablet before Gorgon Redactors destroy it.
- **[Session 3: The Museum Heist in North Carolina](s3.md)** (Chapters 23–25)  
  *Lost Roads transit, Sorbonne intern disguise, Alfie's Wordcraft sheep stampede, and gallery infiltration.*  
  👉 [Read Session 3 Critic Review](../critic/s3-review.md)
- **[Session 4: The Raleigh Museum Gorgon Ambush & Debrief](s4.md)** (Chapters 26–28)  
  *The mezzanine battle, Alfie's traumatic burning coast vision, grounding the relic surge, and return to sanctuary.*  
  👉 [Read Session 4 Critic Review](../critic/s4-review.md)

---

### 🎓 Act III: The University Incursion & The Historical Redactions (Sessions 5–6)
A celestial dispatch from Persephone alerts the Margin to thinning veils. The company travels to University University 
to inspect Dr. Thorne's altered 1948 trial notes, walking directly into a violent planar ambush.
- **[Session 5: The Forgotten Trail & The Mad Doctor's Lecture](s5.md)** (Chapters 29–31)  
  *Hermes arrives with solstice warning, campus demonstrations, altered 1948 'STABLE' to 'STALE' binder, and satyr ambush.*  
  👉 [Read Session 5 Critic Review](../critic/s5-review.md)
- **[Session 6: The Auditorium Incursion & The Memory Seam](s6.md)** (Chapters 32–41)  
  *Pitched combat in the amphitheater, memory-siphoning tendrils, Dravin's lexicon knockout, and janitor cart escape.*  
  👉 [Read Session 6 Critic Review](../critic/s6-review.md)

---

### ⚖️ Act IV: The Interrogation & The Washington Expedition (Session 7+)
Interrogating the captive reveals that the party members are living anomaly vessels targeted for erasure. Following divine 
encounters and domestic respite, the company prepares to infiltrate the Washington, D.C. police evidence locker.
- **[Session 7: The Interrogation, The Redactor & The Dream of Thanatos](s7.md)** (Chapters 42–50)  
  *Cart interrogation, Alfie severs parasitic tendril, Pierre's rabbit patronus, rum pancakes, Thanatos dream, and D.C. mission prep.*  
  👉 [Read Session 7 Critic Review](../critic/s7-review.md)

---

## 🧭 Master Quick Navigation
- 👥 **[Dramatis Personae Hub](../characters/README.md)** — Detailed dossiers on all characters.
- 🏛️ **[Factions & Powers Hub](../factions/README.md)** — Deep profiles on The Margin Wardens and The Redactors.
- 🧶 **[Active Mysteries & Plot Lines](../threads/open-threads.md)** — Track unresolved campaign threads.
- 🎭 **[The Critic & Editorial Reviews Portal](../critic/README.md)** — Comprehensive session scores and player cards.
"""
    with open(CODEX_DIR / "sessions" / "README.md", "w", encoding="utf-8") as f:
        f.write(hub_md)


def generate_characters_hub():
    hub_md = """[🏛️ Campaign Codex Home](../README.md) > **Dramatis Personae Hub**

# 👥 Dramatis Personae (Character Dossiers)
**Publication System:** D&D Scribe Publishing Engine  
**Setting:** Mythic Americana / Urban Fantasy  

Welcome to the **Dramatis Personae Portal**. Here you will find comprehensive character dossiers documenting identities, 
voice cadences, signature abilities, campaign trajectories, and interpersonal dynamics across Sessions 1–7.

---

## 🗡️ The Party (Player Characters)
- **[Pierre](pierre.md)** — Parisian Stonemason & Reluctant Gorgon Scion. Wields epigraphic stonecraft and latent petrifying abilities.
- **[Alfie](alfie.md)** — The Driftwood Duelist & Wordcraft Mage. Living two-foot construct wielding a needle rapier and reality-editing Wordcraft.
- **[Eusacles](eusacles.md)** — Vegas Brawler & Demigod Son of Thanatos. Frontline anchor wielding a chained morningstar and divine sensory awareness.
- **[Prof. Edward Dravin](dravin.md)** — Stanford Classical Historian & Scholar-Necromancer. Academic tactician wielding necrotic frost and ancient lexicons.

---

## 🌲 The Margin Wardens (Recurring Sanctuary Allies)
- **[Teddy](teddy.md)** — Founding Caretaker of The Margin. An 1846 Appalachian surveyor immune to aging within the mountain crease.
- **[Naomi](naomi.md)** — Margin Warden & Tactical Coordinator. Brilliant eleven-year-old strategist operating the strategic Anomaly Board.
- **[Mike](mike.md)** — Gatekeeper of the Lost Roads. Stoic truck mechanic and legendary griddle pancake chef.
- **[Rosa](rosa.md)** — Cabin Matron & Memory Chronicler. Gentle maternal presence preserving oral histories of erased communities.

---

## 🕊️ Rescued Survivors & Academic Allies
- **[Susanna](susanna.md)** — Rescued Operative & Former Redactor Captive. Freed from parasitic tendril corruption; recovering at The Margin.
- **[Dr. Aris Thorne](thorne.md)** — Investigative Medical Historian. Uncovered retroactive tampering in the 1948 Big Pox clinical trial records.

---

## ⚡ Celestial Powers & Cosmic Entities
- **[Thanatos](thanatos.md)** — Greek God of Peaceful Death. Demigod father of Eusacles; operates outside the clerical bureaucracy of the Fates.
- **[The Three Fates](fates.md)** — Clotho, Lachesis, and Atropos. Cosmic weavers of destiny operating the Loom of Time.
- **[Hermes](hermes.md)** — Divine Celestial Courier. Master of the Hermes Express; charges exorbitant fees for interdimensional transit.

---

## 🕶️ Primary Adversary Faction
- **[The Redactors](../factions/redactors.md)** — Hostile planar enforcers and timeline stalkers answering to an unseen 'Master.'
"""
    with open(CODEX_DIR / "characters" / "README.md", "w", encoding="utf-8") as f:
        f.write(hub_md)


def generate_character_pages(manifests):
    chars_dir = CODEX_DIR / "characters"
    chars_dir.mkdir(parents=True, exist_ok=True)

    appearances = defaultdict(list)
    for s, m in manifests.items():
        first_b = m.get("blocks", [])[0]
        last_b = m.get("blocks", [])[-1]
        f_num = first_b.get("scene").split(":")[0].replace("CHAPTER ", "").strip()
        l_num = last_b.get("scene").split(":")[0].replace("CHAPTER ", "").strip()
        ch_span = f"Ch. {f_num}–{l_num}"

        active_in_session = set()
        for b in m.get("blocks", []):
            for seg in b.get("segments", []):
                spk = seg.get("speakerId")
                if spk and spk != "narrator":
                    active_in_session.add(spk)

        for spk in active_in_session:
            appearances[spk].append((s, ch_span))

    character_profiles = {
        "pierre": {
            "name": "Pierre",
            "type": "Player Character (PC)",
            "title": "Parisian Stonemason & Reluctant Gorgon Scion",
            "bio": (
                "Pierre presents himself as a cultured, slightly neurotic Parisian architecture student "
                "with wire-rimmed spectacles, a dark woolen beret, and an instinctive disdain for brutalist "
                "architecture and American convenience-store cuisine. Beneath his fussy exterior lies an ancient, "
                "terrifying heritage: direct maternal bloodline descent from Echidna, the primordial Mother of Monsters. "
                "Sent by his mother to America to discover his origins, Pierre was swept into cosmic freefall aboard a Nevada bus."
            ),
            "voice": (
                "Flamboyant, theatrical French cadence with articulate vocabulary and dramatic flourishes. "
                "Frequently sighs with exasperation, adjusts his wire spectacles when flustered, and peppers his "
                "speech with defensive French polite formulas ('Pardon, monsieur', 'Naturellement'). Under severe "
                "pressure, his voice drops into an intense, quiet focus."
            ),
            "abilities": (
                "- **Petrifying Glare (Gorgon Bloodline):** A golden flare behind his spectacles that can lock living "
                "targets into frozen, rigid paralysis under moments of acute stress.\n"
                "- **Classical Stonecraft & Epigraphy:** Deep tactile resonance with ancient masonry, architectural seams, "
                "and Hellenic inscriptions, allowing him to decipher timeline stele.\n"
                "- **Disguise & Infiltration:** Masterful social deception, disarming guards with the persona of a bumbling academic intern.\n"
                "- **Luminous Patronus:** Ability to conjure a radiant white rabbit patronus to guide refugees through planar mist.\n"
                "- **Signature Gear:** Heavy canvas rucksack containing scrolls stolen from the Fates, spare spectacles, "
                "woolen beret, and bronze javelin."
            ),
            "arc": (
                "From trembling panic in the Library of the Fates to standing as the party's defensive tactician, "
                "Pierre has gradually embraced his dangerous lineage. In Raleigh, he bluffed museum security and "
                "grounded a massive electrical surge through a petrified guard. At University University, he coordinated "
                "the takedown of a transformed operative, and subsequently manifested a radiant patronus in [Session 7](../sessions/s7.md) "
                "to guide [Susanna](susanna.md) to safety."
            ),
            "dynamics": (
                "- **[Alfie](alfie.md):** A fiercely protective, comedic bond. While Pierre complains about Alfie riding on his shoulder "
                "and making blunt Cockney remarks, he treats the tiny duelist with unwavering loyalty.\n"
                "- **[Eusacles](eusacles.md):** Constant banter between Pierre's Parisian refinement and Eusacles' gritty Las Vegas brawling.\n"
                "- **[Prof. Edward Dravin](dravin.md):** Mutual academic respect; Dravin grounds Pierre's architectural passion with historical context."
            ),
        },
        "alfie": {
            "name": "Alfie",
            "type": "Player Character (PC)",
            "title": "The Driftwood Duelist & Wordcraft Mage",
            "bio": (
                "Alfie is a living construct standing roughly two feet tall, carved from salt-crusted driftwood "
                "with sailcloth joints, polished seashell buttons for eyes, and a steel hook for a left hand. "
                "Woven into reality by [The Three Fates](fates.md) in the Library of Destiny, she carries four centuries of "
                "accumulated thread memory from drowned sailor cloaks, despite having walked the world for mere days."
            ),
            "voice": (
                "Raspy, confident Cockney sailor cadence packed with maritime idioms and razor-sharp wit. "
                "Fiercely proud and sensitive regarding her dignity—demanding to be recognized as an 'action figure' "
                "or 'fencing master,' never a 'doll' (which she vehemently dubs 'the D-word')."
            ),
            "abilities": (
                "- **Wordcraft (Reality Editing):** Supernatural ability to alter spells and physical concepts by "
                "substituting a single letter (e.g. *Sleep* into *Sheep* to summon spectral distractions).\n"
                "- **Needle Rapier:** A razor-sharp steel fencing needle wielded with deadly speed and surgical accuracy.\n"
                "- **Tendon Sever:** Low-profile acrobatic melee strikes aimed at crippling large adversaries at the heel.\n"
                "- **Chaos Belt:** An enchanted Fate-bound buckle capable of releasing wild, unexpected planar surges.\n"
                "- **Signature Gear:** Needle rapier, steel hook hand, sailcloth vest, seashell button eyes, and severed tendril scarf."
            ),
            "arc": (
                "Awakening without personal memories in the Library of the Fates in [Session 1](../sessions/s1.md), Alfie immediately "
                "proved her valor fending off ink-beasts. Touching the Raleigh stele in [Session 4](../sessions/s4.md) unlocked harrowing "
                "flashbacks of burning coastal ports. In [Session 7](../sessions/s7.md), she revealed 458 years of collective thread consciousness "
                "over rum pancakes and severed the parasitic tendril that freed [Susanna](susanna.md)."
            ),
            "dynamics": (
                "- **[Pierre](pierre.md):** Her trusted steed and confidant. She perches on his shoulder during travel and infiltration.\n"
                "- **[Eusacles](eusacles.md):** Sparring banter partner; Eusacles watches out for her safety despite her constant protests of independence.\n"
                "- **[Rosa](rosa.md):** A gentle maternal bond; Rosa was the first Margin resident to listen to Alfie's fragmented memories."
            ),
        },
        "eusacles": {
            "name": "Eusacles",
            "type": "Player Character (PC)",
            "title": "Vegas Brawler & Demigod Son of Thanatos",
            "bio": (
                "A cynical, battle-hardened drifter from Las Vegas who was catching a midnight Greyhound to play roulette "
                "when reality tore open. Eusacles is the mortal demigod son of [Thanatos](thanatos.md), the Greek personification of peaceful death. "
                "Despite his gruff exterior and constant longing for a casino lounge, he is the party's unflinching physical protector."
            ),
            "voice": (
                "Dry, gravelly American drawl marked by cynical humor, casino slang, and no-nonsense practicality. "
                "He speaks plainly, cuts through academic theorizing, and demands to see concrete physical evidence."
            ),
            "abilities": (
                "- **Divine Sensory Scout:** Ability to perceive metaphysical auras, distinguishing celestial, necrotic, "
                "and planar signatures.\n"
                "- **Watch-Chain Morningstar:** A five-dollar wristwatch that magically extends into a heavy, spiked iron morningstar.\n"
                "- **Thanatos' Tier 2 Birthright:** An engraved pocket watch enchanted by his divine father that bolsters his "
                "defensive armor whenever his physical vitality falls below a quarter.\n"
                "- **Frontline Brawling:** Spartan kicks, shoulder charges, and brutal close-quarters melee combat.\n"
                "- **Signature Gear:** Heavy denim jacket, aviator sunglasses, combat boots, and engraved Thanatos watch."
            ),
            "arc": (
                "Displaced from the Nevada desert into celestial chaos, Eusacles has embraced his role as frontline guardian. "
                "He rebuilt a damaged cabin at [The Margin](../factions/margin-wardens.md), stood firm against Gorgons in Raleigh, and "
                "suffered psychic memory drain in the University auditorium. In [Session 7](../sessions/s7.md), his father Thanatos visited him in a "
                "campfire dream, validating his lineage and armoring his pocket watch."
            ),
            "dynamics": (
                "- **[Pierre](pierre.md):** Affectionate adversarial banter; Eusacles teases Pierre's Parisian elegance while relying on his magic.\n"
                "- **[Alfie](alfie.md):** Protective big-brother dynamic; he checks the rum content of her breakfast and guards her flanks.\n"
                "- **[Thanatos](thanatos.md):** An estranged, wry father-son dynamic marked by cosmic deadpan humor and unspoken respect."
            ),
        },
        "dravin": {
            "name": "Prof. Edward Dravin",
            "type": "Player Character (PC)",
            "title": "Stanford Classical Historian & Scholar-Necromancer",
            "bio": (
                "Professor Edward Dravin is a senior academic of classical Greek history at Stanford University. Clad in rumpled "
                "tweed coats and wire spectacles, he approaches cosmic timeline ruptures through disciplined historiography and "
                "epigraphic rigor. His maternal Greek ancestry connects him to Persephone, granting him quiet authority over "
                "threshold and preservation magic."
            ),
            "voice": (
                "Patrician, measured scholarly diction with academic cadence. Even in life-or-death combat, he articulates "
                "observations as though delivering a guest seminar, maintaining remarkable analytical calm."
            ),
            "abilities": (
                "- **Necrotic Threshold Magic:** Manifests spectral skeletal hands, frosty mist, and *Chill Touch* to freeze adversaries.\n"
                "- **Toll the Dead & Silver Chime:** Strikes a tarnished pocket bell to inflict psychic dread upon planar beasts.\n"
                "- **Twilight Sanctuary & Moonbeam:** Radiant lunar wards that shield allies and bathe battlefield corridors in twilight.\n"
                "- **Lexicon Strike:** Crushing physical melee strikes delivered with colossal, leather-bound classical lexicons.\n"
                "- **Signature Gear:** Rumpled tweed coat with deep pockets, tarnished silver chime, pomegranate pin, and hoplite shield."
            ),
            "arc": (
                "Dravin provided immediate tactical calm during the bus rift in [Session 1](../sessions/s1.md). In Raleigh, he secured an ancient "
                "hoplite shield. At University University in [Session 5](../sessions/s5.md) and [Session 6](../sessions/s6.md), his scholarship "
                "proved vital in identifying Dr. Thorne's altered trial notes and neutralizing the transformed operative with a lexicon blow."
            ),
            "dynamics": (
                "- **[Pierre](pierre.md):** Fellow intellectual sparring partner; they debate epigraphy, historical truth, and translation.\n"
                "- **[Naomi](naomi.md):** High tactical respect; Dravin admires Naomi's strategic acumen and anomaly tracking models.\n"
                "- **Persephone:** Devotional bond; he wears her pomegranate signet and heeds her seasonal solstice warnings."
            ),
        },
        "teddy": {
            "name": "Teddy",
            "type": "Non-Player Character (NPC)",
            "title": "Founding Caretaker of The Margin · 1846 Surveyor",
            "bio": (
                "Theodore is the founding caretaker of [The Margin](../factions/margin-wardens.md). An Appalachian surveyor and woodsman from 1846, "
                "Teddy was displaced when an upstream timeline redaction wiped his entire home county from mortal maps. Living in the timeless "
                "crease for nearly two centuries without aging, he tends the cabins, smokes his pipe, and guides newly arrived refugees."
            ),
            "voice": "Slow, warm mountain drawl filled with rural wisdom, calm patience, and steady reassurance.",
            "abilities": (
                "- **Cartographic Instinct:** Absolute knowledge of mountain trails, sanctuary borders, and dimensional seams.\n"
                "- **Sanctuary Maintenance:** Woodcraft, carpentry, and tending the protective threshold hearths."
            ),
            "arc": "Serves as the emotional anchor of the compound, welcoming newcomers in [Session 2](../sessions/s2.md) and reporting perimeter sightings.",
            "dynamics": "- **[Mike](mike.md):** Lifelong companion and silent partner in running the sanctuary.\n- **[Naomi](naomi.md):** Provides paternal grounding to Naomi's relentless tactical drive.",
        },
        "naomi": {
            "name": "Naomi",
            "type": "Non-Player Character (NPC)",
            "title": "Margin Warden & Tactical Coordinator",
            "bio": (
                "An intense, extraordinarily brilliant eleven-year-old girl residing at [The Margin](../factions/margin-wardens.md). Her sharp maturity and "
                "tactical discipline far exceed her physical age. Refusing to merely hide in safety, Naomi actively tracks "
                "'fresh ink'—physical stone and parchment Fragments resulting from timeline alterations."
            ),
            "voice": "Rapid-fire, highly articulate cadence with zero tolerance for excuses, foolishness, or hesitation.",
            "abilities": (
                "- **Anomaly Tracking:** Operates the strategic Anomaly Board, analyzing timeline fractures across the continent.\n"
                "- **Combat Drills:** Conducts rigorous blackout drills and dawn push-up regimens to prepare refugees for incursions."
            ),
            "arc": "Directed the company to Raleigh in [Session 2](../sessions/s2.md), and in [Session 7](../sessions/s7.md) uncovered the airline hijacking lead pointing to Washington, D.C.",
            "dynamics": "- **[Alfie](alfie.md):** Mutual respect between two small, formidable powerhouses.\n- **[Teddy](teddy.md):** Relies on Teddy for operational stability while pushing the offensive front.",
        },
        "mike": {
            "name": "Mike",
            "type": "Non-Player Character (NPC)",
            "title": "Gatekeeper of the Lost Roads",
            "bio": (
                "Teddy's quiet, stoic companion who maintains the settlement's vintage 1978 farm truck and operates the hidden "
                "oak-trunk lever that opens the dimensional gateway into the Lost Roads."
            ),
            "voice": "Spares words whenever possible; speaks in quiet, gruff murmurs accompanied by a slight nod.",
            "abilities": "- **Gate Mechanics:** Expert knowledge of the Lost Roads gateway mechanisms.\n- **Camp Cooking:** Legendary rum-infused griddle pancakes that revive exhausted fighters.",
            "arc": "Transports the party to and from the Lost Roads, cooking celebratory breakfasts upon their return in [Session 7](../sessions/s7.md).",
            "dynamics": "- **[Teddy](teddy.md):** Decades of unspoken camaraderie.\n- **[Alfie](alfie.md):** Serves her extra helpings of rum pancakes while listening to her thread tales.",
        },
        "rosa": {
            "name": "Rosa",
            "type": "Non-Player Character (NPC)",
            "title": "Cabin Matron & Memory Chronicler",
            "bio": (
                "A warm, maternal resident of [The Margin](../factions/margin-wardens.md) who weaves wool quilts, prepares cedar sleeping cabins, and gently "
                "interviews newcomers about their earliest pre-Margin memories to preserve their identity against temporal drift."
            ),
            "voice": "Gentle, soothing cadence that disarms trauma and invites honest reflection.",
            "abilities": "- **Memory Preservation:** Skilled at cataloging oral histories of erased communities.\n- **Sanctuary Hospitality:** Provides medical care, bedding, and comfort.",
            "arc": "Helped Alfie process her initial awakening in [Session 2](../sessions/s2.md) and provided refuge for Susanna upon her rescue in [Session 7](../sessions/s7.md).",
            "dynamics": "- **[Susanna](susanna.md):** Nursing Susanna through recovery following the severing of her Redactor tendril.",
        },
        "susanna": {
            "name": "Susanna",
            "type": "Non-Player Character (NPC)",
            "title": "Rescued Operative · Former Redactor Captive",
            "bio": (
                "A mortal woman captured and biologically mutated by [The Redactors](../factions/redactors.md). Grafted with shadowy tendrils and "
                "subjected to memory erasure, she was deployed to recover altered historical documents before being subdued in the "
                "auditorium in [Session 6](../sessions/s6.md) and liberated by Alfie's needle rapier in [Session 7](../sessions/s7.md)."
            ),
            "voice": "Initially raspy and strained with cognitive trauma, warming into quiet gratitude as recovery begins.",
            "abilities": "- **Former Redactor Insight:** Deep familiarity with Redactor tracking patterns and the Master's doctrine.",
            "arc": "Rescued in [Session 7](../sessions/s7.md), she was safely guided to The Margin by Pierre's rabbit patronus to recover under Rosa's care.",
            "dynamics": "- **[Pierre](pierre.md):** Indebted to Pierre for his rabbit patronus escort along the Lost Roads.\n- **[Alfie](alfie.md):** Deeply grateful to Alfie for severing the parasite that enslaved her mind.",
        },
        "thanatos": {
            "name": "Thanatos",
            "type": "Celestial Entity",
            "title": "Greek God of Peaceful Death · Divine Father of Eusacles",
            "bio": (
                "The ancient Greek personification of peaceful, non-violent death. Draped in midnight feathers and possessing "
                "a dark, booming sense of humor, Thanatos operates outside the clerical bureaucracy of the Fates, intervening "
                "through nocturnal dreams and threshold communion."
            ),
            "voice": "Deep, resonant, booming laughter with rich warmth and cosmic irony.",
            "abilities": "- **Divine Armor Blessing:** Can enchant artifacts to bestow divine armor protection during physical peril.",
            "arc": "Manifested in Eusacles' campfire dream in [Session 7](../sessions/s7.md), engraving his watch and laughing uproariously at the mystery of Pierre's mother.",
            "dynamics": "- **[Eusacles](eusacles.md):** His demigod son; tests his resolve while granting quiet, life-saving gifts.",
        },
        "fates": {
            "name": "The Three Fates",
            "type": "Celestial Entity",
            "title": "Cosmic Weavers of Destiny (Clotho, Lachesis, Atropos)",
            "bio": (
                "The primordial Greek personifications of destiny who dwell in a colossal marble Library beyond normal time. "
                "As they weave the cosmic tapestry on the Loom of Time, they actively combat timeline incursions by crafting living champions."
            ),
            "voice": "Multivocal, resonant, urgent, and stressed by cosmic timeline breaches.",
            "abilities": "- **Loom Manipulation:** Weaving, measuring, and severing the threads of mortal history.",
            "arc": "Spun Alfie from driftwood and dead sailors' threads in [Session 1](../sessions/s1.md), extracting the party from ink-beasts via a shimmering tapestry net.",
            "dynamics": "- **[Alfie](alfie.md):** Her cosmic creators and weavers.",
        },
        "thorne": {
            "name": "Dr. Aris Thorne",
            "type": "Non-Player Character (NPC)",
            "title": "Investigative Medical Historian · 1948 Trial Lecturer",
            "bio": (
                "An eccentric, outspoken medical historian who discovered that archival records of the 1948 Big Pox clinical trial "
                "were being retroactively rewritten. His public lecture at University University drew fierce protests and violent Redactor ambush."
            ),
            "voice": "Heated, rapid, passionate academic elocution punctuated by nervous urgency.",
            "abilities": "- **Archival Epigraphy:** Unmatched forensic knowledge of 20th-century institutional trial records.",
            "arc": "Delivered the pivotal lecture in [Session 5](../sessions/s5.md) that exposed the alteration of 'STABLE' to 'STALE' before fleeing into campus tunnels.",
            "dynamics": "- **[Prof. Edward Dravin](dravin.md):** Fellow academic whose discovery of Thorne's binder confirmed the reality of timeline manipulation.",
        },
        "hermes": {
            "name": "Hermes",
            "type": "Celestial Entity",
            "title": "Divine Courier of Olympus · Master of the Hermes Express",
            "bio": (
                "The golden-sandaled messenger god of Olympus. Operating across cosmic creases and planar thresholds, Hermes functions "
                "as an extortionate interdimensional courier who demands exorbitant fees to transport travelers or deliver urgent missives."
            ),
            "voice": "Brisk, smooth, transactional, and relentlessly witty.",
            "abilities": "- **Planar Transit:** The Hermes Express, bypassing normal geographic space in seconds.",
            "arc": "Delivered Persephone's sealed solstice warning in [Session 5](../sessions/s5.md) and extorted Teddy for passage in past decades.",
            "dynamics": "- **Persephone:** Delivers her high-priority threshold correspondence.\n- **[Teddy](teddy.md):** History of high-priced transport bargains.",
        },
    }

    for cid, meta in character_profiles.items():
        name = meta["name"]
        ctype = meta["type"]
        title = meta["title"]
        bio = meta["bio"]
        voice = meta["voice"]
        abilities = meta["abilities"]
        arc = meta["arc"]
        dynamics = meta["dynamics"]

        app_list = list(appearances.get(cid, []))
        if cid == "teddy" and "theodore" in appearances:
            for s, ch in appearances["theodore"]:
                if (s, ch) not in app_list:
                    app_list.append((s, ch))
            app_list.sort(key=lambda x: x[0])

        md = f"""[🏛️ Campaign Codex Home](../README.md) > [👥 Dramatis Personae](README.md) > **{name}**

# {name}
**Type:** {ctype}  
**Title & Role:** {title}  
**Quick Nav:** [🎭 Identity & Backstory](#-character-identity--backstory) · [🎙️ Voice & Cadence](#️-personality-voice--physical-cadence) · [⚡ Abilities & Gear](#-core-abilities-artifacts--equipment) · [📜 Story Trajectory](#-key-story-milestones--campaign-trajectory) · [👥 Relationships](#-ensemble-dynamics--key-relationships) · [📊 Appearance Log](#-campaign-appearance-index)

---

## 🎭 Character Identity & Backstory
{bio}

---

## 🎙️ Personality, Voice & Physical Cadence
{voice}

---

## ⚡ Core Abilities, Artifacts & Equipment
{abilities}

---

## 📜 Key Story Milestones & Campaign Trajectory
{arc}

---

## 👥 Ensemble Dynamics & Key Relationships
{dynamics}

---

## 📊 Campaign Appearance Index
| Session | Chapter Span | In-World Status |
| :--- | :--- | :--- |
"""
        for s, ch in sorted(app_list, key=lambda x: x[0]):
            status = "Active In-Scene"
            if s == 4 and cid == "eusacles":
                status = "Absent (Perimeter scouting trip)"
            elif s == 7 and cid == "dravin":
                status = "Absent (University archive research)"
            md += f"| [Session {s}](../sessions/s{s}.md) | {ch} | {status} |\n"

        if not app_list:
            md += "| None | — | Historical / Celestial Reference |\n"

        out_path = chars_dir / f"{cid}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)


def generate_factions_hub():
    hub_md = """[🏛️ Campaign Codex Home](../README.md) > **Factions & Powers Hub**

# 🏛️ Factions & Powers Portal
**Publication System:** D&D Scribe Publishing Engine  
**Setting:** Mythic Americana / Urban Fantasy  

Welcome to the **Factions Portal**. Here you will find deep briefings on the organizations, threshold protectors, 
and timeline enforcers operating across the mortal realm and cosmic creases.

---

## ⚔️ Active Factions

### 1. 🌲 [The Margin Wardens](margin-wardens.md) (Allied Sanctuary Keepers)
Displaced survivors maintaining a peaceful settlement hidden within an Appalachian reality crease. Immune to aging and 
shielded from upstream timeline redactions, the Wardens guard the Lost Roads gateway and track continental timeline Fragments.
- **Key Personnel:** [Teddy](../characters/teddy.md) (Founding Caretaker), [Naomi](../characters/naomi.md) (Tactical Coordinator), [Mike](../characters/mike.md) (Gatekeeper), [Rosa](../characters/rosa.md) (Cabin Matron).
- 👉 **[Read Full Margin Wardens Dossier →](margin-wardens.md)**

### 2. 🕶️ [The Redactors](redactors.md) (Primary Adversary Faction)
Hostile planar enforcers operating under a veil of normalcy to eliminate temporal anomalies, suppress unauthorized 
historical epigraphy, and enforce retroactive timeline redactions across mortal academies and planar crossings.
- **Operative Classes:** Gorgon Units, Satyr Strike Teams, Tendril-Grafted Operatives, Six-Fingered Stalkers.
- 👉 **[Read Full Redactors Dossier →](redactors.md)**
"""
    with open(CODEX_DIR / "factions" / "README.md", "w", encoding="utf-8") as f:
        f.write(hub_md)


def generate_faction_pages():
    factions_dir = CODEX_DIR / "factions"
    factions_dir.mkdir(parents=True, exist_ok=True)

    redactors_md = """[🏛️ Campaign Codex Home](../README.md) > [🏛️ Factions Portal](README.md) > **The Redactors**

# The Redactors
**Type:** Primary Adversary Faction  
**Role:** Timeline Enforcers & Erasure Operatives  
**Title Rank:** Redactor (Individual operative rank)  

---

## 🏛️ Directives & Methodology
The Redactors are hostile planar enforcers operating under a veil of mundane normalcy to eliminate temporal anomalies, 
suppress unauthorized historical epigraphy, and enforce retroactive timeline redactions across mortal academies and planar crossings. 
Answering to an unseen 'Master,' their operations seek to overwrite historical branch points to manufacture a curated timeline.

Operatives operate across several distinct echelons:
- **Gorgon Units:** Serpent-crowned infiltration operatives capable of direct assault and relic destruction.
- **Satyr Strike Teams:** Heavily muscled frontline assault units employed for rapid kinetic ambushes in confined structures.
- **Tendril-Grafted Operatives:** Captured mortals biologically altered with parasitic shadowy appendages to siphon memories.
- **Six-Fingered Stalkers:** Elite multi-faced tracking specialists capable of hunting anomaly vessels across campus quads.

---

## ⚔️ Known Campaign Engagements
- **[Session 4](../sessions/s4.md) (Raleigh Museum):** Gorgon strike units assault the Aegean antiquity wing to destroy the Greek inscription stele.
- **[Session 5](../sessions/s5.md) & [Session 6](../sessions/s6.md) (University University):** Satyr assault teams and transformed operatives ambush the backstage corridors and storm the auditorium to seize Dr. Thorne's altered trial binder.
- **[Session 7](../sessions/s7.md) (Campus Quad & Lost Roads):** A multi-faced, six-fingered stalker shadows the party across campus before being repelled by Pierre's patronus.
"""
    with open(factions_dir / "redactors.md", "w", encoding="utf-8") as f:
        f.write(redactors_md)

    margin_md = """[🏛️ Campaign Codex Home](../README.md) > [🏛️ Factions Portal](README.md) > **The Margin Wardens**

# The Margin Wardens
**Type:** Allied Sanctuary Faction  
**Role:** Threshold Caretakers & Anomaly Navigators  
**Base:** The Margin Sanctuary (Appalachian Temporal Crease)  

---

## 🏛️ Directives & Sanctuary Keepers
The Margin Wardens are displaced survivors maintaining a peaceful settlement hidden within an Appalachian reality crease. 
Because calendar time does not advance within the mist-shielded compound, residents are immune to aging and shielded from 
upstream timeline redactions.

The Wardens maintain defensive perimeter watches, operate the dimensional gateway to the Lost Roads, and track continental 
anomalies to retrieve loose historical Fragments before Redactor hit squads destroy them.

---

## 👥 Key Personnel
- **[Teddy](../characters/teddy.md):** Founding Caretaker and 1846 surveyor; calm mentor and compound patriarch.
- **[Naomi](../characters/naomi.md):** Warden coordinator, anomaly board strategist, and combat drill instructor.
- **[Mike](../characters/mike.md):** Gatekeeper of the Lost Roads, truck mechanic, and legendary campfire cook.
- **[Rosa](../characters/rosa.md):** Compound logistics coordinator, quilt weaver, and memory chronicler.
"""
    with open(factions_dir / "margin-wardens.md", "w", encoding="utf-8") as f:
        f.write(margin_md)


def generate_threads_page():
    threads_dir = CODEX_DIR / "threads"
    threads_dir.mkdir(parents=True, exist_ok=True)

    threads_md = """[🏛️ Campaign Codex Home](../README.md) > **Active Mysteries & Plot Lines Board**

# 🧶 Open Campaign Threads & Active Mysteries Board
**Codex Category:** Campaign Progression  

Welcome to the **Campaign Mysteries Board**. This living ledger tracks active plot threads, origin questions, 
and major narrative hooks across Sessions 1–7.

To guard against speculative over-joining, this board strictly distinguishes between **Established In-World Evidence** 
(observable facts, recovered documents, physical relics, and confirmed encounters) and **Party Hypotheses & Inquiries** 
(unconfirmed theories, working deductions, and player suspicions).

---

## 🧭 Active Mysteries & Campaign Hooks

| Thread ID | Core Plot Question & Mystery | Origin | Status | Established In-World Evidence (Observed Facts) | Party Hypotheses & Open Inquiries |
| :--- | :--- | :--- | :--- | :--- | :--- |
| <a id="th-01"></a>**TH-01** | **[Alfie's Origin & Carving](../characters/alfie.md):** Who carved the sentient driftwood construct, and what historical coastal raid is burned into her memory? | [Session 1](../sessions/s1.md) | `Active` | Woven from weathered driftwood and drowned sailors' cloaks by the Three Fates. Possesses 458 years of thread memory; experiences vivid sensory flashbacks of freezing brine, dark oarsmen, and a coastal village put to the torch. | The party suspects her wood was salvaged from a specific historical naval raid erased by Redactors. |
| <a id="th-02"></a>**TH-02** | **[The Naval Nightmare Stele Resonance](../characters/alfie.md):** Why did touching the Raleigh Greek inscription tablet trigger traumatic naval flashbacks? | [Session 4](../sessions/s4.md) | `Active` | Touching the fractured Aegean stele triggered violent electrical shock and intense hallucinations of ancient naval warfare. Causes chronic insomnia requiring lanterns burning through the night. | Alfie theorizes that timeline fragments physically discharge the traumatic suffering of the people erased in that branch point. |
| <a id="th-03"></a>**TH-03** | **[1948 Big Pox Clinical Trial Reality](../characters/thorne.md):** Did Dr. Thorne's altered formula cure the disease or poison patients, and why was the word 'STABLE' altered? | [Session 5](../sessions/s5.md) | `Active` | Recovered 1948 trial notes binder from University University green room exhibits physical ink alterations where 'STABLE' was retroactively overwritten to 'STALE'. Satyr strike teams attacked specifically to seize it. | Professor Dravin deduces that an unknown entity ('The Master') altered the historical record to conceal that the clinical trial was an intentional massacre rather than a medical failure. |
| <a id="th-04"></a>**TH-04** | **[Persephone's Winter Solstice Warning](../characters/hermes.md):** What specific danger threatens the Margin as Persephone descends into the underworld? | [Session 5](../sessions/s5.md) | `Active` | Sealed dispatch delivered via the Hermes Express warns that seasonal thinning of cosmic veils exposes reality creases to planar predators. | Teddy and Naomi deduce that the winter solstice will trigger direct Redactor assaults against the Margin perimeter. |
| <a id="th-05"></a>**TH-05** | **[The Six-Fingered Redactor Operative](../factions/redactors.md):** Who is the multi-faced Redactor stalker shadowing the party across university quads? | [Session 7](../sessions/s7.md) | `Active` | An elite tracking specialist possessing six fingers per hand and constantly shifting facial features shadowed the party across campus before being distracted by Pierre's rabbit patronus. | The party hypothesizes that the operative is a specialized biometric tracker keyed to their living anomaly signatures. |
| <a id="th-06"></a>**TH-06** | **[Washington D.C. Police Evidence Locker Expedition](../sessions/s7.md):** Recovering the anomalous cataloged evidence referenced in Naomi's briefing. | [Session 7](../sessions/s7.md) | `Immediate Lead` | Naomi pinned reconnaissance photographs to the Anomaly Board detailing a high-security evidence locker in Washington, D.C. holding an artifact from an unrecorded 1980s airline flight. | The party plans to utilize academic credentials and forged transit paperwork to infiltrate the municipal locker without tripping mortal police alarms. |
| <a id="th-07"></a>**TH-07** | **The Nature of Timeline Fragments:** Can a Fragment exist purely as an unanchored historical event, or must it possess a physical relic anchor? | [Session 5](../sessions/s5.md) | `Active In-World Inquiry` | The Raleigh stele and Thorne's trial notes both functioned as physical anchors for historical anomalies. | The party debates whether historical events can be altered without a physical anchor stone or parchment, or if all timeline folds require a material core. |
| <a id="th-08"></a>**TH-08** | **[Eusacles' Engraved Watch Resonance](../characters/eusacles.md):** Thanatos dream confirmation of watch enchantment and cryptic hints regarding Pierre's lineage. | [Session 7](../sessions/s7.md) | `Confirmed / Resolved` | Thanatos manifested in Eusacles' campfire dream, physically engraving divine armor runes onto his five-dollar wristwatch, and laughed uproariously when asked about Pierre's mother. | Eusacles suspects Pierre's mother is an ancient Olympian or Gorgon deity who deliberately hid Pierre in the mortal world. |
"""
    with open(threads_dir / "open-threads.md", "w", encoding="utf-8") as f:
        f.write(threads_md)


def generate_critic_hub():
    critic_dir = CODEX_DIR / "critic"
    critic_dir.mkdir(parents=True, exist_ok=True)

    hub_md = """[🏛️ Campaign Codex Home](../README.md) > **The Critic & Editorial Reviews Hub**

# 🎭 The Critic & Editorial Reviews Portal
**Publication System:** D&D Scribe Publishing Engine (DEC-037 / DEC-039)  
**Standard of Excellence:** The Stormlight Behavioral Standard (Observable Character Growth & Sacrificial Action)  

Welcome to the **Critic Portal**. The Critic section operates as an independent, public editorial lens evaluating 
narrative momentum, dramatic tension, comedic reversals, and character trajectory across each session.

---

## 🎯 Review Standards
1. **Observable Behaviors:** Evaluates characters strictly on observable actions—protecting others at personal cost, 
   wounds leaking into behavior, oaths tested at costly moments, and bonds forged through small acts.
2. **Plot Line Progression:** Audits which campaign threads opened, deepened, or closed, ensuring satisfying narrative payoff.
3. **GM & Encounter Craft:** Analyzes pacing, atmospheric contrast, adversary tactics, and spatial staging.
4. **Active Bets:** Documents immutable, forward-looking AI bets regarding impending player choices and plot mysteries.

---

## 📜 Session Editorial Reviews
- **[Session 1 Editorial Review](s1-review.md)** — *The Cosmic Freefall & The Emergence of Alfie (Score: 8.8 / 10)*
- **[Session 2 Editorial Review](s2-review.md)** — *Sanctuary Decompression & The First Petrification (Score: 8.5 / 10)*
- **[Session 3 Editorial Review](s3-review.md)** — *Academic Disguises & The Wordcraft Sheep Stampede (Score: 8.7 / 10)*
- **[Session 4 Editorial Review](s4-review.md)** — *Mezzanine Warfare & The Burning Coast Trauma (Score: 9.2 / 10)*
- **[Session 5 Editorial Review](s5-review.md)** — *The Mad Doctor's Lecture & The Altered Ink Seam (Score: 9.0 / 10)*
- **[Session 6 Editorial Review](s6-review.md)** — *The Auditorium Incursion & The Lexicon Knockout (Score: 9.3 / 10)*
- **[Session 7 Editorial Review](s7-review.md)** — *The Tendril Severing, Rum Pancakes & The Dream of Thanatos (Score: 9.5 / 10)*
"""
    with open(critic_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(hub_md)


def generate_critic_pages():
    critic_dir = CODEX_DIR / "critic"
    critic_dir.mkdir(parents=True, exist_ok=True)

    reviews = get_critic_reviews()

    for s in range(1, 8):
        rev = reviews.get(s, {})
        score = rev.get("score", "8.5 / 10")
        highlights = rev.get("highlights", "")
        threads_audit = rev.get("threads_audit", "")
        cards = rev.get("character_cards", {})
        gm_craft = rev.get("gm_craft", "")
        bets = rev.get("bets", [])

        prev_link = f"[⏮️ Session {s-1} Review](s{s-1}-review.md)" if s > 1 else "[⏮️ First Review](s1-review.md)"
        next_link = f"[⏭️ Session {s+1} Review](s{s+1}-review.md)" if s < 7 else "[⏭️ Next Review (Upcoming)]"

        md = f"""[🏛️ Campaign Codex Home](../README.md) > [🎭 The Critic Portal](README.md) > **Session {s} Review**

# 🎭 Editorial Review: Session {s}
**Session Scorecard:** `{score}`  
**Chronicle Link:** [📖 Read In-World Session {s} Chronicle](../sessions/s{s}.md)  
**Navigation:** {prev_link} | [📑 All Reviews](README.md) | {next_link}  

---

## 🎯 Pacing & Narrative Highlights
{highlights}

---

## 🧶 Plot Lines & Thread Audit
{threads_audit}

---

## 🌱 Character Growth Cards (The Stormlight Standard)
"""
        for char, card in cards.items():
            cid = "dravin" if "dravin" in char.lower() else char.lower()
            md += f"### [{char}](../characters/{cid}.md)\n{card}\n\n"

        md += f"""---

## 🎲 GM & Worldcraft Evaluation
{gm_craft}

---

## 🔮 Narrative Bets & Forward Hypotheses
"""
        for bet in bets:
            md += f"- {bet}\n"

        out_path = critic_dir / f"s{s}-review.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)


def generate_master_index():
    index_md = """# 🏛️ The Margin Campaign Codex & World Wiki
**Publication System:** D&D Scribe Publishing Engine  
**Setting:** Mythic Americana / Urban Fantasy (Daggerheart System)  

Welcome to the **Campaign Codex**, the official interactive reference wiki for *The Margin: The Stolen Weave*. 
The codex is organized into dedicated portals providing in-world continuity, character dossiers, session debriefs, 
faction profiles, active mystery boards, and editorial reviews.

---

## 🧭 Master Wiki Portals

### 📜 1. [Session Chronicles Portal](sessions/README.md)
Explore comprehensive in-world session debriefs, chapter-by-chapter breakdowns, character ensemble logs, 
and narrative cliffhangers across all four campaign acts.
- [Session 1: The Bus from Vegas & The Library of the Fates](sessions/s1.md)
- [Session 2: The Margin, The Fragments & The Lost Roads](sessions/s2.md)
- [Session 3: The Museum Heist in North Carolina](sessions/s3.md)
- [Session 4: The Raleigh Museum Gorgon Ambush & Debrief](sessions/s4.md)
- [Session 5: The Forgotten Trail & The Mad Doctor's Lecture](sessions/s5.md)
- [Session 6: The Auditorium Incursion & The Memory Seam](sessions/s6.md)
- [Session 7: The Interrogation, The Redactor & The Dream of Thanatos](sessions/s7.md)

---

### 👥 2. [Dramatis Personae Portal](characters/README.md)
Access deep dossiers covering character backstories, voice cadences, signature abilities, campaign trajectories, 
and interpersonal dynamics.
- **The Party:** [Pierre](characters/pierre.md) · [Alfie](characters/alfie.md) · [Eusacles](characters/eusacles.md) · [Prof. Edward Dravin](characters/dravin.md)
- **Margin Wardens:** [Teddy](characters/teddy.md) · [Naomi](characters/naomi.md) · [Mike](characters/mike.md) · [Rosa](characters/rosa.md)
- **Allies & Rescued Souls:** [Susanna](characters/susanna.md) · [Dr. Aris Thorne](characters/thorne.md)
- **Celestial Powers:** [Thanatos](characters/thanatos.md) · [The Three Fates](characters/fates.md) · [Hermes](characters/hermes.md)

---

### 🏛️ 3. [Factions & Powers Portal](factions/README.md)
Briefings on the allied sanctuary keepers and hostile timeline enforcers shaping the planar conflict.
- [The Margin Wardens](factions/margin-wardens.md) — Appalachian sanctuary guardians maintaining the Lost Roads.
- [The Redactors](factions/redactors.md) — Hostile timeline enforcers seeking to erase historical anomalies.

---

### 🧶 4. [Active Mysteries & Plot Lines Board](threads/open-threads.md)
A living tracking board monitoring 8 active campaign threads, origin mysteries, and impending expedition hooks.
- **Key Threads:** Alfie's Naval Origin (`TH-01`), The Raleigh Stele Flashbacks (`TH-02`), The 1948 Trial Notes (`TH-03`), Persephone's Solstice Warning (`TH-04`), The Washington D.C. Evidence Locker (`TH-06`).

---

### 🎭 5. [The Critic & Editorial Reviews Portal](critic/README.md)
Independent session reviews evaluating narrative momentum, character growth behaviors (The Stormlight Standard), 
encounter staging, and active narrative bets.
- [Session 1 Review](critic/s1-review.md) · [Session 2 Review](critic/s2-review.md) · [Session 3 Review](critic/s3-review.md) · [Session 4 Review](critic/s4-review.md) · [Session 5 Review](critic/s5-review.md) · [Session 6 Review](critic/s6-review.md) · [Session 7 Review](critic/s7-review.md)
"""
    with open(CODEX_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(index_md)


def main():
    print("Compiling Campaign Codex True Wiki (DEC-037, DEC-038 & DEC-039)...")
    manifests, configs, source_decisions, camp_cfg = load_all_data()
    recaps = get_session_recaps()

    generate_session_pages(manifests, configs, source_decisions, recaps)
    print("[OK] Generated Interactive Session Chronicles (s1.md - s7.md)")

    generate_sessions_hub()
    print("[OK] Generated Session Chronicles Hub (sessions/README.md)")

    generate_character_pages(manifests)
    print("[OK] Generated Substantive Character Dossiers")

    generate_characters_hub()
    print("[OK] Generated Dramatis Personae Hub (characters/README.md)")

    generate_faction_pages()
    print("[OK] Generated Faction Dossiers")

    generate_factions_hub()
    print("[OK] Generated Factions Hub (factions/README.md)")

    generate_threads_page()
    print("[OK] Generated Active Mysteries Board (threads/open-threads.md)")

    generate_critic_pages()
    print("[OK] Generated Critic Session Reviews (critic/s1-review.md - s7-review.md)")

    generate_critic_hub()
    print("[OK] Generated Critic Portal Hub (critic/README.md)")

    generate_master_index()
    print("[OK] Generated Master Wiki Portal README.md")

    print("\nTrue Wiki compilation complete! Output written to: campaign/codex/")


if __name__ == "__main__":
    main()
