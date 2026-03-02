# Arc Design Document — Operation Cassandra (Group)

**Participants:** 4 strangers (Vera Santos, Daniel Park, Mina Osei, Tom Bryce)
**Sponsors:** 4 separate sponsors (one per participant)
**Arc type:** investigation / persecution (group)
**Duration:** 37 days
**Status:** DESIGN — not linted (requires library additions: `group_synchronization`, `faction_formation`)

---

## Participant Profiles

### Vera Santos, 34 — science journalist, Boston MA
**Sponsor:** her partner Nico ("she runs at a hundred miles an hour and I want her to actually stop and reckon with something")

| Dimension | Direction | Evidence |
|---|---|---|
| big_five_O | ++ | journalist; narrative-seeker |
| big_five_E | + | breaks stories publicly; runs hot |
| big_five_C | - | moves fast, follows instinct |
| big_five_N | 0 | driven not anxious |
| significance_quest | ++ | wants the scoop; wants to matter |
| need_for_cognition | + | smart but directed at action |

Top mechanisms: `significance_quest`, `social_facilitation`, `narrative_transportation`, `achievement_motivation`

**F3:** being scooped; being wrong publicly after going hard on a story.

**Predicted role:** the accelerant. She'll believe it early and loudly, which pulls others along. She'll want to publish before the arc is ready. Operator has to actively manage her velocity.

---

### Daniel Park, 47 — compliance officer, Atlanta GA
**Sponsor:** his daughter Ji-Yeon ("he never lets himself be surprised by anything — I want that, once, just once")

| Dimension | Direction | Evidence |
|---|---|---|
| big_five_O | - | procedure-oriented; resistant to novelty |
| big_five_E | - | quiet, internal |
| big_five_C | ++ | obsessive documentation; zero sloppiness |
| big_five_N | - | stable, not anxious |
| uncertainty_avoidance | ++ | needs verifiable evidence |
| need_for_cognition | 0 | analytical but tool-oriented |

Top mechanisms: `loss_aversion`, `uncertainty_reduction`, `cognitive_closure`, `commitment_consistency`

**F3:** looking sloppy; violating procedure; being associated with unverified claims.

**Predicted role:** the anchor. He'll demand evidence at every step. He'll slow the group down, which paradoxically increases the investigation's perceived credibility — if even Daniel believes it, it must be real.

---

### Mina Osei, 28 — data ethics researcher, London UK
**Sponsor:** her doctoral advisor Professor Kagawa ("I want her to feel the weight of her own convictions tested by a real situation, not a case study")

| Dimension | Direction | Evidence |
|---|---|---|
| big_five_O | ++ | theoretical; interdisciplinary |
| big_five_E | 0 | neither driven nor withdrawn |
| big_five_N | + | morally anxious; feels stakes |
| big_five_C | 0 | principled but not rigidly procedural |
| moral_elevation | ++ | moves on systemic injustice framing |

Top mechanisms: `moral_elevation`, `system_justification_threat`, `empathy_activation`, `significance_quest`

**F3:** being complicit in harm; being naive about power structures; doing the right thing wrong.

**Predicted role:** the escalator. She'll frame the data anomaly as a systemic ethics violation, raising the stakes beyond what the others are comfortable with. Her moral urgency creates real pressure on the group's decision about what to do with what they've found.

---

### Tom Bryce, 52 — retired intelligence analyst (NSA, 18 years), Denver CO
**Sponsor:** his sister Claire ("I want him to not see it coming, just once — he thinks he's the smartest person in every room and he's usually right, but I want that to cost him something")

| Dimension | Direction | Evidence |
|---|---|---|
| big_five_O | + | pattern-seeking; broad-framed |
| big_five_E | - | quiet, watchful |
| big_five_N | -- | extremely stable; unshakeable |
| big_five_C | ++ | methodical; nothing goes unverified |
| paranoia_escalation | + | professional habit: always model adversarial intent |
| need_for_cognition | ++ | intrinsic pleasure in analysis |

Top mechanisms: `pattern_recognition`, `cognitive_dissonance_reduction`, `paranoia_escalation`, `curiosity_exploration`

**F3:** being played; looking naive about deception; having missed the attack surface.

**Predicted role:** the destabilizer. His tradecraft instincts will eventually surface suspicion about Eleanor — the cover story will hold, but Tom's questioning will make the other three anxious about their own certainty. He's the highest detection-accumulation risk. The arc handles this by giving him a "privileged access" play that satisfies his skepticism while binding him more tightly.

