# Agentic Immersive Experience System — Plan

## Vision

An agent-orchestrated system that creates deeply personalized immersive experiences running inside a participant's actual daily life — using existing real-world channels, systems, and infrastructure as narrative nodes. The participant's ordinary world becomes the stage without requiring custom physical build-out.

Inspired by: The Game (1997), Odyssey Works, Sleep No More, Steve Boyle's Immersive World Adventures (Tulum), the ARG tradition. Economically distinct from all of these.

---

## Core Insight

> The participant's agency is the content, not a delivery mechanism for content.

Most immersive theater is bottlenecked on human execution capacity — the creative vision always exceeds what can be coordinated. Agents invert this. Execution becomes cheap; the constraint becomes the quality of design.

The world already has infrastructure for communication, authority, and attention. The trick is repurposing existing systems as narrative nodes — not building new ones.

---

## What We're Not Building Yet

- The orchestrator / state machine
- The delivery pipeline
- The UI / operator dashboard

**Current focus: build a library of atomic plays — clever, tested, composable beats that can be lego-bricked into an experience.**

---

## System Architecture (conceptual hold)

### Oversight Model: Waymo Remote Operations

The agent runs experiences autonomously with tiered human escalation based on confidence thresholds:

| Level | Agent action | When |
|-------|-------------|------|
| Autonomous | Act and log | Confidence high, routine beat, nominal participant state |
| Flag | Notify operator, proceed unless overridden | Notable but non-alarming signal |
| Request decision | Present options, hold for approval | Threshold moments, real-world elements, ambiguous response |
| Safe-hold | Stop all beats, notify operator | Safety word, distress signal, parameters exceeded |
| Full handoff | Operator takes direct control | Operator judgment |

One operator oversees a fleet of concurrent experiences (target ratio: 40-80) because most experiences are in quiet phases at any given time. Fleet ratio degrades for high-intensity arcs; these are priced accordingly.

**Experience autonomy tiers (set at intake):**
- L1 — routine arc, fully autonomous with exception monitoring
- L2 — standard arc, human approval at threshold moments
- L3 — complex arc or vulnerable participant, human reviews every significant beat
- L4 — human-driven, agent handles logistics only

### Intake Model

Three-pass process producing a structured participant object:

**Pass 1 — Sponsor intake** (before participant knows)
- Guided interview, 30-45 min
- Extracts: profile, current life context, transformation goal, relationships, hard constraints, confederate candidates
- Agent infers drivermap dimensional profile from qualitative responses

**Pass 2 — Participant calibration** (diegetically framed as "orientation")
- Questions designed to elicit dimensional data without being clinical
- Captures current state (person_state_dimensions)
- Captures **genre fluency** — which experience communities the participant has vocabulary for (see below)
- Sets safety words: pause / slow / real-life (participant-chosen)
- Explicit consent layer embedded in the experience artifact itself

**Pass 3 — Agent inference**
- Maps sponsor + participant responses to drivermap dimensions
- Queries drivermap for mechanism profile (which mechanisms activate for this person in this situation)
- Selects arc type, flags contraindications
- Generates structured participant object

**Participant object:**
```json
{
  "profile": { "channels", "daily_patterns", "relationships", "vocabulary_samples" },
  "dimensional_profile": { "big_five_N", "need_for_cognition", "attachment_anxious", ... },
  "mechanism_profile": [{"mechanism": "curiosity_exploration", "score": 0.91}, ...],
  "genre_fluency": {
    "arg": "none|light|heavy",
    "escape_room": "none|light|heavy",
    "immersive_theater": "none|light|heavy",
    "mentalism": "none|light|heavy",
    "spy_fiction": "none|light|heavy",
    "cult_recovery_awareness": "none|light|heavy"
  },
  "arc_recommendation": { "primary", "secondary", "contraindicated" },
  "constraints": { "lines", "veils", "amplifiers", "timing_blocks" },
  "safety": { "pause_word", "slow_word", "real_life_word" },
  "transformation_goal": "..."
}
```

**Genre fluency elicitation (Pass 2):**

These questions must feel natural inside the diegetic frame of "orientation" — never clinical. The framing is curiosity about the participant's tastes, not an assessment. Suggested approaches:

- *Escape room / puzzle:* "Have you done escape rooms or puzzle hunts? If so, what's the most memorable thing that happened in one?" — depth of answer signals fluency level.
- *ARG / mystery:* "Have you ever followed a mystery online — something that felt like it had more going on than was obvious?" — distinguishes passive awareness from active participation.
- *Immersive theater:* "Have you been to an immersive show or experience where you weren't quite sure what role you were supposed to play?" — experience with the social awkwardness of immersive frames is the signal.
- *Mentalism / mentalism-adjacent:* "Do you have any experience with cold reading, personality type frameworks, or performances where someone seems to know things they shouldn't?" — covers both Barnum-aware and mentalism-curious participants.
- *Spy fiction depth:* Sponsor intake usually surfaces this — look for spy fiction mentions in vocabulary samples, not a direct question.
- *Cult recovery awareness:* Never ask directly. Infer from: references to high-control groups, mentions of loaded language or BITE model concepts, explicit past group membership. Flag heavy fluency as a contraindication for cult-induction plays entirely.

**Fluency levels:**
- `none` — no vocabulary for the genre; mechanic lands as real
- `light` — general awareness; may recognize pattern mid-arc but not immediately
- `heavy` — fluent; will name the mechanic on contact, breaking diegetic processing

**Fluency → play selection rule:** When `TROPE_RISK[source] = high` and `genre_fluency[source] = heavy`, exclude or strongly downrank the play. When `medium` and `heavy`, deprioritize. When `high` and `light`, flag for channel-novelty mitigation (see below).

**Cross-domain mitigation:** A play with `TROPE_RISK: arg:high` delivered through a channel the participant has no ARG context for (physical mail, financial document, phone call) can reduce effective recognition risk by one level. The mechanic is the same; the context resets the reflex. Document the mitigation as `trope_mitigated_by_channel: true` on the play instance in the arc plan.

**drivermap** (`~/Documents/drivermap`) — 108 behavioral mechanisms indexed against person dimensions and situational features. Used to predict which mechanisms activate for a given participant profile + situation. The intake's analytical backbone.

### Drivermap Integration

**Query interface** (`python query.py`):
- `--dim BIG_FIVE_N:+` — mechanisms that activate for high neuroticism
- `--dim big_five_N:+ --dim attachment_anxious:+` — compound profile query
- `--feature FEATURE` — mechanisms active in a given situational feature
- `--scenario TEXT` — free-text situation description → ranked mechanisms
- `--verbalize MECHANISM_ID --action TEXT` — how participant rationalizes a specific play
- `--compare A B` — mechanism comparison
- `--export json/csv` — structured output for downstream processing

**Play-matching pipeline (near-term build target: `play_selector.py`):**

```
participant intake → dimensional_profile dict + genre_fluency dict
  → python query.py --dim [all dims] --export json
  → ranked mechanism activation scores (mechanism_profile)
  → filter plays.md where MECHANISMS ∩ top-N mechanisms ≠ ∅
  → exclude plays where TROPE_RISK[source]:high and genre_fluency[source]:heavy
  → downrank plays where TROPE_RISK[source]:medium and genre_fluency[source]:heavy
  → flag plays where TROPE_RISK[source]:high and genre_fluency[source]:light → propose channel-novelty mitigation
  → sort by: arc_fit match + intensity fit + channel variety + somatic compatibility
  → ranked play candidates for current arc position
```

This is the core of what an orchestrator eventually does: at each arc position, given current participant state, ask drivermap what's active, then surface plays that leverage those mechanisms.

**Schema alignment:** The `MECHANISMS` field in plays.md should use exact drivermap mechanism IDs (e.g., `curiosity_exploration`, `loss_aversion`, `reciprocity_norm`). This is not yet enforced — plays currently use approximate labels. When building play_selector.py, normalize the MECHANISMS values to exact IDs as a pre-processing step.

**Verbalize as play design tool:** `--verbalize MECHANISM_ID --action "participant receives an anonymous package"` returns a model of how a participant with a given profile will rationalize the experience at a psychological level. Useful when designing plays to check whether the intended mechanism will actually land for a given profile, and what narrative the participant constructs around it.

**Scenario queries for arc design:** `--scenario "participant just had a high-intensity revelation, now in cool-down"` returns which mechanisms are active in that arc position — useful for selecting post-threshold plays that match the participant's current state, not just their profile.

**Contraindication checking:** The dimensional_profile also indexes which mechanism activations become harmful at extreme values (e.g., `loss_aversion` + high neuroticism + high attachment_anxious without prior trust scaffolding). The play selector should surface contraindicated MECHANISMS as exclusion filters, not just ranking signals.

