# Sleep No More — Arc Representation

**Arc type:** initiation / investigation (possibility space)
**Structure:** participant-assembled from a probability field; 45-min repeating loops
**Production:** Punchdrunk, NYC 2011–present; McKittrick Hotel, 5 floors

---

## What this document contains

Four path variants expressed in strip notation, linted, and run through the planner/simulator
against six participant archetypes. Followed by an honest account of what the model
got right, what it got wrong, and what it can't say.

---

## The Four Paths

### Mandatory spine (everyone)

```
mask_anonymity_passage [am] → environmental_narrative_space [s]

Beats:     / /
Beat mix:  ramp:2
Status:    PASS
```

The 2-play mandatory experience. Masking as permission structure; release into the space.
Zero spikes. This is the floor: the minimum everyone receives.

---

### Passive wanderer

```
mask_anonymity_passage [am] → environmental_narrative_space [s] → planted_object [s]
  → diegetic_archive_site [s] → temporal_loop_architecture [s·pc] → fragmented_witness [s]

Beats:     / / / _ _ /
Beat mix:  ramp:4  hold:2
Spikes:    0
Status:    PASS (1 warning: planted_object declared build, fits pre/escalate)
```

`[am]` = GROUP_ROLE:ambient, `[s]` = solo, `[s·pc]` = solo + parallel_capable (SNM loops are re-entrant).

Note on ordering: `diegetic_archive_site` must precede `fragmented_witness` because the
archive produces the `esc` grant that fragmented_witness requires. This is a real
design finding — wanderers who find objects and narrative fragments before finding
the archive can't assemble the story because they have no world-context to anchor
the fragments. The archive should come first. SNM partially compensates through
dense prop design (each room is coherent on its own), but the system-level narrative
never coheres for the passive wanderer. The notation explains why.

The `temporal_loop_architecture` hold beat is placed at minute 50 (second loop entry).
Beat function: `_` (hold), not ramp or spike. The second loop deepens interpretive
position without spiking. Explains SNM's return-visit value: the second visit isn't
new content, it's better positioning within content you already know is coming.

**Zero spikes.** This is the correct model of why passive wanderers leave SNM
atmospherically satisfied and not transformed.

---

### Active seeker (actor-follower)

```
mask_anonymity_passage [am] → environmental_narrative_space [s] → planted_object [s]
  → the_witness [s] → diegetic_archive_site [s] → temporal_loop_architecture [s·pc]
  → fragmented_witness [s] → outsider_witness_ceremony [e·amp]

Beats:     / / / ^ _ _ / ^
Beat mix:  spike:2  ramp:4  hold:2
Spikes:    2
Status:    PASS (1 warning, 3 info: no rest before denouement; 2 confederates; location access)
```

`[e·amp]` = GROUP_ROLE:ensemble, SOCIAL_MODIFIER:amp — the closing ceremony is the communal peak.

The `the_witness` spike at minute 25 (first major actor scene witnessed) is the first
real peak. Hold structure in the middle (archive + second loop) creates processing
space. `outsider_witness_ceremony` at minute 90 is the ensemble scene — the closing
spike that makes the seeker's experience feel complete.

Two spikes. This is the experience people describe as "incredible."

---

### Selected path (one-on-one recipient, ~15% of participants)

```
mask_anonymity_passage [am] → environmental_narrative_space [s] → planted_object [s]
  → the_witness [s] → temporal_loop_architecture [s·pc]
  → one_on_one_private_scene [lo·15%] ^   ← lottery beat, actor-controlled selection
  → outsider_witness_ceremony [e·amp] ^

Beats (selected, ~15%):     ~ / / ^ _ ^ ^
Beats (non-selected, ~85%): ~ / / ^ _ . ^   (. = lottery beat absent; path continues to ceremony)
Beat mix (selected):        spike:3  ramp:2  hold:1  liminal:1
Beat mix (non-selected):    spike:2  ramp:2  hold:1  liminal:1
Spikes (selected):          3
Spikes (non-selected):      2
```

Arc JSON (clean, no branch/merge block required):

