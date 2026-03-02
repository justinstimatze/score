# Score Notation v2 — Design Spec

**Status:** Implemented. All 8 gap areas addressed in arc_linter.py, arc_planner.py,
compile_strips.py (path fix + new fields), and arc_matchmaker.py (new).
166 tests passing. Original gap analysis below.

**Original pre-implementation status:** Pre-implementation design spec. Documents gaps exposed by:
- Group arc simulation (Marcus × 4 profiles)
- ARG canonical case research (The Beast, I Love Bees, Year Zero, Portal ARGs)
- SNM/Latitude arc analysis
- Current notation limits

This spec defines what needs to change and at what layer. It does not specify implementation — that comes after design review.

---

## Summary of gaps

| Gap | Severity | Exposed by |
|---|---|---|
| Group dynamics — no role asymmetry, social contagion, or matchmaking | Critical | Group simulation |
| Branch/merge — no model for group splits, extraction, and reintegration | Critical | SNM one-on-one, parallel tracks |
| Ambient/parallel plays — no concurrent track model | Critical | ARG research, Marcus pre-arc |
| Participation tiers — no model for mass/tiered audiences | High | ARG research |
| Threshold mechanics — no trigger-on-N-condition notation | High | I Love Bees, The Beast |
| Activation probability — lottery/selection not expressible | High | SNM, group design |
| Pre-arc infrastructure — excluded from linter by convention, not design | Medium | Marcus, Latitude |
| Recovery arc integration — recovery plays outside arc notation | Low | Planner output |

---

## 1. Group dynamics

### The problem

The notation assumes a solo participant throughout. Placing four profiles through Operation Cassandra runs four independent simulations in parallel — no model for how participants affect each other. From the simulation:

- `parallel_threads` scored 76% for Marcus and 39% for Dev. In a group, Dev's disengagement during the hold beat is visible to Marcus. That's a scene. The notation can't represent it.
- `the_false_confirmation` scores 50% across all profiles. In a group where Nadia is skeptical and Marcus believes, their disagreement is the experience. The notation models two identical individuals hitting the same play independently.

### New field: `GROUP_ROLE`

Added to plays.md schema and strip notation. Values:

| Code | Meaning | Example plays |
|---|---|---|
| `solo` | Each participant has an independent experience of this play. Default. | Most plays |
| `ensemble` | All participants experience the play together; group interaction is the mechanism | `communitas_beat`, `stripping_ceremony`, `the_us_signal`, `graduation_ritual` |
| `activated` | One or more participants are in the play; others are witnesses | `one_on_one_private_scene`, `outsider_witness_ceremony` |
| `ambient` | Play fires for the group as environmental context; no participant is singled out | `environmental_narrative_space`, `welcome_flood` |

`witness` is not a role on plays — it's a role for a participant within an `activated` play. The play is activated; some participants are activated within it, others are witnesses.

### New field: `SOCIAL_MODIFIER`

How group presence changes the play's engagement model:

| Code | Meaning |
|---|---|
| `amp` | Group presence amplifies individual engagement — collective disorientation, shared oath |
| `dist` | Group presence dilutes intensity — one-on-one is less special if six people get it |
| `req` | Play requires group presence to function at all |
| `neut` | Group presence is irrelevant to the play's engagement mechanism |

### New strip line: `grp:` (optional)

```
@stripping_ceremony F·A·sd·3
#identity_shift·liminality_induction·commitment_consistency [pbt] ~
C·n·m·r·p·m·r
prm:Q
grp:ensemble·amp
```

Compact: `grp:GROUP_ROLE·SOCIAL_MODIFIER`

### Group arc format

New arc schema. Backwards compatible — a standard flat list still works for solo arcs.

```json
{
  "arc_type": "initiation",
  "group": {
    "profiles": ["marcus.json", "nadia.json", "dev.json", "suki.json"],
    "roles": {
      "marcus": "primary_investigator",
      "nadia": "skeptic",
      "dev": "connector",
      "suki": "executor"
    }
  },
  "plays": [
    {
      "id": "the_false_confirmation",
      "day": 17, "phase": "e",
      "assignment": {
        "activated": ["marcus"],
        "witnesses": ["nadia", "dev", "suki"]
      }
    },
    {
      "id": "communitas_beat",
      "day": 21, "phase": "e"
      // no assignment = GROUP_ROLE:ensemble fires for all
    }
  ]
}
```

