# Project Todos

Derived from structural analysis of House of the Latitude and Sleep No More against the notation.
Each item is actionable and bounded. Items marked with the source finding that motivated them.

---

## Linter

**L1. ✓ DONE. Warn on all-identity LANDSCAPE arc.**
Add check: if no play in the arc has LANDSCAPE:action or LANDSCAPE:both, emit WARN — "no action-plane plays; arc operates entirely on identity plane." An arc with nothing for the participant to do, produce, or complete is structurally at risk of ideology vacancy even if beat shape is correct. Initiation arcs are the clearest target; suppress for grief/memorial arc type if added.
_Source: Latitude — ideology vacancy as structural pattern._

**L2. ✓ DONE. Require short-circuit denouement for initiation arcs.**
Add a field `early_exit` to arc JSON: the play ID to deliver if the operator needs to close the arc before the designed climax. Add linter check: if arc_type=initiation and no early_exit defined, emit WARN — "no early-exit play defined; arc has no graceful short-circuit." Latitude's failure was partly that there was no exit before graduation_ritual at day 120.
_Source: Latitude — operator-terminated arcs._

**L4. ✓ DONE. Mechanism vocabulary drift check.**
Add a `check_mechanisms.py` script (and integrate into arc_linter where applicable) that validates all MECHANISMS fields in plays.md against the drivermap vocabulary. For each play with zero valid drivermap IDs, emit WARN. For each invented mechanism name, list the count and suggested mapping. This is the deterministic guard against LLM drift when new plays are added — the mechanism vocabulary will re-diverge every time the library is extended without this check. Run as part of any plays.md update workflow. The reconciliation mapping in `/tmp/reconcile_mechanisms.py` is the seed for the allowed-synonym list.
_Source: S1 audit — 20 SOMATIC plays, 0 valid drivermap hits before fix; vocabulary drift is structural without a check._

**L3. ✓ DONE. Participation rate check for group ensemble plays.**
Add optional field `expected_participation` (0.0–1.0) to plays in group arcs with group_mode:ensemble or GROUP_ROLE:e. If a spike beat has expected_participation below threshold (suggest 0.7), emit WARN — "LOW_COVERAGE_RISK: spike beat may be unavailable to significant portion of group." Forces designer to confront whether the arc's cathartic beat is actually reachable.
_Source: Latitude — 4% graduation_ritual coverage; SNM — one_on_one_private_scene activation rate._

---

## Planner

**P1. ✓ DONE. Ordinal output framing.**
Change arc_planner.py output to bucket engagement scores into strong / moderate / weak rather than raw percentages. The simulation percentages are ordinal, not cardinal — direction within a profile is reliable, absolute values and cross-profile comparisons are not. False precision in the operator-facing output leads to misplaced confidence in specific numbers. Preserve raw scores in arc_plan.json for internal use; display bucketed labels in the operator-readable summary.
_Source: SNM — "treat as ordinal" finding._

**P2. ✓ DONE. Pre-arc mechanism fit report.**
Add a `--fit-report` mode to arc_planner.py that outputs mechanism fit for each play against the participant profile before running full simulation. Currently, fit scores only appear in simulation output; the designer sees them after the arc is finalized. A fit report at design time lets the operator see weak-fit plays while there's still room to swap them. Format: play ID, engagement bucket, top matching mechanisms, gap mechanisms (in profile but not in play).
_Source: SNM — Sensualist underperformance; mechanism fit as design-time variable._

**P3. ✓ DONE. Arc type × participant register annotation in heuristics table.**
The arc type selection heuristics in Pass 3 (intake.md) name the suggested arc type but not the operator requirement level when the arc type conflicts with the participant's P5 register. Add a third column — `operator requirement` — to the heuristics table. Specifically: persecution arc + "rewired" participant = elevated operator requirement; retroactive_recontextualization must be total and immediate, no delay between ordeal state and reveal. The intake should surface this condition as a named flag, not just leave it implicit.
_Source: Nicholas/CRS intake exercise — CRS ran maximum persecution arc on a "rewired" participant; the intake correctly would have flagged this as elevated-requirement without a mechanism to name it._

**P4. ✓ DONE. Identity anti-filter in play annotation.**
arc_planner.py positive-matches plays against the participant's top mechanisms. It should also run negative matching: plays whose primary mechanisms serve an identity dimension the participant has explicitly rejected (from `identity_negative_space` profile field, populated from P7 + D4b + D5) earn an `identity_fit_warning` annotation. The warning identifies which rejected dimension the play engages and how many mechanism hits triggered it. Does not change the engagement score — it's a flag for the operator to review, not an automated discard.
_Source: Nicholas/CRS intake exercise — identity negative space (not "interesting", not warm/dependent) cleanly filters play categories that the mechanism score doesn't eliminate._

---

## Plays library

**S1. Somatic mechanism vocabulary reconciliation.**
Audit all plays in the somatic, grain/texture, environmental narrative, and location-based sections. For each play, check whether its MECHANISMS field uses names that match drivermap's actual dimension names (sensory_seeking, aesthetic_response, flow_state, somatic_awareness, embodied_cognition). Where plays use substitute names (liminality_induction, social_validation) for what is actually a somatic mechanism, update to drivermap-aligned names. This is the root cause of the Sensualist profile underperformance: the planner can't match what isn't labeled correctly.
_Source: SNM — Sensualist vocabulary mismatch._

---

## Schema / notation

**N1. ✓ DONE. Persona-bound operator flag.**
Add `pb` modifier to AUTONOMY field: AUTONOMY:O·pb indicates the play's efficacy depends on a specific operator identity or relationship rather than any competent operator. Plays that worked because Hull sent them, or because the handler has an established relationship with the participant, carry this flag. Forces arc designers to be explicit about whether a play is reproducible or operator-specific. Affects scale and handoff decisions.
_Source: Latitude — Hull as performance; SNM — actor-controlled selection._

