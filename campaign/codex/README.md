# Campaign Codex Overview
**Codex Category:** Overview

<!-- Clean Master Landing Hub -->
<div class="mb-6 space-y-4">
    <!-- Direct Search Input -->
    <div class="relative my-4">
        <div class="relative flex items-center">
            <span class="absolute left-3.5 text-slate-400 text-sm pointer-events-none">🔍</span>
            <input type="text" id="hubDirectSearchInput" placeholder="Search sessions, characters, lore, mysteries, or critic reviews..." class="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl pl-10 pr-10 py-2.5 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 transition-colors shadow-inner" oninput="hubPerformSearch(this.value)">
            <button type="button" id="hubSearchClearBtn" onclick="clearHubSearch()" class="absolute right-3 text-slate-500 hover:text-slate-300 hidden text-xs font-mono">✕</button>
        </div>
        <div id="hubSearchResults" class="hidden mt-2 p-3 rounded-xl bg-slate-900 border border-slate-700/80 space-y-2 shadow-2xl max-h-80 overflow-y-auto custom-scrollbar"></div>
    </div>

    <!-- Quick Navigation Bar -->
    <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
        <button type="button" onclick="filterCodexCategory('sessions')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-800 transition-colors">📜 9 Sessions</button>
        <button type="button" onclick="filterCodexCategory('characters')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-sky-300 border border-slate-800 transition-colors">👤 13 Dossiers</button>
        <button type="button" onclick="filterCodexCategory('locales')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-amber-400 border border-slate-800 transition-colors">📍 5 Locales</button>
        <button type="button" onclick="filterCodexCategory('factions')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-emerald-300 border border-slate-800 transition-colors">🏛️ 2 Factions</button>
        <button type="button" onclick="selectCodexArticle('open-threads')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-800 transition-colors">🔍 9 Active Mysteries</button>
        <button type="button" onclick="filterCodexCategory('critic')" class="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-rose-300 border border-slate-800 transition-colors">🎭 9 Critic Reviews</button>
    </div>
</div>

## 📜 Session Chronicles (9 Sessions)
Explore comprehensive in-world session debriefs, chapter-by-chapter breakdowns, character ensemble logs, and narrative cliffhangers across all session chronicles.


