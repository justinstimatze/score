#!/usr/bin/env python3
"""
compile_strips.py

Compiles all plays in plays.md to reasoning strips — a dense notation
suitable for LLM arc-design reasoning.

Output: plays_strips.md — one strip per play, ~20-30 tokens each.
Total for 347 plays: ~8-10k tokens (fits in a single context window).

Strip format (reasoning fields only):
  @id C·U·LT·I
  #M1·M2·... [arc] bf
  AT·FR·AD·LA·LG·DE·RV
  prm:MODE[→grant]
  [syn:play_id·...]
  [!ctr:play_id·...]
  [req:code·...]

Implication rules (dots = inferred):
  R1: spike → naive frame (69%)
  R2a: spike → brief dwell (77%)
  R2b: hold → sustained dwell (71%)
  R4: confederate autonomy → responsive feedback (70%)
  R7: identity landscape → personal legacy (99%)
"""

import re
import json
import sys
import subprocess
import yaml
from pathlib import Path
from collections import Counter

PLAYS_FILE = Path(__file__).parent / "plays.md"
YAML_FILE  = Path(__file__).parent / "plays.yaml"
OUTPUT_FILE = Path(__file__).parent / "plays_strips.md"

# ── CODEBOOKS ─────────────────────────────────────────────────────────────────

COST = {"free": "F", "low": "L", "mid": "M", "high": "H",
        "ongoing": "$", "varies": "?", "goodwill": "G"}

AUTONOMY = {
    "agent": "A", "human_assist": "HA", "human_managed": "HM",
    "confederate": "C", "confederate-assist": "CA",
    "confederate-required": "CR", "operator": "O",
}

INTENSITY = {"low": "1", "medium": "2", "high": "3", "extreme": "4", "varies": "?"}

BEAT_FUNCTION = {
    "spike": "^", "ramp": "/", "hold": "-", "rest": "_", "transition": ">", "liminal": "~",
    "spike · transition": "^>", "ramp (setup) · spike (revelation)": "/^",
}

# Extended arc codes — adds threshold(t) and revelation(r) missing from spec
ARC_TOKENS = {
    "pre": "p", "open": "p", "build": "b", "escalate": "e",
    "threshold": "t", "climax": "c", "denouement": "d",
    "revelation": "r", "reinforcement": "R", "any": "*",
}

AGENCY_TYPE = {
    "revealed": "R", "constructed": "C", "borrowed": "B",
    "suspended": "S", "constrained": "X", "mirrored": "M",
    "emergent": "E",
    "revealed · borrowed": "RB",
}

FRAME_REQ = {"naive": "n", "primed": "q", "any": "*", "meta": "m",
             "naive · primed": "nq", "primed · meta": "qm",
             "naive · primed": "nq", "naive (during setup) · meta (after reveal)": "nm",
             "naive → meta": "nm"}

AGENCY_DEMAND = {"passive": "p", "low": "l", "medium": "m", "high": "h"}

LANDSCAPE = {"action": "a", "identity": "i", "both": "+"}

# Legacy scope: multi-value, codes concatenated
LS_TOKENS = {"ephemeral": "e", "personal": "p", "social": "s", "world_mark": "w"}

DETECTION = {
    "immediate": "i", "short": "s", "medium": "m", "long": "l",
    "never_solo": "n", "session": "S", "multi-day": "D", "transparent": "t",
    "none": "n", "low": "s",  # low = short window; none = never_solo
    "varies": "?",
}

REVERSIBILITY = {
    "trivial": "t", "easy": "e", "difficult": "d", "irreversible": "x",
    "low": "d", "moderate": "m",
}

# ── V2 CODEBOOKS ──────────────────────────────────────────────────────────────

GROUP_ROLE = {
    "solo": "s", "ensemble": "e", "activated": "ac", "ambient": "am", "lottery": "lo",
}
GROUP_ROLE_DEFAULT = "s"

SOCIAL_MODIFIER = {
    "amp": "amp", "dist": "dist", "req": "req", "neut": "neut",
}
SOCIAL_MODIFIER_DEFAULT = "neut"

PARTICIPATION_TIER = {
    "passive": "P", "active": "A", "elite": "E",
    "ultra_activated": "U", "ultra-activated": "U",
    "P": "P", "A": "A", "E": "E", "U": "U",
}
PARTICIPATION_TIER_DEFAULT = "U"