### Narrative Structures

**Arc types:**
- **Investigation** — fragment → discovery → revelation. Self-sustaining via curiosity. Contraindicated: low need_for_cognition.
- **Initiation** — separation → liminality → incorporation. Natural social payoff. Requires compelling "thing" to be initiated into.
- **Persecution / paranoia** — forces closing in. Highest engagement. Contraindicated: high big_five_N + high attachment_anxious without careful scaffolding. Always requires explicit consent for this arc type.
- **Reckoning** — past surfaced → confrontation → resolution. Deepest impact. Requires deepest profile. L3-L4 only.
- **Conspiracy** — events connected, participant is the link. Pattern convergence as payoff.
- **The Test** — being evaluated. Works as layer within another arc.

**Pacing rhythm:**
- Daily pulse (low-intensity, maintains presence)
- Weekly event (requires response/action)
- 2-3 threshold moments across full arc
- Climax (participant does something in the real world)
- Denouement (exists outside the fiction — a real conversation, real gift, real meal)

**Key structural principles:**
- Design situations, not scenes — authentic response is easy, performance is hard
- Value clarity at beat level, value complexity at arc level (Nguyen)
- Bleed into real life is the product, not a risk
- The "you've been found" inversion — let them hunt first, then flip it
- Retroactive meaning — plant details early that gain significance later
- Parallel threads that the participant connects before being told
- Somatic sequencing before narrative logic — what state is the participant in, what state does this beat require
- Identity arc coherence — know what self you're inviting them into at each beat; the experience is identity-editing, not just storytelling
- Detection window management — know when each play collapses the deniability frame; sequence accordingly
- Reinforcement phase is designed, not assumed — Revelation → Reinforcement → Replication

**Debrief is structural:** every experience requires a landing. Cross the threshold clearly. The worst ending is an experience that simply stops. The debrief opens the reinforcement phase — day 1/7/30 follow-ups are part of the arc, not epilogue.

### Safety & Consent Layer

- Consent to "a journey" — not to specific contents — is the right model
- Diegetic consent checkpoints at threshold moments ("what you're about to learn cannot be unlearned")
- Three safety words: pause / slow / real-life (not just exit)
- Active de-stigmatization of safety word use
- The real-life card goes experience-dormant, no pressure, no narrative silence that reads as abandonment
- Third-party human available for L3-L4 experiences
- Post-experience debrief is mandatory, not optional
- Nordic LARP safety apparatus (X-card equivalent, pre-brief, post-debrief) as tested reference model

---

## The Plays Library — Current Focus

The orchestrator is useless without a rich library of atomic, composable beats. The plays library is what we're building now. See `plays.md` for the full library.

**A play is:** a specific, concrete technique using an existing real-world system or channel. Atomic. Composable. Executable by an agent with defined autonomy level.

**Current state:** ~200+ plays across 10+ sections. Target: 300+, at which point a Lamina-style schema-discovery pass becomes worth running to surface latent dimensions the current tags don't capture.

### Play Schema

Every play carries 10 structured fields enabling filtering and sequencing:

| Field | Purpose |
|---|---|
| `COST` | Financial cost tier: free / low / mid / high / ongoing |
| `AUTONOMY` | Agent-executable → confederate-required |
| `LEAD_TIME` | Prep time before deployment |
| `INTENSITY` | Arousal level: low → extreme |
| `MECHANISMS` | drivermap behavioral mechanisms activated |
| `ARC_FIT` | Arc position: pre / open / build / escalate / threshold / climax / denouement |
| `BEAT_FUNCTION` | Narrative rhythm role: spike / ramp / hold / rest / transition (from Imagineering contrast principle) |
| `SOMATIC` | Physiological state induced · state required for play to land |
| `IDENTITY_INVITE` | The self the participant gets to try on |
| `REINFORCE` | Post-play touchpoints that extend effect into daily life (3R model) |
| `PERMISSION` | Grants or requires permission · standalone or sequenced |
| `EMOTIONAL_REGISTER` | Qualitative affect: wonder / dread / grief / urgency / warmth / awe / shame / disorientation / triumph / longing / paranoia / tenderness |
| `AGENCY_DEMAND` | Participant effort required: passive → high |
| `FEEDBACK_TYPE` | What participant receives for their actions: none / ambient / diegetic / responsive |
| `AGENCY_TYPE` | Agency sculpted by play: constrained / constructed / revealed / suspended / mirrored / borrowed (Nguyen) |
| `FRAME_REQUIREMENT` | Epistemic state required: naive / primed / meta / any |
| `TROPE_RISK` | Genre-community recognition risk: source:level pairs (arg, escape_room, immersive_theater, mentalism, spy_fiction, cult_recovery) |
| `DETECTION_WINDOW` | How long before a reasonably attentive participant recognizes the beat as constructed |
| `REVERSIBILITY` | Exit cost if experience ends: trivial → irreversible |
| `CHANNEL` | Delivery medium: physical_mail / phone / email / in_person / digital_ambient / physical_world / multi |
| `DWELL_TIME` | How long play occupies participant attention post-deployment: instant / brief / session / multi-day / sustained / permanent |
| `REQUIRES` | Operator resource type: cash_only / social_capital / institutional_access / technical_skill / local_presence / ongoing_maintenance |
| `SYNERGIZES_WITH` | Play IDs that compound well in sequence (informal; seeds the arc planner) |
| `CONTRAINDICATED_AFTER` | Play IDs that should not immediately precede this play |
| `WITNESS_STRUCTURE` | Who witnesses the participant's transformation or action: none / self / character / outsider / document |
| `LANDSCAPE` | Which landscape the play primarily operates on: action / identity / both |
| `LEGACY_SCOPE` | Persistence and reach of effect after the arc: ephemeral / personal / social / world_mark (multi-value: ` · ` separated) |

### Design Principles (from synthesis)

**Somatic sequencing is a constraint, not an afterthought.** Every play has a physiological state it requires and a state it induces. `simulated_loss` deployed cold is destabilizing; after sustained trust-building it is cathartic. Sequence for somatic coherence, not just narrative logic.

**Experiences are identity-editing tools.** Each play extends an implicit invitation to try on a self not available in ordinary life — the investigator, the chosen, the observed. Know what identity invitation you're making at each beat, and sequence toward a coherent identity arc across the full experience. (Raj Samuel, WXO LXW26.)

**The denouement is not the end of operator responsibility.** It is the start of the reinforcement phase. Revelation → Reinforcement → Replication: the perceptual shift that arrives days or weeks later, evidence of the effect persisting, behavior changes the participant didn't predict in themselves. Design for the 30-day arc, not just the climax. (Richard Maddock, WXO LXW26.)

**Permission architecture determines what lands.** Plays that arrive before permission is granted are dismissed or misread. Plays that grant permission make subsequent plays land. Know whether each play is a standalone opener, a permission-granter, or a play that requires prior permission to function. (Terence Leclere, WXO LXW26.)

**Emotional register and intensity are different axes.** Two plays can both be high-intensity but produce opposite registers — wonder vs. dread, triumph vs. shame. Arc design requires balancing registers across beats; identical registers in sequence flatten regardless of intensity variation.

**Detection window is an arc design variable.** Some plays collapse the deniability frame immediately (a character interface is obviously a character within hours); others sustain it for weeks. Know your plays' detection windows and sequence accordingly — a window-collapsing play deployed too early loses the implicit frame for everything that follows.

**Plan your commitment surface.** Every play has a reversibility cost. Know your exit options before deploying plays with difficult or irreversible reversibility ratings. Safety apparatus requires this.

**Channel saturation degrades immersion.** Three plays in the same channel in one week makes the system feel one-dimensional. Use the CHANNEL field to balance delivery media across the arc.

**Operator resource is a real constraint.** Cost is not the only resource dimension. Social capital (confederates, favors), institutional access (business accounts, credentials), technical skill (voice cloning, deepfake), local presence, and ongoing maintenance load are separate axes. A free play requiring institutional_access may be harder to deploy than a mid-cost play requiring cash_only.

**Beat function alternation is structure.** Adjacent spikes flatten; rest without a preceding ramp is aimless. Every arc needs spike/ramp/hold/rest/transition plays in deliberate sequence. From Imagineering contrast principle (Joe Rohde): every element has meaning only in relation to the element before it. The BEAT_FUNCTION field encodes this.

**Alibi for interaction is a design problem, not an assumption.** Every play requires that the participant have a diegetically plausible reason to do what you need them to do. The alibi is not decoration — it is the bridge between their real-world self and the participant role. Plays that lack a clear alibi create discomfort and break immersion even when all other design is correct. FRAME_REQUIREMENT captures the epistemic precondition; alibi quality is about narrative coherence of the "why." (Kathryn Yu, No Proscenium; extensively confirmed in practice reviews.)

