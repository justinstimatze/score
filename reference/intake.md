# Intake Design: Participant Profiling System

Three-pass process. The goal is a drivermap dimensional profile accurate enough to rank
mechanism candidates and select plays.

- **Pass 1 (Sponsor form)** — sponsor fills out about the participant; indirect behavioral
  prediction; no participant exposure
- **Pass 2 (Participant artifact)** — optional; participant fills out a form framed as taste
  calibration or experience enrollment; they know something is coming, not what
- **Pass 3 (Operator inference)** — agent/operator maps collected signals to drivermap
  dimensions; runs `query.py --dim [dims]` to rank mechanism candidates; selects arc type
  and play candidates

---

## Form design principles

### Validity hierarchy (Schmidt & Hunter, 1998)

Behavioral description > situational judgment > self-report. This ordering governs every
design decision:

- **Sponsor form = reference interview.** Third-party behavioral description of specific past
  events. This is the highest-validity input we have. Questions ask "what did they do" and
  "describe a specific instance" — not "how would you describe them." The sponsor's idiosyncratic
  language and the specific stories they choose to tell are themselves data.

- **Participant form = structured situational judgment + forced-choice.** MC questions framed
  as scenarios or forced comparisons. The diegetic cover story changes what the participant is
  optimizing for — if they think they're applying for something, their responses shift from
  identity-performance toward role-fit performance, which is more usable. Elimination questions
  ("which sounds least like you") are more reliable than selection questions because avoidances
  are less defended than affinities.

- **Arc = work sample.** Highest validity instrument in the pipeline. The first handler letter
  response, whether they comply with the first commission, how they process the first reveal —
  all behavioral evidence that updates the profile in real time. The intake is a prior; the arc
  is the real data collection. Design the first three plays well enough; after that, the
  participant is telling you who they are through action.

### Faking and self-disclosure distortion

Self-report faking is worse in explicit applicant contexts (Schmitt & Oswald, 2006). Both
forms of distortion apply: impression management (deliberate) and egoistic bias (sincere
but self-flattering). Mitigations used in this form:

- **Behavioral anchoring**: "describe a specific instance" rather than "in general, how do
  you tend to" — specific recall is harder to sanitize than abstracted self-description
- **Implicit questions**: the C-section scenarios don't signal what's being measured; the
  participant is imagining a situation, not evaluating themselves
- **Elimination over selection**: choosing what doesn't fit is less defended than claiming
  what does
- **Third-party primary**: sponsor data is weighted higher; participant self-report is a
  second signal to validate against sponsor report and arc behavioral evidence

### Divergence as signal

