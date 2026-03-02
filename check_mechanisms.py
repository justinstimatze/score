#!/usr/bin/env python3
"""
check_mechanisms.py

Validates MECHANISMS fields in plays.md against the drivermap vocabulary.
Run after any plays.md extension to catch LLM-invented mechanism names.

Usage:
  python check_mechanisms.py              # check all plays
  python check_mechanisms.py --fix        # suggest fixes (dry run, no write)
  python check_mechanisms.py --summary    # totals only, no per-play output

Exit codes: 0 = clean, 1 = warnings found
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

PLAYS_FILE = Path(__file__).parent / "plays.md"

# ── VALID DRIVERMAP IDs ────────────────────────────────────────────────────────

VALID = {
    "achievement_motivation","affective_polarization","affective_priming","alcohol_myopia",
    "alexithymia","altruistic_punishment","ambient_noise","amygdala_threat_response",
    "anchoring_bias","anxiety_avoidance","attachment_styles","automation_bias",
    "behavioral_inhibition_activation","belief_perseverance","big_five_personality",
    "bystander_effect","caffeine_effects","cannabis_effects","choice_blindness",
    "co2_air_quality","coalition_formation","cognitive_dissonance","cognitive_load_dual_process",
    "collective_narcissism","commitment_consistency","confabulation","confirmation_bias",
    "conformity_social_influence","construal_level_theory","contact_hypothesis","costly_signaling",
    "counterfactual_thinking","curiosity_exploration","dark_triad","deception_lying",
    "dehumanization","disgust_sensitivity","dominance_hierarchy","effort_justification",
    "emotional_contagion","endowment_effect","envy_jealousy","fight_flight_freeze",
    "forgiveness","fundamental_attribution_error","gossip_reputation","gratitude",
    "grief_bereavement","guilt","habit","hindsight_bias","hot_cold_empathy_gap",
    "hunger_effects","hypervigilance","identity_fusion","identity_protective_cognition",
    "illusory_truth_effect","impression_management","in_group_favoritism",
    "institutional_role_adoption","intrinsic_motivation_sdt","learned_helplessness",
    "loneliness","loss_aversion","mating_motivation","mental_accounting","mere_exposure_effect",
    "minimal_group_paradigm","moral_contagion","moral_dumbfounding","moral_elevation",
    "moral_exclusion","moral_licensing","motivated_reasoning","myside_bias","naive_realism",
    "nature_exposure_restoration","need_for_closure","need_for_cognition","need_for_uniqueness",
    "negativity_bias","nostalgia","obedience_authority","out_group_homogeneity",
    "parasocial_attachment","peak_end_rule","planning_fallacy","pluralistic_ignorance",
    "positive_illusions","power_effects","precarious_manhood","prestige_dominance","pride",
    "proportionality_bias","prospect_theory","proxemics_personal_space","psychedelic_effects",
    "reactance","reciprocity","reward_sensitivity","risk_aversion","risk_compensation",
    "sacred_values","scapegoating","scarcity_mindset","self_handicapping","self_serving_bias",
    "sensory_processing_sensitivity","shame_response","significance_quest",
    "sleep_deprivation_effects","social_comparison","social_dominance_orientation",
    "social_facilitation","social_identity_theory","social_intuitionist_model","social_pain",
    "social_proof","somatic_marker_hypothesis","spotlight_effect","status_quo_bias",
    "status_threat_response","stimulant_effects","stress_cognition","sunk_cost_fallacy",
    "sycophancy","temporal_discounting","terror_management","testosterone_status","trust_formation",
}

# Known-invented names with suggested drivermap replacements.
# Sourced from S1 reconciliation mapping (reconcile_mechanisms.py).
# Add entries here when future plays.md extensions introduce new invented names.
KNOWN_INVENTED: dict[str, str] = {
    # Somatic / body-state
    "perceptual_sensitization":            "sensory_processing_sensitivity",
    "attentional_narrowing":               "cognitive_load_dual_process",
    "threshold_amplification":             "sensory_processing_sensitivity",
    "somatic_marker":                      "somatic_marker_hypothesis",
    "somatic_synchronization":             "somatic_marker_hypothesis",
    "somatic_context_coupling":            "somatic_marker_hypothesis",
    "somatic_narrative_coupling":          "somatic_marker_hypothesis",
    "somatic_grounding_through_detail":    "somatic_marker_hypothesis",
    "somatic_cognition":                   "somatic_marker_hypothesis",
    "somatic_pacing":                      "somatic_marker_hypothesis",
    "somatic_awareness_training":          "sensory_processing_sensitivity",
    "somatic_state_shift":                 "somatic_marker_hypothesis",
    "vulnerability_as_data":              "somatic_marker_hypothesis",
    "embodied_cognition":                  "somatic_marker_hypothesis",
    "embodied_action_ritual":              "somatic_marker_hypothesis",
    "embodied_anchoring":                  "somatic_marker_hypothesis",
    "embodied_commitment":                 "somatic_marker_hypothesis",
    "embodied_insight":                    "somatic_marker_hypothesis",
    "embodied_narrative":                  "somatic_marker_hypothesis",
    "embodied_preparation":                "somatic_marker_hypothesis",
    "embodied_reception":                  "somatic_marker_hypothesis",
    "embodied_revision":                   "somatic_marker_hypothesis",
    "embodied_ritual_enactment":           "somatic_marker_hypothesis",
    "embodied_security":                   "somatic_marker_hypothesis",
    "embodied_achievement":                "effort_justification",
    "physicality_anchor":                  "somatic_marker_hypothesis",
    "physiological_state_induction":       "somatic_marker_hypothesis",
    "physiological_state_priming":         "somatic_marker_hypothesis",
    "physiological_suspense":              "amygdala_threat_response",
    "rhythm_entrainment":                  "emotional_contagion",
    "body_memory":                         "somatic_marker_hypothesis",
    # Liminal / threshold / environmental
    "liminal_state_amplification":         "somatic_marker_hypothesis",
    "liminal_state_exploitation":          "somatic_marker_hypothesis",
    "liminality_induction":                "somatic_marker_hypothesis",
    "liminality_deepening":                "somatic_marker_hypothesis",
    "liminal_transition":                  "somatic_marker_hypothesis",
    "boundary_softening":                  "proxemics_personal_space",
    "environmental_attunement":            "nature_exposure_restoration",
    "chronobiological_coupling":           "nature_exposure_restoration",
    "ecological_temporal_anchoring":       "nature_exposure_restoration",
    "natural_cycle_resonance":             "nature_exposure_restoration",
    "environmental_coupling":              "nature_exposure_restoration",
    "ambient_relevance":                   "nature_exposure_restoration",
    # Memory / time / nostalgia
    "autobiographical_elaboration":        "nostalgia",
    "spatial_memory_activation":           "nostalgia",
    "spatial_memory_priming":              "nostalgia",
    "spatial_memory":                      "nostalgia",
    "tactile_memory_activation":           "nostalgia",
    "temporal_anchoring":                  "nostalgia",
    "nostalgia_mobilization":              "nostalgia",
    "state_dependent_memory":              "nostalgia",
    "state_dependent_recall":              "nostalgia",
    "place_attachment":                    "nostalgia",
    # Behavior / habit / commitment
    "behavioral_habituation":              "habit",
    "ritual_formation":                    "habit",
    "ritual_behavior":                     "habit",
    "conditioned_response_installation":   "habit",
    "earned_access":                       "effort_justification",
    "experience_as_identity_proof":        "effort_justification",
    "earned_status":                       "effort_justification",
    "earned_identity":                     "effort_justification",
    "ownership_by_investment":             "endowment_effect",
    "ikea_effect":                         "effort_justification",
    "behavioral_commitment":               "commitment_consistency",
    "commitment_through_action":           "commitment_consistency",
    "incremental_commitment":              "commitment_consistency",
    "escalating_commitment":               "commitment_consistency",
    "commitment_escalation":               "commitment_consistency",
    "commitment_device":                   "commitment_consistency",
    "foot_in_the_door":                    "commitment_consistency",
    # Disorientation / grain
    "disorientation":                      "cognitive_dissonance",
    "paranoia_escalation":                 "hypervigilance",
    "paranoia_induction":                  "hypervigilance",
    "hypervigilance_induction":            "hypervigilance",
    "trust_violation":                     "cognitive_dissonance",
    "territorial_instinct":                "proxemics_personal_space",
    "micro_territory":                     "proxemics_personal_space",
    "legitimacy":                          "obedience_authority",
    "authority_bias":                      "obedience_authority",
    "pattern_completion":                  "need_for_closure",
    "emotional_deepening":                 "emotional_contagion",
    "spatial_anchoring":                   "proxemics_personal_space",
    "proxemics":                           "proxemics_personal_space",
    # Location / place / identity
    "legacy_construction":                 "significance_quest",
    "historical_record":                   "significance_quest",
    "biographical_continuity":             "identity_protective_cognition",
    "collective_identity_formation":       "social_identity_theory",
    "contested_resource":                  "loss_aversion",
    "external_validation":                 "social_proof",
    # Environmental narrative / immersive
    "object_archaeology":                  "curiosity_exploration",
    "environmental_semiotics":             "curiosity_exploration",
    "participant_as_detective":            "need_for_cognition",
    "narrative_without_exposition":        "need_for_cognition",
    "space_as_character":                  "nature_exposure_restoration",
    "identity_suspension":                 "somatic_marker_hypothesis",
    "exploration_license":                 "curiosity_exploration",
    "dual_consciousness":                  "somatic_marker_hypothesis",
    "status_elevation_through_selection":  "significance_quest",
    "undivided_attention":                 "parasocial_attachment",
    "intimate_disclosure":                 "trust_formation",
    "marked_singularity":                  "significance_quest",
    "dyadic_intensity":                    "parasocial_attachment",
    "permission_through_anonymity":        "reactance",
    "transgression_safety":                "reactance",
    # Immersive sim / complicity
    "information_gap":                     "curiosity_exploration",
    "apophenia_induction":                 "confirmation_bias",
    "pattern_recognition":                 "need_for_cognition",
    "pattern_detection":                   "need_for_cognition",
    "reciprocity_norm":                    "reciprocity",
    "trust_scaffolding":                   "trust_formation",
    "trust_calibration":                   "trust_formation",
    "trust_transfer":                      "trust_formation",
    "trust_disruption":                    "cognitive_dissonance",
    "complicity_through_competence":       "commitment_consistency",
    "complicity_recognition":              "cognitive_dissonance",
    "authority_collapse":                  "cognitive_dissonance",
    "epistemic_destabilization":           "cognitive_dissonance",
    "misdirection_by_omission":            "confirmation_bias",
    "compliance_through_reasoning":        "obedience_authority",
    "trust_maintenance":                   "trust_formation",
    "complicity_through_silence":          "commitment_consistency",
    "complicity_through_destruction":      "commitment_consistency",
    "retroactive_attribution":             "hindsight_bias",
    "retroactive_significance":            "hindsight_bias",
    "retroactive_meaning_attribution":     "hindsight_bias",
    # High-confidence general mappings
    "awe_induction":                       "nature_exposure_restoration",
    "incubation_priming":                  "somatic_marker_hypothesis",
    "anticipatory_arousal":                "behavioral_inhibition_activation",
    "anticipatory_tension":                "behavioral_inhibition_activation",
    "anticipatory_attention":              "behavioral_inhibition_activation",
    "anticipatory_cognition":              "behavioral_inhibition_activation",
    "anticipatory_curiosity":              "curiosity_exploration",
    "contextual_anchoring":                "somatic_marker_hypothesis",
    "social_validation":                   "social_proof",
    "in_group_identity":                   "social_identity_theory",
    "social_continuity":                   "social_identity_theory",
    "ingroup_language":                    "social_identity_theory",
    "belonging":                           "social_identity_theory",
    "belongingness":                       "social_identity_theory",
    "disclosure_reciprocity":              "reciprocity",
    "self_disclosure_reciprocity":         "reciprocity",
    "care_receipt":                        "gratitude",
    "shame":                               "shame_response",
    "grief":                               "grief_bereavement",
    "guilt":                               "guilt",
    "self_efficacy":                       "positive_illusions",
    "self_efficacy_amplification":         "positive_illusions",
    "sunk_cost":                           "sunk_cost_fallacy",
    "fear":                                "amygdala_threat_response",
    "fear_then_relief":                    "amygdala_threat_response",
    "relief":                              "amygdala_threat_response",
    "urgency":                             "scarcity_mindset",
    "scarcity":                            "scarcity_mindset",
    "scarcity_framing":                    "scarcity_mindset",
    "significance_loss":                   "significance_quest",
    "recognition_hunger":                  "significance_quest",
    "identity_threat":                     "significance_quest",
    "identity_confrontation":              "identity_protective_cognition",
    "identity_affirmation":                "identity_protective_cognition",
    "identity_investment":                 "identity_protective_cognition",
    "identity_consolidation":              "identity_protective_cognition",
    "identity_crystallization":            "identity_protective_cognition",
    "cognitive_reframing":                 "cognitive_dissonance",
    "cognitive_dissonance_reduction":      "cognitive_dissonance",
    "meaning_construction":                "motivated_reasoning",
    "meaning_making":                      "motivated_reasoning",
    "narrative_gap_filling":               "motivated_reasoning",
    "confabulation":                       "confabulation",
    "epistemic_uncertainty":               "need_for_closure",
    "effort_justification":                "effort_justification",
    "peak_experience_induction":           "peak_end_rule",
    "ambient_information_seeding":         "curiosity_exploration",
    "curiosity_gap":                       "curiosity_exploration",
    "curiosity_induction":                 "curiosity_exploration",
    "temporal_displacement":               "construal_level_theory",
    "temporal_depth":                      "construal_level_theory",
    "reality_threshold_crossing":          "cognitive_dissonance",
    "epistemic_surprise":                  "cognitive_dissonance",
    "obligation_induction":                "reciprocity",
    "authority_cue":                       "obedience_authority",
    "institutional_credibility":           "obedience_authority",
    "unexplained_benefit":                 "curiosity_exploration",
    "unexplained_presence":                "curiosity_exploration",
    "narrative_transportation":            "emotional_contagion",
    "narrative_seeding":                   "curiosity_exploration",
    "epistemic_immersion":                 "need_for_cognition",
    # Additional cult induction / intelligence tradecraft / pre-arc names
    "in-group_language":                   "social_identity_theory",
    "fluency_as_belonging":                "social_identity_theory",
    "incremental_familiarity":             "mere_exposure_effect",
    "selection_effect":                    "effort_justification",
    "identity_via_external_judgment":      "identity_protective_cognition",
    "intimacy_through_vulnerability":      "trust_formation",
    "commitment_via_revelation":           "commitment_consistency",
    "identity_coherence":                  "identity_protective_cognition",
    "behavioral_consistency":              "commitment_consistency",
    "symbolic_commitment":                 "commitment_consistency",
    "ritual_marking":                      "habit",
    "ego_extension_to_role":               "social_identity_theory",
    "milieu_control_narrative":            "conformity_social_influence",
    "reality_framing":                     "motivated_reasoning",
    "sacred_science_rhetoric":             "obedience_authority",
    "in-group_cosmology":                  "social_identity_theory",
    "felt_surveillance_as_care":           "attachment_styles",
    "holding_environment":                 "attachment_styles",
    "attachment_activation":               "attachment_styles",
    "omnipresence_benevolent":             "attachment_styles",
    "cognitive_consonance":                "commitment_consistency",
    "ritual_action":                       "habit",
    "self_perception_theory":              "commitment_consistency",
    "implied_omniscience":                 "obedience_authority",
    "investment_signaling":                "sunk_cost_fallacy",
    "preemptive_intimacy":                 "trust_formation",
    "depth_of_attention_as_care":          "attachment_styles",
    "doubt_redirection":                   "motivated_reasoning",
    "epistemic_authority":                 "obedience_authority",
    "resistance_reinterpretation":         "motivated_reasoning",
    "appetite_creation":                   "curiosity_exploration",
    "transcendence_as_hook":               "peak_end_rule",
    "vulnerability_bonding":               "trust_formation",
    "mutual_disclosure":                   "reciprocity",
    "shame_transmutation":                 "shame_response",
    "collective_holding":                  "social_identity_theory",
    "in-group_out-group_formation":        "minimal_group_paradigm",
    "belonging_via_distinction":           "social_identity_theory",
    "othering_mild":                       "in_group_favoritism",
    "information_tiers":                   "curiosity_exploration",
    "anticipation_scaffolding":            "behavioral_inhibition_activation",
    "readiness_gatekeeping":               "effort_justification",
    "rite_of_passage":                     "effort_justification",
    "status_elevation":                    "significance_quest",
    "ritual_marking_of_threshold":         "habit",
    # Threat / safety / surveillance plays
    "threat_construal":                    "amygdala_threat_response",
    "safety_behavior":                     "anxiety_avoidance",
    "contingency_planning":                "cognitive_load_dual_process",
    "dread_induction":                     "amygdala_threat_response",
    "consistency_pressure":                "commitment_consistency",
    "identity_performance":                "impression_management",
    "working_memory_load":                 "cognitive_load_dual_process",
    "social_evaluation":                   "impression_management",
    "warmth_signaling":                    "trust_formation",
    "specificity_as_credibility":          "trust_formation",
    # Miscellaneous high-frequency
    "ambient_presence":                    "mere_exposure_effect",
    "retrospective_validation":            "hindsight_bias",
    "threat_appraisal":                    "amygdala_threat_response",
    "information_asymmetry":               "curiosity_exploration",
    "signal_salience":                     "negativity_bias",
    "cognitive_load":                      "cognitive_load_dual_process",
    "reality_anchoring":                   "somatic_marker_hypothesis",
    "uncanny_recognition":                 "hypervigilance",
    # Grain / materiality plays
    "materiality_signal":                  "sensory_processing_sensitivity",
    "register_shift":                      "affective_priming",
    "aesthetic_authority":                 "obedience_authority",
    "memory_anchoring":                    "nostalgia",
    "transitional_object":                 "attachment_styles",
    "materiality_as_meaning":              "somatic_marker_hypothesis",
    # Soft ending / denouement plays
    "closure_ritual":                      "grief_bereavement",
    "warm_presence":                       "attachment_styles",
    "low_demand_contact":                  "attachment_styles",
    "designed_absence":                    "attachment_styles",
    "intentional_silence":                 "attachment_styles",
    "graceful_diminuendo":                 "grief_bereavement",
    "autonomy_restoration":                "reactance",
    "dignity_preservation":                "shame_response",
    "unconditional_positive_regard":       "attachment_styles",
    "low_demand_availability":             "reactance",
    "autonomy_protection":                 "reactance",
    "optional_re-entry":                   "reactance",
    "pure_gift":                           "reciprocity",
    "no_ask_offering":                     "reciprocity",
    # Integration / transformation
    "narrative_identity_consolidation":    "identity_protective_cognition",
    "witnessed_selfhood":                  "impression_management",
    "externalized_reflection":             "identity_protective_cognition",
    "diegetic_meta-awareness":             "cognitive_dissonance",
    "frame_repair":                        "trust_formation",
    "trust_through_honesty":               "trust_formation",
    # Recovery / misfire plays
    "reframing":                           "cognitive_dissonance",
    "meta-narrative_inversion":            "cognitive_dissonance",
    "confirmed_suspicion":                 "confirmation_bias",
    "narrative_absorption":                "emotional_contagion",
    "fictional_reframing":                 "cognitive_dissonance",
    "error_as_characterization":           "cognitive_dissonance",
    "implicit_calibration":                "trust_formation",
    "attunement_signal":                   "trust_formation",
    "character_responsiveness":            "trust_formation",
    "meta_transparency":                   "trust_formation",
    "trust_through_radical_honesty":       "trust_formation",
    "consensual_frame_exit":               "reactance",
    "diegetic_contingency":                "cognitive_dissonance",
    "system_characterization":             "cognitive_dissonance",
    "error_as_evidence":                   "cognitive_dissonance",
    "productive_tension":                  "cognitive_dissonance",
    "multiple_perspective_frame":          "cognitive_dissonance",
    "interpretive_multiplicity":           "cognitive_dissonance",
    # Structural / systemic
    "distributed_agency":                  "social_identity_theory",
    "invisible_interdependence":           "social_identity_theory",
    "emergent_completion":                 "social_identity_theory",
    "designed_convergence":                "social_identity_theory",
    "synchrony_without_contact":           "emotional_contagion",
    "shared_meaning_at_distance":          "social_identity_theory",
    "delayed_activation":                  "behavioral_inhibition_activation",
    "dormancy_as_design":                  "behavioral_inhibition_activation",
    "temporal_anticipation":               "behavioral_inhibition_activation",
    # Denouement / grief
    "meaning_reframing":                   "grief_bereavement",
    "narrative_closure":                   "grief_bereavement",
    "symbolic_death_ritual":               "grief_bereavement",
    "identity_transition_marking":         "identity_protective_cognition",
    # Uncanny / identity
    "parasocial_projection":               "parasocial_attachment",
    "identity_mirroring":                  "identity_protective_cognition",
    "mystery_induction":                   "curiosity_exploration",
    # Grief / memorial section plays
    "expressive_writing_catharsis":        "grief_bereavement",
    "epistemic_completion":                "need_for_closure",
    "grief_externalization":               "grief_bereavement",
    "narrative_witness":                   "impression_management",
    "temporal_defamiliarization":          "construal_level_theory",
    "sleep_boundary_vulnerability":        "somatic_marker_hypothesis",
    "altered_attention_state":             "cognitive_load_dual_process",
    "uncanny_intrusion":                   "hypervigilance",
    "auditory_presence_induction":         "parasocial_attachment",
    "temporal_uncanny":                    "hypervigilance",
    "parasocial_activation":               "parasocial_attachment",
    "medium_specificity_affect":           "affective_priming",
    "temporal_perspective_inversion":      "construal_level_theory",
    "anticipatory_grief_induction":        "grief_bereavement",
    "narrative_prolepsis":                 "construal_level_theory",
    "epistemic_defamiliarization":         "cognitive_dissonance",
    "distributed_mourning":                "grief_bereavement",
    "witness_extension":                   "parasocial_attachment",
    "collective_grief_induction":          "grief_bereavement",
    "legacy_transmission_framing":         "significance_quest",
    "protective_enclosure_framing":        "grief_bereavement",
    "temporal_suspension_metaphor":        "construal_level_theory",
    "grief_containment_ritual":            "grief_bereavement",
    "agency_over_mourning_pace":           "reactance",
    "naming_as_sacred_act":               "significance_quest",
    "cataloguing_as_mourning_ritual":      "grief_bereavement",
    "public_record_framing":              "significance_quest",
    "grief_legitimation":                  "grief_bereavement",
    "narrative_retrospection":             "nostalgia",
    "temporal_distance_reframe":           "construal_level_theory",
    "meaning_emergence_facilitation":      "motivated_reasoning",
    "integration_support":                 "attachment_styles",
    # Sleep Data Mirror
    "self_reflection_amplification":       "identity_protective_cognition",
    "data_as_identity":                    "identity_protective_cognition",
    "behavioral_feedback_loops":           "habit",
    "perceived_surveillance":              "hypervigilance",
    # Digital trace / complicity
    "felt_vulnerability":                  "shame_response",
    "real_time_surveillance":              "hypervigilance",
    "urgency_pressure":                    "scarcity_mindset",
    "kinetic_dread":                       "amygdala_threat_response",
    "complicity_through_instruction":      "commitment_consistency",
    "deferred_revelation":                 "curiosity_exploration",
    "retroactive_guilt":                   "guilt",
    "moral_distance":                      "moral_licensing",
    "willing_participation":               "commitment_consistency",
    "real_world_fiction_boundary":         "cognitive_dissonance",
    "unwitting_participation":             "cognitive_dissonance",
    "authentic_choice_under_uncertainty":  "reactance",
    "frame_collapse":                      "cognitive_dissonance",
    "latent_diegesis":                     "cognitive_dissonance",
    # Compressed emotional / Jeepform
    "emotional_compression":               "emotional_contagion",
    "charged_memory":                      "nostalgia",
    "stylized_repetition":                 "habit",
    "temporal_distillation":               "peak_end_rule",
    "intensity_through_abstraction":       "emotional_contagion",
    "temporal_rupture":                    "cognitive_dissonance",
    "disorientation_as_design":            "cognitive_dissonance",
    "multi_temporal_consciousness":        "construal_level_theory",
    "metacognitive_doubling":              "need_for_cognition",
    "externalized_inner_state":            "impression_management",
    "verbal_authenticity":                 "trust_formation",
    "frame_break_as_deepening":            "cognitive_dissonance",
    "external_perspective":                "construal_level_theory",
    "omniscient_voice":                    "parasocial_attachment",
    "narrative_distance_as_intimacy":      "parasocial_attachment",
    "author_stance":                       "construal_level_theory",
    # Structural plays (pre-arc, continuity)
    "continuity_signaling":                "commitment_consistency",
    "pattern_recognition_reward":          "need_for_cognition",
    "long_game_presence":                  "commitment_consistency",
    "planted_callback":                    "mere_exposure_effect",
    "imagined_community":                  "social_identity_theory",
    "social_proof_by_implication":         "social_proof",
    "solidarity_without_contact":          "social_identity_theory",
    "paralleling":                         "emotional_contagion",
    "rupture_repair_bonding":              "attachment_styles",
    "trust_through_crisis":                "trust_formation",
    "attachment_deepening":                "attachment_styles",
    "earned_reconciliation":               "trust_formation",
    "safety_apparatus":                    "anxiety_avoidance",
    "consent_architecture":                "reactance",
    "trust_through_genuine_exit":          "trust_formation",
    "rupture_prevention":                  "anxiety_avoidance",
    # Intelligence tradecraft
    "threat_construal":                    "amygdala_threat_response",
    "safety_behavior":                     "anxiety_avoidance",
    "contingency_planning":                "cognitive_load_dual_process",
    "dread_induction":                     "amygdala_threat_response",
    # Common high-frequency invented names
    "anticipation":                        "behavioral_inhibition_activation",
    "priming":                             "affective_priming",
    "duality":                             "cognitive_dissonance",
    "consistency_pressure":                "commitment_consistency",
    "identity_performance":                "impression_management",
    "working_memory_load":                 "cognitive_load_dual_process",
    "social_evaluation":                   "impression_management",
    "narrative_coherence":                 "motivated_reasoning",
    "environmental_anchoring":             "somatic_marker_hypothesis",
    "novelty":                             "curiosity_exploration",
    "autonomy_illusion":                   "reactance",
    "reality_testing":                     "cognitive_dissonance",
    "pattern_disruption":                  "cognitive_dissonance",
    "expectation_violation":               "cognitive_dissonance",
    "gift_surprise":                       "reciprocity",
    "consistency_bias":                    "commitment_consistency",
    "approach_motivation":                 "behavioral_inhibition_activation",
    "sensemaking_urgency":                 "need_for_closure",
    "exclusivity_framing":                 "scarcity_mindset",
    "authenticity_cues":                   "trust_formation",
    "forward_momentum":                    "commitment_consistency",
    "calendrical_significance":            "construal_level_theory",
    "active_inference":                    "cognitive_load_dual_process",
    "meta_awareness":                      "need_for_cognition",
    "controlled_revelation":               "curiosity_exploration",
    "trust_recalibration":                 "trust_formation",
    "meta_cognition":                      "need_for_cognition",
    "diegetic_consent":                    "reactance",
    "frame_management":                    "cognitive_load_dual_process",
    "autonomy_support":                    "reactance",
    "competence_reward":                   "achievement_motivation",
    "depth_signaling":                     "curiosity_exploration",
    "social_proof_latent":                 "social_proof",
    "collaboration_drive":                 "social_identity_theory",
    "epistemic_humility":                  "need_for_cognition",
    "retroactive_sensemaking":             "hindsight_bias",
    "narrative_anchoring":                 "motivated_reasoning",
    "recursive_structure":                 "need_for_cognition",
    "vertigo_induction":                   "cognitive_dissonance",
    "delayed_payoff":                      "temporal_discounting",
    "patience_reward":                     "temporal_discounting",
    "temporal_depth_signaling":            "construal_level_theory",
    "perspective_conflict":                "cognitive_dissonance",
    "narrative_construction":              "motivated_reasoning",
}

MECH_RE  = re.compile(r'^\*\*MECHANISMS:\*\*\s*(.+)$')
PLAY_RE  = re.compile(r'^### (.+)$')
ID_RE    = re.compile(r'^`id:(\w+)`')   # inline id: format used in newer sections
MECH_SEP = re.compile(r'[·,]')  # plays use either · or , as separator


def parse_plays(text: str):
    """Yield (play_name, [mechanisms]) for each play."""
    play_name = ""
    for line in text.splitlines():
        m = PLAY_RE.match(line)
        if m:
            play_name = m.group(1).strip()
        else:
            mid = ID_RE.match(line.strip())
            if mid:
                play_name = mid.group(1)
        mm = MECH_RE.match(line.strip())
        if mm:
            raw = [x.strip() for x in MECH_SEP.split(mm.group(1)) if x.strip()]
            # Strip parenthetical annotations like "curiosity_exploration (anticipation before opening)"
            mechs = [re.sub(r'\s*\(.*?\)', '', m).strip() for m in raw if m]
            mechs = [m for m in mechs if m]
            yield play_name, mechs


def main():
    parser = argparse.ArgumentParser(description="Check plays.md mechanism vocabulary")
    parser.add_argument("--summary", action="store_true", help="Totals only")
    parser.add_argument("--fix", action="store_true",
                        help="Show suggested drivermap additions (dry run)")
    args = parser.parse_args()

    text = PLAYS_FILE.read_text()
    plays = list(parse_plays(text))

    zero_hit_plays = []
    unknown_names = Counter()
    known_invented_plays = []
    total_plays = 0

    for play_name, mechs in plays:
        total_plays += 1
        valid_hits = [m for m in mechs if m in VALID]
        invented = [m for m in mechs if m not in VALID]
        unknown = [m for m in invented if m not in KNOWN_INVENTED]

        if not valid_hits:
            zero_hit_plays.append((play_name, mechs))

        for m in unknown:
            unknown_names[m] += 1

        if args.fix and invented:
            additions = []
            for m in invented:
                suggestion = KNOWN_INVENTED.get(m)
                if suggestion and suggestion not in valid_hits:
                    additions.append(f"{m} → {suggestion}")
            if additions:
                known_invented_plays.append((play_name, additions))

    # Report
    # Zero-hit plays are blocking (mechanism matching breaks entirely for those plays).
    # Unknown names are informational — they appear alongside valid IDs, don't break matching.
    has_issues = bool(zero_hit_plays)

    if not args.summary:
        if zero_hit_plays:
            print(f"\nWARN — {len(zero_hit_plays)} plays with ZERO valid drivermap mechanisms:")
            for name, mechs in zero_hit_plays[:20]:
                print(f"  {name}")
                print(f"    mechs: {', '.join(mechs[:4])}")
            if len(zero_hit_plays) > 20:
                print(f"  ... and {len(zero_hit_plays) - 20} more")

        if unknown_names:
            print(f"\nINFO — {len(unknown_names)} unknown mechanism names (not in drivermap, not in known-invented list):")
            for name, cnt in unknown_names.most_common(20):
                print(f"  {cnt:>3}  {name}")
            if len(unknown_names) > 20:
                print(f"  ... and {len(unknown_names) - 20} more")

        if args.fix and known_invented_plays:
            print(f"\nFIX SUGGESTIONS (run reconcile_mechanisms.py to apply):")
            for name, suggestions in known_invented_plays[:15]:
                print(f"  {name}")
                for s in suggestions:
                    print(f"    + {s}")

    # Summary
    plays_with_valid = sum(1 for _, mechs in plays if any(m in VALID for m in mechs))
    print(f"\nSummary: {total_plays} plays | "
          f"{plays_with_valid} ({100*plays_with_valid//max(total_plays,1)}%) with ≥1 valid ID | "
          f"{len(zero_hit_plays)} zero-hit plays | "
          f"{len(unknown_names)} unknown names")

    if has_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