**Feedback type determines what the system appears to be.** A play with FEEDBACK_TYPE: none that accidentally appears responsive creates a "ghost in the machine" sensation that may be productive or destabilizing depending on arc position. A play with FEEDBACK_TYPE: responsive that fails to respond feels broken. Match feedback type to operational capacity and to participant expectations set by prior plays.

**Transformation requires consent architecture, not just safety words.** Plays designed to produce meaningful personal transformation are not categorically different from medical interventions — they require informed consent to the *kind* of change being invited, not just consent to "a journey." Negative transformation is trauma. When deploying high-INTENSITY plays with permanent DWELL_TIME and difficult REVERSIBILITY, verify that the transformation goal (from intake) aligns with the play's direction of change. (Noah Nelson, No Proscenium; Ida Benedetto, *Patterns of Transformation*.)

**Participant engagement depth is a routing variable.** Following Gensler's themed-entertainment taxonomy: *waders* — participate peripherally, prefer observation over involvement; *swimmers* — engage willingly when scaffolded; *divers* — seek maximum depth, push experience edges, actively investigate. The same play sequence lands differently across these types. A play designed for divers will confuse or bore waders; a play designed for waders will under-engage divers. Identify participant depth tier in intake and route accordingly. (Gensler 2025 Immersive Industry Report.)

**Iceberg architecture: design for depth, not just surface.** The surface of a play should be coherent and non-alarming to a casual participant; the depth rewards the participant who elects to investigate further. Divers should receive a fundamentally different experience than waders — not because different content is served to them, but because the same artifact contains layers that only patient attention reveals. Hidden content (audio spectrograms, HTML source, mirrored text, backward speech, embedded URLs) serves this layering. The design discipline is building a complete, satisfying surface first, then encoding depth that doesn't read as forced or decorative. From analog horror (Local 58, Mandela Catalogue) and "found game" traditions (Petscop, Home Safety Hotline): the most durable examples use a mundane/safe container whose surface is entirely credible on first pass, hiding revelatory or disturbing content that only manifests when the participant goes looking. (Alex Orona, "Analog Horror and the Rise of the Found Game," Culture Combine 2024.)

**Retro/degraded medium as a trust mechanism distinct from content aging.** Analog-era formatting (VHS aesthetics, CRT scan lines, early-web HTML, cassette hiss, 8-bit graphics) signals that content predates the participant's awareness of it — the opposite of advertising. This lowers the guard before content does anything. It is distinct from document aging (worn paper, faded ink) and social media aging (historical post dates): it ages the *medium itself*, with the implicit claim that the content was made before the participant existed as a target. Deploy when the participant's cultural memory includes the referenced medium era.

**Arc design is peak-end optimization.** Retrospective evaluation is determined almost entirely by the peak intensity and the ending — not by average quality or duration (Kahneman et al. peak-end rule, 1993; 2022 meta-analysis r=0.581). Duration neglect is real: a 3-week arc with a brilliant peak and a graceful close outperforms a 6-week arc with mediocre beats. Optimize the peak and the close above all else. The colonoscopy extension result is operationally applicable: an ending that is slightly gentler than the experience's intensity peak will improve the overall retrospective evaluation even if it sacrifices edge.

**Voluntary dwell beats coerced dwell.** Playground doctrine (Roger Thomas, Wynn/Encore): design rest beats and hold beats for comfort and orientation, and participants will stay longer and engage more deeply than if kept disoriented. The maze doctrine (Bill Friedman) is wrong for immersive: disorientation creates anxiety that terminates engagement; comfort creates safety that sustains it. "Rest" plays should feel like arriving, not like being lost.

**Participant-assembled meaning has more weight than delivered meaning.** IKEA effect (Norton, Mochon & Ariely 2012): participants value conclusions they partially assembled more than identical conclusions delivered complete. Design for discovery moments where the participant connects the dots before being told. The revelation should feel like their conclusion, not your answer. Variable-schedule distribution of clues — where not every fragment is significant — sustains the search behavior that makes this possible.

**Ethical dark pattern test.** A mechanic that activates a psychological bias is ethical when the participant's reflective evaluation — looking back with full knowledge — endorses the effect it had. It is a dark pattern when that evaluation would judge themselves as having been manipulated against their own interests (Zagal dark patterns taxonomy, 2013). Apply this test to plays using variable ratio schedules, near-miss framing, sunk cost exploitation, or urgency construction. The constraint is not "does it work" but "would the participant, with full information, be glad it worked."

**Self-generated reasons are more durable than delivered ones.** Motivational interviewing principle (Miller & Rollnick): when the participant articulates the significance themselves, rather than being told, the change persists longer and is harder to contradict. The righting reflex — the character's urge to explain what the participant should feel — generates resistance. The character who asks questions until the participant explains it themselves generates commitment. OARS technique: Open questions, Affirm, Reflect, Summarize. Characters should ask more than they tell.

**Attend to both landscapes.** Every beat operates on two planes simultaneously: the action landscape (what happened, what was done) and the identity landscape (what this means about who the participant is). Attending only to events without attending to their identity implications misses the deeper transformation vector. The participant who solves a puzzle feels clever; the participant invited to see themselves as an investigator whose expertise was real has been changed. Identity-plane work is the product; action-plane work is the delivery mechanism.

**Outsider witness makes transformation durable.** Narrative therapy's definitional ceremony (White & Epston): a change is most thoroughly integrated when someone else witnesses it and names it back specifically. The participant telling a friend is an outsider witness event — design for it. A character who acknowledges the specific change ("you were afraid and you did it anyway — I need you to know I saw that") is providing outsider witness. This is categorically more powerful than internal recognition. The witness nomination ("I'm going to tell someone what you just did") is more potent than validation ("you should be proud of yourself").