Where sponsor report and participant self-report diverge, the gap is often more informative
than either alone. Operator should explicitly compare D4 (sponsor's identity read) against P7
(participant's identity elimination). Gaps indicate: blind spots, aspiration vs. behavior
mismatch, or sponsor projection. All three are arc-relevant.

---

## Pass 1: Sponsor Form

### Cover story
"To design an experience that actually fits [participant], rather than a generic premium
experience, we need to understand them specifically. Some questions below are unusual for
a gifting service. That's intentional — most services personalize the occasion; we
personalize the person."

The form should feel premium and somewhat clinical — like a bespoke tailor's intake, not
a personality quiz. Brevity is a feature. Sponsors who rush through give lower-signal
answers; the form is designed so that thoughtful completion takes 20-30 minutes.

---

### SECTION A — BASICS

**A1.** Your name and your relationship to the recipient.

**A2.** Recipient's name. Age (approximate is fine). City / region.

**A3.** How long have you known them, and in what context did you meet?

**A4.** On a scale from 1–5, how well do you know their inner life — not just their
preferences, but how they actually process things?
`[ 1 = acquaintance / 3 = close friend / 5 = I could finish their sentences ]`

→ *Operator note: calibrate confidence on all subsequent A/B/C questions by this score.
Low scores (1–2) mean behavioral predictions are lower signal; cross-validate with Section F
open responses.*

---

### SECTION B — THEIR WORLD
*Reference interview style — behavioral description, not category selection.*

**B1.** Describe how [name] actually spends their time — work, what they do when
they're not working, who they're around. Be concrete.
*(Free text — a paragraph)*

→ *Operator reads for: professional context, social density, how they spend discretionary
time. Extract big_five_O (intellectual/creative emphasis), big_five_E (social vs. solitary
default), big_five_C (structured vs. open-ended leisure). A sparse answer signals low-knowledge
sponsor (cross-reference A4). Richness and specificity of the answer are themselves signal.*

**B2.** Their social world — how many people, how close, how central is it to them?
Has that changed in the last few years?
*(Free text)*

→ *big_five_E: many/active = +E; few/deep = -E or high A. "Changed significantly" is a
context flag — probe further in F or note in E3 (live context). Sponsor who says "I don't
really know their social world" = recalibrate A4.*

---

### SECTION C — HOW THEY MOVE
*Core dimensional profiling via behavioral prediction scenarios.*

**C1.** When unexpected changes occur in plans they were looking forward to — a trip
cancelled, an event moved — they typically:
```
[ ] Adapt quickly; they find it easy to shift gears and discover something good in the new plan
[ ] Need a beat to adjust, but get there — mild disruption, not lasting
[ ] Find it genuinely difficult; the disruption lingers for a day or more
[ ] It depends heavily on how invested they were in the original plan
```
→ *big_five_N: difficult/lingers = +N; adapt quickly = -N. "Depends on investment" = moderate
N + sunk_cost_fallacy tendency — flag for ordeal_threshold sensitivity.*

**C2.** Think of the last time they encountered something they couldn't explain — an odd
coincidence, a gap in someone's story, an anomaly. Their most natural response was:
```
[ ] They tried to find an explanation — it nagged at them until they did
[ ] They noted it and moved on without much concern
[ ] They got actively excited about the mystery
[ ] They felt uncomfortable until it resolved somehow
```
→ *curiosity_exploration: excited = high; nagged until explained = need_for_cognition:+.
need_for_closure: uncomfortable until resolved = +NFC; noted and moved on = low NFC.
big_five_O: excited = +O; uncomfortable = -O*

**C3.** If they received a handwritten letter addressed to them with no return address,
their most likely first move would be:
```
[ ] Open it immediately and read everything
[ ] Look for clues about the sender before opening
[ ] Show it to someone close before opening
[ ] Set it aside — come back to it when the moment is right
[ ] Feel genuinely unnerved — not sure they want to open it at all
```
→ *big_five_O: open immediately = +O; look for clues = +O + need_for_cognition.
big_five_N: unnerved = +N. Attachment: show someone first = secure/social attachment.
This is also a direct detection threshold probe: the unnerved response predicts detection
risk in surveillance-adjacent plays.*

**C4.** When given a complex set of instructions for something they want to do:
```
[ ] Read everything carefully before starting — they want the full picture
[ ] Skim for key information, then dive in and figure it out
[ ] Start immediately and consult the instructions only when stuck
[ ] Ask someone to explain it rather than reading
```
→ *big_five_C: read everything = +C; start immediately = -C.
big_five_E: ask someone = +E. need_for_cognition: read everything + skim strategically = +NFC.
High-C participants respond better to plays with clear instructions; low-C do better with
ambiguous invitations.*

**C5.** In disagreements with people in positions of authority — managers, institutions,
officials — their natural posture is:
```
[ ] Defer; they generally trust that systems work for a reason
[ ] Comply outwardly but maintain private reservations
[ ] Push back; they'd rather say what they think, even if it costs something
[ ] Assess case-by-case — depends on whether they respect the authority
```
→ *obedience_authority: defer = high; push back = low. big_five_A: defer = +A; push back
= -A. Deference predicts authority-play responsiveness (handler_letter, commissioning_letter,
the_commission); push-back predicts investigation arc preference. "Assess case-by-case"
is the highest-information response — probe further.
"Comply outwardly / private reservations" is the most arc-relevant response: this describes
a participant who will execute plays while internally skeptical — exactly the posture that
requires sustained handler credibility investment. The arc must earn their private belief,
not just their behavioral compliance. Flag this for: slower permission chain, additional
trust-building plays before the first major ask, and handler persona that rewards skepticism
rather than demanding deference.*

**C6.** After a day of significant social interaction — meetings, gatherings, conversations:
```
[ ] Energized; they want more — social time fills them up
[ ] Satisfied; good day, now ready to wind down
[ ] Drained; they need alone time to recover, even from good interactions
[ ] Depends entirely on whether the interactions felt meaningful
```
→ *big_five_E: energized = +E; drained = -E. "Meaningful" distinction = +A + significance_quest.
High-E participants tolerate confederate-heavy arcs; low-E may find them exhausting.*

**C7.** When they've committed to something — a project, a plan, a relationship — and it
becomes clear it's not working:
```
[ ] Persist and try harder; they believe in seeing things through
[ ] Acknowledge it but struggle to let go; they find pivoting uncomfortable
[ ] Assess the evidence and pivot when it's clearly not serving them
[ ] Exit relatively quickly once the signal is there
```
→ *sunk_cost_fallacy: persist/struggle = high; assess and pivot = low.
big_five_C: persist = +C; exit quickly = -C.
High sunk-cost tendency predicts stronger response to ordeal_threshold and commitment plays.*

**C8.** Their general relationship to risk — financial, physical, social:
```
[ ] They research before committing — they want to know what they're getting into
[ ] They'll take a calculated bet — risk is fine if the logic holds up
[ ] They move toward uncertainty — the unknown is often part of the appeal
[ ] Domain-dependent — careful in some areas, quite willing to risk in others
```
→ *Reframed to remove evaluative loading — "strongly cautious" reads as a limitation,
"comfortable with uncertainty" reads as a strength; sponsors were systematically upgrading.
Research-before-committing = +N, high need_for_closure. Calculated bet = neutral N, high
need_for_cognition. Moves toward uncertainty = -N, high reward_sensitivity, +O. Domain-
dependent is often the truest answer — if selected, ask the sponsor which domains in F or
E3. High risk-aversion in financial/physical domains = calibrate detection window; risk-
tolerance in social/relational domains = can tolerate confederate-heavy arcs.*

---

### SECTION D — WHAT MOVES THEM

**D1.** Describe a specific moment they found genuinely moving or profound — not a
category of things, an actual instance. What happened, and how did they respond?
*(Free text — a specific story, not a type)*

→ *Behavioral description replaces category selection here. The instance itself carries more
signal than any checkbox: what they chose to tell you (the domain), how the person responded
(their emotional register and agency in the moment), what made it moving (the mechanism).
A sponsor who gives a category ("they like artistic experiences") rather than an instance
has low insight into this dimension — weight accordingly. Extract: SOMATIC profile, arc type
affinity, emotional_register, LANDSCAPE (did the moment produce a feeling, a realization,
or an action?). This is the single highest-signal question for arc type selection.*

**D2.** What subjects or domains does their curiosity run deepest?
*(Free text — 2–3 sentences)*

→ *Primary use: extract specific domain names to use as diegetic material. The participant's
curiosity domains are the fictional wrapping for plays — an investigation arc for a maritime
historian doesn't need a generic crime, it can be about a ship's manifest. Specificity here
directly enables specificity in arc design. Secondary: big_five_O (breadth and depth of
domains named), need_for_cognition (how specific and technical the domains are). A sponsor
who says "history" is lower signal than one who says "19th century merchant shipping routes."
Probe for specificity if the answer is vague.*

**D3.** Is there a story — from their life, from fiction, from history — that they return
to, reference often, or that you know means something to them?
*(Free text)*

→ *Operator: highest-signal identity_invite data. The stories people carry are templates
for the roles they want to play. Cross-reference with arc type fit:
investigation story = investigation arc; transformation story = initiation arc;
persecution/injustice story = conspiracy/reckoning arc; reunion/return story = denouement
arcs. Note the role they identify with, not just the story.*

**D4.** What would they most want to be seen as, by the people who know them well?
```
[ ] Dependable — someone who follows through
[ ] Perceptive — someone who sees what others miss
[ ] Creative — someone who makes things that didn't exist
[ ] Influential — someone whose thinking or work matters
[ ] Good — someone of integrity and care
[ ] Interesting — someone with a specific and irreplaceable point of view
[ ] Brave — someone who does hard things
[ ] Something else (describe below)
```
→ *identity_invite calibration. Perceptive = investigation arc; Brave = ordeal arc;
Dependable = handler-relationship plays; Interesting = uniqueness + O; Good = moral arc.
This sets the IDENTITY_INVITE target for the whole arc — every play's identity offer should
build toward this answer.*

*Follow-up (elimination):* And which of these would they most reject as a description
of themselves — the one that would make them say "that's not me"?
*(Same list — mark one)*

→ *Negative space on identity. Cross-reference with participant P7. Divergence between
sponsor's positive read (D4) and participant's rejection (P7) is high signal: if sponsor
says "perceptive" and participant rejects "perceptive," one of them is wrong and that gap
is the arc's entry point.*

**D5.** What is [name] definitely not? The personality description, set of values, or style
of engaging with the world that would make them roll their eyes and say "that's not me."
*(Free text)*

→ *Negative space profiling. People know their avoidances and disidentifications more
reliably than their affinities. A person who can't articulate their positive identity often
has a sharp, clear negative one. Also catches trope risks: if the sponsor says "they hate
anything that feels like a team-building exercise," this constrains play selection directly.*

---

### SECTION E — CALIBRATION AND LIMITS

**E1.** What do you want [name] to be able to do, feel, or understand after this
experience that they can't — or don't — right now?
*(Free text — be as specific as you can)*

→ *Ideology articulation — leads this section because it is the most important input.
A specific, grounded answer ("make a decision they've been avoiding," "feel like they're
allowed to be seen," "believe their work actually matters") gives the arc a transformation
target. A vague or atmospheric answer ("feel good," "be surprised," "have fun") is a red
flag — probe before arc design begins. An arc without a clear transformation target is
structurally at risk of the Latitude failure pattern: correct apparatus, no ideology.
If the sponsor cannot articulate a specific change, ask: "If they came to you six months
from now and said the experience changed something — what would you most want that thing
to be?" Do not begin arc design until this has a specific answer.*

**E2.** Is there anything that would be particularly wrong for them? Content, contexts,
interactions, or types of experience that should be categorically avoided.
*(Free text — be specific. Consider: physical intensity or body involvement; strangers
contacting them directly; workplace or professional scenarios; family references; financial
content; experiences of loss or grief; religious, political, or ideological themes; anything
that would feel like surveillance or invasion of privacy.)*

→ *Operator: direct CONTRAINDICATED and safety input. Any phobias, traumas, or live
stressors named here are absolute constraints. Flag for play-level CONTRAINDICATED
annotation before arc design. Sponsors often don't spontaneously think about categories
like "receives contact from an unknown number" or "workplace play-acting" as things to
exclude — the domain prompts surface blind spots. If the sponsor leaves this blank, probe
verbally before arc design.*

**E3.** What's happening in their life right now that we should know about?
*(Stressors, transitions, live relationships, ongoing projects — anything that changes context)*

→ *Live context data. A person in the middle of a difficult work situation should not
receive plays that add workplace complexity. Someone in early grief should not receive
loss-adjacent plays unless explicitly designed for that context.*

**E4.** Setting aside the transformation you described above — what shape of experience
would feel exactly right for them? Not the outcome, but the form: the setting, the pace,
the degree of involvement, the register.
*(Free text)*

→ *This is a different question from E1. E1 = what change? E4 = what form? A sponsor might
say "they need to start believing in themselves again" (E1) and "they'd want something that
feels like a real mystery, not a game" (E4). Both are necessary; they often don't converge.
High-scoring sponsors give answers that constrain the arc design space (setting, channel,
intensity level). Low-scoring sponsors give mood words ("something warm," "something
surprising") — useful as tone data but not design data.*

---

### SECTION F — FREE RECALL

*These questions take longer to answer. If the sponsor rushes through, the answers are
lower signal. Quality over completeness.*

**F1.** Describe a time they were genuinely surprised by something in their own life —
not just a nice surprise, but something that actually shifted their perspective or
expectation. What happened, and how did they respond?
*(Free text — aim for a paragraph)*

→ *Operator: threat appraisal style, O, N, emotional_register. How they RESPONDED
to surprise (delight vs. alarm vs. investigation vs. paralysis) is more useful than
what the surprise was. Note their agency in the story — did they act or receive?*

**F2.** What's something they've wanted for a long time but haven't moved toward?
*(Free text)*

→ *significance_quest, achievement_motivation, arc seed. The gap between desire and action
is the most important structural opportunity in the arc. Not to be addressed directly (that
would feel manipulative and obvious) but to be approached from an oblique angle: create
conditions where they encounter the gap from a new position, recognize their own agency in
it, or practice the identity that closing the gap would require. E.g., if F2 = "start
writing," the arc doesn't assign them writing — it puts them in a situation where they
discover they're already doing it. If the sponsor answers this question vaguely or says
"I'm not sure they have any unfulfilled wants," either the sponsor's knowledge is shallow
(recalibrate A4) or the participant has a settled, contented character — note this as a
profile modifier (lower significance_quest, weight C-dimension plays more heavily).*

**F3.** What would constitute a genuinely perfect gift for them — not an object, but
an experience? Don't describe what we're going to design; describe your own best guess
at what they'd want most.
*(Free text)*

→ *Sponsor self-reveals: a sponsor with high participant insight gives a specific,
idiosyncratic answer. A low-insight sponsor gives a generic answer ("something relaxing,"
"an adventure") — tells us more about the sponsor's model than the participant. Both
are useful. The gap between this answer and what the arc will actually be is design
space.*

**F4.** Describe a time they were wrong about something — and how they handled it.
*(Free text — a specific instance, not a character summary)*

→ *Threat appraisal and learning style. The behavioral pattern around being wrong is
highly diagnostic: do they deny, withdraw, over-correct, investigate, minimize, or
integrate? This is also the question sponsors are most likely to skip or answer vaguely
— that avoidance is itself a signal (the sponsor may not have seen this in them, or may
be protecting their image of the participant). Specifically useful for: ordeal threshold
calibration, reckoning arc fit, how to design the false_breakthrough and
retroactive_recontextualization plays.*

---

## Pass 2: Participant Form

Only used when the participant knows something is coming (they've been told they're
receiving an experience, or the arc design requires an explicit enrollment). The cover
story must match the arc's opening frame — if the arc is a mystery, the enrollment is a
mystery-adjacent institution; if it's an initiation, it's an application or vetting.

### Framing options by arc type
- **Investigation arc:** "Preference calibration for a personalized investigation experience"
  — frame as taste-matching; questions about preferred ambiguity level, puzzle density,
  pace
- **Initiation arc:** "Application / vetting questionnaire" — frame as selection process;
  participant performs to be chosen; identity-weight questions ("what's your strongest
  quality?") feel natural
- **Conspiracy arc:** "Security clearance / compatibility assessment" — clinical, procedural;
  locus of control and authority questions feel appropriate
- **Test arc:** "Readiness assessment" — frame as self-knowledge check; introspective
  questions feel natural

### Universal participant questions (arc-type independent)

**P1.** When you encounter a story — in fiction, in a film, in real life — that you find
genuinely compelling, what makes it compelling?
```
[ ] The mystery — I want to know what happened and why
[ ] The character — I care about what happens to a specific person
[ ] The stakes — something important is genuinely at risk
[ ] The ideas — it makes me think differently about something real
[ ] The texture — I want to feel inside the world; sensation and atmosphere matter more than meaning
[ ] The surprise — I didn't see it coming and it changed my understanding
```
→ *arc type affinity: mystery = investigation; character = intimate/confederate-heavy plays;
stakes = ordeal/commitment; ideas = intellectual arc; texture = environmental/somatic plays;
surprise = reveal arc.
"Atmosphere" was replaced with "texture" — the previous wording attracted participants
performing aesthetic sophistication. "Texture / sensation / atmosphere matter more than
meaning" is more specific and harder to select without genuine somatic preference.*

**P2.** When you're receiving something important — a briefing, an explanation, a decision —
which of these sounds *least* like how you want it delivered?
```
[ ] The headline first, details only if I ask — I'll decide what I need to know
[ ] Full context before the point — I want to understand before I respond
[ ] Show me, let me arrive at it — don't explain what I haven't seen yet
[ ] Let me ask my own questions — I'll drive the conversation
```
→ *Elimination format. Avoidances are more reliable than affinities here — agency_demand
is something people know from friction, not just preference. The option they reject most
strongly is the delivery mode most likely to cause dropout. need_for_cognition: rejecting
"headline first" = high NFC (they want full context); rejecting "full context" = low NFC
or high reward_sensitivity (they want to get started). "Let me ask my own questions"
rejection = lower agency demand, comfortable being guided.*

**P3.** Think of someone you trust completely. How did you know you could trust them?
*(Free text — a specific person, not a general rule)*

→ *Behavioral anchor. "How do you usually know" invites a procedural rule; "how did you
know" with a specific person forces recall of actual trust-formation events. The process
they describe (time, consistency, a specific moment, a test) maps directly to how the
handler relationship should be built. Also gives language — their trust vocabulary is
often how they'll respond to handler contact.*

**P4.** Something you understood or saw coming before most people around you did.
*(Free text — 1–2 sentences)*

→ *Reframe from "been right" (defensive) to "saw coming" (perceptive). Same signal —
significance_quest + perceptive identity invite — without the threat-appraisal activation
that "right/wrong" framing produces. Reveals pattern-recognition self-concept; high signal
for investigation arc participants.*

**P5.** Name one experience — a film, book, game, real event — from the last few years
that genuinely affected you and has stayed with you.
*(Free text — one line: name it)*

Then: What made it stay?
```
[ ] It unsettled me — pushed me somewhere I didn't expect; the discomfort was the point
[ ] It filled me with wonder — the world got larger; I felt awed
[ ] It rewired how I think — I understood something differently afterward
[ ] It opened me emotionally — I felt connected, raw, moved
[ ] It activated me — something was at stake and I felt it
```
→ *Behavioral anchor before categorization. Naming a specific experience forces recall
of an actual instance, making the subsequent categorization more accurate and harder to
perform — you have to account for a real thing, not describe a preference in the abstract.
The operator can read the named experience independently as a signal (the specific film/book/
event chosen is often a cleaner signal than the category selected).
"Unsettled" = anxiety-tolerant; disorientation-register plays welcome; high N adaptive.
"Wonder" = sensory_seeking, aesthetic_response; atmospheric/spatial plays.
"Rewired" = need_for_cognition, +O; investigation arc.
"Opened" = intimacy, connection; ceremony and confederate plays.
"Activated" = reward_sensitivity; ordeal arc.
This is the primary signal for whether disorientation-register plays land or alienate.*

**P6.** Is there anything you'd want us to know before we begin — hard limits, contexts
to avoid, or anything that should not come near this?
*(Free text — optional but read carefully)*

→ *Participant-side safety input. Complements sponsor E2. Any participant-stated limit
overrides sponsor report absolutely. Also a compliance signal: participants who provide
detailed, specific limits are more engaged and self-aware; participants who say "nothing"
or skip this should be given more conservative early plays.*

**P7.** Of these descriptions, which sounds *least* like you?
```
[ ] Dependable — someone who follows through
[ ] Perceptive — someone who sees what others miss
[ ] Creative — someone who makes things that didn't exist
[ ] Influential — someone whose thinking or work matters
[ ] Good — someone of integrity and care
[ ] Interesting — someone with a specific and irreplaceable point of view
[ ] Brave — someone who does hard things
```
→ *Identity elimination. Same options as sponsor D4. Avoidances are more reliable than
affinities on identity questions. Cross-reference with D4 (sponsor's positive read) and
D4-elimination (sponsor's negative read). Three-way comparison:
  — Sponsor positive (D4) + Participant rejects same (P7) = participant doesn't see themselves
    this way, or actively disidentifies; arc identity offer needs adjustment
  — Sponsor negative (D4-elim) + Participant rejects same (P7) = confirmed blind spot or
    genuine disidentification — arc can use this as entry point
  — All three different = high ambiguity; weight arc behavioral evidence more heavily*

---

## Pass 3: Operator Inference

After passes 1 and 2, the operator maps signals to drivermap dimensions and runs
`query.py` to rank mechanism candidates.

### Dimension scoring sheet

| Dimension | Questions | High signal indicators |
|---|---|---|
| big_five_N | C1, C3, C8 | disruption lingers; unnerved by letter; research-before-committing |
| big_five_O | B1, C2, C3, D1 | intellectual/creative time use; excited by mystery; opens letter; moving moment is intellectual or novel |
| big_five_E | B1, B2, C6 | dense social world; energized by social; many active relationships |
| big_five_A | C5 | defer to authority; conflict-avoidant |
| big_five_C | C4, C7 | reads everything first; persists despite signals |
| need_for_cognition | C2, C4, D2 | nagged by anomalies; reads before starting; specific deep interests |
| need_for_closure | C2 | uncomfortable until resolved |
| curiosity_exploration | C2, C3, D2 | actively excited; opens immediately; investigative domains |
| sunk_cost_fallacy | C7 | persist/struggle to let go |
| significance_quest | D4, P7-inverse, F2 | strong positive identity claim; named long-held desire |
| attachment_styles | B2, C3, C6 | shows letter to someone first; few/deep relationships |
| obedience_authority | C5 | defer vs. push back |
| achievement_motivation | D1-story, D4, F2 | moving moment is accomplishment; dependable/influential identity |
| anxiety_vs_wonder | P5-named + P5-category | named experience + category selected; unsettled = anxiety-tolerant; wonder = sensory_seeking; activated = reward_sensitivity |
| ideology_target | E1 | specific change = arc has transformation target; vague = probe before design |
| identity_negative_space | D4-elim, D5, P7 | what sponsor rejects for participant; what participant disowns |
| threat_appraisal | F1, F4 | how they respond to surprise and to being wrong; agency in the story |

### Divergence checks (run after both passes complete)

| Divergence | Meaning |
|---|---|
| D4 positive (sponsor) vs. P7 rejects same | Blind spot or active disidentification — adjust arc identity offer |
| D4-elim (sponsor negative) + P7 rejects same | Confirmed disidentification — strong arc entry point |
| D1-story register vs. P5 category | Warm/intimate story but selects "unsettled" — may aspire to anxiety-tolerance they don't have |
| E1 (ideology) vague vs. F2 (long-held desire) specific | F2 often contains the real ideology; sponsor couldn't name it directly |
| B1/B2 (social world) vs. C6 (social energy) | Sparse social world + energized = socially hungry; rich social world + drained = obligation-heavy |

### The intake is a prior — arc as calibration

The intake profile is good enough to design the first three plays. After that, the arc is
the data collection.

Treat plays 1–3 as calibration beats: observe how the participant responds to the handler
letter (tone, timing, level of engagement), whether they comply with the first commission
(and how — eagerly, reluctantly, creatively), and how they process the first reveal or
anomaly. Each of these responses updates the profile. Before designing plays 4+, revise the
dimensional profile against behavioral evidence:

- Did they respond to the handler with curiosity or skepticism? (O, N, C5 update)
- Did they follow the first instruction exactly, adapt it, or ignore it? (agency_demand, C update)
- Did they share the experience with someone else immediately? (E, attachment update)
- Did they escalate engagement or disengage? (motivation, reward_sensitivity update)

The intake gives you a starting model. The participant's behavior in the arc is ground truth.

### Running the query

Once dimensions are scored (+/-), run:
```bash
cd ~/Documents/drivermap
python query.py --dim big_five_N:+ --dim big_five_O:+ --dim need_for_cognition:+ \
  --export json --top 15
```

The output ranks mechanisms by score for this participant profile. Cross-reference
against plays.md MECHANISMS field to find candidate plays. This is the bridge between
intake and arc design.

### Arc type selection heuristics

| Profile | Suggested arc type | Operator requirement |
|---|---|---|
| +O, +NFC, -N, perceptive identity | investigation | standard |
| +N, significance_quest, brave identity | ordeal/initiation | standard |
| -A (push back on authority), +O, conspiracy story | persecution/conspiracy | standard |
| +A, deep relationships, connection moves them | initiation with strong confederate | standard |
| +C, dependable identity, accomplishment moves them | test arc | standard |
| persecution/conspiracy + P5=rewired | persecution/conspiracy | **elevated** — retroactive_recontextualization must be total and immediate; any delay between ordeal state and reveal produces harm not transformation. Run a lighter arc or ensure the reveal has no contingencies. |
| persecution/conspiracy + P5=unsettled | persecution/conspiracy | standard — disorientation register is the mechanism, not a risk |

### Divergence → transformation target

When sponsor's F2 (what the participant wants but hasn't moved toward) and participant's P7 (identity elimination) converge on the same gap, the arc has a specific transformation target that the participant has coded as weakness. Flag this pattern explicitly: **the arc can point at the thing they've rejected, but cannot approach it directly.** The arc must work through the participant's dominant identity frame (their P7 positive claims) to reach the thing they've walled off.

Example: sponsor says "he wants to be known" (F2); participant rejects "interesting" (P7) and claims "influential/dependable." The arc must engage through competence and consequence — the dominant frame — and let the longing surface through the arc rather than being named up front. Naming it would trigger identity_protective_cognition.

### Red flags — arcs to avoid

| Signal | Avoid |
|---|---|
| +N, C8 = research-before-committing | high detection accumulation; surveillance-heavy plays early |
| C3 = unnerved by letter | cold-contact plays without priming; slow the permission chain |
| C5 = defer to authority | plays that require participant to actively defy instruction |
| B2 = few/deep relationships | confederate-heavy arcs with unfamiliar actors |
| E2 = live major stressor | any play that mirrors or compounds the stressor content |
| P5 = wonder/emotion dominant | disorientation-register plays without containment (the_witness, manufactured_crisis_reveal) |
| E1 = vague or atmospheric | do not begin arc design — probe for specific transformation target first |