`assignment` is optional. Omitting it: play fires for all participants according to its GROUP_ROLE. Including it: operator specifies exactly who is activated.

### Matchmaking

A new query mode: given a profile pool and arc type, suggest pairings. The signal is the engagement matrix — which profiles have complementary high/low patterns on the same plays.

Matchmaking output flags:
- **Complementary tension**: Profiles with near-opposite engagement on a key play (useful for designed ensemble)
- **Mutual amplification**: Profiles with aligned high engagement on ensemble plays (good for communitas-type beats)
- **Chronic underservice**: A profile whose engagement floor is >20% below group mean across the arc (this person is being neglected)
- **Cascade risk**: Two or more profiles with the same dominant failure mode on the same plays (a cold failure cascades if multiple people disengage simultaneously)

### Linter additions for group arcs

- `GROUP_FLOOR`: WARN if any profile's per-play average is >20% below group mean
- `CLIMAX_COVERAGE`: ERROR if climax plays are not `ensemble` or `assignment:all` — the reveal must land for everyone
- `ACTIVATION_FATIGUE`: WARN if the same participant is `activated` in consecutive plays
- `WITNESS_DENSITY`: WARN if an `activated` play has activated:1, witnesses:0 (solo activation with no witness — defeats the social architecture)
- `DIST_PLAY_CONTEXT`: WARN if a play with `SOCIAL_MODIFIER:dist` is used for an intended peak moment (dilutes intensity at the wrong time)

---

## 2. Branch/merge — group splits, extraction, and reintegration

### The problem

`GROUP_ROLE:activated` says that one participant is extracted from the group for a play. What it cannot express:

- What the non-extracted participants experience simultaneously
- What the extracted participant's changed context (grants, emotional state) means when they return
- What play fires at the moment of reintegration — which is usually the most important moment, because it's where asymmetric context collides
- What happens when a split is permanent (an infiltrator role that never rejoins)

The SNM one-on-one is the clearest case: the selected participant has a private scene with an actor, carries `selected` + elevated status back into the general space, and the group reconvenes with asymmetric context. Without branch/merge, we can't design that reintegration or compute engagement asymmetry afterward.

### Branch/merge as a first-class arc element

A branch/merge block replaces a play in the arc sequence. It is not a play — it is a structural element that contains plays.

```json
{
  "id": "branch_one_on_one",
  "branch_point": {
    "selection": "activation_rate:0.15",
    "visible_to_group": true
  },
  "branches": {
    "activated": {
      "participants": "role:investigator",
      "plays": [
        {"id": "one_on_one_private_scene", "phase": "e"},
        {"id": "sealed_envelope_reveal",   "phase": "e"}
      ],
      "grants": ["selected", "elevated_status"]
    },
    "witness": {
      "participants": "all_others",
      "plays": [
        {"id": "the_witness",                   "phase": "e"},
        {"id": "environmental_narrative_space",  "phase": "e"}
      ]
    }
  },
  "merge_point": {
    "play": "communitas_beat",
    "context_visible": true
  }
}
```

**`branch_point`**
- `selection`: how the split happens. `activation_rate:N` for probabilistic extraction; `role:X` for deterministic role-based split; `operator_signal:ID` for manual operator-triggered split.
- `visible_to_group`: whether all participants know someone was extracted. In SNM, yes — others watch the selection happen. In a spy arc, no — the infiltrator disappears without announcement.

**`branches`**
- Named branches, each with a participant assignment and a mini-arc (list of plays).
- `participants` resolves to a subset of the group: `role:X`, `all_others`, a specific profile ID, or a count (`count:2` for two randomly selected participants).
- Each branch accumulates its own grants and context delta.
- Branch plays are linted within the branch — beat sequence, lead time, and detection checks apply inside each branch.

**`merge_point`**
- The play that fires when participants reconvene. Should almost always be a designed beat, not just a timestamp.
- `context_visible`: whether participants can see each other's differing context at reunion. If true, the merge play's engagement model should include social mechanics (status asymmetry, shared reference, exclusion/inclusion). If false, the asymmetry is latent — it will surface in how participants engage differently with subsequent plays, but not in an explicit scene.
- `merge_point: null` — explicit signal for permanent divergence (infiltrator pattern, never rejoins). Not an oversight; a design choice.

