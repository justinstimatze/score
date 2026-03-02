# Canonical Arc Notation — Reference Expressions

Expressing famous immersive experiences in the plays notation to validate descriptive and
prescriptive power. Each analysis runs through the arc linter with actual play IDs and
surfaces real design findings.

---

## 1. Sleep No More (Punchdrunk, 2011–)

**Arc type:** initiation / investigation (participant-assembled)
**Structure:** designed possibility space, not authored sequence
**Key mechanism:** mask as permission structure; selection mechanic as lottery spike

SNM decomposes into three structural layers:
- **Mandatory spine** — 2 beats every participant receives
- **Probability field** — beats available by spatial/temporal position
- **Selection mechanic** — one-on-one, lottery-distributed (~15% of participants)

### Mandatory spine
```
mask_anonymity_passage → environmental_narrative_space
Beats: / /   Arc codes: pb pb   Beat mix: ramp:2
Status: PASS
```
Pure ramp-ramp. The mandatory spine does nothing except open permission state and release
the participant into the possibility field. Every inch of impact is in the probability field.

### Selected path (one-on-one recipient)
```
mask_anonymity_passage → environmental_narrative_space → planted_object
  → the_witness → one_on_one_private_scene → outsider_witness_ceremony

Beats:     / / / ^ ^ ^
Beat mix:  spike:3  ramp:3
Legacy:    personal:5  social:2
Status:    PASS (3 info)
```
The arc shape `/ / / ^ ^ ^` is the classic slow escalation to triple-spike close.
Three consecutive spikes, each a different modality: discovery → witness → selection → collective.

INFO: `3 plays require a confederate` — correct. SNM needs ~50 concurrent actors to make
selected-path encounters likely within a 2-hour window. The operational cost is baked into
the notation.

### Passive path (wanderer)
```
mask_anonymity_passage → environmental_narrative_space → planted_object
  → fragmented_witness → diegetic_archive_site

Beats:     / / / / _
Beat mix:  ramp:4  hold:1
Status:    PASS (1 warning)
WARN: [4] fragmented_witness — prm:Q→esc requires prior grant 'esc'
```

**Two findings:**

**No spikes.** The passive path has zero spike beats. This correctly models why wanderers
often leave SNM feeling atmospherically satisfied but not transformed. The one-on-one is
the spike delivery mechanism. Without selection, the arc is pure ramp-hold.

**Permission warning is real.** `fragmented_witness` requires the `esc` grant —
investigative license, established by prior committed exploration. A passive wanderer
hasn't earned interpretive authority; the fragmented story pieces don't cohere. In
practice: passive participants can't reconstruct the Macbeth narrative because they
haven't followed a character long enough. The fix: sequence `diegetic_archive_site` before
`fragmented_witness` — the archive establishes world-context first. SNM partially solves
this through dense, coherent prop design per room, but it's imperfect.

### SNM gaps in the notation

**1. Temporal loop architecture.** The 45-minute repeating cycle is a knowledge-accumulation
architecture — second loop, you can position yourself for a scene you now know is coming.
No play captures this. Provisional entry (flagged for addition):
```
@temporal_loop_architecture F·O·hours·2
#epist_imm·parti_det·know_acc·atten_comp [pbe] _
C·n·h·i·p·l·t
prm:S
```
Beat is `_` (hold) — it deepens interpretive position without spiking. Explains why SNM
benefits from multiple visits in a way most immersive work doesn't.

**2. Ambient actor presence.** Unmasked actors moving through masked crowd, not breaking
to interact, generating charged dread-attention. Sub-beat granularity below plays.

**3. Lottery mechanic.** The one-on-one's power is partly from *knowing it exists and
possibly not getting it*. Participants who witness others being selected receive a smaller
beat — FOMO + social proof. We model the one-on-one as a play; we don't model the lottery
observation as a distinct ambient beat available to all.

---

## 2. The Game (Fincher, 1997)

**Arc type:** persecution / conspiracy
**Structure:** tightly authored linear arc, 18 days
**Key mechanism:** retroactive recontextualization; permission front-loaded via diegetic contract

```
cold_read (d0) → barnum_profile_dispatch (d0) → planted_witness (d3)
  → briefed_confederate (d7) → false_breakthrough (d10)
  → surveillance_detection_route (d14) → stripping_ceremony (d16)
  → false_ally (d17) → ordeal_threshold (d18)
  → manufactured_crisis_reveal (d18) → graduation_ritual (d18)

Beats:     ^ ^ ^ ^ / / > / ^ ^ ^
Beat mix:  spike:7  ramp:3  transition:1
Legacy:    personal:9  social:3
Status:    FAIL — 1 error, 8 warnings
```