<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 9 the dc precinct heist & the flight 840 vision">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S9 (Latest)</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">8.8 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 9: The DC Precinct Heist & The Flight 840 Vision</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s9.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s9')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s9-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Operating under strict time and alarm pressure, the coterie executes a multi-vector heist against the Metropolitan Police Department Third Precinct in Washington, D.C. While a crashing gargoyle and Dravin's administrative double-talk draw frontline police away, Pierre scales the exterior fire escape and Alfie smuggles inside an evidence carton.</p>
        <p>When Eusacles batters the vault frame to stage a diversion, Dravin swipes Captain Brenda Bob's keycard and Alfie isolates pursuing officers with <em>Vicious Mockery</em>. Extracting the anomalous silver handcuffs from the Captain's office, Dravin experiences a psychic chronal flashback to 1974 Flight 840 over the Atlantic, witnessing an operative observing a ticking device as the transponder shears from DOA to DCA. The party exfiltrates through stormwater culverts into the boatman's punt, returning safely to The Margin.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 8 infiltration, the lost roads & the dc precinct vault">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S8</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">7.8 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 8: Infiltration, The Lost Roads & The DC Precinct Vault</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s8.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s8')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s8-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Advancing to 5th level at The Margin, the party receives critical birthrights—including Theodore's ancestral boon to Eusacles and Prof. Dravin's 3-seed pomegranate signet pin—before embarking toward Washington, D.C. Guided along Lost Creek's subterranean aqueducts by a reticent boatman, they repel swarming ink-blot stalkers as tracking clocks begin ticking toward Majora.</p>
        <p>Reaching a storm drain opposite the D.C. police precinct, Dravin analyzes downloaded blueprints, Sharpie-inscribes Alfie's foot with contact info, and hurls a brick through a patrol cruiser window before casting <em>Meld into Stone</em> to slip Alfie inside. With a living stone statue sent by Pierre's mother shattering the front portico to create mass panic, Dravin is swept into the processing room where Alfie rests inside a tagged evidence brick as the cliffhanger incursion begins.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 7 the interrogation, the redactor & the dream of thanatos">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S7</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">9.5 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 7: The Interrogation, The Redactor & The Dream of Thanatos</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s7.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s7')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s7-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Tucked away in an abandoned campus arcade at University University, the party interrogates their captive Redactor operative, discovering that the mysterious 'Master' is curating a utopian timeline and that the travelers have become living anomaly vessels targeted for elimination.</p>
        <p>When the captive mocks Alfie, the driftwood duelist executes her with a needle rapier, triggering a blinding violet signal flare that draws an ink-cloaked, six-fingered stalker. Fleeing into the misty Lost Roads behind Pierre's luminous rabbit patronus, the company rescues Susanna. At a secluded campfire, Thanatos visits Eusacles in a divine dream, granting an ancestral ward upon his watch and warning of Pierre's maternal heritage.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 6 the auditorium incursion & the memory seam">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S6</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">9.3 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 6: The Auditorium Incursion & The Memory Seam</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s6.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s6')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s6-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Violent planar combat erupts across the University University amphitheater as satyr strike teams and a tendril-grafted Gorgon operative assault the party amidst student protests.</p>
        <p>Dravin establishes a defensive sanctuary of moonlight while Eusacles smites intruders before suffering a cognitive memory siphon. Pierre manifests defensive stone barriers to hold the perimeter, allowing Alfie to sever the Gorgon's tendrils and capture an operative as the alarm klaxons blare.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 5 the forgotten trail & the mad doctor's lecture">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S5</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">9.0 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 5: The Forgotten Trail & The Mad Doctor's Lecture</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s5.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s5')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s5-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>A celestial dispatch delivered by Hermes bears a sealed winter warning from Persephone, alerting the Margin that planar veils are thinning across North America.</p>
        <p>Traveling across the Lost Roads to University University in Pennsylvania, the company infiltrates a chaotic lecture hall amidst student unrest surrounding medical historian Dr. Aris Thorne, uncovering encrypted notes regarding the 1948 Big Pox trials.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 4 the raleigh museum gorgon ambush & debrief">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S4</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">9.2 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 4: The Raleigh Museum Gorgon Ambush & Debrief</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s4.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s4')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s4-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Ambushed inside the Aegean antiquity wing of the North Carolina Museum of Natural History by serpent-crowned Gorgon Redactors, the company mounts a desperate defense utilizing improvised baguette explosives, a high-altitude clay urn drop, and salvaged ancient armor.</p>
        <p>Touching the fractured Gorgon stele, Alfie is overwhelmed by a traumatic vision of ancient oarsmen and a burning coastal port. Surviving the clash, the party secures the relic and flees through the emergency exits into the foggy outskirts of Raleigh.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 3 the museum heist in north carolina">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S3</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">8.7 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 3: The Museum Heist in North Carolina</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s3.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s3')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s3-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Threading through the dimensional mist of the Lost Roads, the company arrives in downtown Raleigh to infiltrate the North Carolina Museum of Natural History.</p>
        <p>Donning academic disguises, Pierre bluffs security as a visiting Sorbonne intern while Alfie deploys Wordcraft to trigger a spectral sheep distraction in the lobby, allowing Dravin to map security blind spots and locate the subterranean Aegean stele vault.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 2 the margin, the fragments & the lost roads">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S2</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">8.5 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 2: The Margin, The Fragments & The Lost Roads</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s2.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s2')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s2-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Within the timeless mountain refuge of The Margin, Teddy reveals the sanctuary's 1846 surveyor origins as a crease in reality where calendar decay cannot reach.</p>
        <p>While Naomi organizes defensive blackout drills and briefs the company on four scattered timeline Fragments, Pierre inadvertently triggers his ancient petrifying Gorgon gaze during an encounter at a rural station before boarding a vintage farm truck into the Lost Roads.</p>
    </div>