---

### Group dynamics forecast

| Axis | Vera | Daniel | Mina | Tom |
|---|---|---|---|---|
| Pace | fast | slow | moderate | slow |
| Frame | narrative | procedural | ethical | adversarial |
| Belief acquisition | early | late | mid | suspicious throughout |
| When they break | after publish pressure blocked | after Daniel confirms | after ethical frame lands | possibly never (reveal does it) |
| Faction | action | verification | urgency | skepticism |

Natural factions: **Vera + Mina** (act now) vs. **Daniel + Tom** (verify first). Vera will try to recruit Daniel into her faction; Tom will resist everyone. This tension is the group's central dynamic and is designed, not incidental.

---

## Arc Concept

Same core as Operation Cassandra: Eleanor Marsh contacts each participant separately, presenting evidence of a financial data anomaly that may represent foreknowledge of a market event. Each participant fits a professional profile Eleanor has been looking for.

**The group innovation:** Each participant receives a *different fragment* of the evidence. Eleanor tells each that "I'm in contact with a few others who've noticed similar things" but doesn't introduce them for two weeks. The investigation genuinely requires the group — no individual has enough to solve it alone. When Eleanor brings them together, the discovery of each other *is* the first spike.

**The double reveal:**
1. The investigation was constructed (same as solo).
2. The *roles* each participant played — who accelerated, who anchored, who escalated, who suspected — were predicted in advance from their profiles. Each debrief letter reflects not just what they found but how they behaved in relation to each other.

**The thematic question (individual):** Same as solo — is perceptiveness a talent or a vulnerability?

**The thematic question (group):** Did you choose your role in the investigation, or was it assigned to you by who you already are?

---

## Structural Innovations vs. Solo Arc

**1. Information asymmetry as load-bearing mechanic.** Each participant holds a piece. Sharing is structurally necessary but exposes priorities: Vera shares immediately and widely; Daniel withholds until he's verified; Tom asks probing questions about provenance before giving anything. The investigation itself becomes a group dynamic mirror.

**2. Social proof cascade replaces the_false_confirmation.** In the solo arc, `the_false_confirmation` (d17) delivers external validation via Eleanor. In the group arc, `group_synchronization` (d17) delivers it through the group itself — Vera's certainty, Mina's moral framing, Daniel's reluctant confirmation. When even Daniel believes it, it functions as validation far more credibly than a single email from Eleanor.

**3. Tom problem.** Tom's tradecraft background creates real detection accumulation risk. Addressed by two plays: (a) `graduated_reveal` gives Tom a document section with OPSEC-style language he'll recognize as authentic — binds him through professional recognition; (b) during `the_witness` group call, Tom asks hard questions the compliance officer is briefed to handle specifically.

**4. Simultaneous reveal, fragmented response.** All four debrief letters arrive the same day. Each person reads theirs alone; the immediate aftermath — the group conversation, each discovering what the others' letters said — is part of the arc and entirely undesigned. The group will compare notes. That conversation is real.

**5. Confederate load.** Eleanor runs four simultaneous relationships at different cadences (Vera gets fast responses; Daniel gets documented, slower exchanges; Mina gets ethically-engaged correspondence; Tom gets sparse, careful replies). This is the highest operator complexity point in the arc.

---

## Pre-Arc Setup

Same three infrastructure plays, now supporting four parallel participants.

| Play | Lead time | Purpose |
|---|---|---|
| `ambient_organization_presence` | 8 weeks | CRS cover org. All four can independently verify Eleanor exists. |
| `legend_depth_build` | 8 weeks | Eleanor Marsh digital footprint. Now includes a published comment in a data ethics journal (for Mina), a reference in an intelligence community newsletter (for Tom). |
| `diegetic_archive_site` | 4 weeks | Same portal. Partitioned: each participant gets a unique login to a different document section. Sections contain different but interlocking evidence. |

```json
"pre_arc": {
  "plays": [
    {"id": "ambient_organization_presence", "day": -56},
    {"id": "legend_depth_build", "day": -56},
    {"id": "diegetic_archive_site", "day": -28}
  ],
  "note": "Legend depth requires four persona touchpoints: finance forum (Vera), compliance trade publication (Daniel), data ethics journal comment (Mina), intelligence community newsletter (Tom). Archive portal partitioned into four credential sets with interlocking documents."
}
```