### What the linter found

**ERROR — barnum_profile_dispatch at day 0 needs 3d lead time.**
Correct. CRS has pre-researched Van Orton for weeks before Conrad gifts the enrollment.
The film implies days of background work before the intake interview. Real design lesson:
profiling and Barnum dispatch require lead time; you can't do it at enrollment day zero.
This is an operational error in the film's surface logic that the notation catches.

**WARN — No hold beat anywhere in arc.**
The arc is `^ ^ ^ ^ / / > / ^ ^ ^` — relentless escalation with no processing space.
This is The Game's defining quality AND its chief complaint from audiences. The linter
correctly flags it; for a persecution arc, no-hold may be intentional. **This reveals a
notation gap:** arc-type-aware lint rules. A persecution arc should be allowed to suppress
the "no hold" warning.

**WARN — false_breakthrough requires `slv` grant, not yet produced.**
`false_breakthrough` needs the participant in active solve mode, but nothing preceding it
produces `slv`. This is a real design tension in the film: Nicholas isn't really
investigating at day 10, he's confused. The notation exposes why the CRS game works less
well on passive participants than on someone who actively takes the bait. **Also surfaces a
library gap:** `slv` has no seeder plays (see Gap Analysis below).

**WARN — Detection accumulation plays 4–7 (risk=12/10).**
`briefed_confederate` through `stripping_ceremony`. Correct and intentional — this is the
window where Nicholas starts detecting the conspiracy. High detection IS the experience
from his perspective. For persecution arcs, detection accumulation isn't a warning;
it's the mechanism.

**WARN — ARC_FIT violations on 4 plays.**
The most interesting findings:
- `briefed_confederate` tagged [etc] but used in build phase
- `stripping_ceremony` tagged [pb] but used as threshold
- `graduation_ritual` tagged [etc] but used as denouement

This is The Game *inverting normal arc grammar*. The graduation party at the end feels
structurally wrong as a denouement because graduation rituals don't normally go there —
the film uses the category violation to create unease. The notation surfaces this as a
warning but can't distinguish "design bug" from "intentional subversion." **This reveals
a notation gap:** intentional arc grammar inversion as a named technique.

**INFO — 6 plays require a confederate.**
The Game employs dozens of actors, a production company, infrastructure. This is the most
expensive possible implementation of this arc type. The notation prices it correctly.

### What The Game validates

The notation correctly models:
- Why The Game works better as a film than as a real experience design (the 18-day
  compression and the no-hold relentlessness are survivable as a 2-hour film, brutal as
  actual life)
- The operational cost (confederate count) and why this arc type requires deep pockets
- The false_breakthrough permission problem — why the mark has to be *in* investigation
  mode before the false discovery pays off; you can't short-circuit solve mode

---

## 3. Meow Wolf / House of Eternal Return (2016–)

**Arc type:** investigation (environmental-only, actor-free)
**Structure:** designed possibility space, no selection mechanic, social-group oriented
**Key mechanism:** object archaeology; portal discovery; collective sense-making

```
deep_backstory_artifacts → environmental_narrative_space → multi_key_first_fragment
  → physical_object_as_key → diegetic_archive_site → distributed_truth_fragment
  → fragmented_witness → layered_secret_system → parallel_discovery

Beats:     / / / / _ / / / ^
Beat mix:  spike:1  ramp:7  hold:1
Legacy:    ephemeral:2  personal:7  social:1
Status:    PASS — 0 errors, 1 warning, 3 info
```

### What the linter found

**WARN — physical_object_as_key requires `esc` grant, not yet produced.**
Same pattern as SNM passive path. Portal objects (the washing machine, the fireplace) don't
work as keys until you're in investigation mode. In Meow Wolf, the environmental narrative
space and archive should precede the portal beats — but the pacing of a free-exploration
space means participants often hit portals before they've established world-context. This
is a real visitor experience problem: many visitors go through portals without knowing
what they're investigating, which breaks the payload.

Fix confirmed: reordering `diegetic_archive_site` before `physical_object_as_key` drops
from 2 warnings to 1 — the `esc` permission chain is satisfied. Design prescription: the
Selig family archive room should be the first room, not a portal room.