# Extended mechanism codebook (covers actual top-40 + notation spec)
MECH = {
    "significance_quest": "SQ", "hypervigilance": "HV",
    "curiosity_exploration": "CE", "pattern_completion": "PC",
    "need_for_closure": "NC", "reward_escalation": "RE",
    "social_comparison": "SC", "social_validation": "SV",
    "social_proof": "SP", "loss_aversion": "LA",
    "identity_dissonance": "ID", "identity_affirmation": "IA",
    "identity_confrontation": "IC", "autonomy_support": "AU",
    "evidence_collection": "EV", "commitment_consistency": "CO",
    "reciprocity": "RC", "attachment_formation": "AT",
    "trust_formation": "TR", "trust_build": "TR", "trust_calibration": "TR",
    "mystery_sustain": "MS", "shame_honor": "SH",
    "mirror_recognition": "MR", "temporal_pressure": "TP",
    "witness_need": "WN", "counterfactual": "CF",
    "agency_confirm": "AG", "social_obligation": "SO",
    "fear_vigilance": "FV", "anticipation": "AN",
    "story_integration": "SI", "pride": "PD",
    "parasocial_attachment": "PA", "pattern_recognition": "PR",
    "meaning_construction": "MC", "epistemic_uncertainty": "EU",
    "obedience_authority": "OA", "nostalgia": "NS",
    "legitimacy": "LG", "narrative_gap_filling": "NG",
    "emotional_contagion": "EC", "apophenia_induction": "AI",
    "ambient_information_seeding": "AS", "curiosity_gap": "CG",
    "cognitive_dissonance": "CD", "temporal_anchoring": "TA",
    "attentional_narrowing": "AN2", "perceptual_sensitization": "PS",
    "authority_cue": "AC", "uncanny_recognition": "UR",
    "paranoia_escalation": "PE", "relief": "RL",
    "urgency": "UG", "ambient_presence": "AP",
    "sunk_cost": "SK", "emotional_deepening": "ED",
    "disorientation": "DI", "reality_threshold_crossing": "RT",
    "confirmation_bias": "CB", "narrative_transportation": "NT",
    "somatic_marker": "SM", "embodied_cognition": "EM",
    "reality_anchoring": "RA", "gift_surprise": "GS",
    "unexplained_presence": "UP", "social_network_anchoring": "SN",
    "information_asymmetry": "IV", "identity_suspension": "IS",
    "place_attachment": "PL", "retroactive_complicity": "RX",
    "embodied_revision": "EB", "metacognitive_doubling": "MD",
    "artifact_as_authority": "AA", "narrative_coherence": "NC2",
    "future_self_projection": "FS", "identity_weight": "IW",
    "collective_effervescence": "CL", "belonging": "BL",
    "uncanny": "UC", "grief": "GR",
    # ritual / experiential mechanisms
    "rite_of_passage": "RP", "status_elevation": "SE",
    "liminal_transition": "LT2", "ritual_marking_of_threshold": "RT2",
    "liminality": "LM", "communitas": "CM",
    # additional observed mechanisms (top-frequency missing)
    "narrative_gap_filling": "NG", "information_gap": "IG",
    "surveillance_sensation": "SS", "reality_distortion": "RD",
    "paranoia_induction": "PI", "cognitive_load": "CL2",
    "choice_architecture": "CH", "anchoring": "ANC",
    "identity_threat": "IT", "retrospective_validation": "RV2",
    "awe_induction": "AW", "threat_appraisal": "TA",
    "obligation_induction": "OI", "narrative_seeding": "NS2",
    "priming": "PM", "disclosure_reciprocity": "DR",
    "signal_salience": "SL", "unexplained_benefit": "UB",
    "threshold_amplification": "TA2", "environmental_anchoring": "EA",
    "novelty": "NV", "hot_cold_empathy_gap": "HCG",
    "territorial_instinct": "TI", "trust_violation": "TV",
    "guilt": "GT", "recognition_hunger": "RH",
    "pattern_detection": "PDT", "anticipatory_tension": "ANT",
    "autonomy_illusion": "AIL", "meaning_making": "MM",
    "reality_testing": "RTT", "identity_investment": "IIV",
    "in_group_identity": "IGI", "cognitive_reframing": "CRF",
    "behavioral_commitment": "BCM", "self_perception_theory": "SPT",
    "earned_access": "EAC", "competence_reward": "CPR",
    "pattern_disruption": "PDR", "retroactive_significance": "RSG",
    "curiosity_induction": "CIN", "vulnerability_as_data": "VAD",
    "environmental_attunement": "EAT", "chronobiological_coupling": "CBC",
    "expectation_violation": "EXV", "reactance": "RXN",
    "shame": "SHM2", "mere_exposure_effect": "MEE",
    "object_mediated_affect": "OMA", "physical_presence_signaling": "PPS",
    "tactile_memory_encoding": "TME", "sensory_specificity": "SNS",
    "ambient_authority": "AAU", "social_accountability": "SAC",
    "information_withholding": "IWH", "controlled_revelation": "CRV",
    "temporal_displacement": "TDP", "future_self_continuity": "FSC",
    "grief_activation": "GRA", "memorial_anchoring": "MAA",
    "curiosity_resolution": "CRS", "identity_coherence": "ICH",
    "self_verification": "SVF", "role_embodiment": "REM",
    "narrative_immersion": "NIM", "suspension_of_disbelief": "SOD",
}