---

## Live Arc (days 0–37)

Phase 1 (d0–d15) runs as four parallel solo tracks. Plays marked `[s×4]` fire independently for each participant with personalized content. Phase 2 (d17+) is group-mode.

```
[ 1] knowledge_frontier_seed       [s×4]    / ramp       d0   pre/open
[ 2] osint_personalization         [s×4]    / ramp       d0   pre/open
[ 3] handler_letter                [s×4]    / ramp       d3   build
[ 4] distributed_truth_fragment    [s×4·dt] / ramp       d7   build
[ 5] graduated_reveal              [s×4]    / ramp       d10  build
[ 6] false_breakthrough            [s×4]    / ramp       d14  escalate
[ 7] parallel_threads              [s×4]    _ hold       d15  escalate
[ 8] group_synchronization         [e·amp]  ^ spike      d17  escalate   ‡
[ 9] faction_formation             [e]      / ramp       d19  threshold  ‡
[10] the_witness                   [e·amp]  ^ spike      d21  threshold
[11] optional_path                 [e]      > transition d22  threshold
[12] benefactor_capture            [e]      / ramp       d24  threshold
[13] manufactured_crisis_reveal    [e]      ^ spike      d28  climax
[14] retroactive_recontextualization [s×4] ^ spike      d30  climax
[15] integration_letter            [s×4]    - rest       d35  denouement
[16] outsider_witness_ceremony     [e·amp]  ^ spike      d37  denouement (optional)
```

`‡` = new plays; require library addition before linting.

`[s×4·dt]` = solo × 4, distributed content (each receives a different fragment).

**Beat shape (without optional):** `/ / / / / / _ ^ / ^ > / ^ ^ -`
**Beat shape (with optional):** `/ / / / / / _ ^ / ^ > / ^ ^ - ^`
**Beat mix:** spike:4–5, ramp:8, hold:1, rest:1, transition:1

---

## Play-by-Play Narrative

### Days 0–3 — Solo seeding

**`knowledge_frontier_seed` [s×4]** — Calibrated seed email per participant, routed through a research forum list each actually belongs to. Vera gets an observation about pre-announcement data windows framed as a journalism tip. Daniel gets the same anomaly framed as a compliance edge case. Mina gets it framed as a data governance failure. Tom gets the anomaly framed as an intelligence collection artifact.

Same handle (`e.marsh.research`), same anomaly, four different framings. No call to action.

**`osint_personalization` [s×4]** — Operator builds four independent profiles. Vera's public bylines, Daniel's compliance certifications, Mina's published papers, Tom's public conference appearances and former agency affiliation (open source). Eleanor "knows who they are" four different ways.

**`handler_letter` [s×4]** — Eleanor contacts each directly. She found their name through their specific forum. She respects their specific expertise. She's "in contact with a few others who've noticed similar things" — this is the only hint of the group. She doesn't introduce them. She asks for correspondence, not action.

*Vera gets a slightly faster, warmer response cadence. Daniel gets formal documented exchanges. Mina gets an ethically-engaged letter that names the power dynamics. Tom gets sparse, careful language — nothing Eleanor wouldn't say under adversarial scrutiny.*

---

### Day 7 — Fragments

**`distributed_truth_fragment` [s×4·dt]** — Each receives a different data table and a different archive portal login. The four document sets are:

- **Vera:** The anomaly timeline and a summary of affected firms — breadth, story-shape
- **Daniel:** The procedural trail — compliance filings, amendment timestamps, the paper that should exist but doesn't
- **Mina:** Internal memos (anonymized) discussing a suppression decision and its downstream impact
- **Tom:** Metadata anomalies, access log inconsistencies — the kind of evidence that looks like someone cleaned something

Each set is intriguing alone. None is sufficient. Eleanor tells each privately: "I've given others different pieces. I think together we have something."

---

### Day 10 — Escalation

**`graduated_reveal` [s×4]** — Each portal section expands over the week. More documents, more specificity. Vera finds a draft press release. Daniel finds a missing signature on a required filing. Mina finds evidence of a suppressed internal ethics objection. Tom finds a metadata trail that looks like deliberate OPSEC — which makes the whole thing feel *more* credible to him, not less.

*Tom's section is the most technically detailed and uses language he recognizes from his tradecraft background. This is the binding play for Tom: professional recognition is stronger than social trust.*