### Three patterns this handles

**Pattern 1: Extraction and return** (SNM one-on-one)
- `selection: activation_rate:0.15`
- Activated branch: `one_on_one_private_scene` → `sealed_envelope_reveal`
- Witness branch: `the_witness` → `environmental_narrative_space`
- Merge: `communitas_beat`, context_visible:true
- Post-merge: the selected participant carries `elevated_status` grant. All subsequent plays score against the context-enriched profile for that participant.

**Pattern 2: Parallel tracks** (two subgroups investigate different threads)
- `selection: role:skeptic_team / role:believer_team`
- Each branch discovers different evidence
- Merge: high-intensity spike play where teams compare notes — the meaning emerges from the collision of asymmetric knowledge
- This merge beat is the arc's peak. The linter should flag any parallel-track branch/merge whose merge_point has beat `_` or `-` — wasting the asymmetry.

**Pattern 3: Cascade extractions**
- Multiple sequential branch/merge blocks from the same group
- Group shrinks with each extraction; remaining participants accumulate "who's next" tension
- Cascade detection: the linter tracks cumulative activation across sequential branch/merge blocks and warns if the same participant is activated more than once without a sufficient hold between activations

**Pattern 4: Permanent role divergence** (infiltrator)
- `merge_point: null`
- The infiltrator's branch runs for the full arc duration
- Their plays are designed for their role; they share some ensemble plays with the group but have private plays the group doesn't know about
- The reveal (if any) is a regular arc play, not a merge_point

### Context propagation after merge

Grants accumulated inside a branch carry forward into post-merge plays. The planner:

1. Runs each branch separately, accumulating grants and context delta per participant
2. At the merge_point, combines context: activated participant has branch grants + original profile; witnesses have witness grants + original profile
3. Post-merge engagement is computed against context-enriched profiles

The asymmetry is the feature. An extracted participant scores differently on post-merge plays than witnesses — and that difference, in a well-designed arc, is perceptible and meaningful.

### Linter additions for branch/merge

- `MERGE_BEAT`: WARN if a parallel-track branch/merge has `merge_point.play` with beat `_` or `-` — reintegration of asymmetric-context participants should be a spike or transition, not a rest
- `MERGE_DESIGNED`: ERROR if a branch/merge block has no `merge_point` and no explicit `merge_point: null` — undesigned reintegration is not acceptable, force the operator to declare intent
- `WITNESS_VOID`: WARN if an `activated` branch has no corresponding `witness` branch — the non-activated participants' simultaneous experience is undesigned
- `CASCADE_FATIGUE`: WARN if the same participant is activated in more than two branch/merge blocks without an intervening hold beat at the group level
- `PERMANENT_DIVERGENCE_COVERAGE`: INFO when `merge_point: null` is used — confirm the divergent participant's arc is fully designed through the arc's end

---

## 3. Participation tiers

### The problem

Every ARG canonical case used a 4-tier participation model. The Beast (3M participants, 1K core solvers), I Love Bees (250K visitors, ~210 payphone activations), Year Zero (3M participants, 25 phone activations). Our system has no model for this. For a group experience with 12 people, the tiers collapse — everyone is in the same room. But for a public/mass experience, tier differentiation is the core design problem.

### New field: `PARTICIPATION_TIER` on plays

Which participation tier this play is designed for:

| Code | Tier | Scale | Description |
|---|---|---|---|
| `P` | Passive | Thousands–millions | Environmental/ambient content anyone can encounter. No engagement required. |
| `A` | Active | Hundreds–thousands | Requires deliberate effort: community forums, aggregating clues, following instructions. |
| `E` | Elite | Tens–hundreds | Requires specialized skill or deep investment: cipher breaking, SSTV decoding, coordinate travel. |
| `U` | Ultra-activated | Single digits to tens | Direct character interaction, physical event attendance, live voice contact. |

Most plays in the current library are designed for solo or small-group contexts — they're implicitly `U`. For mass experiences, the operator needs plays at all four tiers with designed pathways between them.

### ARG design principles encoded as linter rules

From The Beast and I Love Bees postmortems:

