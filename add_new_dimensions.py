#!/usr/bin/env python3
"""
add_new_dimensions.py

Adds 6 new tag fields immediately after the **PERMISSION:** line in every play
that has a **PERMISSION:** line but does NOT yet have **EMOTIONAL_REGISTER:**.

Fields added (in order):
  EMOTIONAL_REGISTER
  AGENCY_DEMAND
  DETECTION_WINDOW
  REVERSIBILITY
  CHANNEL
  REQUIRES
"""

import re

PLAYS_FILE = "/home/gas6amus/Documents/game/plays.md"

# ---------------------------------------------------------------------------
# Data: keyed by play id (must match the `id:xxx` tag in plays.md exactly)
# Values are tuples of (EMOTIONAL_REGISTER, AGENCY_DEMAND, DETECTION_WINDOW,
#                       REVERSIBILITY, CHANNEL, REQUIRES)
# ---------------------------------------------------------------------------

PLAY_DATA = {
    # --- WEIGHT & AUTHORITY ---
    "certified_mail": (
        "urgency",
        "passive",
        "long",
        "easy",
        "physical_mail",
        "cash_only · institutional_access",
    ),
    "informed_delivery_gap": (
        "disorientation · paranoia",
        "passive",
        "short",
        "trivial",
        "email",
        "institutional_access · ongoing_maintenance",
    ),
    "notarized_doc": (
        "urgency · awe",
        "passive",
        "long",
        "easy",
        "physical_mail",
        "cash_only · institutional_access",
    ),
    "llc_registration": (
        "awe",
        "passive",
        "never_solo",
        "difficult",
        "digital_ambient",
        "cash_only · institutional_access · ongoing_maintenance",
    ),
    "mailbox_address": (
        "disorientation",
        "passive",
        "never_solo",
        "easy",
        "physical_world",
        "cash_only · ongoing_maintenance",
    ),
    "wax_seal": (
        "awe · wonder",
        "passive",
        "immediate",
        "trivial",
        "physical_mail",
        "cash_only",
    ),
    "classified_doc_aesthetic": (
        "urgency · awe",
        "low",
        "medium",
        "trivial",
        "email",
        "technical_skill",
    ),

    # --- INTIMACY & SURVEILLANCE ---
    "osint_personalization": (
        "paranoia · disorientation",
        "passive",
        "short",
        "easy",
        "email",
        "technical_skill",
    ),
    "local_area_code": (
        "paranoia",
        "passive",
        "medium",
        "trivial",
        "phone",
        "cash_only",
    ),
    "voicemail_drop": (
        "urgency · disorientation",
        "low",
        "immediate",
        "trivial",
        "phone",
        "cash_only · technical_skill",
    ),
    "micro_transaction": (
        "disorientation · urgency",
        "passive",
        "immediate",
        "difficult",
        "digital_ambient",
        "cash_only · social_capital",
    ),
    "matched_prefix": (
        "paranoia · disorientation",
        "passive",
        "immediate",
        "trivial",
        "phone",
        "cash_only",
    ),
    "implied_prior_relationship": (
        "disorientation",
        "low",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "planted_object": (
        "paranoia · wonder",
        "medium",
        "immediate",
        "easy",
        "physical_world",
        "local_presence · social_capital",
    ),

    # --- MYSTERY & BREADCRUMB ---
    "accidental_transmission": (
        "wonder · urgency",
        "low",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "real_domain": (
        "wonder",
        "medium",
        "medium",
        "easy",
        "digital_ambient",
        "cash_only · technical_skill · ongoing_maintenance",
    ),
    "classified_ad": (
        "wonder · urgency",
        "medium",
        "long",
        "easy",
        "physical_world",
        "cash_only · local_presence",
    ),
    "physical_dead_drop": (
        "wonder · urgency",
        "medium",
        "short",
        "easy",
        "physical_world",
        "local_presence",
    ),
    "qr_code": (
        "wonder",
        "low",
        "immediate",
        "trivial",
        "physical_world",
        "technical_skill",
    ),
    "annotation_layer": (
        "wonder · disorientation",
        "medium",
        "short",
        "easy",
        "digital_ambient",
        "technical_skill",
    ),

    # --- LEGITIMACY & SOCIAL PROOF ---
    "linkedin_character": (
        "warmth",
        "passive",
        "never_solo",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "google_maps": (
        "disorientation",
        "passive",
        "never_solo",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "press_release": (
        "awe",
        "passive",
        "long",
        "difficult",
        "digital_ambient",
        "cash_only · technical_skill",
    ),
    "aged_social_media": (
        "warmth · longing",
        "passive",
        "never_solo",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "ai_generated_face": (
        "disorientation",
        "passive",
        "never_solo",
        "trivial",
        "digital_ambient",
        "technical_skill",
    ),
    "reddit_history": (
        "warmth · disorientation",
        "medium",
        "long",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "github_repo": (
        "wonder · disorientation",
        "medium",
        "long",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "goodreads_profile": (
        "warmth · longing",
        "medium",
        "long",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),

    # --- TIMING & COINCIDENCE ---
    "weather_message": (
        "paranoia · disorientation",
        "passive",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "calendar_invite": (
        "urgency · disorientation",
        "low",
        "immediate",
        "easy",
        "email",
        "technical_skill",
    ),
    "fedex_tracking": (
        "urgency · wonder",
        "low",
        "short",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "past_tense_timestamp": (
        "paranoia · disorientation",
        "passive",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "timed_delivery": (
        "paranoia · wonder",
        "passive",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),

    # --- REAL-WORLD ACTIVATION ---
    "restaurant_reservation": (
        "wonder · warmth",
        "medium",
        "immediate",
        "difficult",
        "in_person",
        "cash_only · local_presence",
    ),
    "briefed_confederate": (
        "wonder · warmth",
        "medium",
        "immediate",
        "difficult",
        "in_person",
        "social_capital · local_presence",
    ),
    "real_ticket": (
        "wonder · triumph",
        "medium",
        "short",
        "difficult",
        "multi",
        "cash_only · local_presence",
    ),
    "gift_card": (
        "warmth · wonder",
        "low",
        "immediate",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "library_hold": (
        "wonder · disorientation",
        "medium",
        "short",
        "easy",
        "physical_world",
        "social_capital · local_presence",
    ),
    "false_ally": (
        "warmth · grief",
        "high",
        "never_solo",
        "difficult",
        "in_person",
        "social_capital · ongoing_maintenance",
    ),

    # --- TELECOM ---
    "ai_phone_agent": (
        "urgency · warmth",
        "medium",
        "short",
        "easy",
        "phone",
        "cash_only · technical_skill · ongoing_maintenance",
    ),
    "voice_clone": (
        "disorientation · grief",
        "passive",
        "immediate",
        "irreversible",
        "phone",
        "technical_skill · social_capital",
    ),
    "ringless_voicemail": (
        "urgency · disorientation",
        "low",
        "immediate",
        "trivial",
        "phone",
        "cash_only · technical_skill",
    ),

    # --- SYNTHETIC MEDIA ---
    "video_message": (
        "warmth · wonder",
        "passive",
        "short",
        "easy",
        "email",
        "technical_skill · ongoing_maintenance",
    ),
    "deepfake": (
        "disorientation · dread",
        "passive",
        "immediate",
        "irreversible",
        "email",
        "technical_skill · social_capital",
    ),

    # --- PAPER & PRINT ARTIFACTS ---
    "aged_photograph": (
        "longing · wonder",
        "passive",
        "medium",
        "easy",
        "physical_mail",
        "cash_only · technical_skill",
    ),
    "polaroid": (
        "warmth · longing",
        "passive",
        "medium",
        "easy",
        "physical_mail",
        "cash_only · local_presence",
    ),
    "torn_journal_page": (
        "longing · wonder",
        "low",
        "medium",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "newspaper_clipping": (
        "wonder · disorientation",
        "passive",
        "medium",
        "easy",
        "physical_mail",
        "cash_only · technical_skill",
    ),
    "redacted_document": (
        "urgency · wonder",
        "medium",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "handwritten_letter": (
        "warmth · tenderness",
        "low",
        "medium",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "altered_book": (
        "wonder · longing",
        "high",
        "long",
        "difficult",
        "physical_world",
        "cash_only · local_presence · ongoing_maintenance",
    ),

    # --- MISDIRECTION & CONFUSION ---
    "wrong_person_contact": (
        "disorientation · wonder",
        "low",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "misdelivered_package": (
        "wonder · disorientation",
        "medium",
        "immediate",
        "easy",
        "physical_mail",
        "cash_only · local_presence",
    ),
    "unsolicited_subscription": (
        "disorientation · paranoia",
        "passive",
        "medium",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "returned_letter": (
        "disorientation · longing",
        "low",
        "short",
        "easy",
        "physical_mail",
        "cash_only · technical_skill",
    ),
    "vanishing_institution": (
        "dread · paranoia",
        "medium",
        "immediate",
        "difficult",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),

    # --- IMPLIED SYSTEMS ---
    "loyalty_program": (
        "disorientation · wonder",
        "low",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "missed_appointment": (
        "urgency · disorientation",
        "low",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "receipt_unknown_purchase": (
        "urgency · paranoia",
        "low",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "automated_system_call": (
        "urgency · dread",
        "low",
        "immediate",
        "trivial",
        "phone",
        "technical_skill",
    ),

    # --- STRUCTURAL & PSYCHOLOGICAL ---
    "you_ve_been_found": (
        "paranoia · wonder",
        "passive",
        "immediate",
        "irreversible",
        "multi",
        "technical_skill",
    ),
    "retroactive_meaning": (
        "wonder · awe",
        "medium",
        "medium",
        "irreversible",
        "email",
        "technical_skill",
    ),
    "parallel_threads": (
        "wonder · paranoia",
        "high",
        "medium",
        "easy",
        "multi",
        "technical_skill",
    ),
    "nomination_framing": (
        "wonder · warmth",
        "passive",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "dead_mans_switch": (
        "urgency · dread",
        "medium",
        "immediate",
        "difficult",
        "email",
        "technical_skill",
    ),
    "incomplete_sequence": (
        "urgency · wonder",
        "medium",
        "short",
        "easy",
        "email",
        "technical_skill",
    ),
    "profiling_survey": (
        "disorientation · paranoia",
        "medium",
        "short",
        "easy",
        "email",
        "technical_skill",
    ),
    "reference_check_play": (
        "paranoia · wonder",
        "passive",
        "short",
        "difficult",
        "phone",
        "social_capital · institutional_access",
    ),
    "spotify_playlist": (
        "warmth · longing",
        "low",
        "medium",
        "easy",
        "digital_ambient",
        "technical_skill",
    ),
    "rejection_gambit": (
        "longing · wonder",
        "low",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "false_breakthrough": (
        "triumph · wonder",
        "high",
        "medium",
        "easy",
        "digital_ambient",
        "technical_skill",
    ),
    "simulated_loss": (
        "grief",
        "passive",
        "medium",
        "irreversible",
        "multi",
        "social_capital · ongoing_maintenance",
    ),

    # --- UNDERUSED & HIGH-SURPRISE ---
    "fax": (
        "urgency · awe",
        "passive",
        "immediate",
        "easy",
        "physical_world",
        "cash_only · institutional_access",
    ),
    "telegram": (
        "urgency · awe",
        "passive",
        "immediate",
        "easy",
        "physical_mail",
        "cash_only",
    ),
    "real_obituary": (
        "grief · awe",
        "passive",
        "long",
        "irreversible",
        "physical_world",
        "cash_only · institutional_access",
    ),
    "informed_delivery_ridealong": (
        "disorientation · paranoia",
        "passive",
        "short",
        "trivial",
        "email",
        "institutional_access",
    ),

    # --- AI-NATIVE & AMBIENT ---
    "behavioral_ad": (
        "paranoia · disorientation",
        "passive",
        "short",
        "easy",
        "digital_ambient",
        "cash_only · technical_skill",
    ),
    "llm_contamination": (
        "disorientation · paranoia",
        "passive",
        "long",
        "difficult",
        "digital_ambient",
        "technical_skill",
    ),
    "search_planted": (
        "wonder · triumph",
        "medium",
        "long",
        "difficult",
        "digital_ambient",
        "technical_skill",
    ),
    "authenticity_proof": (
        "wonder · awe",
        "medium",
        "immediate",
        "irreversible",
        "in_person",
        "local_presence · ongoing_maintenance",
    ),
    "ai_disclosure": (
        "disorientation · wonder",
        "low",
        "immediate",
        "irreversible",
        "email",
        "technical_skill",
    ),
    "notification_native": (
        "urgency · paranoia",
        "passive",
        "immediate",
        "trivial",
        "digital_ambient",
        "technical_skill",
    ),
    "ai_character_interface": (
        "warmth · wonder",
        "high",
        "medium",
        "easy",
        "digital_ambient",
        "technical_skill · ongoing_maintenance",
    ),
    "personalization_uncanny": (
        "paranoia · disorientation",
        "passive",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),

    # --- GRAIN & TEXTURE ---
    "corrupted_familiar": (
        "disorientation · paranoia",
        "passive",
        "short",
        "trivial",
        "email",
        "technical_skill",
    ),
    "absent_record": (
        "disorientation · dread",
        "high",
        "long",
        "trivial",
        "digital_ambient",
        "technical_skill",
    ),
    "social_graph_leak": (
        "paranoia · disorientation",
        "passive",
        "short",
        "difficult",
        "in_person",
        "social_capital",
    ),
    "simultaneous_convergence": (
        "paranoia · dread",
        "passive",
        "immediate",
        "easy",
        "multi",
        "cash_only · local_presence · ongoing_maintenance",
    ),
    "hyperlocal_civic": (
        "paranoia · disorientation",
        "passive",
        "medium",
        "easy",
        "physical_world",
        "local_presence",
    ),
    "real_system_entry": (
        "awe · wonder",
        "medium",
        "long",
        "difficult",
        "digital_ambient",
        "cash_only · institutional_access · technical_skill",
    ),
    "retroactive_recontextualization": (
        "disorientation · awe",
        "medium",
        "immediate",
        "irreversible",
        "multi",
        "technical_skill · ongoing_maintenance",
    ),
    "spatial_message": (
        "paranoia · wonder",
        "low",
        "immediate",
        "easy",
        "physical_world",
        "local_presence",
    ),
    "the_witness": (
        "paranoia · dread",
        "passive",
        "never_solo",
        "trivial",
        "in_person",
        "local_presence · social_capital",
    ),
    "the_commission": (
        "tenderness · awe",
        "passive",
        "immediate",
        "irreversible",
        "physical_world",
        "cash_only · social_capital · local_presence",
    ),

    # --- CONFIDENCE & CON ARTISTRY ---
    "convincer_win": (
        "triumph · wonder",
        "medium",
        "immediate",
        "easy",
        "multi",
        "cash_only",
    ),
    "convincer_loss": (
        "urgency · grief",
        "medium",
        "immediate",
        "easy",
        "multi",
        "cash_only",
    ),
    "convincer_plant": (
        "wonder · triumph",
        "high",
        "medium",
        "easy",
        "multi",
        "technical_skill · local_presence",
    ),
    "salting": (
        "wonder · paranoia",
        "passive",
        "long",
        "difficult",
        "multi",
        "technical_skill · local_presence · ongoing_maintenance",
    ),
    "shill_validation": (
        "warmth · wonder",
        "passive",
        "never_solo",
        "easy",
        "in_person",
        "social_capital",
    ),
    "roper": (
        "warmth · tenderness",
        "medium",
        "never_solo",
        "difficult",
        "in_person",
        "social_capital · ongoing_maintenance",
    ),
    "convincer_document": (
        "urgency · awe",
        "passive",
        "medium",
        "easy",
        "physical_mail",
        "cash_only · technical_skill",
    ),
    "convincer_location": (
        "wonder · awe",
        "medium",
        "immediate",
        "easy",
        "in_person",
        "local_presence",
    ),
    "convincer_crowd": (
        "warmth · wonder",
        "low",
        "medium",
        "easy",
        "multi",
        "social_capital · technical_skill · ongoing_maintenance",
    ),
    "hurry_up": (
        "urgency · dread",
        "medium",
        "immediate",
        "easy",
        "multi",
        "technical_skill",
    ),
    "spanish_prisoner": (
        "urgency · tenderness",
        "high",
        "medium",
        "difficult",
        "email",
        "technical_skill · ongoing_maintenance",
    ),
    "pigeon_drop": (
        "urgency · wonder",
        "high",
        "medium",
        "difficult",
        "in_person",
        "social_capital · local_presence",
    ),
    "blow_off": (
        "warmth · triumph",
        "passive",
        "immediate",
        "easy",
        "multi",
        "technical_skill",
    ),
    "cooling_the_mark": (
        "warmth · tenderness",
        "passive",
        "immediate",
        "easy",
        "email",
        "technical_skill",
    ),
    "inside_outside": (
        "disorientation · wonder",
        "high",
        "never_solo",
        "difficult",
        "in_person",
        "social_capital · ongoing_maintenance",
    ),
    "wire_convincer": (
        "urgency · triumph",
        "high",
        "immediate",
        "difficult",
        "multi",
        "technical_skill · ongoing_maintenance",
    ),
    "marks_pride": (
        "shame · urgency",
        "medium",
        "immediate",
        "trivial",
        "email",
        "technical_skill",
    ),
    "convincer_return": (
        "wonder · warmth",
        "low",
        "immediate",
        "easy",
        "multi",
        "technical_skill",
    ),
    "newspaper_test": (
        "triumph · wonder",
        "high",
        "medium",
        "easy",
        "digital_ambient",
        "technical_skill",
    ),
    "cooling_letter": (
        "warmth · tenderness",
        "passive",
        "immediate",
        "easy",
        "email",
        "technical_skill",
    ),
    "planted_witness": (
        "wonder · paranoia",
        "medium",
        "never_solo",
        "difficult",
        "in_person",
        "social_capital · local_presence",
    ),
    "cold_read": (
        "wonder · disorientation",
        "passive",
        "medium",
        "trivial",
        "email",
        "technical_skill",
    ),
}


def make_new_fields(data_tuple):
    """Return the 6 new tag lines as a single string (with trailing newline)."""
    emotional_register, agency_demand, detection_window, reversibility, channel, requires = data_tuple
    lines = [
        f"**EMOTIONAL_REGISTER:** {emotional_register}",
        f"**AGENCY_DEMAND:** {agency_demand}",
        f"**DETECTION_WINDOW:** {detection_window}",
        f"**REVERSIBILITY:** {reversibility}",
        f"**CHANNEL:** {channel}",
        f"**REQUIRES:** {requires}",
    ]
    return "\n".join(lines) + "\n"


def main():
    with open(PLAYS_FILE, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Quick sanity check: no EMOTIONAL_REGISTER fields should exist yet in play
    # blocks (only the definition line at the top should be present).
    play_emotional_count = len(re.findall(r"^\*\*EMOTIONAL_REGISTER:\*\*", content, re.MULTILINE))
    if play_emotional_count > 0:
        print(
            f"WARNING: {play_emotional_count} **EMOTIONAL_REGISTER:** line(s) already present. "
            "Only plays without this field will be modified."
        )

    updated_count = 0

    for play_id, data in PLAY_DATA.items():
        # Build a regex that matches the PERMISSION line for this specific play.
        # We search for the block beginning with `id:play_id` and find the first
        # **PERMISSION:** line after it, then insert after it.
        #
        # Strategy: find the PERMISSION line by locating it after the play's id
        # tag line. We do a targeted search-and-replace that is scoped to each
        # play's block.
        #
        # Pattern explanation:
        #   - Matches `**PERMISSION:**` ... up to end of that line
        #   - Only fires if EMOTIONAL_REGISTER does NOT immediately follow
        #     (we check for its absence in the replacement guard below)
        #
        # We use a two-pass approach: find the play block, then patch it.

        # Locate the play's id tag line position.
        id_pattern = re.compile(
            r"^`id:" + re.escape(play_id) + r"`",
            re.MULTILINE,
        )
        id_match = id_pattern.search(content)
        if id_match is None:
            print(f"  SKIP  {play_id}: id tag not found in file")
            continue

        # Find the next **PERMISSION:** line after the id tag.
        permission_pattern = re.compile(
            r"(\*\*PERMISSION:\*\*[^\n]*\n)",
            re.MULTILINE,
        )
        perm_match = permission_pattern.search(content, id_match.start())
        if perm_match is None:
            print(f"  SKIP  {play_id}: no PERMISSION line found after id tag")
            continue

        # Guard: check whether EMOTIONAL_REGISTER already follows this PERMISSION line.
        text_after_perm = content[perm_match.end() : perm_match.end() + 50]
        if "**EMOTIONAL_REGISTER:**" in text_after_perm:
            print(f"  SKIP  {play_id}: EMOTIONAL_REGISTER already present")
            continue

        # Insert the 6 new fields immediately after the PERMISSION line.
        insertion = make_new_fields(data)
        content = (
            content[: perm_match.end()]
            + insertion
            + content[perm_match.end() :]
        )
        updated_count += 1

    with open(PLAYS_FILE, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"\nDone. {updated_count} plays updated.")


if __name__ == "__main__":
    main()