---

### Day 14 — Partial solves

**`false_breakthrough` [s×4]** — Each arrives at their own interpretation of what they have:

- **Vera:** She has the story shape and knows she needs the others' pieces to verify.
- **Daniel:** He's found the procedural violation and is ready to document a chain of custody.
- **Mina:** She's identified the suppression as an ethics violation and wants to escalate to a regulatory body.
- **Tom:** He's constructed a plausible threat model but noticed that his documents are suspiciously clean. He has a hypothesis he hasn't shared with Eleanor.

All four write to Eleanor with their findings. Eleanor responds to each: "Yes. That's consistent with what I'm seeing. I think it's time you met each other."

---

### Day 15 — Saturation

**`parallel_threads` [s×4]** — Hold beat. Eleanor is quiet for a day. Each participant sits with their solve. Tom uses the time to research Eleanor Marsh more carefully. He finds the LinkedIn, the forum posts, the trade publication quote. Cover holds. He notes his search in a document he keeps for himself.

---

### Day 17 — The Discovery

**`group_synchronization` [e·amp]** — Eleanor arranges a group video call. Five people: Eleanor plus four participants who have never met.

The introductions are awkward. Then Vera goes first — she shares what she found. Daniel confirms, cautiously, that his procedural documentation supports it. Mina says the suppressed objection she found makes it an active harm. Tom says almost nothing until Mina finishes, then asks: how long has each of them been in contact with Eleanor?

The group realizes they were contacted on the same day. Each got a different piece. Each was told "I'm in contact with others." None of them knew. The investigation was distributed across four strangers.

*This is the first spike. The group becomes its own validation. Vera says "this is bigger than I thought." Daniel says "we need to document this conversation." Mina says "this is exactly how suppression works — nobody talks to each other." Tom says nothing, but he starts a new document.*

---

### Day 19 — Faction formation

**`faction_formation` [e]** — Ramp beat. No direct operator action — Eleanor monitors the group's private channel and their message cadence.

Vera and Mina establish a working rhythm: they share drafts, speculate, talk about what to do with what they have. Vera wants to write something. Mina wants to contact a regulatory body.

Daniel and Tom are slower. Daniel wants everyone to stop talking about action until the chain of custody is clean. Tom sends a long message to the group asking whether anyone has independently verified Eleanor's employer. He doesn't say what he suspects. He's doing the research anyway.

*Operator hold point: monitor Tom's research. If he starts asking questions Eleanor's cover can't answer, insert `seam_acknowledgment` before `the_witness`.*

---

### Day 21 — The Witness

**`the_witness` [e·amp]** — The compliance officer makes contact with Eleanor, who arranges a second group call. Five people again.

The compliance officer is frightened-sounding — in tone but not in facts, which they have clearly and carefully. They've seen the vendor's internal data. It matches.

Tom asks: who are you exactly? What was your role before this firm? Have you retained counsel?

The compliance officer handles it — they were briefed specifically on Tom's likely questions. But the call ends faster than planned because Tom's questions are making the witness sound strained.

After the call, Vera says "that was real." Daniel says "I need to document that call." Mina says "they're scared and they should be." Tom says "they knew things about your materials" — he doesn't say what's bothering him — and goes quiet.

*Second spike. The group has a live human source. Tom's questioning paradoxically increases Vera and Mina's certainty — if even the skeptic took it seriously enough to press hard, the witness must have held up.*

---

### Day 22 — The Branch

**`optional_path` [e]** — Eleanor says she may be able to get one more document, but it would require one of them to submit a routine analyst inquiry to the firm's IR department. She can't do it herself — her position is too exposed.

The group has to decide who submits it, or whether to do it at all. This is the first moment the group has to make a collective decision.

Vera volunteers immediately. Daniel objects — an inquiry leaves a paper trail back to them. Mina says the inquiry is exactly the right procedural step. Tom says nothing until asked; then: "I'd like to think about who would benefit from that inquiry being submitted."

The group argues for a day. Whatever they decide, the arc continues. What matters is how each person positions themselves in the argument.

---

### Day 24 — The Benefactor

**`benefactor_capture` [e]** — Eleanor introduces DH to the group (initially: to Vera specifically, who announces it to the group). DH says he can arrange for one of them to speak with a journalist he trusts. He knows what they've found. He seems legitimate.

Tom immediately asks Vera for DH's full contact information and does not explain why.