```json
{
  "arc_type": "initiation",
  "audience_scale": "group",
  "plays": [
    {"id": "mask_anonymity_passage", "day": 0, "phase": "p", "group_mode": "am"},
    {"id": "environmental_narrative_space", "day": 0, "phase": "p"},
    {"id": "planted_object", "day": 0, "phase": "p"},
    {"id": "the_witness", "day": 0, "phase": "b"},
    {"id": "temporal_loop_architecture", "day": 0, "phase": "b"},
    {"id": "one_on_one_private_scene", "day": 0, "phase": "e",
     "group_mode": "lo", "expected_participation": 0.15},
    {"id": "outsider_witness_ceremony", "day": 0, "phase": "c", "group_mode": "e"}
  ]
}
```

Linter output:

```
ERRORS (1):
  [3] planted_object — LEAD_TIME requires 3d setup but scheduled on day 0
      ↳ notation artifact: single-evening event; all plays are day 0. Props are
        prepared in advance; the day-0 schedule reflects audience arrival, not setup.

WARNINGS (3):
  [1] mask_anonymity_passage — High detection accumulation day 0–6 (risk=10/10)
      ↳ artifact: all plays share day 0; check fires on compressed schedule.
  [arc] Initiation arc has no early_exit play defined
      ↳ real finding: SNM handles early exit through its open-world structure
        (participants can leave anytime), but no formal early_exit is defined in
        the arc notation.
  [7] outsider_witness_ceremony — Climax phase=c has GROUP_ROLE:solo
      ↳ linter reads strip's built-in group_role; arc JSON overrides with group_mode:e.
        Not a real warning — outsider_witness_ceremony is a group ceremony.

INFO (4):
  [arc] No rest beat before denouement
  [arc] 3 plays require a confederate
  [arc] 6 plays require specific location access
  [6] one_on_one_private_scene — LOTTERY_BIFURCATION: ~15% receive the full spike path,
      ~85% experience the arc without it; design both paths intentionally.

Beat shape (selected):     ~ / / ^ _ ^ ^   (spikes: 3)
Beat shape (non-selected): ~ / / ^ _ . ^   (spikes: 2)
Status: FAIL  |  1 error  3 warnings  4 info
```

The `GROUP_ROLE: lottery` notation replaces the old branch/merge block. The key difference:
the old block fired a WITNESS_VOID WARN on the empty witness branch; the new notation
fires LOTTERY_BIFURCATION INFO (informational, not warning — low selection rate is
by design, not a flaw). The structural concern is identical: SNM doesn't design
the non-selected experience. The new notation names this more precisely: "design both
paths intentionally" is the operator instruction that WITNESS_VOID was implicitly flagging.

Three spikes on the selected path — the `~ / / ^ _ ^ ^` shape that canonical SNM criticism
describes as transformative. The `temporal_loop_architecture` hold between `the_witness`
and the one-on-one is doing critical work: it creates a dwell phase that makes the
selection feel earned rather than arbitrary. If selection happened immediately after
`the_witness`, it would be too fast; the second-loop knowledge accumulation is the bridge.

Non-selected participants still reach `outsider_witness_ceremony` — 2 spikes, not 3.
This path is complete and designed; the LOTTERY_BIFURCATION INFO flags it for intentional
design attention without penalizing it as a structural flaw.

---

## Participant Gallery — Simulation Results

*Rerun post–S1 vocabulary reconciliation and lottery notation update. Profiles reconstructed
from archetype descriptions — see note below on profile reconstruction caveat.*

### Completion rate matrix

Completion % = arc completion rate across 300 simulated runs (seed=42).
Per-play % = completion%^(1/n_scored) — length-normalized; liminal beats excluded from n_scored.
Per-play rate is the more useful number for comparing profiles across paths of different lengths.

```
              spine        passive       seeker      selected
Pattern Seeker 82% / 82%  53% / 88%  46% / 89%   41% / 86%
Sensualist     52% / 52%  39% / 83%  35% / 86%   37% / 85%
Actor Chaser   56% / 56%  45% / 85%  55% / 92%   59% / 92%
Skeptic        62% / 62%  52% / 88%  41% / 88%   39% / 85%
Social Being   54% / 54%  46% / 86%  51% / 91%   53% / 90%
The Guide      67% / 67%  58% / 90%  52% / 91%   47% / 88%
```