# Permission mode inference
def parse_permission(perm_text: str) -> str:
    if not perm_text:
        return "prm:S"
    t = perm_text.lower()
    mode = "Q" if any(w in t for w in ["requires", "sequenced", "prior", "cannot standalone",
                                        "not standalone", "only after", "must follow"]) else "S"
    # Grant inference
    grant = ""
    if "grants" in t:
        grants_part = t[t.index("grants"):]
        if any(w in grants_part for w in ["escalat", "intensit"]):
            grant = "esc"
        elif any(w in grants_part for w in ["trust", "channel"]):
            grant = "trt"
        elif any(w in grants_part for w in ["identity", "self-concept", "shift"]):
            grant = "ids"
        elif any(w in grants_part for w in ["closure", "resolution", "path"]):
            grant = "cls"
        elif any(w in grants_part for w in ["surveil", "ambient"]):
            grant = "asr"
        elif any(w in grants_part for w in ["contact", "ongoing", "continued"]):
            grant = "sct"
        elif any(w in grants_part for w in ["solved", "victory", "won"]):
            grant = "slv"
        elif any(w in grants_part for w in ["knowledge", "knows", "learned",
                                             "experienced", "understanding"]):
            grant = "klg"
    return f"prm:{mode}" + (f"→{grant}" if grant else "")


def parse_requires(req_text: str) -> str:
    if not req_text or req_text.lower() in ("none", "—", "-", ""):
        return ""
    t = req_text.lower()
    codes = []
    if any(w in t for w in ["cash", "money", "payment"]):
        codes.append("csh")
    if any(w in t for w in ["confederate", "actor", "plant"]):
        codes.append("cnf")
    if any(w in t for w in ["local", "location", "on-site", "in person"]):
        codes.append("loc")
    if any(w in t for w in ["osint", "research", "investigation"]):
        codes.append("osn")
    if any(w in t for w in ["trust", "relationship", "rapport"]):
        codes.append("trst")
    if any(w in t for w in ["intake", "data", "profile", "info"]):
        codes.append("inq")
    if any(w in t for w in ["investigation arc", "active arc"]):
        codes.append("inv")
    if any(w in t for w in ["technical", "skill", "expertise"]):
        codes.append("tsk")
    if any(w in t for w in ["sponsor", "client"]):
        codes.append("spn")
    if any(w in t for w in ["license", "legal", "permit"]):
        codes.append("lic")
    if not codes:
        return ""  # unclassifiable REQUIRES — omit rather than emit garbage
    return "req:" + "·".join(codes)


