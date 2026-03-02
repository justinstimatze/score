# Arc Design Document — Operation Cassandra

**Participant:** Marcus Chen, 39, financial analyst, Chicago IL
**Sponsor:** Priya Chen (sister)
**Arc type:** investigation / persecution
**Duration:** 35 days
**Status:** PASS — 0 errors, 0 warnings

---

## Participant Profile

### Intake signals (sponsor form, Pass 1)

Priya's answers, aggregated:

- Marcus is the person she calls when she needs "someone who will actually read the fine print"
- He finds out about problems before everyone else, then holds that quietly — doesn't broadcast
- Story he carries: the Watergate era, investigative mechanics, the people who connected disparate dots
- When something goes wrong, he reconstructs the failure sequence obsessively; when it goes right, he files it
- What she wants for him: "I want him to feel like the sharpest person in the room, but where that turns out to be exactly wrong in an interesting way"
- F3 (what he avoids): "he avoids situations where he looks like he missed something obvious"

### Dimensional inferences (Pass 3 operator)

| Dimension | Direction | Evidence |
|---|---|---|
| big_five_O | + | "fine print," Watergate, pattern-seeking |
| big_five_C | + | obsessive reconstruction, files wins/losses |
| big_five_E | - | quiet holder, doesn't broadcast |
| big_five_N | - | stable, not anxious — processes rather than spirals |
| need_for_cognition | ++ | intrinsic pleasure in analysis |
| significance_quest | + | wants to be *the one who sees it* |
| fear_of_missing | - | FOMO not dominant; more: fear of being seen as having missed |

### Drivermap top mechanisms

Query: `--dim big_five_O:+ --dim big_five_C:+ --dim big_five_E:- --dim big_five_N:- --dim need_for_cognition:+`

1. `curiosity_exploration` (3.0)
2. `achievement_motivation` (2.5)
3. `intrinsic_motivation_sdt` (2.25)
4. `pattern_recognition` (2.0)
5. `cognitive_dissonance_reduction` (1.75)

### Identity invitation

**Seeker/Pattern-Finder** primary
The arc should cast Marcus as the investigator — then reveal that this identity was manufactured for him, and ask whether he's comfortable with that.

---

## Arc Concept: Operation Cassandra

Marcus receives contact from a whistleblower named Eleanor Marsh, apparently inside a financial data firm. She believes the firm is sitting on foreknowledge of a major market event and needs someone who can put the pieces together. Marcus fits the profile she's been looking for.

Over five weeks, he investigates. He finds evidence. He makes a breakthrough. He finds a witness.

The reveal: Eleanor Marsh works for the firm. The investigation was the product. Marcus was never the investigator — he was the subject. The firm built a dossier on a financial analyst who notices things, using him as an unwitting due-diligence subject. Everything he found was placed. Every piece of evidence passed through him to test what he'd do with it.

**The thematic question:** Is being perceptive a talent, or is it a vulnerability? What does it mean that someone could point your pattern-recognition at a constructed reality and get you to authenticate it?

**Sponsor's F3 satisfied:** He was the sharpest person in the room. He was also exactly wrong in the most interesting way.

---

## Pre-Arc Setup

These plays run before day 0. Expressed as a `pre_arc` block — `check_pre_arc` validates lead times and accumulates any grants before the main arc begins.

| Play | Lead time | Purpose |
|---|---|---|
| `ambient_organization_presence` | 8 weeks | Cipher Ridge Solutions (CRS cover org) is searchable: LinkedIn, a sparse website, two industry forum posts, a real-looking 990 filing. Marcus can verify Eleanor exists. |
| `legend_depth_build` | 8 weeks | Eleanor Marsh's digital footprint: LinkedIn history at two prior firms, a quoted comment in a trade publication, a sparse Twitter with industry content. |
| `diegetic_archive_site` | 4 weeks | A restricted-access data portal (believable subdomain). Password delivered by Eleanor in handler_letter. Contains planted documents Marcus will "discover." |

All three require task prep (`req:tsk`). Operator builds these; participant never knows they were constructed.