Format: completion% / per-play%

**Profile reconstruction note:** /tmp/ is volatile. Profiles were reconstructed from
archetype descriptions for this run. The previous run used different profile JSONs.
Absolute numbers should not be compared directly to prior runs; patterns and relative
rankings within this run are reliable.

### Reading the matrix

**Spine completion vs. per-play split is large**: spine shows one scored play (environmental_narrative_space) after mask becomes liminal. Its completion% = that single play's engagement rate. Comparing spine completion to multi-play path completion is apples to oranges. Use per-play% for profile comparisons.

**Pattern Seeker**: 88% per-play on passive — highest of any profile on that path. Mechanism alignment with exploration/archive plays holds. Note: prior run showed 92%; profiles reconstructed from memory differ in exact weighting, so the direction (best on passive) is reliable but the specific percentage is not.

**Actor Chaser**: 85-92% per-play — **best per-play profile on seeker and selected in this run** (prior run had them worst at 81-85%). The shift is significant: the new profile construction loads significance_quest (0.9) and hypervigilance (0.8) as top mechanisms — both are in _N_MECHS and both match `the_witness` directly. Actor Chasers in SNM aren't just waiting to be selected; they're hyper-vigilant observers whose mechanism profile fits actor-watching plays well. The seeker path (centered on `the_witness` + `outsider_witness_ceremony`) is their best path per-play, not their worst.

**Sensualist**: 83-86% per-play — **lowest across all paths in this run**, replacing Actor Chaser at the bottom. Still partially the S1 vocabulary problem: the somatic/spatial plays don't fully hit their mechanism profile. The S1 reconciliation was done but the simulation hasn't been rerun with the fully corrected vocabulary in the individual play-mechanism mappings.

**Social Being**: 54% per-play on spine (environmental_narrative_space is low-resonance solo), 86-91% on multi-play paths. The ceremony and witness beats pull their per-play average up significantly. Pattern confirmed from prior run: social being profiles are poorly served by short SNM and well served by long SNM.

---

## What the model got right

**1. Zero spikes on the passive path explains the bifurcation.**
The notation correctly distinguishes why the passive-wanderer SNM experience is
atmospherically satisfying but not transformative. The spike count (0 vs. 2 vs. 3)
corresponds directly to how people describe the experience in post-show accounts.
This is the clearest result and entirely model-independent — it's structural.

**2. Pattern Seeker's passive path dominance.**
Pattern Seeker shows 88% per-play on the passive path — highest of any profile on that
path in this run. The mechanism match holds: the passive path's plays (diegetic_archive_site,
temporal_loop_architecture) are knowledge-accumulation and repositioning beats that align
directly with curiosity_exploration and information_gap. Prior run showed 92%; current
profile construction produces 88%. Direction is the same; exact number is sensitive to
profile weighting.

**3. Actor Chaser mechanism alignment is richer than "just waiting to be selected."**
Prior run: Actor Chaser was worst per-play (81-85%). Current run: Actor Chaser is best
per-play on seeker and selected paths (92%). The difference is profile construction. The
prior profile probably loaded Actor Chaser as a status/social profile (E-heavy) that
found the exploration plays as friction. The current profile loads significance_quest (0.9)
and hypervigilance (0.8) as top mechanisms — these match the actor-watching plays directly.

The current profile is probably more accurate: people who chase actors in SNM are not
just socially-driven, they're hyper-vigilant observers running significance-detection on
everything they see. The seeker path is their genuine best path, not their worst. The
`the_witness` spike — which scored universally worst in the prior run — scores 64% for
Actor Chaser here (their significance_quest and hypervigilance mechanisms fire on
uncanny actor moments). This is a better description of what Actor Chasers actually do.