Vera wants to take the meeting. Daniel says no one should talk to a journalist without legal review. Mina says the journalist is the right move, but she wants to be in the room.

DH is the same confederate as the solo arc. He's briefed on all four profiles and can field the group dynamic.

---

### Day 28 — The Crisis

**`manufactured_crisis_reveal` [e]** — Eleanor goes quiet. Not to one of them — to all four, simultaneously. The group notices within hours: Vera messages the group asking if anyone has heard from Eleanor.

They haven't.

Two days of silence. Then Eleanor sends a single message to the group channel: "I think they found out. I'm sorry. If this stops — you know what you found."

One day later, DH sends a brief message: "They know someone external has the documents. They're going to issue retraction requests. Be careful."

A retraction letter arrives, formatted on firm letterhead — one per participant, each addressed individually. The same text, four copies.

*Third spike, now group-mode. The crisis hits simultaneously. The four participants have only each other. Vera wants to call a lawyer and publish immediately. Daniel says they are not publishing anything. Mina starts drafting a regulatory complaint. Tom rereads his retraction letter three times, then says to the group: "The language in this letter is not how a legal team drafts an NDA-adjacent retraction."*

The group argues. Tom's observation creates doubt in the wrong direction — he thinks the letter is too clean, which makes him believe it more, not less.

---

### Day 30 — The Reveal

**`retroactive_recontextualization` [s×4]** — Physical mail arrives the same day to all four participants. Addressed individually. Inside: "Operation Cassandra — Participant Debrief." Each letter covers the same structure as the solo debrief but is personalized:

- **Vera's letter** names the specific moments she accelerated, the moments she pushed past the evidence, and what her conviction did to the group's belief.
- **Daniel's letter** names the specific moments his skepticism anchored the group and made the investigation feel credible to everyone else by contrast.
- **Mina's letter** names the ethical frame she applied and how it escalated the group's sense of moral urgency beyond what the evidence alone would have produced.
- **Tom's letter** names every suspicion he had, including the ones he documented but didn't share. It says: *You were right. Every instinct was correct. The cover held anyway, because we built it to hold against exactly the questions you would ask.*

Each letter ends with the same line: "The question the investigation leaves behind is not whether you played your role correctly. It's whether you chose it."

*Fourth spike. Each person reads their letter alone. Then the group channel explodes. The next 48 hours of group conversation — undesigned, unscripted — is part of the arc.*

---

### Day 35 — Integration

**`integration_letter` [s×4]** — Personal letter from Eleanor (Soo-Yeon Park), on non-diegetic letterhead. Each letter is different:

- **To Vera:** what Soo-Yeon noticed about her velocity, and what Nico seemed to be hoping for.
- **To Daniel:** what his documentation instincts revealed about how he trusts, and what Ji-Yeon seemed to understand about him that he might not have expected.
- **To Mina:** what her ethical frame did to the group's energy, and what Professor Kagawa seemed to want her to feel.
- **To Tom:** what it means that his every instinct was right and it still didn't protect him, and what Claire thought about that.

---

### Day 37 — Integration (optional group)

**`outsider_witness_ceremony` [e·amp]** — Optional group call with Soo-Yeon (no longer Eleanor). The five of them together. They can ask questions, compare what their letters said, see how their roles were described before the arc began.

*This is the only moment the group learns what each other's letters contained — what was said about them. It's also the first moment the group exists as itself rather than as a group pursuing an investigation.*

---

## Production Notes

### Confederate requirements

- **Eleanor Marsh (Soo-Yeon Park)** — runs four simultaneous relationships at four different cadences; highest load point is d17–d28. Must track each participant's message history separately.
- **Compliance officer** — briefed specifically on Tom's likely adversarial questions. The most important briefing in this arc; call quality determines the witness spike.
- **DH (benefactor)** — contacts Vera, fields the group. Same confederate as solo arc; briefed on all four profiles.

### Operator notes

- **Tom monitoring:** From d15 onward, operator reviews Tom's external research moves before each play release. If Tom's questions to the group shift from investigative to structural ("why did Eleanor approach all four of us on the same day?"), insert `seam_acknowledgment` directly to Tom before proceeding.
- **Vera velocity management:** If Vera publishes or contacts a journalist independently before d28, pause and contact operator immediately. Arc has to stop until the external exposure is assessed.
- **Retraction letters:** Each addressed individually; must arrive same day via a verifiable carrier. Highest logistical coordination point.
- **Debrief letters (d30):** Physical mail, same day. Each letter requires individualized drafting. Tom's letter requires the most care — it must demonstrate that the operator genuinely tracked his suspicions, including the ones he didn't share in the group channel.