- `TIER_FLOOR`: WARN if a mass-audience arc has no `P`-tier plays — passive participants have no entry point
- `TIER_CEILING`: WARN if a mass-audience arc has no `U`-tier plays — no one gets the peak experience
- `COLLECTIVE_SOLVE_CALIBRATION`: INFO when an arc uses `community_solve_bait` — flag that collective intelligence routinely outpaces individual puzzle difficulty estimates by 10× (The Beast learned this on day 1)

---

## 4. Ambient/parallel plays

### The problem

The notation is strictly sequential. Every play occupies a position in the arc. But many plays run continuously in the background while other plays fire:

- Marcus's three pre-arc plays run for 8 weeks simultaneously
- `behavioral_ad` runs as ambient infrastructure for weeks
- `subscription_infiltration`, `recurring_audio_seed`, `ambient_organization_presence` — all continuous
- In the ARGs: 13 indie games updating simultaneously (Potato Sack); multiple websites advancing asynchronously (The Beast); Morse code ambient in music tracks (Year Zero)

Forcing these into the sequential beat model creates false ordering and prevents the linter from checking them properly.

### Parallel track concept

A play can belong to the **main arc** (sequential, linted as before) or a **parallel track** (concurrent, with its own start/end days and checking rules).

```json
{
  "arc_type": "investigation",
  "parallel_tracks": [
    {
      "track_id": "world_seeding",
      "purpose": "pre-arc infrastructure",
      "plays": [
        {"id": "ambient_organization_presence", "start_day": -56, "end_day": 35},
        {"id": "legend_depth_build",            "start_day": -56, "end_day": 35},
        {"id": "diegetic_archive_site",         "start_day": -28, "end_day": 35}
      ]
    },
    {
      "track_id": "ambient_pressure",
      "purpose": "background presence during arc",
      "plays": [
        {"id": "behavioral_ad",   "start_day": 0,  "end_day": 28},
        {"id": "silent_follower", "start_day": 7,  "end_day": 21}
      ]
    }
  ],
  "plays": [
    // main arc sequence as before
  ]
}
```

### New field: `PARALLEL_CAPABLE` on plays

Boolean. Whether this play can run concurrently with other plays. Most plays are not parallel-capable — they require the participant's focused attention. Ambient infrastructure plays are.

Plays that are parallel-capable: `behavioral_ad`, `ambient_organization_presence`, `ambient_number_seeding`, `recurring_audio_seed`, `subscription_infiltration`, `silent_follower`, `slow_burn_url`, `diegetic_archive_site`, `legend_depth_build`, and others.

### Linter additions for parallel tracks

- `PARALLEL_END_CONDITION`: WARN if a parallel track play has no `end_day` — ambient plays must have a designed endpoint
- `PARALLEL_OVERLAP_WITH_MAIN`: INFO when a parallel track play overlaps with a high-detection main arc play — accumulation check needs to include parallel tracks
- `PARALLEL_LEAD_TIME`: Apply the same LEAD_TIME check to parallel track plays against their `start_day`

---

## 5. Threshold mechanics

### The problem

I Love Bees introduced threshold-gated escalation: 777 successful payphone activations → live voice actor replaces prerecorded system. The Potato Sack used collective solve progress bars. The Beast's community forums accumulated until plot escalation.

None of this is expressible in current notation. Plays fire on days. There is no concept of "when condition X is met, trigger play Y."

### Threshold trigger notation

A new arc element alongside plays:

```json
{
  "thresholds": [
    {
      "id": "community_activates_voice",
      "condition": "play_count:payphone_activation >= 777",
      "triggers": {"play": "live_character_escalation", "phase": "e"}
    },
    {
      "id": "collective_solve_complete",
      "condition": "community_solve_bait:solved == true",
      "triggers": {"advance_phase": "escalate"}
    }
  ]
}
```

Threshold conditions (initial set):
- `play_count:PLAY_ID >= N` — play has fired N or more times (collective participation counter)
- `engagement_rate:PLAY_ID >= X` — rolling engagement rate above threshold
- `community_solve_bait:solved` — boolean, operator-set
- `operator_signal:SIGNAL_ID` — manual operator trigger (catch-all for live adaptation)

### Design principle from ARG postmortems

