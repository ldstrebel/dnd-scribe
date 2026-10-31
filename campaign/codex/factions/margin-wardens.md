# The Margin Wardens
**Codex Category:** Allied Sanctuary Faction
**Role:** Threshold Caretakers & Anomaly Navigators


# 📜 The Margin Wardens

<strong class="text-slate-100 font-semibold">Role:</strong> Threshold Caretakers & Anomaly Navigators

<strong class="text-slate-100 font-semibold">Base:</strong> The Margin Sanctuary (Appalachian Temporal Crease)

<hr class="my-4 border-slate-800/80">
## 🏛️ Directives & Sanctuary Keepers

The Margin Wardens are displaced survivors maintaining a peaceful settlement hidden within an Appalachian reality crease.

Because calendar time does not advance within the mist-shielded compound, residents are immune to aging and shielded from

upstream timeline redactions.

The Wardens maintain defensive perimeter watches, operate the dimensional gateway to the Lost Roads, and track continental

anomalies to retrieve loose historical Fragments before Redactor hit squads destroy them.

<hr class="my-4 border-slate-800/80">
## 👥 Key Personnel

- <strong class="text-slate-100 font-semibold">Teddy:</strong> Founding Caretaker and 1846 surveyor; calm mentor and compound patriarch.

- <strong class="text-slate-100 font-semibold">Naomi:</strong> Warden coordinator, anomaly board strategist, and combat drill instructor.

- <strong class="text-slate-100 font-semibold">Mike:</strong> Gatekeeper of the Lost Roads, truck mechanic, and legendary campfire cook.

- <strong class="text-slate-100 font-semibold">Rosa:</strong> Compound logistics coordinator, quilt weaver, and memory chronicler.

    <!-- Codex Entry Feedback & Lore Critique Card -->
    
        
            <!-- Header -->
            
                
                    ✍️
                    
                        ### Feedback &amp; Lore Refinement

                        Have a correction, missing canon detail, or suggestion for this entry?

                    
                
                
                    factions
                    The Margin Wardens
                
            

            <!-- Reviewer Handle Row -->
            
                <label class="text-xs text-slate-400 font-medium whitespace-nowrap">Your Scribe Handle:</label>
                
                    <input type="text" id="codexReviewerNameInput" placeholder="Your name or handle..." class="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 font-mono transition-colors">
                    <button type="button" onclick="rollCodexReviewerName()" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-amber-300 text-xs font-semibold whitespace-nowrap active:scale-95 transition-all flex items-center gap-1" title="Roll random D&D character pun name">
                        🎲 Roll Name
                    </button>
                
            

            <!-- Category Selector -->
            
                <label class="text-xs text-slate-400 font-medium block mb-1.5">Critique Category:</label>
                
                    <button type="button" class="codex-fb-cat-pill active px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/50 transition-all" data-cat="Continuity / Canon" onclick="selectCodexFeedbackCategory(this, 'Continuity / Canon')">⚖️ Continuity / Canon</button>
                    <button type="button" class="codex-fb-cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700 hover:text-slate-200 transition-all" data-cat="Lore Inaccuracy" onclick="selectCodexFeedbackCategory(this, 'Lore Inaccuracy')">⚠️ Lore Inaccuracy</button>
                    <button type="button" class="codex-fb-cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700 hover:text-slate-200 transition-all" data-cat="Missing Detail" onclick="selectCodexFeedbackCategory(this, 'Missing Detail')">🔍 Missing Detail</button>
                    <button type="button" class="codex-fb-cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700 hover:text-slate-200 transition-all" data-cat="Tone / Voice" onclick="selectCodexFeedbackCategory(this, 'Tone / Voice')">🎭 Tone / Voice</button>
                    <button type="button" class="codex-fb-cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700 hover:text-slate-200 transition-all" data-cat="General Suggestion" onclick="selectCodexFeedbackCategory(this, 'General Suggestion')">💡 Suggestion</button>
                
            

            <!-- Directive Textarea -->
            
                <label class="text-xs text-slate-400 font-medium block mb-1">Your Directive / Critique Note: *</label>
                <textarea id="codexFeedbackDirective" rows="3" placeholder="Identify an inconsistency, missing lore detail, character cadence nuance, or timeline error..." class="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-3 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 transition-colors leading-relaxed"></textarea>
            

            <!-- Optional Rewrite Textarea -->
            
                <label class="text-xs text-slate-400 font-medium block mb-1">Suggested Revision / Text (Optional):</label>
                <textarea id="codexFeedbackRewrite" rows="2" placeholder="Proposed replacement phrasing, corrected stat, or additional lore paragraph..." class="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-400 font-mono transition-colors leading-relaxed"></textarea>
            

            <!-- Status Message Banner -->
            

            <!-- Action Buttons -->
            
                <button type="button" onclick="copyCodexFeedbackToClipboard('margin-wardens', 'The Margin Wardens', 'factions')" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold active:scale-95 transition-all flex items-center gap-1.5" title="Copy formatted feedback note to clipboard">
                    📋 Copy Note
                </button>
                <button type="button" id="codexSubmitPrBtn" onclick="submitCodexFeedbackPr('margin-wardens', 'The Margin Wardens', 'factions')" class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 active:scale-95 transition-all flex items-center gap-1.5" title="Open Pull Request against ldstrebel/dnd-scribe">
                    🚀 Submit Codex Feedback
                </button>
