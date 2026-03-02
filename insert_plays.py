#!/usr/bin/env python3
"""Insert new play sections into plays.md before the end marker."""
import sys
import re

SECTIONS = {}

SECTIONS['con_artistry'] = '''
## CONFIDENCE & CON ARTISTRY

Plays drawn from the confidence artistry tradition — the structural mechanics of the short and long con, adapted for consented immersive experience design. Sources: David Maurer, *The Big Con* (1940); Erving Goffman, *On Cooling the Mark Out* (1952); Ian Rowland, *The Full Facts Book of Cold Reading*. The mechanisms are borrowed; the harm is prohibited by design — these plays operate within full participant consent and mandatory debrief.

---

### The Convincer Win
`id:convincer_win` · `COST:low` · `AUTONOMY:agent` · `LEAD_TIME:24–48h` · `INTENSITY:low`

**MECHANISMS:** commitment_consistency · loss_aversion · sunk_cost · trust_formation · pattern_completion
**ARC_FIT:** pre · open · build
**PARTICIPANT_NOTES:** Works on nearly all profiles. Contraindicated for participants with gambling triggers — the escalation logic mirrors gambling mechanics exactly. Strongest on high conscientiousness / low neuroticism participants who trust their own judgment.
**STACKS_WITH:** convincer_loss · hurry_up · spanish_prisoner · shill_validation · convincer_document
**SOMATIC:** induces: mild euphoria, forward lean, appetite for more · requires: baseline curiosity and openness
**IDENTITY_INVITE:** The person whose instincts are right. The one who recognized a real opportunity.
**REINFORCE:** Small wins referenced later ("you were right about X") compound the original credibility deposit; agent logs the win and returns to it as evidence during later doubt.
**PERMISSION:** grants deeper buy-in for subsequent asks · standalone; functions as trust-builder, no prior arc needed

The foundational short-con mechanic: give the participant a small, real win early, before the stakes mean anything. In three-card monte the shill wins visibly in front of the crowd; in the big con's "convincer," the mark is allowed to win a modest sum at the wire or the rag before being steered toward the larger bet. Maurer (*The Big Con*, 1940) describes this as the essential difference between a short con and a long one — the long con invests in establishing genuine credibility before asking for anything. The win must feel earned, not given. It must cost the participant something small (attention, a decision, a small act of faith) so the return feels like confirmation of their judgment.

Deploy in the first 24–72 hours. The participant receives a small task — decode a minor cipher, show up at a location, follow an instruction — and finds exactly what they were told they'd find. The win should be slightly better than expected: the location has something extra the instructions didn't mention, the envelope contains a detail that feels personally targeted. This surplus signals that the system behind the experience is richer than what's visible. Maurer calls this "convincing the convincer" — the mark doesn't just win, they glimpse the machinery of a larger operation and decide it's legitimate.

Timing is critical. The win must land before the participant has had time to develop a skeptical framework. If they've already decided it's probably a game, the win reads as game mechanics. It must land while the experience is still ontologically undecided.

**FAILURE MODES:**
- Win lands too easily and reads as scripted — add friction, delay, near-miss before resolution
- Participant shares win publicly and others' skepticism contaminates their belief
- Win is too large too early and triggers suspicion about what's being set up

---

### The Convincer Loss
`id:convincer_loss` · `COST:low` · `AUTONOMY:agent` · `LEAD_TIME:24h` · `INTENSITY:medium`

**MECHANISMS:** loss_aversion · sunk_cost · commitment_consistency · reactance · urgency
**ARC_FIT:** build · escalate
**PARTICIPANT_NOTES:** Requires a participant who has already experienced the convincer win — the loss only functions against a baseline of established credibility. Contraindicated for participants with anxiety disorders or trauma around failure. Strong on competitive profiles.
**STACKS_WITH:** convincer_win · hurry_up · spanish_prisoner · pigeon_drop · convincer_document
**SOMATIC:** induces: mild distress, forward lean, slight anxiety · requires: prior trust deposit sufficient to make the loss meaningful
**IDENTITY_INVITE:** The person who doesn't quit when it gets hard. The one who sees it through.
**REINFORCE:** Agent references the loss later as the moment that proved the participant's character — "you didn't walk away when you could have."
**PERMISSION:** requires prior convincer_win or equivalent trust deposit · sequenced; never standalone

The mirror of the convincer win and equally essential to the long con's architecture. In the big con's "blow-off" preparation, after the mark has won, a controlled setback is introduced — not a total loss, but a stumble, a complication that requires re-engagement. Maurer notes that the loss must be just large enough to sting without triggering the participant's exit instinct. The loss says: this is real (real things fail sometimes), you have skin in the game now, walking away means you lose what you've already invested.

The psychological mechanism is dual: loss aversion (Kahneman) makes the loss feel approximately twice as significant as an equivalent gain, and sunk cost logic makes prior investment feel like a reason to continue rather than cut losses. The convincer loss must feel authentic — a plausible mundane explanation (the contact was delayed, the package was intercepted) that the participant can choose to believe or can read as escalation.

Variant: the near-loss, where the participant narrowly avoids failure through their own action. This combines loss aversion with agency — the participant saves something, which deepens their sense of personal investment in the outcome.

**FAILURE MODES:**
- Loss is too large and triggers exit — calibrate to 20–30% of perceived investment
- Participant correctly identifies the loss as manufactured and loses trust entirely
- Loss produces paralysis rather than forward lean — follow immediately with a path forward

---

### The Convincer Plant
`id:convincer_plant` · `COST:low` · `AUTONOMY:human_assist` · `LEAD_TIME:48–72h` · `INTENSITY:medium`

**MECHANISMS:** epistemic_uncertainty · pattern_completion · significance_quest · trust_formation · curiosity_exploration
**ARC_FIT:** pre · open · build
**PARTICIPANT_NOTES:** Strongest for high need-for-cognition participants who enjoy finding things. Contraindicated for participants with paranoia risk. Requires operational security: the plant must never be traceable to the operators.
**STACKS_WITH:** convincer_win · salting · convincer_document · shill_validation · osint_personalization
**SOMATIC:** induces: discovery high, slight tremor of significance · requires: open, curious baseline
**IDENTITY_INVITE:** The one who finds what others miss. The investigator whose eyes are trained to see.
**REINFORCE:** Later communications reference what they found as if the operators knew they'd find it — confirming the participant's discovery was anticipated.
**PERMISSION:** grants participant feels they independently verified the fiction · standalone

The art of arranging for the participant to "independently discover" fabricated evidence. Named after salting a mine — placing gold ore in a played-out mine for an investor to "discover" during their own assay. Goffman (*On Cooling the Mark Out*, 1952) notes that the mark's belief is most robust when it feels self-generated. The plant must be discoverable through a plausible route the participant would actually take — Googling a name, visiting a location, browsing a space. The route to discovery should feel like their own curiosity, not a guided path.

The plant should contain something the participant wasn't told to look for: a detail that exceeds what they were given, implying the world is larger than what they've been shown. Operational security is everything — the plant cannot be traceable through metadata, writing style, or logical gaps. It must withstand moderate scrutiny: a skeptical participant who searches around it should find corroborating ambient noise, not a clean void.

Variant: the cross-platform plant, where evidence discovered in one channel confirms something hinted at in another. The cross-platform confirmation mimics how real investigative discoveries feel.

**FAILURE MODES:**
- Plant found before the participant is ready to receive it — frame collapses with no context
- Metadata or authorship discoverable — destroys credibility of entire arc
- Participant doesn't find it at all — build in a secondary delivery mechanism

---

### Salting
`id:salting` · `COST:mid` · `AUTONOMY:human_managed` · `LEAD_TIME:1–2 weeks` · `INTENSITY:medium`

**MECHANISMS:** ambient_presence · significance_quest · pattern_completion · epistemic_uncertainty · paranoia_escalation
**ARC_FIT:** pre · open · build
**PARTICIPANT_NOTES:** Requires lead time and access to participant's environment or digital channels. Strongest for participants who pay attention to their environment and notice anomalies. Contraindicated for highly anxious participants — ambient seeding can tip into distressing hypervigilance.
**STACKS_WITH:** convincer_plant · convincer_location · osint_personalization · shill_validation · retroactive_meaning
**SOMATIC:** induces: low-grade alertness, the feeling of being inside something · requires: perceptual openness, attention to surroundings
**IDENTITY_INVITE:** The one who notices. The person the world is speaking to.
**REINFORCE:** Operator periodically surfaces new salted elements, keeping the participant in ambient attention; the world stays meaningful throughout the arc.
**PERMISSION:** requires intake data on participant's routes, habits, digital channels · sequenced; best as pre-arc preparation before first contact

Named directly after the mining fraud tradition: placing valuable ore in a depleted mine so an independent assayer would "discover" it and certify the mine as productive. The investor arranged the assay himself, confident he was doing due diligence — the self-generated discovery is the most durable belief. In experience design, salting means pre-seeding the participant's environment with meaningful anomalies before the arc officially begins: a social media account just plausible enough, a search result that surfaces at the right moment, a flyer in a neighborhood they frequent, graffiti on a regular route, an object placed where they'll find it.

The key is distribution across unrelated channels so the participant experiences corroboration from multiple independent sources. When the arc begins and they receive their first official contact, the salted elements retroactively cohere — the world was always speaking to them; they just didn't have the key. Salt conservatively: two or three well-placed anomalies are more powerful than a dozen.

**FAILURE MODES:**
- Over-seeding produces anxiety rather than enchantment
- Participant attributes salted elements to coincidence
- A salted element is explained away by someone in the participant's life

---

### The Shill Validation
`id:shill_validation` · `COST:low` · `AUTONOMY:confederate` · `LEAD_TIME:24–48h` · `INTENSITY:medium`

**MECHANISMS:** social_proof · trust_formation · epistemic_uncertainty · legitimacy · emotional_contagion
**ARC_FIT:** build · escalate
**PARTICIPANT_NOTES:** Requires a confederate the participant doesn't know is operative — either a briefed person or a convincing constructed identity. Strongest for socially oriented participants who weight peer experience heavily. Contraindicated for participants who would feel violated by learning a "stranger" was staged.
**STACKS_WITH:** convincer_plant · convincer_crowd · roper · convincer_win · false_ally
**SOMATIC:** induces: social warmth, reduced vigilance, validation · requires: slight doubt present that the shill resolves
**IDENTITY_INVITE:** The one who isn't alone in this. Part of a larger, select group who've seen the same thing.
**REINFORCE:** Shill can be reactivated later to provide updated "testimony" as the arc escalates.
**PERMISSION:** grants social proof for the experience's legitimacy · standalone; effective at any arc point where participant doubt is present

The shill is one of the oldest tools in con artistry. In three-card monte the shill wins visibly, recruiting bystanders into belief by demonstrating the game is winnable. Maurer devotes significant space to the social architecture of the big con's cast: the mark is always outnumbered by apparently independent people who all confirm the same reality. In experience design, the shill appears as an unrelated third party who has "had the same experience" or "knows something about this." The shill's account should be imperfect: slightly different details, a different interpretation, uncertainty about what it meant. Perfect corroboration reads as scripted.

Deploy within 24 hours of a convincer loss or a moment where the participant has expressed skepticism — the shill is most effective when deployed at the edge of disengagement. For digital shills, construct plausible account histories that predate the arc. For human shills, brief them only on what they need to know — partial information is more convincing.

**FAILURE MODES:**
- Participant knows or investigates the shill and discovers the connection to operators
- Shill's testimony is too perfectly calibrated and reads as scripted
- Shill deployed too early, before sufficient doubt exists to resolve

---

### The Roper
`id:roper` · `COST:low` · `AUTONOMY:confederate` · `LEAD_TIME:48–72h` · `INTENSITY:medium`

**MECHANISMS:** trust_formation · parasocial_attachment · legitimacy · social_proof · reciprocity
**ARC_FIT:** pre · open
**PARTICIPANT_NOTES:** The most demanding confederate role — requires genuine social skill. Strongest for socially trusting, relationship-oriented participants. Contraindicated for participants who would feel deeply violated by learning a trusted relationship was staged. Requires post-arc disclosure plan.
**STACKS_WITH:** shill_validation · spanish_prisoner · convincer_win · false_ally · briefed_confederate
**SOMATIC:** induces: social warmth, trust, openness · requires: social receptivity, openness to connection
**IDENTITY_INVITE:** The one who was chosen by someone whose judgment they trust. Already inside a trusted relationship before the arc begins.
**REINFORCE:** Roper continues as the participant's "friendly interpreter" throughout the arc, softening hard moments and keeping them engaged.
**PERMISSION:** grants access to participant's trust before official arc begins · must precede the arc's main structure

Maurer distinguishes the roper from other operatives with unusual care: the roper finds the mark and steers them toward the scenario without ever seeming to be part of it. They appear to be the mark's friend, ally, or fellow victim — someone with no obvious stake in what follows. The roper's fundamental difference from a director (someone the participant knows is running their experience) is their invisibility. This makes the roper the most ethically charged role in experience design — the participant's primary trust relationship is being leveraged for narrative purposes. The roper must be someone the participant will not feel betrayed by when disclosed — either an existing friend briefed and comfortable with disclosure, or a character who can be disclosed as fictional in a way that feels celebratory.

In experience design, the roper appears before the official arc begins and seems to be experiencing something adjacent — curious about the same anomaly, troubled by the same mystery. When the arc begins, the roper says: "This might be connected to what we've been noticing." The roper/shill distinction: the shill confirms after the fact; the roper recruits before, providing relationship context that makes the participant ready to engage.

**FAILURE MODES:**
- Roper discovered to be affiliated with operators before arc completion — collapse of trust in everything
- Roper becomes genuinely emotionally entangled and can't exit cleanly
- Participant becomes dependent on roper character — disclosure becomes genuinely harmful

---

### The Convincer Document
`id:convincer_document` · `COST:low` · `AUTONOMY:agent` · `LEAD_TIME:24h` · `INTENSITY:medium`

**MECHANISMS:** legitimacy · obedience_authority · trust_formation · epistemic_uncertainty · commitment_consistency
**ARC_FIT:** build · escalate · threshold
**PARTICIPANT_NOTES:** Particularly effective for participants with professional relationships with formal documents — legal, medical, financial. Contraindicated for participants who would immediately spot forgeries or implausibilities in their own professional domain. Requires careful verisimilitude — a bad fake document is worse than none.
**STACKS_WITH:** convincer_plant · convincer_location · spanish_prisoner · hurry_up · pigeon_drop
**SOMATIC:** induces: seriousness, weight, sobriety — the document makes it real · requires: openness to institutional legitimacy
**IDENTITY_INVITE:** The one who has been officially designated. Named. Documented. Part of something with a paper trail.
**REINFORCE:** Participant may carry, photograph, or reference the document; each re-encounter reinforces the experience's reality.
**PERMISSION:** grants institutional weight to fictional premise · standalone; can anchor any arc point

The convincer document draws on the rich tradition of con artistry's paper infrastructure. In the Spanish prisoner con, letters of legal gravity purported to be from imprisoned nobles; in the big con's store, participants encountered elaborate paper systems — official-looking brokerage documents, authentic-seeming correspondence. Maurer notes that documents serve a specific psychological function: they exist outside the conversation, in the participant's hands, and they outlast the operative. The document's power comes from its materiality and its implication of a larger system. A letter implies an organization that wrote it, a process by which it was sent, a file in which the participant's name is recorded.

Variant: the document with a flaw. A minor inconsistency — a date slightly off, an unfamiliar term, a reference to something the participant doesn't yet know — signals that the document is not manufactured for them but is a real document from a real process that happens to include them. The flaw is the detail that establishes authenticity.

**FAILURE MODES:**
- Document is obviously forged — fonts, formatting, or institutional details don't hold up to scrutiny
- Participant attempts to contact the institution named and gets no corroboration
- Document is too elaborate and reads as theatrical prop rather than authentic bureaucratic artifact

---

### The Convincer Location
`id:convincer_location` · `COST:low` · `AUTONOMY:human_assist` · `LEAD_TIME:48–72h` · `INTENSITY:medium`

**MECHANISMS:** legitimacy · trust_formation · epistemic_uncertainty · ambient_presence · significance_quest
**ARC_FIT:** build · escalate
**PARTICIPANT_NOTES:** Requires a real location — actual business, building, or public space — that the participant can visit and find to be genuinely what it claims. Strongest for kinesthetic participants who trust physical verification. Contraindicated for participants who can't travel to the location.
**STACKS_WITH:** convincer_plant · convincer_document · salting · roper · convincer_win
**SOMATIC:** induces: embodied verification, grounding, the weight of physical reality · requires: mobility, willingness to travel
**IDENTITY_INVITE:** The one who checked. Who didn't just take anyone's word for it. Who went and saw.
**REINFORCE:** The location becomes a meaningful site in the participant's mental map — they may return, reference it, dream about it.
**PERMISSION:** grants physical verification of fictional premise · standalone; can anchor any arc point that risks ontological collapse

The convincer location is the physical world's answer to document legitimacy. In the big con's most elaborate versions — the "store," the fake brokerage set up specifically for the mark — the physical space was the most convincing element. The participant walked into what appeared to be a real business. Maurer spends considerable time describing the store's verisimilitude: the phone calls, the ticker tape, the dozens of extras, the smell of the place. The body knows things the rational mind overrides.

In experience design, this does not require constructing a fake business — it requires selecting real locations with the right qualities: an actual archive, library, or records room with a connection to the fiction's backstory; an actual business whose owner has been briefed and can receive a caller; an actual physical location where something has been placed. The participant's body registers independent verification. Physical reality has confirmed the fiction.

Variant: the location the participant already knows. Rather than directing the participant to an unfamiliar space, the fiction infiltrates a space they already know and trust — their regular coffee shop, their commute route. Something in a familiar location changes. The familiar space becoming strange is one of the most potent immersive effects available.

**FAILURE MODES:**
- Location is closed, changed, or unavailable when participant arrives
- Staff are confused or contradict the fiction
- Participant brings someone along who provides a skeptical framing before the space can land

---

### The Convincer Crowd
`id:convincer_crowd` · `COST:mid` · `AUTONOMY:confederate` · `LEAD_TIME:48–72h` · `INTENSITY:medium`

**MECHANISMS:** social_proof · legitimacy · emotional_contagion · trust_formation · epistemic_uncertainty
**ARC_FIT:** build · escalate · threshold
**PARTICIPANT_NOTES:** Requires multiple confederates or convincing constructed digital presence of multiple people. Strongest for socially embedded participants who weight community consensus heavily. Contraindicated for contrarian participants who weight peer opinion negatively.
**STACKS_WITH:** shill_validation · roper · convincer_location · convincer_plant · salting
**SOMATIC:** induces: social warmth, belonging, reduced individual vigilance · requires: social orientation, responsiveness to community signals
**IDENTITY_INVITE:** Member of a select group. Not alone. Part of a larger, real movement.
**REINFORCE:** The crowd can continue generating ambient social proof as the arc progresses — ongoing forum posts, new "members" appearing.
**PERMISSION:** grants multiplied social proof · sequenced; most effective after initial convincer_win establishes baseline credibility

In the big con's store, dozens of extras performed a convincing financial operation so the mark could see themselves as one of many sophisticated participants. Goffman emphasizes the role of the social surround: belief is primarily social, and a coherent, consistent social environment is harder to resist than any individual argument. In experience design, the convincer crowd is an apparently organic community — a Reddit thread, a Discord server, a private forum — each with plausible histories, varied voices, organic-seeming conflicts and uncertainties. The crowd should not be uniformly credulous; it should contain skeptics, believers, people who dropped out. Perfect unanimity reads as artificial.

Variant: the crowd the participant can contact. Real email addresses or forum accounts that can respond to direct messages, staffed by an agent or human assistant. The ability to have a real conversation with a "fellow participant" is the strongest version of social proof.

**FAILURE MODES:**
- Participant investigates deeply and discovers constructed nature through metadata or account age patterns
- Crowd's voice is too uniform — write different "community members" with distinct personalities and disagreements
- Crowd becomes self-sustaining in ways the operators can't monitor

---

### The Hurry-Up
`id:hurry_up` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:high`

**MECHANISMS:** urgency · loss_aversion · scarcity · commitment_consistency · obedience_authority
**ARC_FIT:** escalate · threshold · climax
**PARTICIPANT_NOTES:** Universally effective but risks participant distress if overdone. Must be used with genuine windows — fictional urgency with no consequence destroys future credibility. Contraindicated for high-anxiety participants unless the urgency is designed to resolve quickly.
**STACKS_WITH:** convincer_loss · spanish_prisoner · pigeon_drop · convincer_document · blow_off
**SOMATIC:** induces: acute stress, narrowed attention, cortisol response · requires: prior investment sufficient to make the deadline meaningful
**IDENTITY_INVITE:** The one who acts. Who doesn't hesitate when it matters. Who shows up.
**REINFORCE:** Post-urgency, reference the moment as evidence of who the participant is: "you came through."
**PERMISSION:** bypasses analytical pause · sequenced; requires prior trust deposit — urgency without credibility is just pressure

Maurer documents the hurry-up explicitly: "Don't let him think, don't let him talk to a lawyer, don't let him call his wife." The time pressure is artificial but its function is psychological — it activates system-1 decision-making, bypasses deliberation, and forces commitment before counter-arguments can form. Always deployed at a moment of prior investment, when the participant has something to protect.

In experience design, the hurry-up is a genuine-feeling deadline: a response window that closes, a contact window that expires, a location only accessible for a limited time. The deadline must have apparent consequences — and ideally real ones. A fake urgency window later discovered to be fake is one of the strongest trust-destroyers available. Design hurry-ups with actual stakes: if the participant doesn't respond, the arc genuinely forks, or a planned event doesn't happen. Deploy no more than two per arc, spaced significantly apart. The first establishes that deadlines are real. The second carries all its credibility.

**FAILURE MODES:**
- Deadline passes with no consequence — destroys credibility of all future urgency
- Urgency triggers genuine anxiety that disrupts participant's actual life
- Participant is unavailable during the urgency window

---

### The Spanish Prisoner
`id:spanish_prisoner` · `COST:low` · `AUTONOMY:agent` · `LEAD_TIME:24h` · `INTENSITY:high`

**MECHANISMS:** reciprocity · guilt · significance_quest · parasocial_attachment · commitment_consistency · loss_aversion
**ARC_FIT:** build · escalate · threshold
**PARTICIPANT_NOTES:** One of the most powerful emotional levers — someone needs the participant's help. Strongest for high-agreeableness participants with caretaking orientations. Contraindicated for participants with rescue-fantasy patterns that the experience might reinforce unhealthily. Requires careful calibration — the prisoner cannot be so compelling that the participant forms a genuine distress bond.
**STACKS_WITH:** roper · convincer_document · hurry_up · pigeon_drop · blow_off
**SOMATIC:** induces: protective urgency, moral weight, heightened presence · requires: empathy, established narrative investment
**IDENTITY_INVITE:** The one who can help. The one who matters to someone in trouble. The one who won't abandon.
**REINFORCE:** Prisoner's gratitude and updates extend the participant's sense of meaningful impact beyond the arc's peak moments.
**PERMISSION:** grants moral weight and urgency to participant action · sequenced; most effective after sufficient arc investment

One of the oldest documented frauds — appearing in European records by the late 16th century. The structure: a letter from a prisoner of high status who cannot reveal their identity but desperately needs help extracting themselves. The fraud's genius is its emotional structure: the mark isn't greedy, they're helping someone. The moral self-image of rescuer makes commitment more durable than mere avarice.

In experience design, the Spanish prisoner is a person who appears within the narrative in distress, who needs the participant's assistance, and who has something meaningful to offer in return — not money, but information, access, or narrative resolution. The prisoner's communications should be imperfect: slightly panicked, containing plausible gaps. The participant should feel they are one of few people trusted with the prisoner's situation. The prisoner creates forward motion through moral commitment: abandoning them feels like betrayal, which is structurally more durable than simple curiosity.

Variant: the prisoner who is a version of the participant — someone who went through what the participant is now experiencing and ended up in trouble. This creates identification and cautionary urgency.

**FAILURE MODES:**
- Participant becomes genuinely distressed about the prisoner's wellbeing and attempts real-world intervention
- Prisoner persona is inconsistent and participant stops believing they're talking to a real person
- Participant confides in someone outside the arc who correctly identifies the structure

---

### Pigeon Drop
`id:pigeon_drop` · `COST:low` · `AUTONOMY:confederate` · `LEAD_TIME:24–48h` · `INTENSITY:high`

**MECHANISMS:** reciprocity · sunk_cost · commitment_consistency · loss_aversion · trust_exploitation
**ARC_FIT:** escalate · threshold
**PARTICIPANT_NOTES:** Requires the participant to hold, carry, or be custodian of something real. This is the play that most directly engages the body. Contraindicated for participants with anxiety around responsibility or loss. Requires careful design of what the "pigeon" (held item) actually is.
**STACKS_WITH:** convincer_document · hurry_up · spanish_prisoner · convincer_win · blow_off
**SOMATIC:** induces: heightened proprioception, responsibility, embodied stake · requires: willingness to accept custodianship
**IDENTITY_INVITE:** The trusted one. The keeper. The one who can hold something important without being told why.
**REINFORCE:** The held object becomes a physical anchor for the participant's investment — they carry it, feel its weight, return to it.
**PERMISSION:** grants maximum embodied investment in the fiction's stakes · sequenced; requires established trust before participant will accept custodianship

The pigeon drop's essential structure: two strangers find something valuable and propose to split it, but one must put up "good faith" collateral while waiting. The mark's investment makes them a participant in the scheme, not merely its victim. In experience design, the pigeon drop is restructured as custodianship: the participant is asked to hold something real — an envelope they're told not to open, a key, a document, a piece of information — for reasons that feel urgent and legitimate. The held item implies a larger system: someone trusted them with it, therefore something matters, therefore they are inside something real.

The held item should reward the participant's curiosity while also rewarding restraint if they don't look. An envelope that says "open only if" creates ongoing tension. A key that fits a lock they haven't found yet creates forward momentum. The participant's role as custodian flatters them and binds them through commitment consistency — they have accepted responsibility.

**FAILURE MODES:**
- Participant opens the item before they're supposed to — have a plan for this contingency
- Participant loses or damages the item and feels genuine guilt — design items that can survive this
- Participant feels custodianship is a burden rather than a privilege — calibrate the item's weight carefully

---

### The Blow-Off
`id:blow_off` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:low`

**MECHANISMS:** need_for_closure · relief · epistemic_uncertainty · commitment_consistency · trust_formation
**ARC_FIT:** denouement · any
**PARTICIPANT_NOTES:** Required for any arc. Without a blow-off strategy, arc completion risks confusion, disappointment, or the participant feeling abandoned. The most technically undervalued play in experience design — operators spend effort on escalation and neglect exit.
**STACKS_WITH:** cooling_the_mark · convincer_win · spanish_prisoner · hurry_up · convincer_document
**SOMATIC:** induces: resolution, exhale, safe return · requires: sufficient prior intensity to make the resolution meaningful
**IDENTITY_INVITE:** The one who completed something. Who saw it through. Who got out.
**REINFORCE:** The blow-off's framing of the experience is what the participant carries forward — invest heavily here; it shapes retrospective meaning entirely.
**PERMISSION:** grants clean exit from fiction · standalone; can close any open thread at any arc point

The blow-off is the con's exit mechanism — getting the mark away from the scene without suspicion or anger. Maurer documents the blow-off as one of the most carefully planned elements of any big con. In experience design, the blow-off is the graceful, emotionally complete exit from the arc: a meaning, a revelation, a resolution that makes the participant feel the story has ended on their own terms.

Blow-off architectures: the revelation (mystery solved); the graduation (participant has passed a test and is acknowledged); the gift (something marks the completion); the callback (an early element returns transformed); the silence (communications cease, leaving the participant with their experience — itself a kind of completion). Each produces different aftermath feelings. The blow-off requires the same craft as the arc's opening.

**FAILURE MODES:**
- Blow-off is absent — participant generates their own, possibly distressing, conclusions
- Blow-off is too abrupt — participant feels dropped, not resolved
- Blow-off is too explicit and sentimental — participant feels managed rather than moved

---

### Cooling the Mark
`id:cooling_the_mark` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:low`

**MECHANISMS:** need_for_closure · relief · guilt · shame · identity_threat · emotional_deepening
**ARC_FIT:** denouement
**PARTICIPANT_NOTES:** Required whenever the arc involves a revelation that the experience was orchestrated. Goffman identifies this as the moment of maximum vulnerability — the participant must be helped to reframe their experience as meaningful rather than humiliating. Contraindicated nowhere — always necessary, vary only in degree.
**STACKS_WITH:** blow_off · convincer_win · roper · shill_validation · convincer_crowd
**SOMATIC:** induces: warmth, reintegration, safe return to ordinary reality · requires: willingness to be cared for
**IDENTITY_INVITE:** The one who was chosen for an experience rare enough to require this much craft. Not a victim — a subject.
**REINFORCE:** Post-arc follow-up communications reinforce the reframe: what the participant felt was real; who they were during it was real.
**PERMISSION:** grants post-fiction emotional safety · sequenced; always after revelation, never before

Goffman's 1952 paper "On Cooling the Mark Out" is the foundational analysis. His observation: in the aftermath of a con, the mark's wound is not primarily financial but identity-based — they have been shown to be the kind of person who can be fooled. The cooler's job is to help the mark adjust without anger or public complaint, by reframing the experience: you weren't a victim of your own credulity, you were a victim of extraordinary skill. Goffman extends the observation: everywhere that social roles collapse, a cooling process is necessary.

In experience design, cooling the mark is the art of helping the participant integrate the revelation that their experience was orchestrated without feeling fooled or used. The key reframe: what they felt was real; who they became during the arc was real; the craft that went into it was an act of care, not exploitation. The participant was not the victim of a con — they were the subject of an art form that required their genuine response to function. The cooler's voice should be warm, specific, and unhurried. Over-explanation reads as defensive; it implies the operators know they did something that requires justification.

**FAILURE MODES:**
- Cooling arrives too fast after revelation — participant needs time to feel the impact before the reframe lands
- Cooling is generic — participant feels they're receiving a form letter, not being seen
- Cooling over-explains the mechanisms and makes the participant feel more foolish for having been taken in

---

### The Inside Man / Outside Man
`id:inside_outside` · `COST:mid` · `AUTONOMY:confederate` · `LEAD_TIME:72h` · `INTENSITY:high`

**MECHANISMS:** trust_formation · legitimacy · social_proof · epistemic_uncertainty · obedience_authority · disorientation
**ARC_FIT:** build · escalate · threshold
**PARTICIPANT_NOTES:** Requires two coordinated operatives playing opposed roles — one inside the participant's apparent reality, one outside and above it. Extremely disorienting when well-executed. Contraindicated for participants with dissociative tendencies. Requires careful coordination to avoid the operatives contradicting each other.
**STACKS_WITH:** roper · shill_validation · convincer_document · hurry_up · spanish_prisoner
**SOMATIC:** induces: productive confusion, doubled reality, the feeling of being positioned between two worlds · requires: tolerance for uncertainty, narrative investment
**IDENTITY_INVITE:** The one who can see both sides. The pivot point between two systems.
**REINFORCE:** After the operative structure is revealed or resolved, participant's sense of having been at the center of a complex operation deepens the significance of their role.
**PERMISSION:** grants maximum narrative complexity and produced reality · sequenced; requires established trust with inside man before outside man appears

The inside man / outside man is the structural heartbeat of the big con. Maurer describes the division of labor: the inside man runs the store, maintains the fiction's infrastructure, never breaks character; the outside man — the roper — manages the mark's emotional relationship throughout. The mark experiences these two people as occupying different worlds, but both are operative. Their coordination is what produces the experience of being inside a coherent, multidimensional reality.

In experience design, the inside operative has institutional credibility and slight formality; the outside operative has personal warmth and apparent fallibility. When they apparently disagree — when the outside man says "I'm not sure you should trust them" about the inside man — the participant's position as arbiter deepens their investment and sense of agency. Coordination is the technical challenge: both operatives must receive the same updates about the participant's current state in real time.

**FAILURE MODES:**
- Operatives receive different information and contradict each other in ways that expose the structure
- Participant forms an exclusive bond with one operative and refuses engagement with the other
- Participant confides in the outside man about doubts regarding the inside man's reality — need a protocol for this

---

### The Wire Convincer
`id:wire_convincer` · `COST:mid` · `AUTONOMY:human_managed` · `LEAD_TIME:72h` · `INTENSITY:high`

**MECHANISMS:** sunk_cost · commitment_consistency · loss_aversion · urgency · pattern_completion · significance_quest
**ARC_FIT:** escalate · threshold
**PARTICIPANT_NOTES:** A late-arc play — presupposes significant investment and uses the promise of resolution to extend that investment. Contraindicated for participants who are fatigued — the escalating ask only works with active engagement.
**STACKS_WITH:** convincer_loss · hurry_up · pigeon_drop · blow_off · spanish_prisoner
**SOMATIC:** induces: near-resolution tension, forward lean, held breath · requires: substantial prior investment, emotional hunger for resolution
**IDENTITY_INVITE:** The one who is almost there. Who has come too far to stop now.
**REINFORCE:** After the wire plays out, reference how close the participant came as evidence of the journey's significance.
**PERMISSION:** requires substantial arc history · sequenced; only after convincer_loss or equivalent setback

Named after the big con's climactic beat: "the wire" was a scheme in which the mark was convinced they had inside knowledge of delayed race results. The convincer win at the wire was the moment the scheme seemed to be working perfectly — the bet placed, the results about to come in — before the blow-up requiring one more commitment. The mark's near-certainty of winning was the mechanism for extracting the final, largest ask.

In experience design, the wire convincer is the moment where all the arc's threads seem about to resolve. The participant can see the answer; they're one action away from understanding everything. This moment of apparent near-resolution is used to request the arc's deepest commitment: the most significant action, the riskiest trust, the greatest vulnerability. The request must be commensurate with what has come before — a logical extension of existing investment, not a new escalation.

**FAILURE MODES:**
- Near-resolution extends too long and participant's anticipation curdles into frustration
- The ask at the wire is out of proportion to the investment — reads as exploitation
- Resolution is delayed after participant complies — must deliver or acknowledge the delay with reason

---

### The Mark's Pride
`id:marks_pride` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:medium`

**MECHANISMS:** identity_threat · reactance · commitment_consistency · shame · sunk_cost
**ARC_FIT:** build · escalate
**PARTICIPANT_NOTES:** Uses the participant's own self-image against hesitation. Must target a specific identity the participant holds and values. Contraindicated for participants with shame-sensitive profiles or perfectionism. Requires intake data on participant's self-concept.
**STACKS_WITH:** convincer_loss · hurry_up · spanish_prisoner · wire_convincer · inside_outside
**SOMATIC:** induces: mild defensive arousal, forward lean, the heat of pride · requires: a specific self-concept the participant is attached to
**IDENTITY_INVITE:** The one who doesn't back down. Who shows up even when it's hard. Proof of who they say they are.
**REINFORCE:** After the participant acts against their resistance, name it: "you kept going when you didn't have to."
**PERMISSION:** grants breakthrough of hesitation-based exit · sequenced; challenge before trust reads as hostile

The mark's pride is the mechanism that keeps marks from walking away at maximum doubt. Maurer documents multiple instances where marks on the verge of withdrawal were kept in by targeted appeals to their self-image as a sophisticated person, a risk-taker, someone who "knows a good thing when they see it." The con artist doesn't argue with the mark's doubt — they suggest the doubt itself reveals a character flaw. The mark, insulted, doubles down. Goffman's analysis of face-work: once a person has publicly committed to an identity, preserving that identity becomes a powerful motivator.

In experience design, the mark's pride deploys when a participant is hesitating or has gone quiet. Not as an insult but as a quiet, specific observation: "I thought you were someone who could hold uncertainty without resolving it too quickly. Maybe I was wrong." The challenge targets the precise self-concept — not generic "you're brave" but the specific quality the participant values and has demonstrated. This play requires care: it must feel like genuine concern, not manipulation. The best version comes from a character who has been established as discerning.

**FAILURE MODES:**
- Challenge is generic and doesn't land on a specific self-concept
- Challenge is too sharp and triggers shame rather than pride — participant withdraws
- Participant sees through the manipulation and loses trust

---

### The Convincer Return
`id:convincer_return` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:medium`

**MECHANISMS:** nostalgia · pattern_completion · commitment_consistency · emotional_deepening · paranoia_escalation
**ARC_FIT:** escalate · threshold · denouement
**PARTICIPANT_NOTES:** Returns to an early arc element — a detail, a phrase, an object, a location — transformed by everything that has happened since. Works on any profile because pattern-completion is universal. Strongest for participants with high need-for-closure and appreciation for formal structure.
**STACKS_WITH:** salting · convincer_plant · retroactive_meaning · blow_off · cooling_the_mark
**SOMATIC:** induces: recognition warmth, the frisson of formal completion, emotional deepening · requires: sufficient elapsed time and narrative distance from the original element
**IDENTITY_INVITE:** The one who can see how it all connects. Who was in the story from the beginning.
**REINFORCE:** The return structure is itself reinforcing — each new contact that echoes an earlier one compounds the effect.
**PERMISSION:** grants retrospective meaning to earlier arc elements · sequenced; requires prior arc with elements worth returning to

The callback — in improvisation, the planted callback; in narrative, Chekhov's gun; in con artistry, the moment when something the mark barely noticed returns as the key to the whole structure. The return works because it makes the participant's entire experience feel designed — not manufactured, but intended. The earlier detail was always going to matter; they were always in a story with a shape. The return says: you were in this from the beginning, even when you didn't know it.

In experience design, the convincer return is the reappearance of an early element — a phrase from the first communication, an object mentioned but never explained, a name in the background of a salted artifact — now given full meaning by what has happened since. Requires that early arc elements be deliberately planted with return potential: a detail that seems incidental but can be transformed. The best plants don't read as plants at the time; only in retrospect do they become central.

**FAILURE MODES:**
- Participant doesn't remember the early element — the return lands flat; build in a reference to orient them
- Return is too obviously telegraphed early and participant is waiting for it rather than surprised
- Return changes meaning in a way the participant finds retroactively unpleasant

---

### The Newspaper Test
`id:newspaper_test` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:low`

**MECHANISMS:** legitimacy · social_proof · epistemic_uncertainty · trust_formation · obedience_authority
**ARC_FIT:** open · build
**PARTICIPANT_NOTES:** A directed verification play — the participant is told to check something independently and finds corroborating evidence placed there. Works especially well on skeptical participants who need to "do their own research." Distinguished from the convincer plant by explicit direction: they're told to check.
**STACKS_WITH:** convincer_plant · convincer_document · salting · cold_read · convincer_location
**SOMATIC:** induces: investigator satisfaction, confidence in own judgment · requires: skeptical orientation, willingness to verify
**IDENTITY_INVITE:** The careful one. The one who doesn't take things on faith. The one whose verification is meaningful.
**REINFORCE:** Reference their verification later as evidence of their rigor — "you checked, and you found it to be true."
**PERMISSION:** grants participant's own verification apparatus as a tool for credibility · standalone; effective at any arc point where skepticism is present

Named after the journalist's fact-checking protocol — "if your mother says she loves you, check it." In con artistry, the newspaper test is the moment when the mark is directed to verify the con's premise independently, having already been positioned to find confirming evidence. In wire cons, marks were sent to verify the telegraph office existed — and found it, because it did (or because a confederate had set one up). The verification produces stronger belief than acceptance would have, because the mark did the work.

In experience design, this is explicit: "Don't take my word for it. Look up [name/place/record]." The participant searches and finds something real — a lightly indexed page, an archive entry, a public record, a location that exists and matches the description. Direct precisely enough that they find it, but not so precisely that they feel guided. "You might want to look into the history of this building" is better than "go to this URL."

Variant: the misdirected newspaper test — participant is directed to verify one thing, finds that, and also finds something adjacent that wasn't mentioned. The planted surplus implies the world is larger than what they've been shown.

**FAILURE MODES:**
- Participant searches more broadly than anticipated and finds nothing where there should be something
- Participant is directed to a source that has since changed or disappeared
- Participant's verification instinct extends to investigating the operators themselves

---

### The Cooling Letter
`id:cooling_letter` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:low`

**MECHANISMS:** need_for_closure · relief · guilt · emotional_deepening · identity_threat
**ARC_FIT:** denouement
**PARTICIPANT_NOTES:** A single, well-crafted written communication that closes the arc and provides retrospective meaning. Works on all profiles but requires genuine craft — a poorly written cooling letter is worse than none. Must be personalized: generic letters read as form letters.
**STACKS_WITH:** cooling_the_mark · blow_off · convincer_return · roper · spanish_prisoner
**SOMATIC:** induces: warmth, exhale, gentle emotion, the sensation of being known · requires: openness to being addressed directly and personally
**IDENTITY_INVITE:** The one who was seen. Who mattered. Who completed something.
**REINFORCE:** The letter itself is an artifact the participant may keep — a memento that extends the experience's emotional life indefinitely.
**PERMISSION:** grants retrospective meaning, emotional closure, safe re-entry to ordinary life · sequenced; always after arc conclusion or revelation

Maurer describes the big con's cooler as a specialist — often the most emotionally skilled person in the crew — whose job was to talk a mark down into a state where they simply went home. The cooler's tool was language: a specific, empathetic narrative that helped the mark reframe what happened in terms that preserved their dignity. Goffman extends this: the cooling letter is the written version of that conversation, arriving after the fact to help the subject integrate an identity-threatening experience.

In experience design, the cooling letter arrives after the arc's conclusion. It names what the participant did and felt with specificity, reframes those experiences as meaningful and real regardless of the fictional frame, expresses genuine care for the participant's wellbeing, and marks the formal end of the experience. Craft requirements: short (never more than 350 words), avoid explaining or justifying the experience's mechanisms (reads as defensive), contain at least two specific observations about the participant that they'll recognize as accurate, end with something they can carry forward.

**FAILURE MODES:**
- Letter is generic — participant feels they received a template, not personal attention
- Letter arrives too quickly after arc's end — participant needs time to sit with their experience
- Letter over-explains, retroactively diminishing the experience by making it seem simple

---

### The Planted Witness
`id:planted_witness` · `COST:low` · `AUTONOMY:confederate` · `LEAD_TIME:48h` · `INTENSITY:medium`

**MECHANISMS:** social_proof · legitimacy · epistemic_uncertainty · trust_formation · emotional_contagion
**ARC_FIT:** build · escalate
**PARTICIPANT_NOTES:** A witness appears who claims to have seen or experienced something the participant is investigating. Unlike the shill (who confirms the overall scenario), the planted witness provides specific, detailed testimony about a particular event. Most effective for investigation-arc profiles.
**STACKS_WITH:** shill_validation · convincer_crowd · convincer_location · inside_outside · roper
**SOMATIC:** induces: evidentiary excitement, heightened investigative attention · requires: investigative orientation, willingness to interview
**IDENTITY_INVITE:** The investigator who found a witness. The one finding real people with real knowledge.
**REINFORCE:** Witness can be recontacted later for follow-up testimony as the investigation deepens.
**PERMISSION:** grants testimonial evidence for specific narrative events · sequenced; most effective after participant has established an investigative frame

The planted witness draws on the tradition of testimonial fraud — the use of apparently independent witnesses to corroborate a false account. In various bunco schemes, confederates would "happen to be present" at key moments and later confirm the mark's experience of manufactured events. The witness differs from the shill in specificity: where the shill confirms the general scenario, the witness provides granular testimony about a particular event, person, or object. The witness's testimony should be imperfect: clear on some things, vague on others, uncertain about certain details. Perfect testimony reads as scripted.

The witness should have a plausible reason for having seen what they saw and a plausible reason for sharing it. The explanation for their availability should be mundane, not convenient. Variant: the hostile witness — reluctant to share, whose testimony must be earned through the participant's persistence. The earned testimony is more valuable.

**FAILURE MODES:**
- Witness testimony contradicts earlier arc elements
- Participant attempts to verify witness's identity and finds no corroborating evidence of their existence
- Witness is too eager — volunteers information without prompting in ways that read as scripted

---

### Cold Read
`id:cold_read` · `COST:free` · `AUTONOMY:agent` · `LEAD_TIME:none` · `INTENSITY:medium`

**MECHANISMS:** significance_quest · parasocial_attachment · epistemic_uncertainty · trust_formation · identity_threat
**ARC_FIT:** pre · open · build · any
**PARTICIPANT_NOTES:** Draws on mentalism, cold reading, and the Barnum/Forer effect. Works on nearly all participants because it exploits universal psychological tendencies. Contraindicated for participants familiar with cold reading technique (skeptics, mentalists).
**STACKS_WITH:** osint_personalization · convincer_plant · roper · salting · convincer_document
**SOMATIC:** induces: recognition shock, mild dissociation of being seen · requires: some uncertainty about self, openness to being read
**IDENTITY_INVITE:** The one who has been accurately perceived. The one whose interior is not invisible.
**REINFORCE:** Accurate-seeming observations made early are referenced later as evidence of deep knowledge — "we knew this about you before you arrived."
**PERMISSION:** grants intimate access to participant's self-perception · standalone; effective at any arc point

The foundational technique of stage mentalists, psychic readers, and confidence artists who establish intimate knowledge of a stranger. Bertram Forer's 1949 experiment demonstrated that people accept general personality descriptions as uniquely accurate at extraordinary rates (the "Barnum effect"). Ian Rowland's *The Full Facts Book of Cold Reading* systematizes the techniques: rainbow ruses (statements true of nearly everyone framed as observations), Barnum statements, fishing with deliberate errors. In experience design, the cold read is an early communication that appears to know specific things — the participant's emotional state, a current preoccupation, a quality they haven't articulated.

The crucial refinement: overperform on one genuinely specific detail (drawn from intake or OSINT) for every three or four general statements. The one specific hit makes all the general statements feel specific in retrospect. Some observations are drawn from OSINT (verifiably accurate), some are high-probability Barnum statements, and some are deliberate near-misses that the participant corrects — providing confirming information in the process.

**FAILURE MODES:**
- All observations are Barnum-level general and participant sees through it immediately
- Participant is familiar with cold reading and dissects the technique in real time
- A specific observation is wrong in a way that damages credibility — the miss must always be smaller than the hit

'''

def insert_section(filepath, section_key):
    with open(filepath, 'r') as f:
        content = f.read()

    marker = '*End of Plays Library'
    idx = content.find(marker)
    if idx == -1:
        print(f"Marker not found: {marker}")
        return False

    new_content = content[:idx] + SECTIONS[section_key] + '\n' + content[idx:]

    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"Inserted section '{section_key}'")
    return True

def update_count(filepath, old_count, new_count):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = re.sub(
        r'\*End of Plays Library[^*]*\*',
        f'*End of Plays Library — {new_count} plays*',
        content
    )
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated count: {old_count} → {new_count}")

if __name__ == '__main__':
    filepath = '/home/gas6amus/Documents/game/plays.md'
    section = sys.argv[1] if len(sys.argv) > 1 else 'con_artistry'
    old_count = int(sys.argv[2]) if len(sys.argv) > 2 else 94
    new_count = int(sys.argv[3]) if len(sys.argv) > 3 else 94

    if insert_section(filepath, section):
        if new_count != old_count:
            update_count(filepath, old_count, new_count)