</div>

<div class="session-showcase-card rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 sm:p-5 my-3.5 shadow-md hover:border-amber-500/30 transition-all flex flex-col md:flex-row gap-4 items-stretch" data-title="session 1 the bus from vegas & the library of the fates">
    <div class="w-full md:w-5/12 flex-shrink-0 flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800/80 pb-3 md:pb-0 md:pr-4 space-y-3">
        <div>
            <div class="flex items-center gap-2 mb-1.5">
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold uppercase tracking-wider">S1</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">8.8 / 10</span>
            </div>
            <h3 class="text-sm sm:text-base font-bold font-serif text-slate-100 leading-snug">Session 1: The Bus from Vegas & The Library of the Fates</h3>
        </div>
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
            <a href="uneraseable-s1.html" class="px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold border border-amber-500/40 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📖</span> <span>Full Narrative</span>
            </a>
            <button type="button" onclick="selectCodexArticle('s1')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>📜</span> <span>Codex Entry</span>
            </button>
            <button type="button" onclick="selectCodexArticle('s1-review')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-rose-300 hover:text-rose-200 border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm">
                <span>🎭</span> <span>Critic Audit</span>
            </button>
        </div>
    </div>
    <div class="w-full md:w-7/12 flex-1 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed space-y-2">
        <span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 font-bold block">Quick Summary</span>
        <p>Displaced from a midnight Las Vegas Greyhound bus into dimensional freefall, four disparate strangers awaken inside the marble colonnades of the celestial Library of the Fates.</p>
        <p>As predatory ink-beasts tear through the stacks to consume severed timeline threads, the Three Fates rapidly weave Alfie from driftwood and sea-thread to bolster the frontline. Escaping through a cosmic tapestry rift, the survivors tumble into the Appalachian threshold of The Margin.</p>
    </div>
</div>

## 👥 Dramatis Personae (13 Dossiers)
Access deep dossiers covering character backstories, voice cadences, signature abilities, campaign trajectories, and interpersonal dynamics.

- **The Party:** <button type="button" onclick="selectCodexArticle('pierre')" class="text-amber-400 hover:text-amber-300 underline font-semibold">Pierre</button> · <button type="button" onclick="selectCodexArticle('alfie')" class="text-emerald-400 hover:text-emerald-300 underline font-semibold">Alfie</button> · <button type="button" onclick="selectCodexArticle('dravin')" class="text-indigo-400 hover:text-indigo-300 underline font-semibold">Prof. Edward Dravin</button> · <button type="button" onclick="selectCodexArticle('eusacles')" class="text-sky-400 hover:text-sky-300 underline font-semibold">Eusacles</button>
- **Margin Wardens:** <button type="button" onclick="selectCodexArticle('teddy')" class="text-orange-400 hover:text-orange-300 underline font-semibold">Theodore (Teddy)</button> · <button type="button" onclick="selectCodexArticle('naomi')" class="text-rose-400 hover:text-rose-300 underline font-semibold">Naomi</button> · <button type="button" onclick="selectCodexArticle('mike')" class="text-slate-300 hover:text-white underline font-semibold">Mike</button> · <button type="button" onclick="selectCodexArticle('rosa')" class="text-pink-400 hover:text-pink-300 underline font-semibold">Rosa</button>
- **Allies & Rescued Souls:** <button type="button" onclick="selectCodexArticle('susanna')" class="text-teal-400 hover:text-teal-300 underline font-semibold">Susanna</button> · <button type="button" onclick="selectCodexArticle('thorne')" class="text-yellow-400 hover:text-yellow-300 underline font-semibold">Dr. Aris Thorne</button>
- **Celestial Powers:** <button type="button" onclick="selectCodexArticle('thanatos')" class="text-purple-400 hover:text-purple-300 underline font-semibold">Thanatos</button> · <button type="button" onclick="selectCodexArticle('hermes')" class="text-amber-300 hover:text-amber-200 underline font-semibold">Hermes</button> · <button type="button" onclick="selectCodexArticle('fates')" class="text-violet-400 hover:text-violet-300 underline font-semibold">The Three Fates</button>