def encode_lead_time(lt: str) -> str:
    lt = lt.lower().strip().replace("\u2013", "-").replace("\u2014", "-")
    if lt in ("none", "0", ""):
        return "0"
    if "same day" in lt:
        return "sd"
    if re.search(r"\b(8|8\+)\s*week", lt):
        return "8w"
    if re.search(r"\b4\s*week", lt):
        return "4w"
    if re.search(r"\b(14|two weeks|2 weeks)\b", lt):
        return "2w"
    if re.search(r"\b1[\s-]?2\s*week|1-2w", lt):
        return "2w"
    if re.search(r"\b2\s*week|2w\b", lt):
        return "2w"
    if re.search(r"\b[2-9][\s-]\d+\s*day", lt):   # e.g. "2-5 days", "3-7 days"
        return "3d"
    if re.search(r"\b1[\s-]\d+\s*day|1-3d", lt):  # "1-3 days", "1-2 days"
        return "3d"
    if re.search(r"\b1\s*week|7\s*day|1w\b", lt):
        return "1w"
    if re.search(r"\b3\s*day|3d\b", lt):
        return "3d"
    if re.search(r"\b1\s*day|24h|1d\b", lt):
        return "1d"
    if re.search(r"\b[<1]\s*hour|immediate|instant\b", lt):
        return "0"
    # fallback: first token stripped to alnum
    return re.sub(r"[^a-z0-9+]", "", lt.split()[0])[:4]