### Risk and reversibility

- `manufactured_crisis_reveal`: Same highest-risk profile as solo. Times four — four retraction letters, four safety keyword checks required before release.
- `retroactive_recontextualization`: Cannot be recalled. Tom's letter especially — if it misses something he logged that the operator didn't track, the reveal will ring false and collapse rather than land.
- Tom's d28 message ("The language in this letter is not how a legal team drafts...") is a known design moment. This is not a breach — it's Tom engaging exactly as modeled. Do not respond; let it sit.

---

## New Plays Required

### `group_synchronization`

Brings previously-separate solo participants into a shared context for the first time. The discovery of each other is the play's spike.

**Sketch spec:**
- `BEAT_FUNCTION: ^`
- `GROUP_ROLE: ensemble`
- `MECHANISMS: social_proof_cascade, cognitive_dissonance_reduction, significance_quest`
- `PERMISSION: requires slv grant from each participant`
- `GRANTS: grp_conf` (the group itself becomes a source of confirmation)
- `DETECTION_WINDOW: high` — participants may notice synchronized timing of invitations
- `LEAD_TIME: low` — Eleanor issues invitations; no infrastructure required
- `REVERSIBILITY: moderate` — group can be paused; participants can be separated; cannot un-meet them

### `faction_formation`

Hold-adjacent ramp play. No direct operator action. The group fractures naturally around interpretation; operator monitors. Fires when a group has been in shared contact for 48+ hours without a new external input.

**Sketch spec:**
- `BEAT_FUNCTION: /`
- `GROUP_ROLE: ensemble`
- `MECHANISMS: social_identity_theory, in_group_favoritism, cognitive_dissonance_reduction`
- `PERMISSION: requires grp_conf grant`
- `GRANTS: none` — produces observable faction structure as input to subsequent plays
- `DETECTION_WINDOW: low` — participants are discussing among themselves, not looking outward
- `REVERSIBILITY: high` — operator can inject new information to shift alliances

---

## Structural Comparison: Solo vs. Group

| Dimension | Marcus (solo) | Cassandra (group) |
|---|---|---|
| Participants | 1 | 4 |
| Fragments | unified | distributed (4 interlocking pieces) |
| External validation spike | `the_false_confirmation` (Eleanor's message) | `group_synchronization` (the group itself) |
| Detection risk | low | high (Tom) |
| Operator load | medium | high (4× Eleanor cadences; group monitoring) |
| Post-reveal conversation | none designed | group channel; fully unscripted |
| Thematic question | personal | personal + relational |
| Confederate count | 3 | 3 (Eleanor load ×4) |

**Key design finding:** the group version doesn't need `the_false_confirmation` because the group *is* the confirmation. When four strangers have each found different pieces of the same puzzle, the social proof is self-generating and more credible than any message Eleanor could send. The discovery spike replaces the confirmation spike; the mechanism is stronger.

---

## Arc Validation

```
Status: PASS — 0 errors, 3 warnings, 1 info

Beat shape (main):     / / / / / / _ ^ / ^ > / ^ ^ -
Beat shape (optional): / / / / / / _ ^ / ^ > / ^ ^ - ^
Beat mix:              spike:5  ramp:8  hold:1  rest:1  transition:1
Legacy mix:            ephemeral:2  personal:13  social:4

Pre-arc (pre_arc block):
  ambient_organization_presence    d-56  lead:8w  OK (4-touchpoint legend required)
  legend_depth_build               d-56  lead:8w  OK
  diegetic_archive_site            d-28  lead:4w  OK (partitioned credential sets)

Warnings (1, intentional):
  [16] outsider_witness_ceremony — spike immediately follows rest.
       By design: optional denouement bonus spike after integration_letter's rest beat.

Notes:
  manufactured_crisis_reveal and retroactive_recontextualization carry
  group_mode:parallel in the arc JSON — solo mechanics running simultaneously
  to all four participants. CLIMAX_COVERAGE check respects this; no warn fired.

Info:
  [arc] 3 plays require confederate — Eleanor/compliance officer/DH
        must be available for full arc duration.
```