**INFO — No transition beat in 9-play arc.**
Correct. Meow Wolf has no central revelation, no pivot point. The experience is pure
accumulation without a gear change. This explains the most common complaint: "It was cool
but I didn't know what I was working toward." The notation identifies the structural
absence. Compare: SNM's selected path has a transition implied by the selection event; The
Game has `stripping_ceremony` as an explicit `>` transition. Meow Wolf has neither.

**Only 1 spike (parallel_discovery).**
Compare to SNM selected path (3 spikes) and The Game (7 spikes). Meow Wolf is almost
entirely ramps ending in a single social-comparison spike. The experience is exploratory
and atmospheric but not cathartic. The notation captures why it produces a different
emotional register: curiosity and wonder, not transformation.

**INFO — 2 plays require a confederate.**
`parallel_discovery` requires someone to compare notes with. Meow Wolf is designed for
groups, not solo visitors — the social sense-making IS the peak beat. The notation
surfaces this design assumption.

### SNM vs. Meow Wolf contrast

| | SNM | Meow Wolf |
|---|---|---|
| Spikes | 3 (selected path) | 1 |
| Hold beats | 1 (passive) | 1 |
| Transition | implied (selection) | none |
| Confederates | ~50 actors | visiting group only |
| Selection mechanic | yes (lottery spike) | no |
| Peak beat type | actor-mediated (personal) | peer comparison (social) |
| Legacy scope | personal dominant | personal dominant |

The notation confirms: Meow Wolf is SNM with the actors removed and the possibility space
made static. The structural consequence is one spike vs. three, and no lottery mechanism.
The experience cost is ~100x lower; the peak intensity ceiling is commensurately lower.

---

## Gap Analysis

### Gap 1 — `slv` grant bootstrap ✓ FIXED

`slv` (solve mode) was only produced by `false_breakthrough` itself, making it
self-referential. **Fixed:** `knowledge_frontier_seed` now produces `slv`
(`prm:S→slv`) — semantically correct, as it's the play that creates the "epistemic itch"
and names the knowledge gap. Any investigation arc that opens with `knowledge_frontier_seed`
now correctly chains through `false_breakthrough` without a permission warning.

The fix: updated `knowledge_frontier_seed` PERMISSION field in plays.md to include
"grants: mystery to be solved" + recompiled strips.

### Gap 2 — Persecution arc type suppression

The linter warns about no-hold-beat, detection accumulation, and ARC_FIT violations. For
persecution arcs, all three may be intentional design. Proposed: arc-type flag on lint
invocation (`--arc-type persecution`) that suppresses these warnings and instead checks
for correct structure: escalating detection, no processing hold, retroactive recontextualization
play present in final third.

### Gap 3 — No minimum spike density check ✓ FIXED

Added WARN to arc_linter.py: if arc > 6 plays with < 2 spikes, fires "low cathartic
density" warning. Now fires correctly on Meow Wolf (1 spike in 9 plays) and SNM passive
path (0 spikes in 5 plays once expanded).

### Gap 4 — Temporal loop architecture play

SNM's repeating 45-minute cycles and Meow Wolf's portal-world transitions are structural
elements no existing play captures. `temporal_loop_architecture` is the most immediately
needed addition — it covers any experience where time or space repeats, allowing knowledge
accumulation without additional content cost.

### Gap 5 — Lottery/selection mechanic

SNM's one-on-one is powerful partly because it's probabilistic. The *possibility* of
selection changes every participant's experience, not just those who are selected. This
is a meta-structural mechanism, not a beat. No current way to express: "this play exists
in the arc but is experienced differently depending on whether the participant receives it
or merely knows it could happen."

---

## Notation Validation Summary

Across three canonical experiences:

**What the notation gets right:**
- Correctly identifies why SNM bifurcates into qualitatively different participant experiences
- Prices operational cost (confederate count) accurately for all three
- Catches real permission sequencing problems (esc/slv grants) that match observed visitor
  failure modes
- Arc shape visualizations (`/ / / ^ ^ ^` vs `/ / / / _`) correspond to experiential
  descriptions from critical literature
- Beat type vocabulary (spike/ramp/hold/transition) has sufficient resolution to
  distinguish SNM, The Game, and Meow Wolf from each other

**What the notation cannot yet express:**
- Probability-distributed beats (lottery/selection mechanics)
- Temporal loop structures as first-class elements
- Intentional arc grammar inversion as distinct from arc grammar errors
- Arc-type-aware constraint sets (persecution, investigation, initiation require different
  validity rules)
- Sub-beat granularity (ambient actor presence, sound zone architecture)