def encode_arc(arc_raw: str) -> str:
    """Parse messy ARC_FIT strings into compact bracket notation."""
    if not arc_raw:
        return "[*]"
    # Normalize separators
    normalized = re.sub(r"[,/·→()\[\]]", " ", arc_raw.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    # Extract known arc tokens
    found = []
    order = ["p", "b", "e", "t", "c", "r", "d", "R", "*"]
    for word in normalized.split():
        word = word.strip(".,;")
        code = ARC_TOKENS.get(word)
        if code and code not in found:
            found.append(code)
    if not found:
        if "any" in arc_raw.lower() or "*" in arc_raw:
            return "[*]"
        return "[?]"
    # Sort by canonical order
    sorted_codes = sorted(found, key=lambda x: order.index(x) if x in order else 99)
    return "[" + "".join(sorted_codes) + "]"


def mech_abbr(name: str) -> str:
    """Readable 8-char mechanism abbreviation — semantic enough for LLM reasoning."""
    code = MECH.get(name)
    if code:
        return code
    # Readable truncation: first word up to 5 chars + underscore + first word of remainder up to 3
    words = name.split("_")
    if len(words) == 1:
        return words[0][:8]
    return words[0][:5] + "_" + words[-1][:3]


def encode_mechanisms(mech_raw: str) -> str:
    if not mech_raw:
        return "#?"
    # Normalize: strip parenthetical notes, split on · or ,
    cleaned = re.sub(r"\s*\([^)]*\)", "", mech_raw)
    parts = [m.strip() for m in re.split(r"[·,]", cleaned) if m.strip()]
    codes = [mech_abbr(p) for p in parts]
    return "#" + "·".join(codes)


def encode_legacy(ls_raw: str) -> str:
    if not ls_raw:
        return "?"
    parts = [p.strip() for p in ls_raw.split("·")]
    codes = []
    for p in parts:
        code = LS_TOKENS.get(p)
        if code:
            codes.append(code)
        else:
            codes.append("?")
    # Canonical order: e p s w
    ordered = []
    for code in ["e", "p", "s", "w"]:
        if code in codes:
            ordered.append(code)
    return "".join(ordered) if ordered else "?"


def encode_synergizes(raw: str) -> str:
    if not raw or raw.lower() in ("none", "—", "-", ""):
        return ""
    # Extract play IDs (snake_case words)
    ids = re.findall(r"\b[a-z][a-z0-9_]+\b", raw)
    ids = [i for i in ids if len(i) > 3 and "_" in i][:6]  # cap at 6
    return "syn:" + "·".join(ids) if ids else ""


def encode_contraindicated(raw: str) -> str:
    if not raw or raw.lower() in ("none", "—", "-", ""):
        return ""
    ids = re.findall(r"\b[a-z][a-z0-9_]+\b", raw)
    ids = [i for i in ids if len(i) > 3 and "_" in i][:6]
    return "!ctr:" + "·".join(ids) if ids else ""


# ── PARSER ────────────────────────────────────────────────────────────────────

def parse_play(block: str) -> dict | None:
    """Extract all fields from a play block (Markdown source)."""
    id_m = re.match(r"`id:([^`]+)`", block)
    if not id_m:
        return None
    rec = {"id": id_m.group(1)}

    # Inline tags
    for field in ["COST", "AUTONOMY", "LEAD_TIME", "INTENSITY"]:
        m = re.search(r"`" + field + r":([^`]+)`", block)
        rec[field] = m.group(1).strip() if m else ""

    # Bold fields
    for field in ["MECHANISMS", "ARC_FIT", "BEAT_FUNCTION", "AGENCY_TYPE",
                  "FRAME_REQUIREMENT", "AGENCY_DEMAND", "LANDSCAPE", "LEGACY_SCOPE",
                  "DETECTION_WINDOW", "REVERSIBILITY", "PERMISSION",
                  "SYNERGIZES_WITH", "CONTRAINDICATED_AFTER", "REQUIRES",
                  "GROUP_ROLE", "SOCIAL_MODIFIER", "PARTICIPATION_TIER",
                  "PARALLEL_CAPABLE", "ACTIVATION_RATE", "WITNESS_MECHANISMS"]:
        m = re.search(r"\*\*" + field + r":\*\*\s*([^\n]+)", block)
        rec[field] = m.group(1).strip() if m else ""

    return rec


def load_plays_yaml(yaml_path: Path = None) -> list[dict]:
    """Load plays from plays.yaml and return list of dicts with UPPERCASE keys.

    This is the YAML-based replacement for the Markdown parse_play() path.
    The returned dicts have uppercase keys matching what compile_strip() expects,
    with list fields joined back to the · separated string format.
    """
    if yaml_path is None:
        yaml_path = YAML_FILE

    with yaml_path.open(encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))

    plays = []
    for doc in docs:
        if not doc or not isinstance(doc, dict):
            continue

        # YAML has lowercase keys and list fields.
        # compile_strip() and generate_qfi_sections() expect uppercase string fields.
        # Map back:

        def join_dot(lst):
            """Join a list with ' · ' separator (how MD stores list fields)."""
            if not lst:
                return ""
            if isinstance(lst, list):
                return " · ".join(str(x) for x in lst)
            return str(lst)

        def first_or_empty(lst):
            """Get first item of a list or the value itself."""
            if isinstance(lst, list):
                return lst[0] if lst else ""
            return str(lst) if lst else ""

        rec = {
            "id":                doc.get("id", ""),
            "COST":              doc.get("cost", ""),
            "AUTONOMY":          doc.get("autonomy", ""),
            "LEAD_TIME":         doc.get("lead_time", ""),
            "INTENSITY":         doc.get("intensity", ""),
            # List fields joined with · for the existing encode_* functions
            "MECHANISMS":        join_dot(doc.get("mechanisms", [])),
            "ARC_FIT":           join_dot(doc.get("arc_fit", [])),
            "BEAT_FUNCTION":     doc.get("beat_function", ""),
            "AGENCY_TYPE":       doc.get("agency_type", ""),
            "FRAME_REQUIREMENT": doc.get("frame_requirement", ""),
            "AGENCY_DEMAND":     doc.get("agency_demand", ""),
            "LANDSCAPE":         doc.get("landscape", ""),
            "LEGACY_SCOPE":      join_dot(doc.get("legacy_scope", [])),
            "DETECTION_WINDOW":  doc.get("detection_window", ""),
            "REVERSIBILITY":     doc.get("reversibility", ""),
            "PERMISSION":        doc.get("permission", ""),
            "SYNERGIZES_WITH":   join_dot(doc.get("synergizes_with", [])),
            "CONTRAINDICATED_AFTER": join_dot(doc.get("contraindicated_after", [])),
            "REQUIRES":          join_dot(doc.get("requires", [])),
            # QFI needs these as strings too
            "FEEDBACK_TYPE":     doc.get("feedback_type", ""),
            "DWELL_TIME":        doc.get("dwell_time", ""),
            # V2 group fields (not in schema, default empty)
            "GROUP_ROLE":        doc.get("group_role", ""),
            "SOCIAL_MODIFIER":   doc.get("social_modifier", ""),
            "PARTICIPATION_TIER": doc.get("participation_tier", ""),
            "PARALLEL_CAPABLE":  doc.get("parallel_capable", ""),
            "ACTIVATION_RATE":   doc.get("activation_rate", ""),
            "WITNESS_MECHANISMS": doc.get("witness_mechanisms", ""),
        }
        plays.append(rec)

    return plays