## 📍 Key Locales & Havens (5 Locales)
In-depth canonical records of the havens, transit corridors, and historical investigation sites.

- **Sanctuary & Transit:** <button type="button" onclick="selectCodexArticle('the-margin')" class="text-teal-300 hover:text-teal-200 underline font-semibold">The Margin Sanctuary</button> · <button type="button" onclick="selectCodexArticle('lost-roads')" class="text-cyan-300 hover:text-cyan-200 underline font-semibold">The Lost Roads</button>
- **Expedition Targets:** <button type="button" onclick="selectCodexArticle('raleigh')" class="text-amber-300 hover:text-amber-200 underline font-semibold">Raleigh Museum</button> · <button type="button" onclick="selectCodexArticle('university-university')" class="text-sky-300 hover:text-sky-200 underline font-semibold">University University</button> · <button type="button" onclick="selectCodexArticle('dc-precinct')" class="text-slate-200 hover:text-white underline font-semibold">MPD Third Precinct (D.C.)</button>

## 🏛️ Factions & Orders
Briefings on the allied sanctuary keepers and hostile timeline enforcers shaping the planar conflict.

- **<button type="button" onclick="selectCodexArticle('margin-wardens')" class="text-emerald-400 hover:text-emerald-300 underline font-semibold">The Margin Wardens</button>:** Appalachian sanctuary guardians maintaining the Lost Roads and reality creases.
- **<button type="button" onclick="selectCodexArticle('redactors')" class="text-red-400 hover:text-red-300 underline font-semibold">The Redactors</button>:** Hostile timeline enforcers seeking to erase historical anomalies and forge a synthetic calendar.

## 🔍 Investigation Quest Board
A living tracking board monitoring active campaign mysteries, origin secrets, and impending expedition hooks.

- **Active Threads:** <button type="button" onclick="selectCodexArticle('open-threads')" class="text-cyan-400 hover:text-cyan-300 underline font-semibold">TH-01 to TH-09 Mysteries Board</button>
- **Dedicated Mystery Pages:** <button type="button" onclick="selectCodexArticle('th-01')" class="text-emerald-400 hover:text-emerald-300 underline">TH-01 (Alfie)</button> · <button type="button" onclick="selectCodexArticle('th-02')" class="text-cyan-400 hover:text-cyan-300 underline">TH-02 (Stele)</button> · <button type="button" onclick="selectCodexArticle('th-03')" class="text-yellow-400 hover:text-yellow-300 underline">TH-03 (Thorne)</button> · <button type="button" onclick="selectCodexArticle('th-04')" class="text-orange-400 hover:text-orange-300 underline">TH-04 (Teddy)</button> · <button type="button" onclick="selectCodexArticle('th-05')" class="text-red-400 hover:text-red-300 underline">TH-05 (Six-Fingered Man)</button> · <button type="button" onclick="selectCodexArticle('th-06')" class="text-cyan-400 hover:text-cyan-300 underline">TH-06 (DC Precinct)</button> · <button type="button" onclick="selectCodexArticle('th-07')" class="text-teal-400 hover:text-teal-300 underline">TH-07 (Anchors)</button> · <button type="button" onclick="selectCodexArticle('th-08')" class="text-purple-400 hover:text-purple-300 underline">TH-08 (Thanatos)</button> · <button type="button" onclick="selectCodexArticle('th-09')" class="text-red-400 hover:text-red-300 underline">TH-09 (Majora)</button>

## 🎭 The Critic & Editorial Reviews
Independent session reviews evaluating narrative momentum, character growth behaviors (The Stormlight Standard), emotional stakes, and world coherence.

- Access full editorial audits from the sidebar directory under **Critic Editorial Reviews** for all 9 sessions.