```json
"pre_arc": {
  "plays": [
    {"id": "ambient_organization_presence", "day": -56},
    {"id": "legend_depth_build", "day": -56},
    {"id": "diegetic_archive_site", "day": -28}
  ],
  "note": "No grants emitted — world-state infrastructure only. ambient_organization_presence and legend_depth_build run in parallel from d-56."
}
```

---

## Live Arc (days 0–35)

```
[ 1] knowledge_frontier_seed       / ramp       d0   pre/open
[ 2] osint_personalization         / ramp       d0   pre/open
[ 3] handler_letter                / ramp       d3   build
[ 4] distributed_truth_fragment    / ramp       d7   build
[ 5] graduated_reveal              / ramp       d10  build
[ 6] false_breakthrough            / ramp       d14  escalate
[ 7] parallel_threads              _ hold       d15  escalate
[ 8] the_false_confirmation        ^ spike      d17  escalate
[ 9] the_witness                   ^ spike      d21  escalate
[10] optional_path                 > transition d22  escalate
[11] benefactor_capture            / ramp       d24  threshold
[12] manufactured_crisis_reveal    ^ spike      d28  climax
[13] retroactive_recontextualization ^ spike   d30  climax
[14] integration_letter            - rest       d35  denouement
```

**Beat shape:** `/ / / / / / _ ^ ^ > / ^ ^ -`
**Beat mix:** spike:4, ramp:7, hold:1, rest:1, transition:1
**Legacy:** personal:11, ephemeral:2, social:1

---

## Play-by-Play Narrative

### Day 0 — Opening

**`knowledge_frontier_seed`** — The inciting object. A forwarded email arrives in Marcus's personal inbox, appearing to come from a research forum list he's on. Subject: "Re: data latency in pre-announcement windows." The content is legitimately interesting: someone is suggesting there are systematic anomalies in certain reporting windows. The sender's handle is `e.marsh.research`. No call to action. Just a thought. It names a gap that is genuinely puzzling if you think about it. Marcus, who reads everything carefully, files it.

*This play plants the `slv` grant: Marcus now has a named knowledge gap. The mystery to be solved is live.*

**`osint_personalization`** — The play runs silently. Operator has assembled Marcus's public footprint, publication history, LinkedIn connections, conference attendance, financial certifications. This shapes every subsequent play. Eleanor "knows who he is" because she does — the operator built the profile before anything was sent.

---

### Day 3 — First Contact

**`handler_letter`** — Eleanor Marsh emails Marcus directly. She says she found his name in a published comment thread responding to the data latency question. She works in quantitative compliance at a data firm she can't name. She's noticed the same anomalies. She'd like to correspond. She is careful, formal, slightly nervous. She doesn't ask for anything yet.

*This is the first direct contact. The relationship is established as peer-to-peer, not whistleblower-to-journalist. She respects his expertise.*

---

### Day 7 — First Fragment

**`distributed_truth_fragment`** — Eleanor sends a data table, anonymized, showing the window anomalies. It's real-looking — not conclusive, but legitimately interesting. She says she can't send more through email and suggests he look at something she's put in a shared repository. She provides a URL: the pre-built diegetic archive portal.

*First breadcrumb. Marcus now has something tangible. The archive portal is live. He can log in; there are more documents there.*

---

### Day 10 — Escalation Tier

**`graduated_reveal`** — Over the week, Marcus accesses the archive and finds escalating documentation: internal memos (anonymized, authentically formatted), a timeline of the anomalies, cross-referenced with public events. Each document is more specific than the last. Eleanor sends a message: "I think you can see where this is going."

*This play produces the `esc` grant: Marcus is now in investigation/escalation mode. He has the next tier of access. The `the_false_confirmation` play is now unlocked.*

---

### Day 14 — The Breakthrough

**`false_breakthrough`** — Marcus finds the pattern. The anomalies cluster around a specific dataset vendor. He cross-references public information on the vendor — finds a corporate restructuring two years ago, a quiet acquisition, an executive who moved to the firm Eleanor works at. It's circumstantial, but it connects. He writes it up and sends it to Eleanor.