**N2. ✓ DONE. early_exit field in arc JSON schema.**
See L2. Schema addition: `"early_exit": "play_id"` at the arc level. The referenced play should be a hold or denouement beat that can be delivered at any point after the build phase begins. Document in notation_v2_spec.md.
_Source: Latitude — operator-terminated arcs._

---

## Intake

**I1. ✓ DONE. Anxiety-vs-wonder surface.**
Add explicit question to Pass 2 (participant) intake distinguishing anxiety-tolerant/seeking from wonder-seeking engagement style. Current intake surfaces interests and what moves the participant, but doesn't distinguish between participants who find the uncanny/disorienting register thrilling vs. destabilizing. This is both a safety variable (Nordic LARP apparatus — what kinds of activation should be avoided) and an engagement variable (plays like the_witness engage via hypervigilance and paranoia; they land differently depending on N-loading). Map the answer to BIG_FIVE_N and relevant mechanism dimensions in Pass 3 inference.
_Source: SNM — the_witness 47-56% across most profiles; anxiety vs. wonder mechanism split._

**I2. ✓ DONE. Ideology articulation requirement.**
Add a field to Pass 1 (sponsor) intake: "What do you want [participant] to be able to do, feel, or understand after this experience that they can't now?" This is the ideology test. If the sponsor's answer is vague, atmospheric, or describes a mood rather than a change, flag it in Pass 3 operator inference. A structurally complete arc with an unarticulated transformation target is the Latitude failure mode. The operator should not approve an arc without a clear answer to this question.
_Source: Latitude — ideology vacancy; intake as the mechanism that prevents it._

**I3. ✓ DONE. P5 register → arc ordering constraint.**
Pass 3 should generate a `p5_register` field in the participant profile (rewired / unsettled / wonder / opened / activated). arc_planner.py reads this field and applies a register ordering constraint: when `p5_register = rewired`, any play with disorientation-register mechanisms (hypervigilance, paranoia_escalation, disorientation, uncanny_recognition) earns a penalty and a warning if fewer than 2 cognitive-scaffolding plays have preceded it in the arc. The constraint fires as a warning annotation on the play and a score penalty (-15). "Rewired" participants need intellectual scaffolding before the frame destabilizes; disorientation-first causes shutdown, not engagement.
_Source: Nicholas/CRS intake exercise — "rewired" vs. "unsettled" as load-bearing arc register distinction._

**I4. ✓ DONE. E2 → CONTRAINDICATED passthrough.**
E2 (sponsor limits) should feed a `hard_constraints` list into the participant profile JSON. arc_planner.py reads this list and flags any play whose mechanisms or play ID match a constraint keyword. Currently E2 is advisory text that the operator must manually remember and apply; it has no mechanical connection to play selection. The match is intentionally approximate (substring against mechanism names and play ID) — the goal is surfacing candidates for human review, not automated blocking.
_Source: Nicholas/CRS intake exercise — Conrad's E2 correctly would have flagged CRS's ordeal escalation; no mechanical connection existed._

---

## Planner

**G1. ✓ DONE. Participation rate annotation.**
See L3. For any arc with group plays, the arc design workflow should include a step where the operator estimates expected participation rate for each ensemble beat. Arc_planner.py should incorporate this into engagement calculations — a spike beat with expected_participation:0.4 produces a very different arc shape than one with expected_participation:1.0. This also changes the "low cathartic density" check: if the spike is reachable by only 40% of the group, the effective cathartic density for the other 60% is lower than the notation shows.
_Source: Latitude — graduation_ritual coverage; SNM — lottery mechanic._

---

## Library Format

**F1. Migrate plays library from plays.md to YAML.**
YAML is the right source-of-truth format: block scalars handle multi-line prose cleanly, schema validation works via JSON Schema after yaml.safe_load(), and contributors get field enforcement rather than free-form Markdown parsing. Migration plan: (1) write a plays.md → plays.yaml converter (reuse the existing block parser in compile_strips.py), (2) update compile_strips.py to read YAML instead of MD, (3) generate plays.md from YAML for LLM readability rather than treating it as source. The compile_strips.py parser is already ~80% of the YAML reader; the main work is the schema definition and round-trip test. JSONL is not suitable — prose paragraphs become unreadable escaped single-line strings.
_Source: format discussion — schema enforcement without sacrificing contributor legibility._

---

## Miro App

**M1. Submit to Miro Marketplace.**
After a small group of testers has confirmed the app works end-to-end (plays library, linter, planner, Miro card drop), submit to the Miro Developer Console for Marketplace review. This enables one-click install for non-technical users without needing to manually register the app URL. Prerequisites: app must be public (GitHub Pages URL stable), must pass Miro's review checklist (permissions scoping, privacy policy or "no data collected" statement, icon + description). Estimated review time: 1–2 weeks.
_Source: user request — ease of install for non-technical Miro users._

---

## Not todos (genuine limits)

These came up in analysis and are confirmed out of scope — not gaps to fix.

- **Vicarious participation** ("my arc is your arc") — Guide profile in SNM, sponsor's interior arc. No representation and none planned.
- **Community-level arc** — what 1,200 members collectively experience, produce, or lose. Individual GROUP_ROLE is in scope; community arc is not.
- **Navigational agency in possibility spaces** — SNM's room-choice, Meow Wolf. System is designed for administered arcs; prescriptive power breaks down in environmental possibility spaces.
- **Ideology vacancy detection** — the notation can flag structural problems; it cannot detect whether the experience points at something real. That's the boundary between design tools and design wisdom.
- **Monetization / economic structure** — not a design domain the notation was built to cover.