The Beast and Portal 2 both failed when their time-based pacing ran into reality. The Beast lesson: **shift from puzzle bottlenecks to narrative escalation when community outpaces design**. Portal 2 lesson: **extending a time delay does not substitute for new content**.

Threshold mechanics let you design for fast or slow community solve without committing to a fixed day. The linter should flag arcs that rely entirely on day-based timing for their climax — when the community's engagement determines the pace, hard deadlines fail.

---

## 6. Activation probability

### The problem

`one_on_one_private_scene` activates for ~15% of SNM participants. The notation scores engagement *given activation* but cannot express the probability of activation. For a group arc, who gets selected and what the other 85% experience as witnesses are both design problems.

### New field: `ACTIVATION_RATE` on plays

`1.0` (default, fires for everyone) down to `0.01` (fires for 1%). For group arcs, activation rate × group size gives expected number of activations.

Combined with GROUP_ROLE:activated, this gives the full picture:
```
GROUP_ROLE: activated
ACTIVATION_RATE: 0.15
```
→ In a group of 10, expect 1–2 activations. Others are witnesses. Witness experience must be designed.

### Linter addition

- `ACTIVATION_VOID`: WARN if a play has GROUP_ROLE:activated and ACTIVATION_RATE < 1.0 but no witness engagement model is specified — the non-activated participants' experience is undesigned

---

## 7. Pre-arc infrastructure (formalization)

### The problem

Currently handled by prose notes ("not linted"). This is fragile — lead times aren't checked, detection accumulation isn't tracked, operator timing isn't validated.

### Formal pre-arc block

```json
{
  "pre_arc": {
    "note": "Infrastructure builds. Not in main sequence. Checked separately.",
    "plays": [
      {"id": "ambient_organization_presence", "day": -56},
      {"id": "legend_depth_build",            "day": -56},
      {"id": "diegetic_archive_site",         "day": -28}
    ]
  },
  "plays": [/* main arc */]
}
```