Eleanor responds: "Yes. That's exactly it."

*This is the false breakthrough. Marcus has solved a puzzle that was built to be solvable by him, using his specific research style. The solve mode (`slv`) has been satisfied — from his perspective, he cracked it. In reality, the "pattern" was constructed to be findable.*

---

### Day 15 — Saturation

**`parallel_threads`** — The day after his breakthrough, Marcus starts seeing the pattern everywhere. A news item mentions the vendor. A colleague references the firm in passing. A podcast he already had queued discusses data latency in compliance contexts. He wasn't looking for confirmation, but it keeps arriving.

*This is the hold beat. Nothing happens narratively — Eleanor is quiet. But Marcus is now in active pattern-saturation mode. This is what happens after a false breakthrough: the mind retrieves confirming instances. The hold creates processing space but paradoxically deepens the false conviction.*

---

### Day 17 — The Confirmation

**`the_false_confirmation`** — Eleanor sends a message: she's been approached by someone inside the firm — a compliance officer — who has confirmed what Marcus found. She attaches a brief statement (anonymized, deniable). The compliance officer has seen the vendor's internal data. It matches. Eleanor says she's starting to be afraid.

*First spike. The participant's solve is externally validated by a second source. From Marcus's perspective, this is the moment the investigation became real — he had a theory and now has a witness. The `esc` grant is consumed and transformed: Marcus is now not just a solver but a person with corroboration. His identity as investigator is solidified.*

---

### Day 21 — The Witness

**`the_witness`** — The compliance officer makes direct contact. A brief email, more frightened-sounding than Eleanor. They are willing to speak on background. A phone call is arranged for a specific time. The call happens (conducted by a confederate). The compliance officer provides specific details that match and amplify what Marcus found. They hang up quickly, sounding scared.

*Second spike. A human being has now confirmed the investigation to Marcus in real time. This is the highest point of false credibility. Marcus has gone from: curious email → theory → external confirmation → live witness. He has reason to believe something real is happening.*

---

### Day 22 — The Branch

**`optional_path`** — Marcus is given a choice (diegetic): Eleanor says she may be able to get one more document, but it would require Marcus to request it through a specific channel — a form submission to the firm's investor relations department, phrased as a routine analyst inquiry. He can do it or not. If he does, an additional layer of investigation opens. If he declines, the arc continues regardless.

*This is the transition beat. Whether Marcus takes the optional path or not, the arc pivots here. He's been receiving; now he's asked to act. The optional path deepens his investment but is not required for the climax. This play establishes the `esc` grant for the benefactor encounter.*

---

### Day 24 — The Benefactor

**`benefactor_capture`** — Eleanor introduces a third party: someone at the firm who is sympathetic and wants to help get the information out. He goes by "DH." DH contacts Marcus directly and says he can arrange a meeting if Marcus wants to go on record with what he's found — "a journalist is interested, someone we trust." This is a moment of escalation and potential commitment. Marcus doesn't have to agree to the journalist meeting; the meeting itself is notional. But DH is real, engaged, and seems to know what Marcus found.

*The benefactor is a confederate. The play deepens Marcus's sense that the investigation has external weight — he's being recruited, not just corresponding. His identity as the person who figured it out is being named by others.*

---

### Day 28 — The Crisis

**`manufactured_crisis_reveal`** — Eleanor goes quiet. Two days of silence. Then: a brief message. "I think they found out. I have to be careful. I'm sorry — if this stops, you know what you found." Then silence.

One day later, DH sends a brief message: "They know someone external has the documents. They're going to send a retraction request. Be careful about what you've saved."

A retraction request arrives from the firm's legal department (diegetic, letter-format): a routine NDA-adjacent request asserting that proprietary documents may have been shared without authorization and requesting confirmation that no records are being kept.

*Third spike. The crisis is manufactured but feels entirely real. Marcus now has legal pressure, a frightened source, and a sense that the investigation has become dangerous. His pattern-recognition has been pointed at a constructed threat and authenticated it.*