def compile_strip(play: dict) -> str:
    """Compile a play dict to its reasoning strip."""
    pid = play["id"]

    # L1
    cost = COST.get(play["COST"], f"~{play['COST'][:3]}")
    auto = AUTONOMY.get(play["AUTONOMY"], f"~{play['AUTONOMY'][:3]}")
    lt = encode_lead_time(play["LEAD_TIME"])
    inten = INTENSITY.get(play["INTENSITY"], "?")
    l1 = f"@{pid} {cost}·{auto}·{lt}·{inten}"

    # L2
    mechs = encode_mechanisms(play["MECHANISMS"])
    arc = encode_arc(play["ARC_FIT"])

    # Beat function — normalize
    bf_raw = play["BEAT_FUNCTION"].lower().strip()
    bf = BEAT_FUNCTION.get(bf_raw)
    if bf is None:
        for k, v in BEAT_FUNCTION.items():
            if bf_raw.startswith(k.split("·")[0].split(" ")[0]):
                bf = v
                break
    if bf is None:
        bf = "?"
    l2 = f"{mechs} {arc} {bf}"

    # L3 (reasoning subset: AT·FR·AD·LA·LG·DE·RV, 7 positions)
    at = AGENCY_TYPE.get(play["AGENCY_TYPE"], "?")

    fr_raw = play["FRAME_REQUIREMENT"].lower().strip()
    fr = FRAME_REQ.get(fr_raw)
    if fr is None:
        fr = FRAME_REQ.get(fr_raw.split("·")[0].strip(), "?")

    ad = AGENCY_DEMAND.get(play["AGENCY_DEMAND"].lower().split("(")[0].strip().split()[0] if play["AGENCY_DEMAND"] else "", "?")
    la = LANDSCAPE.get(play["LANDSCAPE"], "?")
    lg = encode_legacy(play["LEGACY_SCOPE"])
    de_raw = play["DETECTION_WINDOW"].lower().split("(")[0].strip()
    de = DETECTION.get(de_raw, "?")
    rv_raw = play["REVERSIBILITY"].lower().split("(")[0].strip()
    rv = REVERSIBILITY.get(rv_raw, "?")
    l3 = f"{at}·{fr}·{ad}·{la}·{lg}·{de}·{rv}"

    # L4 constraints
    prm = parse_permission(play["PERMISSION"])
    syn = encode_synergizes(play["SYNERGIZES_WITH"])
    ctr = encode_contraindicated(play["CONTRAINDICATED_AFTER"])
    req = parse_requires(play["REQUIRES"])

    lines = [l1, l2, l3, prm]
    if syn:
        lines.append(syn)
    if ctr:
        lines.append(ctr)
    if req and req != "req:":
        lines.append(req)

    # grp: line — only emit when any value is non-default
    grp_raw = play.get("GROUP_ROLE", "").lower().strip()
    grp = GROUP_ROLE.get(grp_raw, GROUP_ROLE_DEFAULT)

    sm_raw = play.get("SOCIAL_MODIFIER", "").lower().strip()
    sm = SOCIAL_MODIFIER.get(sm_raw, SOCIAL_MODIFIER_DEFAULT)

    tier_raw = play.get("PARTICIPATION_TIER", "").strip()
    tier = PARTICIPATION_TIER.get(tier_raw, PARTICIPATION_TIER.get(tier_raw.lower(), PARTICIPATION_TIER_DEFAULT))

    pc_raw = play.get("PARALLEL_CAPABLE", "").lower().strip()
    pc = "1" if pc_raw in ("yes", "true", "1") else "0"

    ar_raw = play.get("ACTIVATION_RATE", "").strip()
    try:
        ar = float(ar_raw) if ar_raw else 1.0
    except ValueError:
        ar = 1.0
    ar_str = f"{ar:.2f}" if ar != 1.0 else "1.0"

    is_default_grp = (grp == GROUP_ROLE_DEFAULT and sm == SOCIAL_MODIFIER_DEFAULT
                      and tier == PARTICIPATION_TIER_DEFAULT and pc == "0" and ar == 1.0)
    if not is_default_grp:
        lines.append(f"grp:{grp}·{sm}·{tier}·{pc}·{ar_str}")

    # wit: line — only emit when GROUP_ROLE is activated AND WITNESS_MECHANISMS provided
    wit_raw = play.get("WITNESS_MECHANISMS", "").strip()
    if grp == "ac" and wit_raw and wit_raw.lower() not in ("none", "—", "-", ""):
        cleaned = re.sub(r"\s*\([^)]*\)", "", wit_raw)
        wit_parts = [m.strip() for m in re.split(r"[·,]", cleaned) if m.strip()]
        wit_codes = [mech_abbr(p) for p in wit_parts]
        lines.append("wit:" + "·".join(wit_codes))

    return "\n".join(lines)