Linting rules for pre-arc block are the same as main arc but:
- Days are relative to arc day 0 (negative = before)
- No beat sequence checks (pre-arc isn't a beat sequence)
- No FRAME_REQ checks (participant has no frame yet)
- Lead time checks apply
- Detection accumulation tracked separately from main arc

---

## 8. Recovery arc integration

### The problem

The planner suggests recovery plays but they're outside the arc notation. In today's simulation, `elegant_failure` was the most common recovery play — but the linter has never seen it. If it fires at day 17, does it affect phase? Does it consume the next slot? What happens if the recovery play itself fails?

### Recovery block notation

```json
{
  "id": "the_false_confirmation",
  "day": 17, "phase": "e",
  "recovery": {
    "cold": ["wrong_read_recovery", "breadcrumb_without_demand"],
    "confused": ["elegant_failure", "misfire_as_story"],
    "over_engaged": ["optional_path", "open_door_signal"]
  }
}
```

Recovery plays:
- Are optional (operator-triggered if failure mode fires)
- Do not advance the phase
- Do not consume a sequential beat slot
- Are linted for LEAD_TIME and CONTRAINDICATED against the parent play and its neighbors
- Contribute to detection accumulation tracking

---

## Schema delta — fields being added

### plays.md new fields

| Field | Values | Notes |
|---|---|---|
| `GROUP_ROLE` | `solo` / `ensemble` / `activated` / `ambient` | Default: `solo` |
| `SOCIAL_MODIFIER` | `amp` / `dist` / `req` / `neut` | Default: `neut` |
| `PARTICIPATION_TIER` | `P` / `A` / `E` / `U` | Default: `U` for most existing plays |
| `PARALLEL_CAPABLE` | `yes` / `no` | Default: `no` |
| `ACTIVATION_RATE` | `0.0–1.0` | Default: `1.0` |

### Strip notation additions

Current strip (5 lines max):
```
@id C·U·LT·I
#M·M [arc] bf
AT·FR·AD·LA·LG·DE·RV
prm:S|Q[→grant]
[syn:] [!ctr:] [req:]
```

New optional line after `prm:`:
```
grp:GROUP_ROLE·SOCIAL_MODIFIER·TIER·PC·AR
```

Where:
- `GROUP_ROLE`: s/e/ac/am (solo/ensemble/activated/ambient)
- `SOCIAL_MODIFIER`: amp/dist/req/neut
- `TIER`: P/A/E/U
- `PC`: parallel_capable 1/0
- `AR`: activation_rate (e.g., `1.0` or `0.15`)

Example: `grp:ac·dist·U·0·0.15` = activated, dilutes intensity, ultra-tier, not parallel-capable, 15% activation rate.

---

## New plays exposed by ARG research

The ARG cases reveal mechanics that aren't in the current library:

| Play (proposed) | Mechanism | Model |
|---|---|---|
| `threshold_escalation` | Community counter reaches N → character/content escalates | I Love Bees 777 calls |
| `collective_counter` | Visible progress bar toward group threshold; creates urgency | Potato Sack GLaDOS@Home, axon groups |
| `specialization_gate` | Puzzle that naturally filters by expertise domain | The Beast chemistry/music/morse puzzles |
| `geographic_activation` | Play fires based on participant's real-world location | I Love Bees payphones |
| `cross_platform_fragment` | Content distributed across multiple unrelated platforms | Potato Sack 13 games |

These are candidates, not commitments. Assess before adding — the library doesn't need plays for every mechanic, only plays that operators will actually use.

---

## What stays the same

- The 27-field schema for individual plays is extended (5 new fields), not replaced
- The strip format is extended (1 new optional line), not replaced
- Solo arc linting is unchanged — the new checks only fire when group/parallel/threshold elements are present
- Existing canonical arc documents (SNM, Latitude, Marcus) remain valid — they're solo arcs using the existing format

---

## Implementation order (suggested)

1. **Pre-arc infrastructure formalization** — quickest win, low risk, addresses a known fragile convention
2. **Branch/merge** — first-class arc structural element; required before group dynamics can be fully specified
3. **Ambient/parallel plays** — needed for Marcus's arc to be fully lintable; affects compile_strips.py and arc_linter.py
4. **Group dynamics** (GROUP_ROLE + SOCIAL_MODIFIER + group arc format + matchmaking) — most complex, most important
5. **Participation tiers** — add PARTICIPATION_TIER field and tier-aware linter checks
6. **Activation probability** — ACTIVATION_RATE field + witness engagement model in planner
7. **Threshold mechanics** — new arc schema element + conditional trigger model
8. **Recovery arc integration** — inline recovery blocks, linter and planner updates
9. **New ARG plays** — add post-implementation, after the schema is stable

---

## Design decisions (resolved)

1. **Group role assignment granularity**: Per-play `assignment` with per-profile default roles. Profile roles define defaults (e.g., `marcus: primary_investigator` → operator knows which plays to activate Marcus for); per-play `assignment` overrides when the operator needs explicit control. Maximum expressiveness without requiring verbose assignment on every play.

2. **Witness engagement model**: Option (b) — separate `WITNESS_MECHANISMS` field on plays. Plays that have an `activated` GROUP_ROLE can carry a second mechanism list specifically for witness engagement. Planner scores witness experience against witness mechanisms, not against activated mechanisms with a flat penalty. This is more principled and lets witness experience be intentionally designed (social_proof, status_signaling, tension_holding) rather than approximated.

3. **Threshold condition language**: Stay simple. The initial condition vocabulary (`play_count:N`, `engagement_rate:N`, `community_solve_bait:solved`, `operator_signal:ID`) covers the known ARG cases. The `operator_signal` escape hatch handles anything compound or context-dependent — the operator makes the judgment call and signals it manually. Formal expression language is not worth the implementation cost at this stage.

4. **GROUP_ROLE backfill**: Full backfill — GROUP_ROLE is a required field on all plays. `solo` is the correct default for most existing plays and is accurate, not just a fallback. A migration script backfills `solo` across all 348 plays; non-solo plays are hand-assigned. This is the same approach used for LEGACY_SCOPE and WITNESS_STRUCTURE.

5. **Matchmaking as linter feature or separate tool**: Separate tool — `arc_matchmaker.py`. Matchmaking is pre-arc design work, not arc validation. The linter runs on a completed arc spec; matchmaking runs on a profile pool before the arc is designed. Different moment in the workflow, different interface. The matchmaker reads the engagement matrix output from the planner and suggests groupings; the linter then validates the resulting arc.