---

### Day 30 — The Reveal

**`retroactive_recontextualization`** — A package arrives. Physical mail, addressed to Marcus specifically. Inside: a brief, formally formatted document. Header: "Operation Cassandra — Participant Debrief." Subheader: "A Summary of Your Experience."

The document explains, plainly:
- Eleanor Marsh is not a whistleblower. She is an experience designer.
- Cipher Ridge Solutions is a real organization, but not a data firm. It designs personalized investigative experiences for private clients.
- Everything Marcus found was placed for him, calibrated to his specific research style.
- His sister Priya commissioned this experience.
- The "investigation" was real — but Marcus was the subject, not the investigator.

The document is written with genuine respect for what Marcus did. It names the specific things he found, the methods he used, the accuracy of his inference. It says: *you were correct about the pattern. We just built the pattern.*

*Fourth spike. The retroactive recontextualization hit. Every prior event is simultaneously confirmed (it happened) and inverted (the meaning was different). The personal legacy plays that followed are now about Marcus deciding what this means about his pattern-recognition, his identity as someone who sees things, and whether that capacity can be weaponized.*

---

### Day 35 — Integration

**`integration_letter`** — A final letter from Eleanor (her real name: Soo-Yeon Park), on non-diegetic letterhead. She explains what she noticed about how Marcus worked. What was accurate about the profile they built of him. What surprised them. She says Priya told her about Marcus's relationship to Watergate-era journalism and that she tried to honor that interest. She invites Marcus to reach out if he has questions.

The letter ends: "The question Operation Cassandra always leaves behind is the same one Marcus Aurelius was sitting with: not 'what is true?' but 'how do I know what's true, and does that question change how I act?'"

*The rest beat. No ask, no spike, no new information. Just: here is what happened, and here is a way to think about it that doesn't diminish what you brought to it.*

---

## Production Notes

### Confederate requirements
- **Eleanor Marsh (Soo-Yeon Park)** — primary confederate, handles all email contact, adapts to Marcus's response cadence
- **Compliance officer** — voice confederate for the Day 21 phone call; receives a briefing packet from operator
- **DH (benefactor)** — secondary confederate; brief text-based contact only; can be same operator if necessary

### Operational infrastructure
- CRS digital footprint (8-week build): website, LinkedIn, 990 filing, forum posts
- Eleanor Marsh legend (8-week build): LinkedIn, publication credit, sparse social
- Diegetic archive portal (4-week build): password-protected subdomain, document library seeded with 8–12 planted documents
- Legal retraction letter (1 week): formatted on firm letterhead, delivered via email

### Adaptation points
- If Marcus doesn't take optional_path, arc proceeds from Day 24 unchanged
- If Marcus forwards documents or contacts a journalist independently, pause and contact operator — this is an early escalation requiring a response play
- If Marcus seems distressed rather than engaged at Day 21 witness call, benefactor_capture at Day 24 can be softened to a check-in rather than a recruitment play

### Risk and reversibility
- `manufactured_crisis_reveal` is the highest-risk play: legal-register communication in real life. Requires participant has confirmed safety keywords are not active; operator reviews Marcus's responses before sending retraction.
- `retroactive_recontextualization` physical mail cannot be recalled after delivery. Operator reviews Marcus's response to manufactured_crisis before authorizing print.
- Hold protocols: if Marcus's Day 21–24 messages show anxiety rather than investigation engagement, insert `seam_acknowledgment` before benefactor_capture.

---

## Arc Validation

```
Status: PASS — 0 errors, 0 warnings, 0 info

Beat shape:  / / / / / / _ ^ ^ > / ^ ^ -
Beat mix:    spike:4  ramp:7  hold:1  rest:1  transition:1
Legacy:      personal:11  ephemeral:2  social:1

Pre-arc (pre_arc block, check_pre_arc pass):
  ambient_organization_presence    d-56  lead:8w  OK
  legend_depth_build               d-56  lead:8w  OK
  diegetic_archive_site            d-28  lead:4w  OK
```