**Integration requires explicit design.** Wilderness therapy research on the transfer problem: powerful bounded experiences rarely transfer to ordinary life without an explicit bridge. Front-loading (naming the transferable insight before the experience), isomorphic framing (identifying the structural parallel between experience and participant's real challenges), generalization contract (explicit agreement about what will be applied), and timed follow-up (30/90 days) are the transfer mechanisms. If these are not designed, the "it changed everything" feeling fades within two weeks. The 3R model is not automatic — it requires these structural elements.

**Affective contract must persist through close.** Parasocial relationship research (Horton & Wohl 1956): when a participant has formed attachment to a character, that character must remain consistent with that attachment at arc close. A warm character who goes cold at the climax breaks the affective contract and damages transformation value — participants experience it as rejection, not denouement. Participant-initiated closure produces substantially better outcomes than character-initiated. Ambiguous endings — character simply disappears — are design failures producing grief responses with no resolution path.

**All three phases are required.** Van Gennep's rites of passage: separation (taken out of ordinary life), liminality (threshold state where identity is suspended and available), reincorporation (returned to ordinary life as a changed person). Most immersive executes separation and liminality competently; almost none design for reincorporation. An experience that ends without marking the participant's return as a changed person is not a transformation — it is a liminal state left open, which is psychologically unstable. Reincorporation requires: (1) a clear signal the liminal phase has ended, (2) naming of who the participant now is, (3) return of their ordinary-world identity recontextualized by the experience.

**Kinesthetic encoding is categorically different from perceptual.** Physical acts — writing, walking, folding, washing, placing — produce memories with different durability and somatic integration than what is seen or heard. If the transformation needs to be remembered in the body, include at least one kinesthetic beat. The act of physically sealing an envelope, placing an object, or writing a letter is not ceremony for its own sake — it is encoding.

**Commission, don't conclude.** Two closing modes: *concluding* ("the story is over, you may leave") versus *commissioning* ("you have been changed — here is what you are now equipped to do, go do it"). Concluding denouements terminate the arc. Commissioning denouements project the participant forward into ordinary life carrying something new. Commissioning requires naming a specific thing the participant is now equipped to do — not a vague "you're different" but a directed "you now know how to X."

**Persona capture is structural, not psychological.** A participant who has built reputation, relationships, and history as a persona has created real infrastructure that depends on the persona continuing. Exit cost is not "stopping pretending" — it is destroying something genuinely theirs. This is distinct from bleed (persona emotions affecting the person's real emotions). Persona capture is material investment in a constructed identity. Arcs that create persona capture give the participant something real to protect, which dramatically increases engagement and stakes.

**Operator neutrality is a legitimacy condition.** The T20 principle (EVE Online, 2006): when a developer used game-master access to give personal advantage to a preferred alliance, the perceived fairness of the entire game collapsed for many players. Applied to immersive: the moment an operator uses privileged access to the participant's real data — calendar, location, contacts — to manufacture narrative moments the participant experiences as meaningful coincidence, the experience crosses a legitimacy threshold. Use real-world data to understand the participant's world; never use it to create events the participant cannot distinguish from real life without your knowledge.

**Structure precedes behavior.** EVE Online design observation (Alex Gianturco "The Mittani," GDC 2010): EVE didn't teach players to be paranoid or deceptive — it created structural conditions (low visibility, high stakes, permissive rules) where those behaviors were adaptive. Applied to immersive: you cannot script a participant to be suspicious, curious, or loyal. You can design conditions where those responses emerge naturally. Information asymmetry generates curiosity and paranoia. Shared perceived enemies generate loyalty. Incomplete information about a credible threat generates urgency. Design the conditions; the behaviors follow.

**Failure cascades require narrative intervention, not event escalation.** The failure cascade (Mittani, 2009): when collective identity collapses, adding more challenges accelerates dissolution. The fix is narrative — offer a new identity frame, restore agency, show a path forward. Applied to arc management: when a participant disengages or tests the fiction's seams, deploying more plays is the wrong response. Disengagement is a narrative crisis — the participant no longer believes in the identity the arc is inviting them to occupy. Correct response: acknowledge the doubt, offer a new foothold, restore their sense of authorship.

**The metagame is the actual game.** What matters most in EVE is not what happens in the game client but what is believed, discussed, and theorized outside it (Mittani/GIA doctrine). Applied to immersive: the participant's telling their friends, the theories they develop, the interpretations they propagate between beats — this is the experience. The designed content is the input; the metagame narrative the participant constructs is the output. Design for the metagame: build gaps that reward theorizing, artifacts that reward sharing, moments that compel retelling.

**Each revelation should open more questions than it closes.** Deus Ex fractal conspiracy model: the player's confidence in understanding the situation decreases with each layer of truth revealed, not increases. What was "the answer" becomes a pawn-layer in a larger game. UNATCO is the enemy → MJ12 controls UNATCO → Illuminati created MJ12 → AIs operate above human institutions. Design the revelation arc so each layer is conclusive in the moment and is rendered incomplete by the next. The participant who thinks they finally understand should be the participant who's most exposed.

**Design for retroactive complicity.** Deus Ex's deepest structural mechanic: make the participant efficient and effective within a role whose real purpose they don't yet know. Give the handler institutional authority, information advantage, and selective generosity. Make following orders feel like good decision-making. The psychological hit comes not from discovering the deception but from recognizing they were the mechanism — that their competence served the wrong agenda. The guilt is specific: "I did this well."

**Strategic silence is more credible than false assertion.** The JC/Manderley moment: JC can truthfully say "Lebedev. A surprise attack" — technically accurate, actively misleading — and permit the handler's false conclusion to stand without correcting it. Lies by omission are more credible than false statements because they leave the participant's reasoning intact. Design beats where characters give technically-accurate partial truths and let the participant complete the interpretation. The participant's own reasoning becomes the mechanism of misdirection.

**Verifiability distinguishes justified suspicion from paranoia.** Deus Ex's answer to its own conspiracy premise: accusations gain credibility through evidence → corroboration → pattern recognition, not through assertion. The NSF's claims against UNATCO sound paranoid until: physical evidence appears, Paul's testimony corroborates it, the false flag operation is reconstructed from fragments. Make the truth discoverable — embedded in the antagonist's own infrastructure, requiring cross-referencing of multiple independent sources. The participant who finds the proof in the enemy's files is a different psychological state from one who is told.

**The contract structure creates deniability and complicity simultaneously.** The "you accepted the job, we didn't explain why" frame (Uplink / Deus Ex): the participant operates on instructions from an authority they trust without full knowledge of the mission's purpose. They cannot be fully blamed for outcomes they didn't know were coming; they cannot be fully absolved from outcomes they enabled. The contract structure is how you build ethical weight into participant action without requiring them to consciously choose wrongdoing.

### Library Expansion — Source Domains

Target: 300+ plays. Mining in waves:

**Wave 1 (complete):**
- Confidence / con artistry — Maurer (*The Big Con*), Goffman (*On Cooling the Mark Out*), the short con and long con structural library
- Mentalism / street magic — Rowland, Derren Brown, psychological forcing, cold reading, dual reality, coincidence engineering
- Intelligence tradecraft — MICE appeals, legend building, walk-in protocol, cut-out, compartmentalization, mole hunt
- Cult induction mechanics — love bombing, incremental commitment, floating experience, lexical world-building (BITE model, Lifton, Cialdini)
- Escape room / ARG design — SCRAP philosophy, TINAG doctrine, rabbit holes, multi-key locks, fragmented evidence (Her Story / Obra Dinn)
- Structural gaps — post-climax / denouement plays, resistance handling, failure recovery, multi-participant arc plays, long-arc infrastructure
- Analog horror / found game — iceberg architecture, retro medium trust signals (Local 58, Mandela Catalogue, Petscop)

**Wave 2 (complete):**
- Grief, memorial, sacred time plays — loss register, anniversary architecture, ghost presence
- Economic / financial plays — debt clocks, net worth statements, financial document authority
- Somatic / sleep plays — circadian timing, dream state, hypnagogic induction
- Pre-arc world-seeding — aging the world before first contact, legend infrastructure

**Wave 3 (in progress):**
- Behavioral economics + casino design — peak-end rule, IKEA effect, playground vs. maze doctrine, variable ratio schedules (Kahneman, Roger Thomas, Zagal)
- Game design / f2p dark patterns — ethical appropriation of variable reward, knowledge-frontier design, parasocial in games (Outer Wilds model, Zagal taxonomy)
- EVE Online sandbox — persona capture, failure cascade, metagame as actual game, trust as attack surface (Mittani/GIA; GHSC heist; BoB dissolution; T20 scandal; Jabberlon5/Vile Rat)
- Motivational interviewing — change talk elicitation, righting reflex, OARS, rolling with discord (Miller & Rollnick)
- Narrative therapy — externalizing, dual landscape, outsider witness, definitional ceremony, re-membering (White & Epston)
- Wilderness therapy + transfer design — front-loading, isomorphic framing, generalization contract, 30/90-day follow-up
- Parasocial relationship research — affective contract, participant-initiated closure, ambiguous endings (Horton & Wohl 1956)
- Ritual design + liturgy — van Gennep three phases, Turner communitas, kinesthetic encoding, commissioning denouement
- Tactical / negotiation communication — FBI Behavioral Change Stairway, Voss tactical empathy, Schwartz awareness stages
- Console metacampaigns — Steel Battalion: Line of Contact PAX metacampaign (persistent consequence, faction decision-making at convention scale)
- Immersive sim game design — Deus Ex (Ion Storm Austin, 2000) conspiracy architecture, benefactor capture, fractal revelation, emergent agency (Warren Spector); Uplink (Introversion, 2001) trace/surveillance mechanic, distributed evidence reconstruction, moral distance abstraction (Chris Delay)
- Ingress / location-based pervasive games (Niantic, 2013–) — Anomaly events (body-here-on-this-day mechanics), persistent world consequences, faction intelligence culture, queryable historical ledger, portal ownership as place attachment, pre-game ARG seeding (Niantic Project)
- Augusto Boal / Theater of the Oppressed — Forum Theater / spect-actor mechanic, Image Theater (frozen embodied tableau), Invisible Theater (unannounced public performance), Rainbow of Desire / "cops in the head" (internalized oppressor), Joker system (amoral complicator)
- Immersive theater — Punchdrunk / Sleep No More (Felix Barrett): mask as anonymity license, one-on-one private scenes, environmental pre-loading (objects as primary narrative), temporal loops, site-sympathetic approach
- Jeepform (Danish/Nordic LARP form) — chamber scenarios, author-stance design (tight emotional arc imposed), "hell" technique (compressed stylized replay of charged moments), framekick (designed temporal rupture), internal monologue voicing (externalized inner state), narrative voice-over (omniscient author narration)
- **Lamina schema analysis** — latent dimension discovery across 300+ plays; identify which of the 27 designed fields are genuinely orthogonal vs. redundant; compress toward minimal complete basis. Cite: Lamina (schema compression framework). Run after schema finalization.

**Long con as arc-level infrastructure (not atomic plays):**
The long con is not a play — it's a sustained background condition that raises the stakes of every play. Weeks or months of ambient world-building: aged social media, search presence, confederate history, organizational legend that predates first contact. These are `REQUIRES: ongoing_maintenance` plays deployed in pre, running throughout. The participant's first direct contact occurs inside a world that already has history. Lamina-style schema discovery becomes worth running when the library reaches 300+ and latent dimensions start escaping the current tag system.

### Structural Gaps Being Filled

The current library is strong on: first-contact plays, investigation arc fuel, surveillance sensation, authority/weight, ambient presence.

Gaps being addressed in current wave:
- **Post-climax / denouement** — day 1/7/30 landing sequences; the debrief is structural but not sufficient
- **Resistance handling** — participant disengages, tests the fiction, or finds a seam; plays that offer graceful re-entry or release without manipulation
- **Failure recovery** — misfired plays turned into story material; broken immersion acknowledged and reframed
- **Multi-participant** — two participants' arcs intersecting without them knowing they're coordinating
- **Long-arc infrastructure** — background conditions running for months; the felt sense that the world existed before first contact

---

## Economic Model

**Target: gifted milestone experiences, then subscription, then platform**

Unit economics (gifted experience, $500 ticket):
- Agent compute: ~$3-8
- SMS: ~$10-20
- Physical touches: ~$25-50
- Human QA: ~$15-25
- Gross margin: ~85-87%

**Scale model:** Waymo fleet ratio. One operator oversees 40-80 concurrent experiences. L3-L4 experiences priced higher to reflect operator time.

**Moat:** the plays library + narrative templates tested at volume, confederate networks in cities, intake methodology, brand reputation for experiences that actually land.

**Failure modes to avoid:**
- Latitude failure: compelling vibe, no ideology. Agency without purpose.
- Starcruiser failure: luxury product at mass-market price point, high capex, no repeat purchase.
- Evermore failure: spectacle-only, no sustainable foundation, high fixed costs.

---

## Reference Material

**Design theory:**
- C. Thi Nguyen, *Games: Agency as Art* — games as medium of agency itself; striving play vs. achievement play; value capture / gamification warning
- Odyssey Works — *Transformative Experiences for an Audience of One*; *Experience Design: A Participatory Manifesto*; Phase Zero research model
- Nordic LARP tradition — safety apparatus (X-card, pre-brief, post-debrief), bleed, play to lose, design for authentic response not performance
- Steve Boyle / Epic Immersive — current high-water mark of in-person model (Tulum, Quintessence of Dust)
- Stephanie Riggs — *The End of Storytelling* (storyplex); *Quantum Narratives* — VR-specific but the grammar argument applies broadly

**Plays source material (by domain):**
- David Maurer, *The Big Con* (1940) — con artistry structural library; long con mechanics
- Erving Goffman, *On Cooling the Mark Out* (1952) — mark cooling as design problem
- Ian Rowland, *The Full Facts Book of Cold Reading* — mentalism and async cold reading
- Derren Brown — psychological forcing, dual reality, progressive anesthesia, coincidence engineering
- CIA *Tradecraft Primer* (open source); *The Art of Intelligence* (Crumpton) — legend building, MICE, cut-out, compartmentalization
- JTRIG toolkit (Snowden / declassified) — digital influence plays at individual scale
- Steven Hassan, *Combating Cult Mind Control* (BITE model); Robert Lifton, *Thought Reform and the Psychology of Totalism* — induction mechanics in ethical register
- SCRAP escape room design philosophy; Jane McGonigal ARG theory; Sean Stewart on rabbit hole design; TINAG doctrine
- Her Story / Obra Dinn — fragmented evidence, player-constructed narrative structure

**Industry signals (WXO LXW26):**
- Raj Samuel (#53) — experiences as identity-editing tools; IDENTITY_INVITE dimension
- Richard Maddock (#66) — 3R model (Revelation → Reinforcement → Replication); reinforcement phase design
- Terence Leclere (#31) — permission architecture; why plays misfire when permission is absent
- Full synthesis: `reference/wxo_lxw26_synthesis.md`; all 125 abstracts: `reference/wxo_lxw26_abstracts.md`

**Immersive practice criticism (No Proscenium):**
- Kathryn Yu, "What Is 'Immersive'?" (NoPro, 2024) — formal vocabulary: magic circle, casting the audience, alibis for interaction, presence/agency/embodiment as distinct outputs, physical/narrative/emotional distance as separate failure-mode axes. The "alibi for interaction" concept is the most operationally useful term from this source: every play must give the participant a diegetically coherent reason to do what the design requires.
- Noah Nelson, "Transformational Experiences Are The New Buzzword" (NoPro, 2023) — wader/swimmer/diver audience segmentation (from themed entertainment), designed vs. accidental transformation, negative transformation = trauma, informed consent as structural requirement for transformation-intended work. Points to Ida Benedetto's *Patterns of Transformation* as the formal framework.
- Felix Barrett / Punchdrunk, book excerpt via NoPro (2026) — site sympathetic approach (vs. site specific), loop structure, neutral mask as empowerment-through-anonymity device, sound zone architecture (31 zones in Sleep No More), transposition (narrative line → environmental/sensory channel, non-verbal), ecosystem vocabulary for a live world.
- Gensler *2025 Immersive Industry Report* — five attributes taxonomy (sensory/emotional, participatory, distinctive location, story-driven, transformative moment); wader/swimmer/diver confirmed as standard themed-entertainment segmentation.

**Canonical transformation framework:**
- Ida Benedetto, *Patterns of Transformation: Designing Sex, Death, and Survival in the 21st Century* (patternsoftransformation.com) — formal design framework for experiences intended to produce genuine personal change. Essential reading before designing high-INTENSITY, irreversible, or transformation-claiming plays. NoPro episode 130 (2017) is the podcast companion.

**Analog horror / found game (iceberg + retro medium):**
- Alex Orona, "Analog Horror and the Rise of the Found Game Storytelling" (Culture Combine, 2024) — design analysis of analog horror (Local 58, Mandela Catalogue, Walten Files) and found-game traditions (Petscop, Home Safety Hotline, Amanda the Adventurer, Inscryption). Key principles: mundane container as trust scaffold; iceberg architecture (surface innocent, depth disturbing); retro-medium aesthetics (VHS, cable access, GeoCities, 8-bit) as authenticity/trust signal; community-driven discovery via Reddit/Discord; ARG cross-pollination (spectrograms, Polybius ciphers, HTML inspection, Morse code). Welcome Home (website-only ARG) as minimal-infrastructure example. Generated `retro_medium_artifact` play (id:retro_medium_artifact).

**Analytical backbone:**
- `~/Documents/drivermap` — 108 behavioral mechanisms, query interface (`python query.py --scenario "..."` or `--dim big_five_N:+`)

**Canonical failure modes:**
- House of the Latitude / In Bright Axiom — vibe without ideology; distributed agency without purpose; the Latitude failure
- Disney Galactic Starcruiser — wrong price point for wrong audience, high capex, no repeat purchase
- Evermore — spectacle-only, no sustainable foundation, high fixed costs

**Behavioral economics + casino design:**
- Daniel Kahneman et al., peak-end rule (1993) and duration neglect — retrospective evaluation is determined by peak + ending, not average or duration; the colonoscopy extension result is operationally applicable to arc close design; 2022 meta-analysis r=0.581
- IKEA effect (Norton, Mochon & Ariely 2012) — partial self-assembly produces higher valuation than complete delivery; applies to fragment-synthesis, participant-constructed narrative
- Endowed progress effect (Nunes & Drèze 2006) — perceived progress increases commitment; applies to giving participants partial completion of a challenge at arc start
- Roger Thomas (Wynn/Encore casino design) — playground doctrine: design for comfort, orientation, and exploration; voluntary dwell increases with safety and invitation; contrast with Bill Friedman (maze doctrine): disorientation retains by confusing, not engaging
- Natasha Dow Schüll, *Addiction by Design: Machine Gambling in Las Vegas* (2012) — machine zone (dissociative absorption state produced by rhythm and feedback); near-miss engineering; decompression zone design; zone entry vs. choice architecture. The machine zone is a cautionary model, not a design target.
- Near-miss engineering — incomplete reward activates dopaminergic circuits at higher rate than clean success; ethical use: as discovery signal (you almost found something real) not as extraction mechanic

**Game design / f2p dark patterns:**
- José P. Zagal et al., "Dark Patterns in the Design of Games" (Foundations of Digital Games 2013) — taxonomy: pay to skip, grinding, artificial scarcity, social obligation/guilt, disguised cost, playing by appointment, purchasable competitive advantages. Ethical test: would the participant's reflective evaluation endorse the mechanic? Key: transparency and alignment of participant interest are the discriminators, not the mechanic category.
- B.F. Skinner, variable ratio reinforcement — most durable schedule; applies to clue distribution, fragment revelation; ethical use: produces curiosity not compulsion when stakes are social/narrative not financial
- Knowledge-frontier design — Outer Wilds (Mobius Digital, 2019) as the canonical model: the expanding edge of what you don't know yet is itself the reward; discovery of a new question is as satisfying as discovery of an answer. Design for epistemic expansion, not just revelation.
- IKEA effect applied to narrative — participant-assembled meaning has more weight than delivered meaning; design clue structures that require synthesis rather than simple reception
- Parasocial mechanics in games — parasocial attachment to NPCs/characters increases investment; character consistency and warmth must persist; see also parasocial relationship research below

**EVE Online / sandbox MMORPG metagame:**
- Alex Gianturco ("The Mittani"), "Uniquely Ruthless: The Espionage Metagame of EVE Online" (GDC 2010) — structure precedes behavior; espionage as emergent sandbox property; metagame vs. game client; information asymmetry as compounding advantage; "you don't constantly have to crap out new raids, players will amuse themselves trying to tear each other's throats out"
- *Sins of a Solar Spymaster* columns #87-88, Ten Ton Hammer — political maxims: "abhor democracy, mistrust reason"; legitimacy derives from perceived strength and narrative, not procedure; "implicit customs trump overt laws"; leaders must be decisive not nice; feudalism vs. democracy as organizational models; team structures prevent single-point-of-failure
- Guiding Hand Social Club heist (2005) — 30-agent, 10-month infiltration culminating in corporate theft and officer assassination; real months of functional trust built to enable betrayal; trust as attack surface; most dangerous agents are native opportunists turned by exploiting dissatisfaction, not external operatives inserted by force
- Band of Brothers dissolution (2009) — Haargoth Agamar (BoB director with grievances against leadership) flipped to Goonswarm; used director-level access to disband the alliance entirely, kicking all member corporations and raiding assets; failure cascade: organizations larger than several hundred people reach a tipping point where identity collapses; cascade is psychological (identity-based), not material; once members see themselves in a failing collective, defection becomes rational
- T20 scandal (2006) — CCP developer used developer access to benefit preferred alliance; illustrates operator neutrality doctrine: any use of privileged access to manufacture narrative advantage destroys legitimacy of the entire system
- Jabberlon5 / Vile Rat (Sean Smith) — out-of-game communication infrastructure (Jabber server) as real political power; the player who controls the information channel controls the metagame; infrastructure creation is power independent of in-game assets
- The three-persona problem (Mittani) — The Mittani / Mittens / Alex Gianturco: three roles in overlapping contexts create irresolvable conflict of interest; the Fanfest 2012 incident as bleed event: intoxication collapsed the boundary between in-game ruthlessness (acceptable) and real-world harm potential (unacceptable); personas are credible under low-stakes conditions and fail under high-stakes ones; the mask has a half-life; using Mittani as design reference: persona capture is distinct from bleed; failure cascade is deliberately engineerable; information environment (INN/propaganda) shapes how members interpret wins and losses
- Failure cascade vocabulary (Mittani, 2009) — coined term for identity-based organizational collapse; distinct from material defeat; triggered by: relentless defeats, leadership credibility loss, available alternative identity, information asymmetry; reversed by: narrative reframe, identity restoration, restored agency

**Motivational interviewing (MI):**
- William R. Miller & Stephen Rollnick, *Motivational Interviewing: Helping People Change* (3rd ed., 2013) — PACE spirit (Partnership, Acceptance, Compassion, Evocation); OARS technique (Open questions, Affirm, Reflect, Summarize); change talk (participant-generated reasons for change); sustain talk (reasons against); righting reflex (clinician's urge to explain what participant should do) as the enemy of change
- Self-generated reasons are more durable — when the participant articulates the significance themselves, change is harder to contradict and more likely to persist; characters should elicit, not deliver
- Rolling with discord — when participant pushes back, reflecting rather than correcting maintains the alliance; "Yes, and" not "No, but"

**Narrative therapy:**
- Michael White & David Epston, *Narrative Means to Therapeutic Ends* (1990) — externalizing conversations (the problem is separate from the person: "the fear" not "my fear"); thin vs. thick description (dominant problem-saturated narrative vs. alternative rich narrative); dual landscape — landscape of action (events/sequence) and landscape of identity (what events mean about who the person is)
- Unique outcomes — moments that contradict the dominant problem narrative; these are the raw material of re-authoring; equivalent to the arc moment where participant's behavior doesn't fit the constraint the arc has implied about them
- Outsider witness / definitional ceremony — structured witnessing practice: the outsider witnesses a retelling, identifies what resonated, says what image or word came to mind, and says what it suggests about the person's values; the participant listens, then responds to what was witnessed. Produces durable identity shift. Applicable to: character acknowledging participant's specific action; sponsor debriefing after arc close; designed social sharing moments.
- Re-membering — deliberate act of bringing valued figures (living or dead) back into the membership of one's life; relevant for arcs that involve honoring relationships, grief, or legacy

**Wilderness therapy + transfer design:**
- Front-loading — before the experience begins, explicitly name the transferable insight you'll be asking the participant to apply. Creates expectation of application, increases attention during experience, and provides the conceptual hook for post-experience integration.
- Isomorphic framing — identify and name the structural parallel between the experience and the participant's real-life challenge. ("This moment of deciding to trust the rope is structurally identical to what you're facing with your business partner.")
- Generalization contract — explicit agreement before or during the experience: "After this, I'm going to do X in my real life." Commitments made in liminal states are more durable when they're specific and named.
- The transfer problem — research finding: powerful bounded experiences rarely transfer to ordinary life without an explicit bridge. Program intensity and duration predict in-program outcomes; facilitation quality (not program length) predicts transfer. Applies to immersive: the 3R model is not automatic; transfer requires these structural elements.
- 30/90-day follow-up — timed follow-up calls at 30 days (still in integration, still motivated) and 90 days (has either transferred or has forgotten) are standard in wilderness therapy; applicable to arc denouement design as "reinforcement phase" beats

**Parasocial relationships:**
- Donald Horton & Richard Wohl, "Mass Communication and Para-Social Interaction" (1956) — foundational definition: the viewer develops a relationship with a media persona that mirrors real social relationships in affective structure but is one-directional; the persona addresses an imagined audience; the viewer develops ongoing investment, loyalty, and grief at the relationship's end
- Affective contract — implicit agreement between audience and character: character will remain consistent with the warmth, wit, and interest they've established. Violating the affective contract at arc close (going cold, becoming different, or disappearing) is experienced as abandonment, not conclusion.
- Participant-initiated closure — closure initiated by the participant (they choose the goodbye, they decide when it's done) produces substantially better grief outcomes than character-initiated (character disappears or formally ends the relationship) or ambiguous ending (relationship simply stops). Design arc close to give participant meaningful agency over farewell.
- Parasocial breakup — the emotional experience when a parasocial relationship ends; can produce genuine grief responses; ambiguous endings (character simply disappears) produce the worst outcomes because there is no resolution path. Never allow a character to simply go silent without a designed farewell.

**Ritual design + liturgy:**
- Arnold van Gennep, *Rites of Passage* (1909) — three phases: separation (subject removed from ordinary social structure), liminality (threshold state; identity suspended, available for change), reincorporation (returned to social structure as changed). All three phases are required for transformation. Missing reincorporation = liminal state left open (psychologically unstable).
- Victor Turner, *The Ritual Process* (1969) — communitas: the egalitarian social bond produced in the liminal phase; Turner distinguishes liminal (embedded in social structure, obligatory) from liminoid (leisure-based, optional, potentially subversive); modern experiences are liminoid but can carry liminal's transformative weight if the participant has consented to take them seriously; communitas for single-participant: dyadic form (participant + guide or implied prior initiates) or the participant's relationship with their past/future self
- Kinesthetic encoding — physical acts produce episodic memories with different durability, embodiment, and accessibility than perceptual content; liturgical traditions use movement, touch, handling objects, writing, and walking precisely because these produce body-memory; design at least one kinesthetic beat for transformation-intended arcs
- Commissioning vs. concluding denouement — commissioning sends the participant forward into ordinary life carrying a specific new capacity; concluding closes the story without propelling them; commissioning requires naming what they now know how to do; compare: "your journey is complete" (concluding) vs. "you now know how to hold doubt without flinching — go use it" (commissioning)
- Preparatory phase / container building — the liminal phase is more available and more permeable after an intentional preparation; don't open the transformative space cold; the preparation ritual creates the container that the transformation fills

**Tactical / negotiation communication:**
- Gary Noesner (FBI), Behavioral Change Stairway Model (BCSM) — five-step stairway: (1) active listening, (2) empathy, (3) rapport, (4) influence, (5) behavioral change. Cannot be skipped. Characters that push influence before rapport generate resistance. Arc design implication: early-arc characters must do steps 1-3 before any character or system attempts influence. The righting reflex (urge to skip to influence) is the enemy here too.
- Chris Voss, *Never Split the Difference* (2016) — tactical empathy: labeling the participant's emotional state ("It sounds like you're frustrated…"); mirroring (last 1-3 words of what they said); calibrated questions ("How am I supposed to do that?" vs. "Can you do X?"); late-night FM DJ voice (deliberate calm, lower register); accusing audit (preempt negative assumptions); tactical empathy produces rapport faster than agreement-seeking
- Eugene Schwartz awareness stages — five levels of market awareness: Unaware / Problem-aware / Solution-aware / Product-aware / Most-aware. Each stage requires a different opening move. Applicable to play selection: a naive participant (FRAME_REQUIREMENT: naive) is Unaware or Problem-aware; a primed participant is Solution-aware; a meta participant is Most-aware. The correct communication for each stage differs dramatically; the wrong stage assumption is why plays misfire before permission is granted.

**Console metacampaigns — Steel Battalion: Line of Contact:**
- From Software / Capcom, 2004-2005; PAX East 2010 revival (metacampaign). 4-faction persistent war over Sea City Island; 8-week rounds × 8 turns. Field Manual archived at Scribd (PDF complete). Core insight: the decision loop (faction → mission → resource allocation → respawn-or-eject) is granular enough that the 8-week campaign compresses into a single convention day without losing its economy or stakes — proving metacampaign persistence can be temporal, spatial (convention floor), or community-narrative (ARG forum).
- **Eject button as kinetic commitment device** (Atsushi Inaba, producer): the eject button covered under a physical plastic cap requires deliberate action; failure to eject when VT is dying = permanent pilot KIA + save wipe. Hardware affordance + consequence binding = player agency becomes somatic and costly. Design principle: physical action that is required for an irreversible consequence creates stronger memory and stakes than a dialog box.
- **Resource economy as pacing structure**: supply points (mission earnings) controlled which VTs were accessible per turn; supply pool depleted on respawn; win/loss split plus participation bonus ensured continued play regardless of outcome. Campaign failure (2005 shutdown): no redistribution mechanism → top-tier VTs locked in abandoned trial accounts → progressive scarcity → degraded competitive balance → server shutdown. Lesson: persistent economies require active equilibrium maintenance; passive designs that assume constant new players collapse when growth stalls.
- **Comparative ARG metacampaigns**: The Beast (Microsoft, 2001) — 12-week ARG, 50 websites, 4500 active in central forum; asynchronous decryption model. I Love Bees (Bungie, 2004) — 210 GPS-linked payphones, 3M unique visitors, real-world convergence beats. Perplex City (2005-2007) — 2-year run, physical puzzle cards, 60-person Clapham Common event with diegetic "mole" extracted by black helicopter as narrative closure. All show: persistent state as witness mechanism; mixed async + real-world participation modes; community coordination producing more than individual play.

**Ritual corpus — common, esoteric, and obscure:**
- Key structural sources: Arnold van Gennep *Rites of Passage* (1909); Victor Turner *The Ritual Process* (1969); Masonic ritual (three degrees + Royal Arch); Eleusinian Mysteries; Vodou kanzo initiation; SCA peerage vigil and elevation; Irish wake and keening tradition; Cosa Nostra blood oath; military induction; Hermetic/Golden Dawn ritual structure.
- **10 structural patterns extractable as design principles:**
  1. *Clear boundary marking*: the liminal space must be felt, not just intellectual — spatial (chapel, lodge), temporal (midnight, full day), vestmental (robe, uniform), or linguistic (a formula, a vow).
  2. *Witness as requirement*: the participant cannot transform alone; peers, an expert-authority, a collective, or an absent other (God, the organization, the dead) must witness.
  3. *Secrecy as the lock*: the secret's power is not its content (often banal: passwords, handshakes) but the fact of shared silence; shared silence creates shared risk and locked commitment.
  4. *Irreversibility as stakes*: the participant must enter believing they cannot exit unchanged; once they believe this, they commit accordingly; the belief is self-fulfilling.
  5. *Somatic registration before cognition*: the body must feel the change before the mind understands it (water, vestment, rhythm, ordeal); nervous system precedes interpretation.
  6. *Artifact as persistent proof*: the object (ring, diploma, insignia) persists in daily life; it is worn, carried, found in a drawer; it activates the ritual memory on contact.
  7. *Status crystallization through social enforcement*: others must treat the participant differently after reincorporation; the organization doesn't police — society does.
  8. *Layered disclosure* (degree systems): Masonic degrees, Hermetic grades, kanzo levels — the participant believes there are higher secrets above; this incentivizes continued participation and deepening commitment indefinitely.
  9. *Communitas as brief peak*: Turner's temporary dissolution of hierarchy; profound relief and direct connection; must be brief — it cannot last or it becomes ordinary; the memory of dissolution remains.
  10. *The unutterable as limit*: Eleusinian Mysteries survived 2000 years because the final revelation was never described; the mystery is not in knowing but in the inviolability of the not-telling.
- **New play candidates from ritual corpus**: `layered_secret_system`, `ordeal_threshold`, `absent_witness_invocation`, `temporal_rupture_opening`, `communitas_beat` — see wave 3 expansion targets above.

**Immersive sim game design — Deus Ex (2000):**
- Ion Storm Austin / Eidos; Warren Spector (director). Primary reference for conspiracy architecture, benefactor capture, and emergent player agency.
- Fractal conspiracy model: UNATCO (public authority) → Majestic 12 (shadow government) → Illuminati (deeper layer) → AI substrate (Daedalus/Icarus/Helios). Each layer feels conclusive until the next is revealed. The player's model of the situation is wrong at every stage.
- Gray Death / Ambrosia structure: manufactured plague + withheld cure = population dependency; participant unknowingly enforces the control mechanism they later discover they were protecting. Complicity is designed before the reveal.
- Benefactor capture: handler (Manderley) provides institutional authority + information advantage + selective generosity → participant trusts and performs efficiently → handler revealed as serving Majestic 12. The participant's competence is the mechanism of their complicity.
- Strategic silence: JC permits Manderley's false conclusion through omission — "Lebedev. A surprise attack" (technically true, actively misleading). Lies by omission preserve the participant's reasoning while redirecting their conclusions.
- Three denouement architectures: Tracer Tong (destroy all control structures — no hidden hands), Helios (merge with AI — become the system you were fighting), Illuminati (restore older conspiracy — choose the moderate faction). Each represents a genuinely different value hierarchy; none is "correct."
- Invisible Hand doctrine (Everett): "We only influence. Suggest. Insinuate." Boxes stacked in boxes; plausible deniability through indirect action. Internal factionalism (Everett/moderate vs. Page/accelerationist) makes the conspiracy feel alive.
- Warren Spector's design philosophy: "Never judge the player." Build systems that afford multiple interaction points; emergent solutions (not scripted paths) produce the most resonant moments. Player discovering unintended pathways validates agency more than executing designer intent. The world communicates available possibilities; the player performs within them.
- Verifiability distinguishes paranoia from justified suspicion: accusations gain credibility through evidence + corroboration + pattern recognition, not assertion. Truth is discoverable in enemy infrastructure (their datacubes, their emails, their systems).
- Environmental narrative: character, subplot, and motivation baked into spaces. Bodies and damage indicate recent events. Personal logs explain motivations. Participants reconstruct rather than receive.
- Warrent Spector (2021): "I'm not sure I'd make Deus Ex today." The line between satirical conspiracy premise and literal conspiracy thinking has blurred — the game's prescience has become a liability.

**Immersive sim game design — Uplink (2001):**
- Introversion Software (Chris Delay, Mark Morris). Hacker simulation; covert operative accepts black-market contracts through Uplink Corporation.
- Trace/surveillance mechanic: every action leaves a network trace; you must cover your tracks or investigators close in; the link monitor shows you being traced in real time — felt vulnerability in an information environment. Design principle: asymmetric information + real-time escalation + audio pressure. The vulnerability is felt while the participant is acting, not after.
- Distributed evidence reconstruction: ARC (Andromeda Research Corporation) conspiracy discovered through intercept emails, news feeds, academic papers, memory archives; no single source is sufficient; truth requires cross-referencing. The conspiracy is assembled by the participant from fragments; no one character ever explains it.
- Moral distance abstraction: interface abstracts the human cost of actions (bankruptcy, prison framing, ruined reputation, suicide); operator sees numbers and systems, not people. Design principle: moral weight is most powerful when suddenly un-abstracted — when the numbers become legible as a specific person's life.
- Active erasure: cover-your-tracks mechanic as design element. Participant must actively delete logs, wipe traces, shred records. The act of erasure is the complicity — voluntary, deliberate, irreversible within the system. Distinct from passive complicity; participant chose to cover the evidence.
- Contract structure: participant operates on instructions without knowing the mission's full purpose; complicity without explicit choice at the contract stage; deniability and guilt coexist. "You accepted the job — we didn't explain why."
- Introversion design philosophy (Delay): systems-first; recurring theme across all Introversion games (Uplink, Defcon, Prison Architect) — you are the administrator of a system that produces harm at a distance. The participant is not the monster; the system is. The participant is the efficient operator of the monstrous system. Most powerful when the system's consequences are suddenly personalized.
- New play candidates from Uplink: `trace_exposure`, `contract_complicity`, `active_erasure`.

**Ingress / location-based pervasive games (Niantic, 2013–):**
- Two-faction persistent war over real-world portals (art, murals, notable architecture). Every portal is a real GPS-tagged location. Every capture, attack, and link is permanently logged.
- Anomaly events (body-here-on-this-day mechanic): faction operations requiring physical presence at a specific real-world location during a specific time window. Side that deploys more bodies wins. Record is permanent and queryable. Design principle: physical presence at a real place on a real date creates a record that is distinct from performance — the body is the resource, the ledger is the proof.
- Portal ownership as place attachment: participant owns a specific corner of real geography through repeated action and resource investment. Location becomes personally meaningful through contested stewardship. Design principle: claiming a real-world place as yours (even in a game system) produces genuine place attachment that persists beyond the game.
- Queryable legacy / historical ledger: all participant actions are recorded in a public, independently queryable database. Participant can look up their own history; others can verify it. Design principle: the transition from private memory to external record is a categorical shift in legacy weight. "I can show you" vs. "let me tell you."
- Pre-game ARG seeding (Niantic Project ARG, 2012): elaborate fictional frame seeded on forums, Google+ posts, fake scientist persona ("Devra Bogdanovich"), conspiracy threads, viral imagery — deployed months before game launch to create a mythology that preceded the game. Participants who found the ARG before the game felt they had discovered something rather than been marketed to.
- Faction intelligence culture: real-world operational security, Discord coordination, counter-intelligence between factions, spy flips, double agents. The social layer became more compelling than the game layer for many veteran players. Design principle: faction identity + operational culture + real stakes (contested physical territory) produces genuine in-group loyalty.
- Pokemon Go (2016) as mass-market tradeoff: Niantic stripped the narrative to achieve mainstream scale; daily active users 10-50× Ingress but zero faction depth, no persistent narrative, no intelligence culture. Confirmed: the narrative/competitive layer is what generates committed participants; the casual layer is reach without depth.
- New play candidates from Ingress: `anomaly_attendance`, `territorial_claim`, `queryable_legacy`.

**Theater of the Oppressed (Augusto Boal, 1970–2009):**
- Brazilian director Augusto Boal developed Theater of the Oppressed as a methodology for social change through theatrical rehearsal. Core premise: theater is not representation of reality but rehearsal for it.
- Forum Theater: a scene depicting oppression or constraint is performed; at the point of failure, a "Joker" (amoral facilitator) invites the audience ("spect-actors") to stop the scene, replace the protagonist, and try a different response. The scene replays with the intervention. Multiple interventions may be tried. No single solution is offered as correct. Design principle: embodied rehearsal produces different learning than cognitive analysis — muscle memory of a different response changes what the body does when the real situation arises.
- Image Theater: participants pose their bodies (or each other) into frozen tableaux representing power relations, emotional states, or situations. No words. The image is read by facilitator and group, then micro-adjusted toward an "ideal image" through a sequence of transitional poses. Design principle: somatic cognition — the body knows the power structure before the mind names it; physical externalization of internal states reveals what verbal account would rationalize.
- Invisible Theater: a scene is performed in a public space (restaurant, bus, market) without the audience knowing it is theater. Bystanders become unwitting participants. The ethics: never create real distress; never deceive about material facts; always reveal to individuals who ask. Design principle: when participants act under the belief that consequences are real, their responses are unperformed and therefore more informative — both to them and to the designer.
- Rainbow of Desire / "cops in the head": the internalized oppressor. Boal's technique for working with internalized self-limiting voices — externalized as characters in dialogue with the protagonist. The participant negotiates with their own doubt, shame, or compliance rather than an external antagonist. Design principle: the most durable form of constraint is self-applied; the most powerful intervention makes the participant's own complicity visible and negotiable.
- The Joker system: a facilitator role that is deliberately amoral — neither protagonist's ally nor antagonist. The Joker introduces complications, asks "what if the opposite?", refuses to validate the protagonist's framing. Not a therapist; not a director. A systematic difficulty-maker. Design principle: characters who complicate rather than help generate more participant agency than characters who validate.
- New play candidates from Boal: `forum_intervention`, `image_theater_freeze`, `invisible_theater_event`.

**Immersive theater — Punchdrunk / Sleep No More (expanded):**
*(Reference begun in No Proscenium section above; expanded here.)*
- Felix Barrett / Punchdrunk (UK, founded 2000). Sleep No More (NYC, 2011–): a Macbeth-derived immersive experience across six floors of a former hotel, running continuously for 12+ years. Approximately 100 performers; audience of up to 500 masked participants nightly.
- The mask: white Venetian mask for all audience members; performers are unmasked. Key design insight (Barrett): the mask suspends social legibility — you cannot be identified, recognized, or judged by others in the space. This creates permission for behaviors unavailable to the socially-legible self: sitting in rooms for 20 minutes, following characters into dark spaces, reading private objects. The mask is a permission structure, not costume.
- One-on-one moments: performers select individual audience members for 2-3 minute private scenes in a bounded space (a bed, a closet, a booth). These scenes are not repeatable and not announced. The singling-out is done by performer choice. Design principle: status elevation through selection — being chosen by a performer who could have chosen anyone produces disproportionate emotional weight relative to scene duration. Participants consistently describe their one-on-one as the peak of the experience.
- Environmental pre-loading (site-sympathetic approach): every room in the McKittrick Hotel contains pre-loaded objects — nursing records, personal letters, taxidermied animals, worn furniture — arranged so that a patient observer can reconstruct a life and narrative from residue alone. No explanatory text. The design principle (Barrett): "the building is the actor." Objects are chosen for their emotional charge, not their narrative efficiency. More objects does not mean more narrative; it means more texture.
- Temporal loops: the same scenes play on a 45-minute cycle throughout the building. An audience member who follows a performer through a full loop sees a complete dramatic arc. One who jumps between scenes assembles a fragmented view. Neither is "correct." Design principle: temporal loop structure means the experience is never finished — there is always more to see, always a different angle on the same events.
- Sound zone architecture: Sleep No More uses 31 distinct audio zones, each with its own sonic identity. Moving between zones is a sensory transition that marks space as dramatically distinct. Sound is environment, not background.
- New play candidates from Punchdrunk: `mask_anonymity_passage`, `one_on_one_private_scene`, `environmental_narrative_space`.

**Jeepform (Danish/Nordic LARP form, early 2000s–):**
- Originated with Vi åker Jeep (Sweden/Denmark, ~2002): Tobias Bindslet, Marie Holm-Andersen, Morten Jaeger, others. Short-form, chamber LARP scenarios: 2-8 participants, 1-2 hours, typically single location or minimal locations.
- Author-stance design: the designer imposes a specific emotional arc and thematic structure. Participants have agency within the arc but not over it. Contrast with sandbox LARP (participants determine direction). The authorial structure creates emotional safety — participants know there is a designed arc — which paradoxically enables deeper vulnerability.
- Meta-techniques: designed frame-breaks that deepen authenticity rather than breaking immersion. Key examples:
  - *Internal monologue voicing*: a player pauses their character's scene to voice the character's inner state directly, in first person. The scene continues with this doubled consciousness: external action + voiced interiority simultaneously audible.
  - *Narrative voice-over*: a narrator voice (separate from any character) speaks the protagonist's inner life, backstory, or consequences while the protagonist acts. Participant and narrator may converge or diverge.
  - *Framekick*: mid-scene shift in time, space, or register without warning or preparation. The participant must re-orient in real time. Designed disorientation as technique rather than failure.
- "Hell" technique: a previously played scene that had emotional weight is replayed in compressed, stylized, or abstracted form. The repetition-with-variation distills the emotional core. Like a musical phrase transposed — the essential quality becomes audible stripped of situational surface.
- Chamber compression: 48 hours of psychological drama compressed into 90 minutes. Every scene matters; no ambient filler. Participants have no time to intellectualize; they react at real-time emotional speed.
- Key design principle (Bindslet et al.): the tightest constraint produces the most authentic feeling. The form's brevity and structural rigidity are not limitations — they are the mechanism of intensity.
- Nordic Larp Wiki (nordiclarp.org) — primary documentation archive. Key articles: "Jeepform," "Meta-technique," "Narrative voice-over," "Monologue."
- New play candidates from Jeepform: `hell_replay`, `framekick_temporal_shift`, `internal_monologue_voiced`, `author_narration_beat`.