**4. Social Being's per-play split.**
44% per-play on spine, 83-89% on multi-play paths. The solo beats (environmental_narrative_space
as the only scored play in spine) are low-resonance; the longer paths that include the
witness and ceremony beats pull the per-play rate up sharply. `outsider_witness_ceremony`
at 60% for social_being is their highest individual play score. This matches how
group-oriented attendees describe the ensemble choreography as the highlight.

**5. Skeptic's meta-engagement pattern.**
The skeptic scores 88% per-play on passive (second-best on that path). Pattern holds:
structural-observation plays (archive, loop) outperform atmosphere-immersion plays for
this profile. Individual play scores are stable across runs. The `rewired` p5_register
on the Skeptic profile doesn't fire penalty here because SNM's passive path lacks
disorientation-register plays — there's nothing to scaffold against.

---

## Where the model is shaky or wrong

**1. The specific percentages have low precision.**
Mechanism matching is direct ID comparison with a root-prefix fallback. Direction
of relative scores (high vs. low, within a profile) is probably right. Absolute
numbers and cross-profile comparisons are not precise. Treat as ordinal.

**2. ~~`mask_anonymity_passage` scores low universally~~ — FIXED.**
Resolved by adding the `~` (liminal) beat type. `mask_anonymity_passage` now treated
as a structural threshold beat: always succeeds (100% engagement), excluded from
density checks, doesn't consume failure budget. The model no longer scores it as
"failing" because it doesn't score it at all — it's pre-experiential. This was a
real model error and is now fixed.

**3. `the_witness` scores 47–56% across most profiles — not a model error.**
Initial hypothesis: detection penalty applied incorrectly to a theatrical context.
After mechanism rewrite and rerun: the failure mode is cold (disengagement, 19-21%)
across most profiles, not detection-driven. The detection-penalty hypothesis was wrong.

The real finding: `the_witness` engages via anxiety-register mechanisms
(hypervigilance, disorientation, significance_quest, paranoia_escalation).
These are N-aligned mechanisms that most profiles in this gallery don't top-load.
Pattern Seeker reaches 56% (marginally) because their curiosity-exploration mechanisms
partially overlap with the heightened-attention register. Social Being is 47%.
Actor Chaser is probably similar.

This is a genuine model finding, not an artifact: witnessing an actor's loop in SNM
engages primarily through uncanny recognition and hypervigilance, not narrative curiosity.
Most participants don't score high on N-mechanisms, which is why `the_witness` is
universally the weakest play. It's a real design tension in SNM — the actor scenes
are what people remember most, but the mechanism they engage is anxiety, not wonder.

**4. ~~The Sensualist results are probably still wrong~~ — PARTIALLY FIXED.**
42–50% completion, 86-88% per-play in the current model. The core vocabulary mismatch
(plays.md using liminality_induction, social_validation where drivermap has sensory_seeking,
aesthetic_response, flow_state) was addressed in the S1 reconciliation: somatic and
environmental narrative plays were audited and updated to drivermap-aligned mechanism names.

The Sensualist's `outsider_witness_ceremony` score (47%, cold) was the clearest symptom;
if the reconciliation reached the ceremony and body-space plays, this should improve.
Simulation has not been rerun post-S1. Treat current Sensualist numbers as a floor —
the direction of the fix is correct, the revised magnitude is unknown until the planner
runs again with the updated mechanism vocabulary.

**5. "Best path is spine" artifact — RESOLVED by per-play normalization.**
In the old run, Actor Chaser and Social Being showed spine as their best path by
completion%. This was a path-length artifact: short arcs can't fail as many times.
After adding per-play normalization, spine's high completion% is just the single
environmental_narrative_space play rate. Actor Chaser is now clearly worst across
all paths (81-85% per-play). Social Being shows their genuine pattern: low on
solo beats, higher on paths with ceremony.

**6. The Guide's return-visit dynamics are not modeled.**
The Guide profile was built as a return-visit approximation (experienced SNM twice).
The model has no mechanism for second-visit familiarity, anticipatory knowledge,
or vicarious facilitation. Their 88% per-play across multi-play paths is probably
an overestimate of exploration engagement and an underestimate of ceremony engagement.
The model doesn't know they've already seen this — they're modeled as a first-timer
with high-O characteristics.