# ── QFI AUTO-SECTION GENERATOR ────────────────────────────────────────────────

def generate_qfi_sections(plays: list) -> str:
    """Regenerate the 4 auto-deterministic QFI sections from parsed plays.

    Sections: By Beat Function, By Feedback Type, By Frame Requirement, By Dwell Time.
    Multi-value fields (separated by ' · ') are split so a play appears in each sub-group.
    Play IDs within each group are sorted alphabetically.
    """
    from collections import defaultdict

    FIELDS = [
        ("BEAT_FUNCTION",     "By Beat Function"),
        ("FEEDBACK_TYPE",     "By Feedback Type"),
        ("FRAME_REQUIREMENT", "By Frame Requirement"),
        ("DWELL_TIME",        "By Dwell Time"),
    ]

    section_parts = []
    for field, heading in FIELDS:
        idx: dict[str, list[str]] = defaultdict(list)
        for play in plays:
            val = play.get(field, "").strip()
            if not val:
                continue
            if " · " in val:
                for v in val.split(" · "):
                    v = v.strip()
                    if v:
                        idx[v].append(play["id"])
            else:
                idx[val].append(play["id"])
        for v in idx:
            idx[v].sort()

        lines = [f"### {heading}", ""]
        for val in sorted(idx.keys()):
            pids = idx[val]
            lines.append(f"**{val}** ({len(pids)}): " + " · ".join(pids))
            lines.append("")
        section_parts.append("\n".join(lines))

    return "\n\n".join(section_parts) + "\n"


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Load from YAML (source of truth) if available, else fall back to MD
    if YAML_FILE.exists():
        print(f"Loading plays from {YAML_FILE}...")
        plays = load_plays_yaml(YAML_FILE)
        print(f"Loaded: {len(plays)} plays from YAML")
    else:
        # Fallback: parse Markdown directly (legacy path)
        print(f"WARNING: plays.yaml not found, falling back to plays.md...")
        content = PLAYS_FILE.read_text()
        blocks = re.split(r"(?=^`id:)", content, flags=re.MULTILINE)
        blocks = [b.strip() for b in blocks if b.strip().startswith("`id:")]
        print(f"Parsing {len(blocks)} play blocks...")
        plays = []
        failed = []
        for block in blocks:
            play = parse_play(block)
            if play:
                plays.append(play)
            else:
                failed.append(block[:60])
        print(f"Parsed: {len(plays)}  Failed: {len(failed)}")

    # Compile strips
    strips = []
    total_tokens = 0
    for play in plays:
        strip = compile_strip(play)
        strips.append((play["id"], strip))
        # rough token estimate
        total_tokens += len(strip.split()) * 1.3

    print(f"Compiled {len(strips)} strips")
    print(f"Estimated total tokens: ~{int(total_tokens):,}")
    print(f"Avg per play: ~{int(total_tokens / len(strips))} tokens")

    # Field coverage check
    unknowns = Counter()
    for _, strip in strips:
        for tok in strip.split():
            if tok.startswith("~") or tok == "?":
                unknowns[tok] += 1
    if unknowns:
        print(f"\nUnknown/fallback tokens (top 20):")
        for tok, c in unknowns.most_common(20):
            print(f"  {tok}: {c}")

    # Write output
    out_lines = [
        "# Plays — Reasoning Strips",
        "",
        "Dense notation for LLM arc-design reasoning.",
        "Each strip: ~20-30 tokens. Full library: ~8-10k tokens.",
        "",
        "## Notation (Reasoning Strip Format)",
        "",
        "```",
        "@id  C·U·LT·I         cost · autonomy · lead_time · intensity",
        "#M·M [arc] bf         mechanisms · arc_fit · beat_function",
        "AT·FR·AD·LA·LG·DE·RV  agency_type · frame_req · agency_demand · landscape · legacy · detection · reversibility",
        "prm:MODE[→grant]      permission mode (S=standalone Q=sequenced) + grant",
        "[syn:id·id]           synergizes_with",
        "[!ctr:id·id]          contraindicated_after",
        "[req:code·code]       hard prerequisites",
        "```",
        "",
        "Cost: F=free L=low M=mid H=high $=ongoing",
        "Autonomy: A=agent HA=human_assist HM=human_managed C=confederate CA=confederate-assist CR=confederate-required O=operator",
        "Lead time: 0=<1h sd=same_day 1d 3d 1w 2w 4w 8w",
        "Intensity: 1=low 2=medium 3=high 4=extreme",
        "Beat: ^=spike /=ramp _=hold -=rest >=transition ~=liminal",
        "Arc: p=pre/open b=build e=escalate t=threshold c=climax r=revelation d=denouement *=any",
        "Agency type: R=revealed C=constructed B=borrowed S=suspended X=constrained M=mirrored",
        "Frame req: n=naive q=primed *=any m=meta",
        "Landscape: a=action i=identity +=both",
        "Legacy: e=ephemeral p=personal s=social w=world_mark (concatenated for multi)",
        "Detection: i=immediate s=short m=medium l=long n=never_solo",
        "Reversibility: t=trivial e=easy d=difficult x=irreversible",
        "Permission grants: sct=sustained_contact asr=ambient_surveillance slv=solved-not-done",
        "  trt=trust_channel ids=identity_shift esc=escalation_ready cls=closure_path klg=knowledge",
        "",
        "[grp:GR·SM·T·PC·AR]  group_role · social_modifier · participation_tier · parallel_capable · activation_rate",
        "  GR: s=solo e=ensemble ac=activated am=ambient lo=lottery",
        "  SM: amp dist req neut",
        "  T: P=passive A=active E=elite U=ultra_activated",
        "  PC: 1=parallel_capable 0=not",
        "  AR: 0.0-1.0 activation rate (default 1.0)",
        "[wit:MECH·...]        witness_mechanisms (only on activated plays)",
        "",
        "Implication rules (dot = inferred): spike→naive frame · spike→brief dwell · hold→sustained dwell",
        "  confederate→responsive feedback · identity landscape→personal legacy",
        "",
        "---",
        "",
    ]

    for pid, strip in strips:
        out_lines.append(strip)
        out_lines.append("")

    OUTPUT_FILE.write_text("\n".join(out_lines))
    print(f"\nWritten to {OUTPUT_FILE}")

    # Also save as JSON for programmatic use
    json_out = Path(__file__).parent / "plays_strips.json"
    json_out.write_text(json.dumps(
        [{"id": pid, "strip": strip} for pid, strip in strips],
        indent=2
    ))
    print(f"JSON: {json_out}")

    # Regenerate plays.md from plays.yaml (plays.md is no longer source of truth)
    md_gen_script = Path(__file__).parent / "plays_md_generator.py"
    if md_gen_script.exists() and YAML_FILE.exists():
        subprocess.run([sys.executable, str(md_gen_script)], check=True)

        # Regenerate QFI sections in the freshly-written plays.md
        qfi_text = generate_qfi_sections(plays)
        content = PLAYS_FILE.read_text()
        START = "### By Beat Function\n"
        END   = "\n\n### Certified / Registered Mail"
        if START in content and END in content:
            si = content.index(START)
            ei = content.index(END)
            new_content = content[:si] + qfi_text.rstrip() + content[ei:]
            PLAYS_FILE.write_text(new_content)
            print("Updated QFI auto sections in plays.md")
        else:
            print("WARNING: QFI section boundaries not found — skipped plays.md update")
    else:
        # Legacy path: update QFI in plays.md directly
        qfi_text = generate_qfi_sections(plays)
        content = PLAYS_FILE.read_text()
        START = "### By Beat Function\n"
        END   = "\n\n### Certified / Registered Mail"
        if START in content and END in content:
            si = content.index(START)
            ei = content.index(END)
            new_content = content[:si] + qfi_text.rstrip() + content[ei:]
            PLAYS_FILE.write_text(new_content)
            print("Updated QFI auto sections in plays.md")
        else:
            print("WARNING: QFI section boundaries not found — skipped plays.md update")

    # Rebuild mechanisms index as part of the build
    mech_script = Path(__file__).parent / "build_mechanisms_index.py"
    subprocess.run([sys.executable, str(mech_script)], check=True)


if __name__ == "__main__":
    main()