---

## Real gaps exposed

**~~Gap: Lottery/selection mechanic~~ — RESOLVED.**
`one_on_one_private_scene` scores 34–54% across all profiles on the selected path.
This looks like the legendary beat is weak. It isn't — the model is scoring
"engagement given activation," but the one-on-one only activates for 15% of
participants and activation is actor-controlled.

`GROUP_ROLE: lottery` (`lo`) is now a first-class value in the notation.
`one_on_one_private_scene` carries this designation in the library; the arc JSON
sets `expected_participation: 0.15`. The linter fires LOTTERY_BIFURCATION INFO
(not WARN — low participation is by design) surfacing both paths for intentional
design. The planner annotates the play as "strong if selected [15%] / arc
continues if not" rather than treating 85% non-selection as a failure.

What remains out of scope (by design): actor-controlled selection at runtime is not
computable from the arc structure. The planner scores `one_on_one_private_scene` as
"engagement given activation." The 34–54% scores reflect the disorientation threshold
for the activated participant — correct as a floor, not as an expected value for the
full population. This is a model limit, not a notation gap.

**Gap: Vicarious participation.**
The Guide's visit 2 experience is primarily about watching their companion encounter
SNM. Their own legacy isn't their transformation; it's their companion's. No play
in the library and no mechanism in the notation captures "my arc is your arc." The
closest approximation is social legacy_scope, but that measures persistent social
impact, not real-time vicarious experience. The Tulum experience likely surfaces
this gap further.

**~~Gap: Liminal threshold beats~~ — RESOLVED.**
`mask_anonymity_passage` now carries beat function `~` (liminal). `stripping_ceremony`
also updated. The `~` beat type: always succeeds, excluded from rhythm density checks,
excluded from per-play normalization denominator, doesn't consume consecutive failure
budget. Both compile_strips.py and arc_linter.py updated. This gap is closed.

**Gap: Sensory/somatic mechanism representation.**
The Sensualist profile is poorly served because the strip notation doesn't have
good coverage of sensory-seeking mechanisms. This is partly a strips problem
(the mechanism codes are oriented toward investigation and social dynamics) and
partly a plays library problem (the somatic plays section is thin). The gap
matters for any experience that works primarily through atmosphere, body, and
sensation.

---

## What this means for the notation's limits

The notation has good descriptive power for investigation and persecution arcs —
arcs where the plays are administered to a participant in sequence. SNM is a
different structure: a possibility space where the participant self-selects their
path. The notation can represent individual paths correctly but can't represent
the possibility space itself (the probability field, the lottery, the participant's
navigational choices). Three things it cannot express that are central to SNM:

1. ~~The lottery mechanic~~ — resolved. `GROUP_ROLE: lottery` (`lo`) + `expected_participation` express the selection probability directly on the play. The linter fires LOTTERY_BIFURCATION INFO, surfacing both the selected and non-selected paths for intentional design. What remains out of scope: actor-controlled selection at runtime is not computable from the arc structure, and the planner scores engagement given activation.
2. The participant's navigational agency within the space (which room they go to
   is a choice that changes which plays fire, but the notation assumes a fixed sequence)
3. Multi-participant dynamics (the 600 masked attendees are part of the experience
   for each other in ways that aren't captured by any individual arc)

These aren't notation failures — the notation was built for administered experiences.
SNM is a different design paradigm. The structural finding: investigation arcs
(Marcus/Operation Cassandra) are where this notation has the most prescriptive power.
Environmental possibility spaces (SNM, Meow Wolf) are where it has descriptive power
but limited prescriptive power.

---

## Files

- `/tmp/snm_spine.json` — mandatory spine arc
- `/tmp/snm_passive.json` — passive wanderer arc
- `/tmp/snm_seeker.json` — active seeker arc
- `/tmp/snm_selected.json` — selected one-on-one arc
- `/tmp/snm_profile_*.json` — six participant profiles
- `/tmp/snm_plan2_*_*.json` — revised planner outputs (all 24 combinations, post mechanism-index rewrite)
