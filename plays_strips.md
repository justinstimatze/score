# Plays — Reasoning Strips

Dense notation for LLM arc-design reasoning.
Each strip: ~20-30 tokens. Full library: ~8-10k tokens.

## Notation (Reasoning Strip Format)

```
@id  C·U·LT·I         cost · autonomy · lead_time · intensity
#M·M [arc] bf         mechanisms · arc_fit · beat_function
AT·FR·AD·LA·LG·DE·RV  agency_type · frame_req · agency_demand · landscape · legacy · detection · reversibility
prm:MODE[→grant]      permission mode (S=standalone Q=sequenced) + grant
[syn:id·id]           synergizes_with
[!ctr:id·id]          contraindicated_after
[req:code·code]       hard prerequisites
```

Cost: F=free L=low M=mid H=high $=ongoing
Autonomy: A=agent HA=human_assist HM=human_managed C=confederate CA=confederate-assist CR=confederate-required O=operator
Lead time: 0=<1h sd=same_day 1d 3d 1w 2w 4w 8w
Intensity: 1=low 2=medium 3=high 4=extreme
Beat: ^=spike /=ramp _=hold -=rest >=transition ~=liminal
Arc: p=pre/open b=build e=escalate t=threshold c=climax r=revelation d=denouement *=any
Agency type: R=revealed C=constructed B=borrowed S=suspended X=constrained M=mirrored
Frame req: n=naive q=primed *=any m=meta
Landscape: a=action i=identity +=both
Legacy: e=ephemeral p=personal s=social w=world_mark (concatenated for multi)
Detection: i=immediate s=short m=medium l=long n=never_solo
Reversibility: t=trivial e=easy d=difficult x=irreversible
Permission grants: sct=sustained_contact asr=ambient_surveillance slv=solved-not-done
  trt=trust_channel ids=identity_shift esc=escalation_ready cls=closure_path

[grp:GR·SM·T·PC·AR]  group_role · social_modifier · participation_tier · parallel_capable · activation_rate
  GR: s=solo e=ensemble ac=activated am=ambient lo=lottery
  SM: amp dist req neut
  T: P=passive A=active E=elite U=ultra_activated
  PC: 1=parallel_capable 0=not
  AR: 0.0-1.0 activation rate (default 1.0)
[wit:MECH·...]        witness_mechanisms (only on activated plays)

Implication rules (dot = inferred): spike→naive frame · spike→brief dwell · hold→sustained dwell
  confederate→responsive feedback · identity landscape→personal legacy

---

@certified_mail L·HA·3d·2
#SQ·OA·CE [ptcr] /
B·n·p·a·p·l·e
prm:S
syn:wax_seal·notarized_doc·informed_delivery_gap·mailbox_address·llc_registration
req:csh

@informed_delivery_gap F·HA·2w·1
#AN·duality·PM·behav_act·CD·affec_pri [*] /
S·n·p·a·p·s·t
prm:Q

@notarized_doc L·HA·sd·2
#OA·SQ·TR [pet] /
B·n·p·a·p·l·e
prm:S
syn:certified_mail·llc_registration·mailbox_address·classified_doc_aesthetic
req:csh

@llc_registration H·HA·3d·1
#SP·TR [p] /
B·n·p·a·w·n·d
prm:S→ids
syn:mailbox_address·google_maps·press_release·notarized_doc·real_domain
req:csh

@mailbox_address $·HA·3d·1
#SP·TR [p] /
B·n·p·a·w·n·e
prm:S
syn:llc_registration·google_maps·notarized_doc·real_domain
req:csh

@wax_seal L·HA·3d·2
#SQ·NV·PM·CE [ptc] /
B·n·p·a·p·i·t
prm:Q
syn:certified_mail·notarized_doc·handwritten_letter·informed_delivery_gap
req:csh

@classified_doc_aesthetic F·A·sd·2
#OA·SQ·CE [pbet] /
B·n·l·a·p·m·t
prm:S
syn:redacted_document·accidental_transmission·notarized_doc·real_domain
req:tsk

@osint_personalization F·HA·sd·?
#HV·SQ·CE [p*] /
S·n·p·i·p·s·e
prm:S→asr
req:tsk

@local_area_code $·A·sd·1
#MEE·TR [p*] /
B·n·p·a·p·m·t
prm:S
syn:ai_phone_agent·voicemail_drop·matched_prefix
req:csh

@voicemail_drop F·A·sd·2
#SQ·HV·CE [pbe] /
S·n·l·a·e·i·t
prm:S→sct
syn:local_area_code·ai_phone_agent·implied_prior_relationship
req:csh·tsk

@micro_transaction L·HA·3d·3
#RC·CO·RT·CD [bt] /
C·n·p·a·e·i·d
prm:Q
syn:gift_card·nomination_framing·profiling_survey
req:csh

@matched_prefix $·A·sd·2
#HV·UR [et] /
R·n·p·a·p·i·t
prm:Q
syn:you_ve_been_found_inversion·ai_phone_agent
req:csh

@implied_prior_relationship F·A·sd·2
#HV·HCG·CE [pb] /
R·n·l·i·p·s·t
prm:S
syn:accidental_transmission·voicemail_drop·past_tense_timestamp
req:tsk

@planted_object L·HA·3d·3
#HV·SQ·CE·TI·proxe_spa [pe] /
C·n·m·a·p·i·e
prm:Q
syn:implied_prior_relationship·past_tense_timestamp·qr_code·voicemail_drop·accidental_transmission
req:loc

@accidental_transmission F·A·sd·3
#CE·CB·SQ [ber] /
C·n·l·a·e·s·t
prm:S
syn:real_domain·linkedin_character·parallel_threads·classified_doc_aesthetic
req:tsk

@real_domain $·HA·2+·1
#SP·TR·CE [pb] -
C·n·m·a·w·m·e
prm:S
syn:llc_registration·press_release·linkedin_character·google_maps·annotation_layer
req:csh·tsk

@classified_ad L·HA·3d·2
#CE·SQ [be] /
B·n·m·a·w·l·e
prm:Q
syn:physical_dead_drop·incomplete_sequence·nomination_framing
req:csh·loc

@physical_dead_drop ?·C·3d·3
#HV·CE·you_fou [etc] /
C·n·m·a·p·s·e
prm:Q
syn:qr_code·certified_mail·you_ve_been_found_inversion·briefed_confederate
req:loc

@qr_code F·A·sd·1
#CE·CO [*] /
C·n·l·a·e·i·t
prm:S
syn:physical_dead_drop·certified_mail·notarized_doc·redacted_document
req:tsk

@annotation_layer F·A·sd·2
#CE·SP·SQ [be] /
C·n·m·a·p·s·e
prm:Q
syn:real_domain·accidental_transmission·parallel_threads
req:tsk

@linkedin_character F·HM·4w·1
#SP·TR·PA [p] /
B·n·p·a·w·n·d
prm:S→sct
syn:ai_generated_face·real_domain·aged_social_media·press_release
req:tsk

@google_maps F·HA·4w·1
#SP·TR [p] /
B·n·p·a·w·n·d
prm:S
syn:llc_registration·mailbox_address·real_domain
req:tsk

@press_release M·HA·3d·1
#SP·illus_eff [pb] /
B·n·p·a·sw·l·d
prm:S→sct
syn:real_domain·llc_registration·linkedin_character
req:csh·tsk

@aged_social_media F·HM·36·1
#SP·PA·TR [pb] /
B·n·p·a·w·n·d
prm:S
syn:linkedin_character·ai_generated_face·real_domain
req:tsk

@ai_generated_face F·A·12·1
#MEE·TR [p] /
B·n·p·a·p·n·t
prm:S
syn:linkedin_character·aged_social_media·video_message·real_domain
req:tsk

@reddit_history M·HA·4w·1
#SP·CE·PA [pb] /
R·n·m·a·w·l·d
prm:S
syn:real_domain·aged_social_media·linkedin_character·annotation_layer
req:tsk

@github_repo F·HA·2+·2
#CE·SP·SQ [pbe] /
R·n·m·a·w·l·d
prm:S
syn:real_domain·linkedin_character·annotation_layer
req:tsk

@goodreads_profile F·HA·1w·1
#PA·CE [be] /
B·n·m·a·w·l·d
prm:S
syn:linkedin_character·aged_social_media·altered_book
req:tsk

@weather_message F·A·sd·1
#HV·SQ [*] ^
R·n·p·a·e·i·t
prm:S→asr
syn:past_tense_timestamp·osint_personalization
req:tsk

@calendar_invite F·A·sd·2
#CO·SQ [etc] ^
C·n·l·a·e·i·e
prm:S
syn:restaurant_reservation·fedex_tracking·real_domain
req:tsk

@fedex_tracking L·HA·3d·3
#AN·SQ·CE·behav_act [bec] ^
R·n·l·a·p·s·e
prm:S
syn:qr_code·gift_card·wax_seal·notarized_doc·you_ve_been_found_inversion
req:csh

@past_tense_timestamp F·A·sd·2
#HV·HCG·SQ [pb] ^
R·n·p·i·p·s·t
prm:Q→trt
syn:weather_message·osint_personalization·implied_prior_relationship
req:tsk

@timed_delivery F·A·sd·1
#SQ·HV [*] ^
R·n·p·a·e·i·t
prm:Q→asr
syn:calendar_invite·weather_message·certified_mail
req:tsk

@restaurant_reservation F·A·3d·3
#CO·RT·RC·CD [cd] /
B·n·m·a·e·i·d
prm:Q
syn:calendar_invite·briefed_confederate·certified_mail
req:csh·loc

@briefed_confederate G·C·3d·4
#EC·SP·RT·CD [etc] ^
C·n·m·a·s·i·d
prm:Q
syn:physical_dead_drop·restaurant_reservation·voice_clone·reference_check_play
req:loc

@real_ticket H·HA·vari·3
#CO·RT·AN·CD·behav_act [cd] /
B·n·m·a·p·s·d
prm:Q
syn:calendar_invite·certified_mail·briefed_confederate
req:csh·loc

@gift_card H·HA·3d·3
#RC·CO·RT·CD [btc] /
B·n·l·a·p·i·e
prm:S
syn:certified_mail·micro_transaction·restaurant_reservation
req:csh

@library_hold F·HA·1w·2
#RC·CE·SQ [be] /
C·n·m·a·p·s·e
prm:Q
syn:altered_book·retroactive_meaning·accidental_transmission
req:loc

@false_ally $·C·vari·4
#PA·TR·betrayal·ED·EC [bet] /
S·n·h·+·p·n·d
prm:Q
syn:planted_object·you_ve_been_found·ai_phone_agent·voice_clone·briefed_confederate

@ai_phone_agent $·A·24·3
#PA·TR·EC [etc] /
B·*·m·a·e·s·e
prm:Q→trt
syn:local_area_code·voicemail_drop·video_message
req:csh·tsk

@voice_clone L·HA·1w·4
#EC·RT·SQ·CD [c] /
S·n·p·i·p·i·x
prm:Q
syn:briefed_confederate·real_ticket
req:tsk

@ringless_voicemail F·A·sd·2
#SQ·HV·CE [pbe] /
B·n·l·a·e·i·t
prm:S→sct
req:csh·tsk

@video_message $·A·sd·3
#PA·EC·SQ [etc] ^
C·n·p·i·p·s·e
prm:Q→trt
syn:ai_generated_face·ai_phone_agent·linkedin_character
req:tsk

@deepfake ?·HA·vari·4
#RT·EC·SQ·CD [c] ^
S·n·p·i·p·i·x
prm:Q
syn:voice_clone·briefed_confederate
req:tsk

@aged_photograph L·HA·3d·3
#NS·TR·SQ [pber] /
R·n·p·i·p·m·e
prm:Q
syn:torn_journal_page·handwritten_letter·altered_book·retroactive_meaning
req:csh·tsk

@polaroid L·HA·3d·3
#NS·TR·SQ [pecr] /
R·n·p·+·p·m·e
prm:Q
syn:aged_photograph·torn_journal_page·handwritten_letter
req:csh·loc

@torn_journal_page L·HA·3d·3
#NS·CE·PA [ber] /
R·n·l·i·p·m·e
prm:Q
syn:aged_photograph·handwritten_letter·accidental_transmission·altered_book
req:csh

@newspaper_clipping L·HA·3d·2
#SP·SQ·CE [ber] /
B·n·p·a·p·m·e
prm:S
syn:real_obituary·aged_photograph·accidental_transmission·classified_doc_aesthetic
req:csh·tsk

@redacted_document F·A·sd·3
#CE·NC·SQ [bet] /
S·n·m·a·p·s·t
prm:Q
syn:classified_doc_aesthetic·accidental_transmission·parallel_threads·retroactive_meaning
req:tsk

@handwritten_letter L·HA·3d·3
#PA·NS·TR·EC [pecd] /
B·n·l·+·p·m·e
prm:Q
syn:wax_seal·certified_mail·aged_photograph·torn_journal_page
req:csh

@altered_book H·HM·2+·3
#NS·CE·SQ·PA [berd] /
C·n·h·a·p·l·d
prm:Q
syn:library_hold·torn_journal_page·retroactive_meaning·goodreads_profile
req:csh·loc

@wrong_person_contact F·A·sd·2
#CE·SQ·HCG [pb] ^
S·n·l·i·p·i·t
prm:S
syn:implied_prior_relationship·accidental_transmission·parallel_threads
req:tsk

@misdelivered_package L·HA·3d·3
#CE·SQ·CO [be] ^
S·n·m·a·p·i·e
prm:Q
syn:qr_code·redacted_document·torn_journal_page
req:csh·loc

@unsolicited_subscription M·HA·2w·2
#SQ·CE·CO [pb] ^
C·n·p·a·p·m·e
prm:S→ids
syn:loyalty_program·nomination_framing·implied_prior_relationship
req:csh

@returned_letter L·HA·3d·2
#CE·NS·SQ [be] ^
R·n·l·i·p·s·e
prm:Q
syn:aged_photograph·torn_journal_page·accidental_transmission
req:csh·tsk

@vanishing_institution F·A·sd·3
#HV·DI·isolatio·PE·CD [ec] ^
S·n·m·i·p·i·d
prm:Q
syn:llc_registration·real_domain·linkedin_character·google_maps
req:tsk

@loyalty_program F·A·sd·3
#SQ·CO·CE [pb] -
B·n·l·a·p·s·t
prm:S→sct
syn:implied_prior_relationship·nomination_framing·real_domain·profiling_survey
req:tsk

@missed_appointment F·A·sd·3
#OA·SQ·anxiety·CE [pb] -
S·n·l·a·e·i·t
prm:S
syn:profiling_survey·implied_prior_relationship·accidental_transmission
req:tsk

@receipt_unknown_purchase F·A·sd·3
#LA·CE·SQ [pb] -
S·n·l·i·p·i·t
prm:S
syn:fedex_tracking·misdelivered_package·loyalty_program
req:tsk

@automated_system_call F·A·sd·2
#OA·SQ·CE [pe] -
B·n·l·a·e·i·t
prm:S→sct
syn:missed_appointment·ai_phone_agent·voicemail_drop
req:tsk

@you_ve_been_found F·A·sd·4
#HV·SQ·fear_rel [et] /
R·*·p·i·p·i·x
prm:Q
syn:matched_prefix·physical_dead_drop·certified_mail·ai_phone_agent
req:tsk

@retroactive_meaning F·A·sd·3
#CE·CB·SQ [ec] /
R·*·m·+·p·m·x
prm:Q
syn:torn_journal_page·redacted_document·parallel_threads·incomplete_sequence
req:tsk

@parallel_threads F·A·sd·3
#CE·SQ·patte_sat [be] -
C·n·h·i·p·m·e
prm:Q
syn:accidental_transmission·classified_ad·real_domain·retroactive_meaning
req:tsk

@nomination_framing F·A·sd·2
#need_uni·SQ·CE [p] /
R·*·p·i·p·s·t
prm:S
syn:osint_personalization·implied_prior_relationship·profiling_survey
req:tsk

@dead_mans_switch F·A·sd·3
#LA·time_pre·OA [et] /
C·*·m·a·p·i·d
prm:Q
syn:incomplete_sequence·automated_system_call·calendar_invite
req:tsk

@incomplete_sequence F·A·sd·2
#NC·CE·Zeiga_eff [etc] /
X·n·m·a·p·s·e
prm:Q
syn:retroactive_meaning·dead_mans_switch·parallel_threads
req:tsk

@profiling_survey F·A·sd·1
#CO·complian·self_per [pt] /
C·*·m·a·p·s·e
prm:Q
syn:nomination_framing·missed_appointment·loyalty_program
req:tsk

@reference_check_play F·C·3d·4
#SQ·SP·HV·in_fav [be] ^
C·n·p·i·p·s·d
prm:Q
syn:nomination_framing·linkedin_character·you_ve_been_found_inversion

@spotify_playlist F·A·sd·2
#EC·PA·NS·CE [bed] /
C·*·l·a·p·m·e
prm:Q→asr
syn:aged_social_media·video_message
req:tsk

@rejection_gambit F·A·sd·1
#CE·ambig_tol·false_clo·SQ [pb] /
R·*·l·i·p·i·t
prm:S
syn:nomination_framing·certified_mail·implied_prior_relationship·accidental_transmission
req:tsk

@false_breakthrough F·A·sd·2
#CE·PC·NC·RE [be] /
S·*·h·i·p·m·e
prm:Q→slv
syn:real_domain·linkedin_character·reddit_history·parallel_threads·vanishing_institution
req:tsk

@simulated_loss F·A·sd·4
#LA·fear·helpless·RL·ED·amygd_res·EC [ec] ^
C·n·p·+·p·m·x
prm:Q
syn:false_ally·automated_system_call·accidental_transmission·vanishing_institution

@fax F·A·sd·3
#SQ·NV·OA·CE [pe] ^
B·n·p·a·p·i·e
prm:S
syn:classified_doc_aesthetic·automated_system_call
req:csh

@telegram M·HA·3d·4
#SQ·OA·NV·UG·scarc_min·CE [pe] ^
B·n·p·a·p·i·e
prm:S
syn:certified_mail·wax_seal
req:csh

@real_obituary H·HA·1w·4
#NS·GR·SQ·SP·grief_ber [br] ^
R·n·p·+·w·l·x
prm:Q
syn:aged_photograph·newspaper_clipping·retroactive_meaning
req:csh

@informed_delivery_ridealong F·HA·2w·1
#behav_act·CD·affec_pri·antic_att [*] /
S·n·p·a·e·s·t
prm:Q

@behavioral_ad L·A·3d·2
#SP·LG·AP·DI·OA·CD [pb*] -
S·n·p·a·e·s·e
prm:S→asr
syn:llc_registration·real_domain·linkedin_character·press_release
req:csh·tsk

@llm_contamination F·A·2w·2
#LG·SP·AP·DI·OA·CD [pb] -
S·n·p·i·p·l·d
prm:S→asr
syn:real_domain·linkedin_character·press_release·search_planted·false_breakthrough
req:tsk

@search_planted L·HA·2w·2
#CE·PC·LG·SP·NC·OA [be] -
C·*·m·a·w·l·d
prm:Q
syn:real_domain·llm_contamination·reddit_history·parallel_threads·false_breakthrough
req:tsk

@authenticity_proof F·HM·sd·3
#TR·epist_sur·RL·RT·CD·amygd_res [etc] -
S·*·m·i·p·i·x
prm:Q
syn:ai_disclosure·false_ally·ai_phone_agent·ai_character_interface
req:loc

@ai_disclosure F·A·sd·2
#EU·TR·CE·DI·NC·TR·CD [bet] -
S·*·l·i·p·i·x
prm:Q
syn:ai_phone_agent·ai_character_interface·false_ally·authenticity_proof
req:tsk

@notification_native F·A·sd·2
#SQ·UG·AP·CE·scarc_min [*] -
X·n·p·a·e·i·t
prm:Q
syn:calendar_invite·accidental_transmission·dead_mans_switch·behavioral_ad·ai_character_interface
req:tsk

@ai_character_interface L·A·3d·3
#PA·CE·TR·CO [pbe*] -
C·q·h·i·p·m·e
prm:Q→sct
syn:ai_disclosure·false_ally·real_domain·linkedin_character·voice_clone·authenticity_proof
req:tsk

@personalization_uncanny F·A·sd·3
#HV·SQ·DI·TV·CD [pe] ^
S·n·p·i·p·i·t
prm:S→asr
syn:behavioral_ad·osint_personalization·past_tense_timestamp·implied_prior_relationship
req:tsk

@corrupted_familiar F·A·sd·2
#HV·DI·TV·NC·CD [be] -
S·n·p·i·p·s·t
prm:S→asr
syn:vanishing_institution·retroactive_recontextualization·absent_record·implied_prior_relationship
req:tsk

@absent_record F·HA·vari·2
#CE·HV·NC·DI·CD [be] -
S·n·h·i·p·l·t
prm:Q
syn:real_system_entry·corrupted_familiar·parallel_threads·false_breakthrough·vanishing_institution
req:tsk

@social_graph_leak F·C·3d·2
#HV·SP·TV·SQ·CD [be] ^
S·n·p·i·p·s·d
prm:Q
syn:you_ve_been_found·parallel_threads·simultaneous_convergence·osint_personalization

@simultaneous_convergence L·A·sd·3
#HV·DI·SQ·PE·CD [etc] ^
R·n·p·i·p·i·e
prm:Q→trt
syn:certified_mail·voicemail_drop·social_graph_leak·spatial_message·accidental_transmission
req:csh·loc

@hyperlocal_civic L·HA·3d·2
#HV·TI·SQ·DI·proxe_spa·CD [pbe] -
B·n·p·a·w·m·e
prm:Q
syn:spatial_message·osint_personalization·classified_ad·real_system_entry
req:loc

@real_system_entry L·HA·2w·3
#LG·SP·DI·OA·CD [pbe] -
B·n·m·a·w·l·d
prm:S
syn:llc_registration·absent_record·real_domain·linkedin_character·corrupted_familiar
req:csh·tsk

@retroactive_recontextualization F·A·sd·4
#SQ·HV·DI·PC·NS·CD·NC [etc] ^
R·q·m·+·p·i·x
prm:Q
syn:osint_personalization·you_ve_been_found·parallel_threads·retroactive_meaning·absent_record
req:tsk

@spatial_message F·HA·3d·3
#HV·TI·SQ·DI·proxe_spa·CD [pet] -
C·n·l·a·p·i·e
prm:Q→asr
syn:hyperlocal_civic·planted_object·simultaneous_convergence·osint_personalization
req:loc

@the_witness F·C·sd·2
#HV·DI·SQ·PE·CD [be] ^
R·n·p·a·s·n·t
prm:Q
syn:simultaneous_convergence·spatial_message·you_ve_been_found·briefed_confederate
req:loc

@the_commission H·HA·13·4
#SQ·PA·NS·ED·RC·EC [tcd] /
C·*·p·i·p·i·x
prm:Q
syn:retroactive_recontextualization·handwritten_letter·aged_photograph·real_ticket·briefed_confederate
req:csh·loc

@convincer_win L·A·2448·1
#CO·LA·SK·TR·PC·sunk_fal·NC [pb] ^
R·n·m·i·p·i·e
prm:Q→trt
syn:convincer_loss·hurry_up·spanish_prisoner·shill_validation·convincer_document
req:csh

@convincer_loss L·A·1d·2
#LA·SK·CO·RXN·UG·sunk_fal·scarc_min [be] ^
R·n·m·i·p·i·e
prm:Q
syn:convincer_win·hurry_up·spanish_prisoner·pigeon_drop·convincer_document
req:csh

@convincer_plant L·HA·4872·2
#EU·PC·SQ·TR·CE·NC [pb] ^
R·n·h·a·p·m·e
prm:S
syn:convincer_win·convincer_document·shill_validation·osint_personalization
req:loc·tsk

@salting M·HM·2w·2
#AP·SQ·PC·EU·PE·NC·HV [pb] ^
R·n·p·a·p·l·d
prm:Q
syn:convincer_plant·convincer_location·osint_personalization·shill_validation·retroactive_meaning
req:loc·tsk

@shill_validation L·C·2448·2
#SP·TR·EU·LG·EC·NC·OA [be] ^
R·n·p·a·s·n·e
prm:S
syn:convincer_plant·convincer_crowd·convincer_win·false_ally

@roper L·C·4872·2
#TR·PA·LG·SP·RC·OA [p] ^
R·n·m·i·p·n·d
prm:S→trt
syn:shill_validation·spanish_prisoner·convincer_win·false_ally·briefed_confederate

@convincer_document L·A·1d·2
#LG·OA·TR·EU·CO·NC [bet] ^
R·n·p·a·p·m·e
prm:S
syn:convincer_plant·convincer_location·spanish_prisoner·hurry_up·pigeon_drop
req:csh·tsk

@convincer_location L·HA·4872·2
#LG·TR·EU·AP·SQ·OA·NC [be] ^
R·n·m·a·p·i·e
prm:S
syn:convincer_plant·convincer_document·convincer_win
req:loc

@convincer_crowd M·C·4872·2
#SP·LG·EC·TR·EU·OA·NC [bet] ^
R·n·l·a·s·m·e
prm:Q
syn:shill_validation·convincer_location·convincer_plant
req:tsk

@hurry_up F·A·0·3
#UG·LA·scarcity·CO·OA·scarc_min [etc] ^
R·n·m·a·e·i·e
prm:Q
syn:convincer_loss·spanish_prisoner·pigeon_drop·convincer_document·blow_off
req:tsk

@spanish_prisoner L·A·1d·3
#RC·GT·SQ·PA·CO·LA [bet] ^
R·n·h·i·p·m·d
prm:Q
syn:convincer_document·hurry_up·pigeon_drop·blow_off
req:tsk

@pigeon_drop L·C·2448·3
#RC·SK·CO·LA·trust_exp·sunk_fal [et] ^
R·n·h·a·p·m·d
prm:Q→trt
syn:convincer_document·hurry_up·spanish_prisoner·convincer_win·blow_off
req:loc

@blow_off F·A·0·1
#NC·RL·EU·CO·TR·amygd_res [d*] ^
R·n·p·a·e·i·e
prm:S
syn:cooling_the_mark·convincer_win·spanish_prisoner·hurry_up·convincer_document
req:tsk

@cooling_the_mark F·A·0·1
#NC·RL·GT·SHM2·IT·ED·amygd_res·shame_res·SQ·EC [d] ^
R·n·p·i·p·i·e
prm:Q
syn:blow_off·convincer_win·shill_validation·convincer_crowd
req:tsk

@inside_outside M·C·72h·3
#TR·LG·SP·EU·OA·DI·NC·CD [bet] ^
R·n·h·i·p·n·d
prm:Q→trt
syn:shill_validation·convincer_document·hurry_up·spanish_prisoner

@wire_convincer M·HM·72h·3
#SK·CO·LA·UG·PC·SQ·sunk_fal·scarc_min·NC [et] ^
R·n·h·a·p·i·d
prm:Q
syn:convincer_loss·hurry_up·pigeon_drop·blow_off·spanish_prisoner
req:tsk

@marks_pride F·A·0·2
#IT·RXN·CO·SHM2·SK·SQ·shame_res·sunk_fal [be] ^
R·n·m·i·p·i·t
prm:Q→trt
syn:convincer_loss·hurry_up·spanish_prisoner·wire_convincer·inside_outside
req:tsk

@convincer_return F·A·0·2
#NS·PC·CO·ED·PE·NC·EC·HV [etd] ^
R·n·l·a·p·i·e
prm:Q
syn:convincer_plant·retroactive_meaning·blow_off·cooling_the_mark
req:tsk

@newspaper_test F·A·0·1
#LG·SP·EU·TR·OA·NC [pb] ^
R·n·h·i·p·m·e
prm:S
syn:convincer_plant·convincer_document·cold_read·convincer_location
req:tsk

@cooling_letter F·A·0·1
#NC·RL·GT·ED·IT·amygd_res·EC·SQ [d] ^
R·n·p·i·p·i·e
prm:Q→cls
syn:cooling_the_mark·blow_off·convincer_return·spanish_prisoner
req:tsk

@planted_witness L·C·48h·2
#SP·LG·EU·TR·EC·OA·NC [be] ^
R·n·m·a·s·n·d
prm:Q
syn:shill_validation·convincer_crowd·convincer_location·inside_outside
req:loc

@cold_read F·A·0·2
#SQ·PA·EU·TR·IT·NC [pb*] ^
R·n·p·i·p·m·t
prm:S
syn:osint_personalization·convincer_plant·convincer_document
req:tsk

@barnum_profile_dispatch L·A·3d·2
#RH·self_con·uniqu_ill·TR·DR·SQ·RC [pb] ^
R·n·p·i·p·m·e
prm:S

@cold_voicemail_drop L·CA·3d·2
#CE·PDT·coinc_apo·IT·SP·need_cog·SQ [p] ^
C·n·l·a·e·s·e
prm:S
req:loc

@resonance_letter L·A·3d·2
#RH·PA·TR·ident_cry·DR·SQ·ident_cog·RC [be] ^
R·n·p·i·p·m·e
prm:Q

@sealed_envelope_reveal L·A·1w·3
#RV2·ANT·CO·PC·AW·behav_act·NC·natur_res [pc] ^
R·q·l·i·p·n·d
prm:Q
req:loc·tsk

@forced_choice_architecture F·A·3d·1
#AIL·CO·self_eff·agenc_att·PC·posit_ill·NC·RXN [pbe] ^
X·n·m·a·p·l·t
prm:S
req:tsk

@one_ahead_sequence L·A·1w·2
#RV2·TR·CE·PC·ANT·NC·behav_act [bet] ^
R·n·l·i·p·m·e
prm:Q

@coincidence_stack L·A·3d·2
#AI·PDT·CE·AW·MM·CB·need_cog·natur_res·motiv_rea [pbe] /
S·n·p·i·p·s·e
prm:S
req:loc

@ambient_number_seeding F·CA·2w·1
#retro_att·AI·CO·CE·PC·hinds_bia·CB·NC [pb] -
X·n·p·i·p·m·t
prm:S
req:loc

@progressive_anesthesia F·A·ongo·1
#habituat·normaliz·escal_tol·CO·sunk_ass [pbet] -
X·n·l·i·p·l·e
prm:S

@dual_reality_dispatch M·CR·1w·3
#SP·RTT·CB·PI·TR·HV·CD [bec] ^
S·n·m·i·p·s·e
prm:Q
req:cnf·loc

@retroactive_biography L·A·2w·3
#UR·TR·PA·ident_des·tempo_dis [bet] ^
R·n·l·i·p·m·e
prm:Q
req:tsk

@thoughtform_plant F·A·2w·2
#AI·PC·MM·CE·IIV·CB·NC·motiv_rea·ident_cog [pbec] -
X·n·p·i·p·l·t
prm:S
req:loc

@async_book_test F·A·3d·3
#AIL·RV2·AW·TR·PC·natur_res·NC·RXN [bec] ^
R·n·m·i·p·n·d
prm:Q
req:tsk

@ambient_symbol_echo F·CA·1w·1
#PDT·retro_att·CO·CE·AI·need_cog·hinds_bia·CB [pbe] -
X·n·p·i·p·m·t
prm:S
req:loc

@intake_echo F·A·3d·2
#RH·TR·UR·PA·DR·SQ·RC [be] ^
R·n·p·i·p·m·t
prm:Q

@filed_prediction L·CA·2w·3
#RV2·AW·SP·CO·ANT·natur_res·behav_act [pc] ^
R·n·l·i·p·n·d
prm:Q
req:loc

@directed_dream F·A·over·2
#IIV·MM·CB·CE·DR·ident_cog·motiv_rea·RC [bet] -
C·q·m·i·p·l·t
prm:Q

@third_party_confirmation L·CR·3d·3
#SP·RTT·CB·TR·PI·HV·CD [betc] /
B·n·l·a·s·s·e
prm:Q
req:loc

@self_fulfilling_dispatch F·A·3d·2
#behav_exp·CO·ident_con·self_eff·AIL·posit_ill·RXN [bet] ^
C·n·m·i·p·l·t
prm:Q
req:tsk

@named_stranger L·CR·1w·3
#CB·PC·SP·AW·RTT·NC·natur_res·CD [etc] ^
C·n·m·i·p·n·e
prm:Q
req:cnf·loc

@calibrated_miss F·A·3d·2
#TR·RV2·LA·autho_att·CO [be] ^
R·n·m·i·p·s·t
prm:Q

@threshold_naming F·A·ongo·3
#ident_cry·namin_pow·CO·self_exp·closu_com·ident_cog [tcd] ^
C·q·l·i·ps·l·d
prm:Q

@legend_seed L·A·4w·1
#antic_cog·NT·consi_bia·PC·behav_act·EC·NC·CO [p] /
B·n·p·a·p·l·e
prm:Q
req:tsk

@walk_in_approach F·A·3d·2
#PR·CG·socia_inv·appro_mot·need_cog·CE·behav_act [p] /
C·q·m·i·p·i·e
prm:Q

@brush_pass_transfer L·CR·3d·3
#somat_hyp·RA·NT·EC [be] ^
B·n·l·a·p·i·e
prm:Q→sct
req:cnf·loc

@dead_drop_receive L·CA·3d·2
#CG·somat_hyp·spati_mem·NT·CE·NS·EC [bet] /
B·q·m·a·p·s·e
prm:Q
req:loc

@challenge_response_protocol F·A·1d·2
#ritua_beh·IGI·consi_bia·authe_heu·TR·habit·socia_the·TR·CO [pbe] /
B·q·l·a·p·i·t
prm:S

@cut_out_introduction F·A·3d·2
#SP·compa_cog·trust_tra·IV·CG·TR·CE [pb] /
B·q·l·a·p·m·e
prm:Q

@mice_ego_appeal F·A·3d·2
#self_enh·SC·IA·scarc_fra·appro_mot·ident_cog·scarc_min·behav_act [pb] /
C·q·l·i·p·s·e
prm:S
req:inq

@mice_ideology_appeal F·A·3d·2
#value_con·moral_ide·socia_ide·commi_esc·purpo_fra·CO [pbe] /
C·q·m·i·p·s·e
prm:Q
req:inq

@mice_coercion_shadow F·A·3d·4
#TA·LA·vigil_res·behav_inh·compl_cas [et] /
S·q·m·+·p·i·d
prm:Q
req:inq

@mice_money_signal L·A·3d·2
#RC·LA·mater_inc·TR·trans_fra·TR [pb] /
B·q·m·a·p·s·e
prm:S
req:csh

@surveillance_detection_route F·A·3d·2
#hyper_ind·spati_att·PR·TA·behav_pri·HV·need_cog [be] /
B·q·h·a·p·s·t
prm:Q
req:loc·inq

@mole_hunt_brief F·A·3d·3
#PI·trust_dis·inves_mot·socia_ana·sense_urg·HV·CD·NC [bet] /
B·q·h·+·p·m·d
prm:Q

@compartmentalization_brief F·A·1d·2
#exclu_fra·IV·IGI·secre_mot·TR·socia_the·TR·scarc_min [be] /
B·q·l·a·p·m·e
prm:S

@legend_stress_test F·CA·3d·3
#consi_pre·ident_per·worki_loa·socia_eva·commi_tes·CO·impre_man·cogni_pro [bet] ^
B·n·h·i·p·i·e
prm:Q
req:cnf

@exfiltration_protocol F·A·3d·2
#threa_con·safet_beh·conti_pla·dread_ind·RA·amygd_res·anxie_avo·cogni_pro [be] /
B·q·l·a·p·n·t
prm:Q

@legend_depth_build L·A·13·2
#RA·CD·tempo_ext·disco_mot·NT·EC [pb] -
B·n·m·a·p·l·e
prm:Q
req:tsk

@asset_validation_request F·A·3d·1
#SP·role_con·TR·task_ori·opera_bel·TR [be] /
B·q·m·a·p·s·t
prm:S
req:inq

@dry_cleaning_walk F·CA·3d·3
#hyper_ind·somat_hyp·spati_pri·TA·HV [et] /
B·q·h·a·p·s·e
prm:Q
req:cnf·loc

@one_time_pad_receipt L·A·3d·2
#symbo_enc·mater_cul·ritua_beh·IV·exclu_fra·habit·scarc_min [be] /
B·q·m·a·p·m·e
prm:S
req:csh·tsk

@handler_letter L·A·3d·2
#PA·epist_int·trust_sca·care_rec·relat_con·TR·gratitud [bed] /
B·q·p·+·p·m·e
prm:S
req:inq

@safe_house_assignment F·A·3d·1
#spati_anc·safet_beh·conti_pla·RA·TR·proxe_spa·somat_hyp·anxie_avo·cogni_pro [be] /
B·q·l·a·p·n·t
prm:Q
req:loc

@mice_full_profile M·A·2w·4
#IC·self_dis·surve_awa·sense_urg·metac_dis·ident_cog·NC [tc] /
B·q·l·+·p·i·x
prm:Q
req:inq·tsk

@welcome_flood L·A·3d·2
#SP·RC·warmt_sig·speci_cre [p] /
C·n·p·i·ps·s·e
prm:Q
req:inq

@lexical_handshake F·A·0·1
#in-gr_lan·socia_the·fluen_bel·incre_fam [pb] /
C·n·l·i·ps·m·t
prm:S

@the_vetting_letter L·A·3d·2
#selec_eff·commi_esc·RC·ident_jud·CO [pb] /
B·n·p·i·p·s·e
prm:Q

@first_disclosure_invitation F·A·0·2
#self_rec·intim_vul·commi_rev·ICH·RC [pb] /
C·n·m·i·p·m·e
prm:Q

@incremental_oath F·A·0·2
#foot_doo·escal_com·cogni_red·behav_con·CO·CD [be] /
C·n·m·i·ps·l·d
prm:Q

@lexical_deepening F·A·0·2
#in-gr_lan·CRF·reali_tun·ident_voc·CD [be] /
C·n·l·i·ps·l·e
prm:Q

@the_naming_ceremony L·CA·3d·3
#IIV·symbo_com·ritua_mar·ego_rol·ident_cog [bet] ^
C·q·m·i·ps·m·d
prm:Q
req:cnf

@milieu_letter L·A·3d·2
#milie_nar·reali_fra·sacre_rhe·in-gr_cos·confo_inf·motiv_rea·OA·socia_the [pb] /
B·n·p·i·p·s·e
prm:S

@the_shadow_walk L·A·1d·2
#felt_car·holdi_env·attac_act·omnip_ben·attac_sty [be] /
C·n·p·+·ps·m·e
prm:Q
req:cnf·inq

@the_purity_protocol F·A·3d·2
#BCM·cogni_con·ritua_act·SPT·CO [be] /
X·n·m·i·p·s·e
prm:Q

@the_deep_archive_pull L·A·3d·3
#impli_omn·inves_sig·preem_int·depth_car·OA·sunk_fal·TR·attac_sty [be] ^
R·q·p·i·p·s·e
prm:Q
req:osn·inq

@thought_stopping_interrupt F·A·0·2
#doubt_red·CRF·epist_aut·resis_rei·CD·motiv_rea·OA [be] /
X·n·l·i·p·m·e
prm:S

@the_floating_moment M·CR·2w·3
#peak_ind·appet_cre·state_mem·trans_hoo·peak_rul·NS [bet] ^
R·n·m·i·p·l·t
prm:Q
req:cnf

@witnessed_confession F·CA·3d·3
#vulne_bon·mutua_dis·shame_tra·colle_hol·TR·RC·shame_res·socia_the [et] ^
C·q·h·i·ps·m·d
prm:Q
req:cnf·trst

@the_us_signal F·A·0·2
#in-gr_for·socia_the·belon_dis·other_mil·minim_par·in_fav [be] /
B·n·p·i·ps·m·e
prm:Q

@graduated_reveal L·A·1w·2
#EAC·infor_tie·antic_sca·readi_gat·effor_jus [pbe] /
R·n·m·i·p·l·e
prm:S→esc
req:inq

@graduation_ritual M·CA·3d·3
#RP·SE·LT2·RT2·somat_hyp [etc] ^
C·q·m·i·ps·s·d
prm:Q
req:cnf

@the_long_echo F·A·arcl·3
#conti_sig·patte_rew·long_pre·plant_cal·CO·need_cog·MEE [cd] ^
R·q·p·i·p·i·t
prm:Q
req:cnf

@parallel_correspondent L·A·3d·2
#imagi_com·socia_imp·solid_con·parallel·socia_the·SP·EC [be] /
C·n·p·+·ps·m·e
prm:S

@borrowed_authority F·A·1d·1
#SP·autho_ass·legit_tra·insti_end [pb] /
B·n·p·a·p·s·t
prm:S
req:inq

@productive_rupture M·CA·2w·4
#ruptu_bon·trust_cri·attac_dee·earne_rec·attac_sty·TR [et] ^
C·m·h·+·ps·l·d
prm:Q
req:cnf

@exit_honored F·A·0·1
#safet_app·conse_arc·trust_exi·ruptu_pre·anxie_avo·RXN·TR [pbetcd] _
C·q·p·i·ps·i·t
prm:S

@anomalous_receipt L·A·3d·1
#CG·PR·situa_amb·CE·need_cog [p] /
S·*·l·a·p·s·e
prm:Q→sct
req:loc

@dead_letter_office L·CA·4w·2
#TDP·authe_cue·narra_wei·const_the·TR [pb] /
R·*·l·i·p·i·e
prm:Q→sct
req:loc·tsk

@cipher_in_plain_sight F·A·3d·2
#PR·CPR·CG·need_cog·CE·achie_mot [pb] /
C·*·h·a·p·m·t
prm:Q
req:tsk

@multi_key_first_fragment L·A·3d·1
#CG·compl_dri·forwa_mom·CE·CO [p] /
C·n·m·a·e·i·t
prm:S

@time_locked_page F·A·1w·2
#AN·preci_rew·calen_sig·behav_act·need_cog·const_the [bet] /
X·n·l·a·p·i·e
prm:Q→esc
req:tsk

@fragmented_witness L·A·2w·2
#persp_con·activ_inf·narra_con·CD·cogni_pro·motiv_rea [be] /
R·*·h·i·p·m·t
prm:Q→esc

@the_unreliable_archive L·A·23·2
#EU·activ_inf·TR·NC·TR·cogni_pro [bet] /
S·*·h·i·p·l·t
prm:Q
req:tsk

@puppet_master_near_miss M·CR·2w·3
#meta_awa·CRV·trust_rec·need_cog·CE·TR [et] ^
S·n·m·+·p·s·d
prm:Q
req:cnf

@tinag_frame_break F·A·3d·3
#meta_cog·diege_con·frame_man·need_cog·RXN·cogni_pro [etc] >
S·m·l·i·p·i·d
prm:Q

@optional_path L·A·1w·2
#AU·CPR·depth_sig·RXN·achie_mot·CE [be] >
C·q·h·a·p·m·t
prm:S→esc

@community_solve_bait L·A·2w·2
#socia_lat·colla_dri·epist_hum·SP·socia_the·need_cog [be] -
C·n·h·a·s·l·e
prm:Q→esc
req:tsk

@the_false_confirmation F·A·3d·2
#retro_sen·PM·narra_anc·hinds_bia·affec_pri·motiv_rea [be] ^
S·n·l·i·p·s·e
prm:Q→esc

@meta_game_layer L·A·4w·3
#recur_str·meta_cog·verti_ind·need_cog·CD [et] >
S·m·h·i·p·l·t
prm:Q
req:tsk

@slow_burn_url F·A·36·2
#delay_pay·patie_rew·tempo_sig·tempo_dis·const_the [pbe] /
C·n·l·a·p·l·e
prm:Q→esc
req:tsk

@personalized_glitch L·A·3d·3
#uncan_per·PDR·atten_cap·CD [pbe] /
S·*·l·i·p·i·e
prm:S→esc
req:tsk

@relay_handler M·CR·23·2
#socia_con·compa_eff·ritua_han·socia_the [be] -
B·q·l·a·p·s·e
prm:Q→esc
req:cnf

@physical_object_as_key M·A·13·3
#somat_hyp·affor_sig [bet] /
C·*·h·a·p·m·d
prm:Q→esc
req:csh·loc·tsk

@breadcrumb_sequence L·A·2w·2
#forwa_mom·self_dir·CPR·CO·achie_mot [pbe] /
C·n·h·a·p·m·t
prm:Q→esc
req:tsk

@witness_who_returns L·CA·vari·2
#NC2·socia_con·RSG·socia_the·hinds_bia·motiv_rea [bec] ^
R·n·l·i·ps·i·e
prm:Q→esc
req:cnf

@diegetic_archive_site M·A·4w·2
#world_den·epist_imm·self_exp·need_cog [pbe] -
C·n·h·i·p·l·t
prm:S→esc
req:tsk

@scheduled_interruption F·A·3d·2
#preci_kee·livin_pro·calen_sig·const_the [be] /
X·*·l·a·e·i·t
prm:Q→sct

@convergence_point M·A·36·3
#PC·multi_syn·revel_arc·NC [etc] ^
R·q·h·+·p·m·t
prm:Q
req:tsk

@wax_seal_letter L·A·3d·2
#mater_sig·regis_shi·aesth_aut·senso_sen·affec_pri·OA [pbt] /
B·*·p·+·p·i·t
prm:S
req:csh·loc

@one_wrong_word F·A·3d·2
#close_rew·PDR·signa_det·CD [be] /
S·*·h·i·p·l·t
prm:Q→esc

@retro_medium_artifact L·A·3d·2
#NS·authe_cue·CE·AI·CB·TR [pb] /
R·n·m·a·p·m·e
prm:S
syn:archive_snapshot·indexed_ghost_page·community_solve_bait·slow_burn_url·diegetic_archive_site
req:tsk

@soft_landing L·A·1d·1
#closu_rit·warm_pre·low_con·grief_ber·attac_sty [d] _
R·q·p·+·p·i·t
prm:Q

@artifact_as_relic L·CA·3d·1
#memor_anc·trans_obj·mater_mea·NS·attac_sty·somat_hyp [d] >
R·m·l·i·p·i·e
prm:Q
req:loc

@day_seven_reframe F·A·setu·1
#RSG·tempo_ins·delay_mea·hinds_bia [d] ^
R·q·l·i·p·s·t
prm:S

@integration_letter L·A·2·2
#narra_con·witne_sel·exter_ref·ident_cog·impre_man [d] _
R·q·p·i·p·i·d
prm:Q

@long_shadow F·A·plan·1
#conti_rel·felt_per·tempo_dep·const_the [d] _
R·q·p·i·p·i·t
prm:Q

@quiet_withdrawal F·A·plan·1
#desig_abs·inten_sil·grace_dim·attac_sty·grief_ber [d] _
X·q·p·a·e·m·e
prm:Q

@graceful_release F·A·0·1
#auton_res·digni_pre·uncon_reg·RXN·shame_res·attac_sty [pbet] _
R·q·p·+·p·i·e
prm:S

@open_door_signal F·A·0·1
#low_ava·auton_pro·optio_re-·RXN [pbet] _
C·q·l·+·p·i·t
prm:Q

@breadcrumb_without_demand L·CA·3d·1
#pure_gif·AP·no_off·RC [pb] /
C·n·p·a·p·l·t
prm:Q
req:loc

@seam_acknowledgment L·CA·3d·2
#diege_met·frame_rep·trust_hon·CD·TR [bet] _
R·m·m·i·p·s·d
prm:Q
req:tsk

@test_reframe L·A·1d·2
#reframin·meta-_inv·confi_sus·CD·CB [et] ^
R·m·m·i·p·s·d
prm:Q
req:tsk

@misfire_as_story L·A·3d·1
#narra_abs·ficti_ref·error_cha·EC·CD [betc] >
R·m·l·i·p·s·e
prm:Q
req:tsk

@wrong_read_recovery L·CA·3d·1
#impli_cal·attun_sig·chara_res·TR [bet] _
R·m·l·i·p·s·e
prm:Q
req:tsk

@shadow_correspondent M·CR·3d·2
#produ_ten·multi_fra·inter_mul·CD [bet] -
B·n·m·i·p·s·d
prm:Q
req:cnf

@broken_immersion_honor L·CA·0·3
#meta_tra·trust_hon·conse_exi·TR·RXN [betc] _
R·m·h·i·p·i·d
prm:Q
req:cnf·loc

@elegant_failure L·A·1d·1
#diege_con·syste_cha·error_evi·CD [betc] _
R·m·l·i·p·s·e
prm:Q
req:tsk

@unknowing_collaboration M·CA·2w·2
#distr_age·invis_int·emerg_com·socia_the [etc] -
C·n·m·a·s·l·d
prm:Q
req:tsk

@parallel_discovery M·CA·2w·2
#desig_con·synch_con·share_dis·socia_the·EC [bet] ^
C·n·m·i·p·l·d
prm:Q
req:tsk

@convergence_signal F·A·1d·2
#revel_int·world_sig·RSG·hinds_bia [tcd] _
R·q·l·i·p·s·d
prm:Q
req:tsk

@ambient_organization_presence M·A·8w·1
#world_pre·searchab·insti_cre·ambie_ver·OA [p] -
B·n·l·a·p·n·d
prm:S
req:tsk

@deep_backstory_artifacts M·CA·8w·1
#mater_his·tempo_dep·world_pre·artif_cre·const_the [pbe] /
R·n·m·a·p·l·d
prm:S
req:tsk

@dormant_frequency L·A·esta·2
#delay_act·dorma_des·tempo_ant·behav_act [petc] /
R·n·l·a·p·i·e
prm:Q
req:tsk

@unmarked_anniversary F·A·1d·3
#TA·impli_rec·meani_att·emoti_cui·NS [*] ^
R·q·p·i·p·i·t
prm:S
syn:calendar_holding·elegiac_obituary·time_capsule_dispatch
req:inq

@calendar_holding F·A·1w·2
#TA·susta_sig·laten_exp·patte_rew·NS·need_cog [pb*] /
X·q·p·a·e·s·e
prm:Q→esc
syn:unmarked_anniversary·first_anniversary_dispatch·year_mind_return
req:inq

@first_anniversary_dispatch L·A·365·3
#TA·antic_rec·closu_rit·conti_sig·NS·grief_ber [d*] ^
R·*·l·i·p·i·t
prm:Q
syn:year_mind_return·calendar_holding·unmarked_anniversary

@elegiac_obituary L·HA·5·3
#meani_ref·narra_clo·symbo_rit·ident_mar·grief_ber·ident_cog [tcd] ^
R·*·l·i·p·i·e
prm:Q→cls
syn:time_capsule_dispatch·letter_never_sent·small_ceremony_instruction
req:inq·tsk

@time_capsule_dispatch L·HA·3d·3
#tempo_shi·self_act·nosta_mob·epist_ref·NS [btd] ^
R·*·l·i·p·i·t
prm:S→ids
syn:elegiac_obituary·letter_never_sent·calendar_holding
req:inq·tsk

@photograph_stranger_knows_you L·HA·1w·3
#UR·paras_pro·ident_mir·myste_ind·PA·ident_cog·CE [pbe] ^
R·n·l·i·p·s·e
prm:Q
syn:absent_presence_character·voice_from_disconnected_number·last_known_address_letter
req:inq·tsk

@last_known_address_letter L·HA·3d·2
#displ_aff·spati_act·nosta_mob·EU·NS·NC [pb*] ^
R·*·l·i·p·s·t
prm:S
syn:time_capsule_dispatch·unmarked_anniversary·calendar_holding
req:inq

@locate_photograph_assignment F·A·1d·2
#CO·spati_act·grief_inv·activ_int·somat_hyp·NS [bet] /
C·q·m·+·p·s·t
prm:Q
syn:elegiac_obituary·letter_never_sent·small_ceremony_instruction
req:inq

@letter_never_sent F·A·1d·3
#expre_cat·epist_com·grief_ext·narra_wit·grief_ber·NC·impre_man [betc] ^
C·q·h·i·p·i·d
prm:Q
syn:elegiac_obituary·small_ceremony_instruction·time_capsule_dispatch

@small_ceremony_instruction F·A·1d·2
#CO·sacre_fra·atten_foc·somat_hyp [tcd*] ^
C·q·m·+·p·i·t
prm:Q
syn:liminal_hour_dispatch·letter_never_sent·elegiac_obituary·natural_calendar_beat
req:inq

@liminal_hour_dispatch F·A·1d·3
#tempo_def·sleep_vul·alter_sta·uncan_int·const_the·somat_hyp·cogni_pro·HV [etc] ^
X·q·p·a·e·i·t
prm:Q
syn:voice_from_disconnected_number·natural_calendar_beat·small_ceremony_instruction

@natural_calendar_beat F·A·2w·2
#ecolo_anc·natur_res·sacre_fra·meani_att·natur_res [*] /
R·*·p·+·p·s·t
prm:S
syn:small_ceremony_instruction·liminal_hour_dispatch·unmarked_anniversary

@absent_presence_character L·HM·2w·3
#PA·postm_pre·objec_rel·susta_mys [pbe*] -
B·*·l·i·p·n·d
prm:Q
syn:photograph_stranger_knows_you·voice_from_disconnected_number·time_capsule_dispatch·locate_photograph_assignment

@voice_from_disconnected_number L·HA·3d·3
#audit_ind·tempo_unc·paras_act·mediu_aff·PA·HV·affec_pri [bet] ^
S·n·l·i·p·i·e
prm:Q
syn:absent_presence_character·photograph_stranger_knows_you·liminal_hour_dispatch
req:cnf

@past_tense_prophecy F·A·2·3
#tempo_inv·antic_ind·narra_pro·epist_def·const_the·grief_ber·CD [bet] ^
R·n·p·i·p·i·t
prm:Q
syn:time_capsule_dispatch·calendar_holding·first_anniversary_dispatch
req:tsk

@memorial_object_arrival L·HA·5·3
#OMA·proxe_spa·somat_hyp·sacre_des·NS [tcd*] ^
R·*·p·i·p·i·t
prm:S
syn:small_ceremony_instruction·elegiac_obituary·absent_presence_character

@year_mind_return L·A·365·3
#TA·ritua_rec·conti_wit·grief_ack·NS [d] ^
R·*·p·i·p·i·t
prm:Q
syn:first_anniversary_dispatch·calendar_holding·small_ceremony_instruction

@inventory_of_what_remains F·A·2·2
#catal_rit·atten_shi·post_mak·senso_sen·somat_hyp·grief_ber [btd] -
C·q·m·i·p·s·t
prm:Q
syn:locate_photograph_assignment·elegiac_obituary·memorial_object_arrival
req:inq

@forwarded_grief L·HA·5·2
#distr_mou·witne_ext·colle_ind·legac_fra·grief_ber·PA·SQ [bed] ^
R·*·l·i·p·s·t
prm:Q
syn:absent_presence_character·photograph_stranger_knows_you·inventory_of_what_remains
req:tsk

@sealed_room F·A·3d·2
#prote_fra·tempo_met·grief_rit·agenc_pac·grief_ber·const_the·RXN [td*] ^
R·q·l·i·p·i·t
prm:S→cls
syn:small_ceremony_instruction·letter_never_sent·inventory_of_what_remains

@witness_register F·A·1d·2
#namin_act·catal_rit·publi_fra·grief_leg·SQ·grief_ber [tcd] ^
R·q·l·i·ps·i·e
prm:Q
syn:elegiac_obituary·letter_never_sent·year_mind_return
req:tsk

@grief_time_legible F·A·2w·3
#narra_ret·tempo_ref·meani_fac·integ_sup·NS·const_the·motiv_rea·attac_sty [d] -
R·q·l·i·p·i·t
prm:Q
syn:inventory_of_what_remains·elegiac_obituary·year_mind_return·witness_register
req:tsk

@memo_field_transmission F·A·1d·2
#PR·SL·MC·atten_cap·need_cog·motiv_rea [pbe] /
M·q·l·a·p·i·e
prm:Q
syn:ticker_feed_events·portfolio_life_decisions·receipt_anomaly_line_item
req:tsk

@receipt_anomaly_line_item L·HA·3d·2
#PDR·MC·SL·NG·motiv_rea·CD [bet] ^
S·n·l·a·p·s·e
prm:Q
syn:memo_field_transmission·statement_of_account·appraisal_letter
req:loc

@refund_from_nowhere L·HA·5·3
#UB·CD·NG·CIN·CE·motiv_rea [pbt] ^
S·n·m·a·p·s·d
prm:Q
syn:memo_field_transmission·grant_award_letter·escrow_formal_notice
req:csh·tsk

@invoice_intangible_services F·A·2·3
#OI·IC·MC·CL2·RC·ident_cog·motiv_rea [betc] ^
M·n·l·i·p·s·e
prm:Q
syn:statement_of_account·promissory_note·lien_on_abstract·receipt_anomaly_line_item
req:tsk

@statement_of_account L·A·5·3
#IC·PR·NG·MC·CL2·ident_cog·need_cog·motiv_rea [bet] /
M·n·l·i·p·s·e
prm:Q
syn:invoice_intangible_services·promissory_note·portfolio_life_decisions·credit_report_parallel_self
req:tsk

@escrow_formal_notice L·A·3d·3
#suspe_ind·OI·CL2·uncer_ext·RC [betc] ^
B·n·m·i·p·s·e
prm:S
syn:statement_of_account·invoice_intangible_services·grant_award_letter·promissory_note
req:tsk

@beneficiary_selection_notice L·A·3d·3
#SE·UB·NG·CIN·MC·CE·motiv_rea [pbe] ^
R·n·l·i·p·s·e
prm:Q
syn:grant_award_letter·escrow_formal_notice·refund_from_nowhere·memo_field_transmission
req:tsk

@grant_award_letter M·HA·1w·3
#SE·IA·MC·effor_jus·CIN·ident_cog·motiv_rea·CE [pbt] ^
R·n·m·i·p·m·d
prm:Q
syn:beneficiary_selection_notice·escrow_formal_notice·w2_fictional_employer·appraisal_letter
req:tsk

@bearer_bond_certificate L·A·1w·2
#objec_inv·MC·NG·IA·motiv_rea·ident_cog [betc] ^
B·n·p·i·p·m·t
prm:Q
syn:escrow_formal_notice·appraisal_letter·ticker_feed_events·w2_fictional_employer
req:tsk

@ticker_feed_events L·A·2w·2
#PR·SL·MC·TA·suspe_ind·need_cog·motiv_rea·NS [betc*] -
M·q·m·i·p·n·t
prm:Q
syn:bearer_bond_certificate·portfolio_life_decisions·commodity_narrative_report·statement_of_account
req:tsk

@portfolio_life_decisions L·A·1w·3
#IC·MC·PR·NG·self_inv·ident_cog·motiv_rea·need_cog [betd] -
M·q·l·i·p·s·e
prm:Q
syn:ticker_feed_events·statement_of_account·appraisal_letter·credit_report_parallel_self
req:tsk

@commodity_narrative_report F·A·5·2
#PR·SL·MC·coded_com·NG·need_cog·motiv_rea [bet*] -
M·q·l·i·p·m·t
prm:Q
syn:ticker_feed_events·portfolio_life_decisions·memo_field_transmission·bearer_bond_certificate
req:tsk

@collections_agency_notice L·A·5·4
#TA·OI·IC·CL2·urgen_ind·RC·ident_cog [etc] ^
M·n·m·a·p·i·d
prm:Q
syn:statement_of_account·lien_on_abstract·invoice_intangible_services·promissory_note
req:tsk

@promissory_note L·HA·5·3
#commi_dev·OI·IA·ritua_fra·MC·CO·RC·ident_cog·motiv_rea [tcd] ^
B·n·h·i·p·s·d
prm:Q
syn:escrow_formal_notice·invoice_intangible_services·lien_on_abstract·statement_of_account
req:tsk

@lien_on_abstract L·A·5·4
#IC·TA·MC·CD·OI·ident_cog·motiv_rea·RC [etc] ^
M·n·m·i·p·i·d
prm:Q
syn:collections_agency_notice·promissory_note·statement_of_account·invoice_intangible_services
req:tsk

@credit_report_parallel_self L·A·1w·4
#IC·UR·NG·CD·PR·ident_cog·motiv_rea·need_cog [etc] ^
M·n·p·i·p·s·x
prm:Q
syn:portfolio_life_decisions·statement_of_account·w2_fictional_employer·property_tax_notice
req:tsk

@w2_fictional_employer L·A·5·3
#IA·MC·NG·IC·PR·ident_cog·motiv_rea·need_cog [bet] ^
M·n·p·i·p·s·e
prm:Q
syn:grant_award_letter·credit_report_parallel_self·property_tax_notice·statement_of_account
req:tsk

@property_tax_notice L·A·1w·3
#spati_anc·IC·MC·owner_dis·NG·proxe_spa·ident_cog·motiv_rea [bet] ^
M·n·l·a·p·s·e
prm:S
syn:credit_report_parallel_self·w2_fictional_employer·lien_on_abstract·bearer_bond_certificate
req:loc·tsk

@appraisal_letter L·A·5·3
#MC·IA·value_ass·SE·CD·motiv_rea·ident_cog [bed] ^
R·n·p·i·p·s·t
prm:Q
syn:grant_award_letter·portfolio_life_decisions·w2_fictional_employer·bearer_bond_certificate
req:tsk

@market_analysis_participant_choices L·A·5·2
#PR·IC·MC·self_inv·tempo_fra·need_cog·ident_cog·motiv_rea [bed] -
M·q·l·i·p·s·t
prm:S
syn:portfolio_life_decisions·ticker_feed_events·appraisal_letter·commodity_narrative_report
req:tsk

@dividend_notice L·HA·3d·2
#UB·MC·rewar_sig·tempo_fra·NG·CE·motiv_rea [bd*] ^
R·n·p·a·p·i·t
prm:Q
syn:bearer_bond_certificate·ticker_feed_events·beneficiary_selection_notice·grant_award_letter
req:csh·tsk

@inheritance_fraction_notice M·HA·10·3
#MC·IC·grief_ind·TA·NG·UB·motiv_rea·ident_cog·NS·CE [pbed] ^
RB·n·m·i·p·m·d
prm:Q
syn:escrow_formal_notice·beneficiary_selection_notice·credit_report_parallel_self·statement_of_account
req:tsk

@pre_sleep_sensory_dispatch F·A·1d·2
#antic_aro·AN2·incub_pri·TA2·behav_act·cogni_pro·somat_hyp·senso_sen [pbt] -
X·n·l·i·p·s·t
prm:S
syn:hypnagogic_image_seed·dream_report_request·circadian_dispatch_series

@sleep_data_mirror F·A·3d·2
#self_amp·data_ide·behav_loo·perce_sur·patte_pri·ident_cog·habit·HV [pbe] -
M·n·l·i·p·m·e
prm:Q
syn:circadian_dispatch_series·hunger_window_delivery·physical_threshold_unlock
req:tsk

@three_am_dispatch F·A·1d·3
#limin_exp·reali_deg·TA2·urgen_ind·AN2·somat_hyp·senso_sen·cogni_pro [etc] ^
X·n·p·a·e·i·d
prm:Q
syn:pre_sleep_sensory_dispatch·somatic_key_installation·physical_threshold_unlock

@dream_report_request F·A·2·2
#autob_ela·creat_pro·VAD·self_esc·narra_aut·NS·somat_hyp [pbe] -
C·q·l·i·p·s·t
prm:S→trt
syn:pre_sleep_sensory_dispatch·hypnagogic_image_seed·sensory_diary

@hypnagogic_image_seed F·A·1d·2
#incub_pri·image_ind·AN2·TA2·PS·somat_hyp·cogni_pro·senso_sen [pbt] -
X·n·p·i·p·s·t
prm:S
syn:pre_sleep_sensory_dispatch·dream_report_request·three_am_dispatch

@breath_gate F·A·1d·2
#behav_seq·physi_ind·EAC·somat_hyp·AN2·effor_jus·cogni_pro [betc] >
C·q·m·i·p·i·t
prm:S
syn:somatic_key_installation·pre_sleep_sensory_dispatch·physical_threshold_unlock

@somatic_key_installation F·A·3d·2
#condi_ins·somat_hyp·state_rec·signa_com·ritua_for·habit·NS [pbetc] ^
C·q·l·i·p·l·e
prm:Q
syn:breath_gate·three_am_dispatch·physical_threshold_unlock·somatic_key_activation

@stress_state_calibration F·A·1w·1
#self_ind·behav_col·senso_sen·VAD·patte_pri·somat_hyp [pb] -
R·*·l·a·p·m·t
prm:S
syn:sleep_data_mirror·sensory_diary·circadian_dispatch_series

@contemplative_walk_instruction F·A·1d·1
#EAT·PS·atten_dir·somat_hyp·meani_lay·natur_res·senso_sen [pb*] -
C·q·m·+·p·s·t
prm:S
syn:threshold_crossing_practice·sensory_diary·temperature_weather_dispatch·circadian_dispatch_series
req:loc

@carry_this F·A·1d·2
#objec_anc·meani_tra·behav_hab·CO·semio_loa·habit·somat_hyp [pbet] -
C·q·m·+·p·m·t
prm:S
syn:somatic_key_installation·home_environment_task·threshold_crossing_practice
req:loc

@home_environment_task F·A·1d·2
#BCM·envir_mod·spati_mak·somat_hyp·owner_esc·CO [bet] -
C·q·m·+·p·m·e
prm:S
syn:carry_this·threshold_crossing_practice·somatic_key_installation
req:loc

@threshold_crossing_practice F·A·1d·1
#limin_amp·atten_pri·behav_not·PS·ritua_for·somat_hyp·senso_sen·habit [pbet] /
C·q·l·+·p·s·t
prm:S
syn:contemplative_walk_instruction·carry_this·somatic_key_installation·home_environment_task
req:loc

@sensory_diary F·A·2·1
#PS·autob_ela·atten_tra·creat_dis·VAD·senso_sen·NS·somat_hyp [pb*] -
C·q·l·+·p·m·t
prm:S
syn:stress_state_calibration·dream_report_request·contemplative_walk_instruction·sleep_data_mirror

@temperature_weather_dispatch F·A·1d·1
#envir_cou·natur_res·ambie_rel·conte_anc·PS·somat_hyp·senso_sen [pb*] -
R·q·p·a·e·s·t
prm:S
syn:contemplative_walk_instruction·sensory_diary·seasonal_body_dispatch·dusk_dawn_dispatch
req:tsk

@anticipatory_signal_state F·A·3d·3
#antic_aro·susta_ten·waiti_exp·physi_sus·AN2·behav_act·amygd_res·cogni_pro [betc] /
X·q·l·i·p·i·d
prm:Q
syn:somatic_key_installation·breath_gate·three_am_dispatch·physical_threshold_unlock

@hunger_window_delivery F·A·3d·2
#physi_pri·somat_hyp·atten_sha·bound_sof·senso_sen·proxe_spa [bet] ^
X·q·l·a·e·i·t
prm:Q
syn:breath_gate·stress_state_calibration·anticipatory_signal_state
req:tsk

@circadian_dispatch_series F·A·3d·1
#CBC·behav_hab·rhyth_ent·ambie_rel·conte_anc·natur_res·habit·EC·somat_hyp [pb*] /
X·q·p·i·p·m·e
prm:S
syn:temperature_weather_dispatch·sleep_data_mirror·stress_state_calibration·pre_sleep_sensory_dispatch
req:tsk

@seasonal_body_dispatch F·A·1d·1
#CBC·EAT·natur_res·PS·meani_lay·somat_hyp·senso_sen [pb*] -
R·n·p·i·p·m·t
prm:S
syn:temperature_weather_dispatch·dusk_dawn_dispatch·contemplative_walk_instruction·circadian_dispatch_series

@dusk_dawn_dispatch F·A·1d·2
#limin_amp·CBC·TA2·EAT·AN2·somat_hyp·natur_res·senso_sen·cogni_pro [pbetcd] -
X·n·p·a·e·s·t
prm:S
syn:seasonal_body_dispatch·temperature_weather_dispatch·pre_sleep_sensory_dispatch·contemplative_walk_instruction
req:tsk

@physical_threshold_unlock F·A·1d·2
#BCM·EAC·achie_mot·effor_jus·self_amp·somat_hyp·CO·posit_ill [betc] ^
C·q·h·+·p·s·t
prm:Q
syn:breath_gate·sleep_data_mirror·stress_state_calibration·anticipatory_signal_state

@indexed_ghost_page F·A·28·1
#PR·EXV·CB·need_cog·CD [p] /
R·n·p·a·w·n·d
prm:S
syn:search_surface_reveal·archive_snapshot·dossier_drop
req:tsk

@archive_snapshot F·A·35·1
#TDP·PR·CB·AC·const_the·need_cog·OA [p] /
R·n·p·a·w·n·d
prm:S→sct
syn:indexed_ghost_page·dossier_drop·search_surface_reveal
req:tsk

@silent_follower F·HA·21·1
#SP·PR·ambie_cue·EXV·need_cog·CD [p] -
S·n·p·i·p·l·e
prm:S
syn:social_graph_bridge·character_reveal·dossier_drop
req:tsk

@minor_wikipedia_edit F·HA·42·1
#AC·PR·AS·CB·OA·need_cog·CE [p] -
R·n·p·a·w·n·d
prm:S
syn:indexed_ghost_page·archive_snapshot·dossier_drop·search_surface_reveal
req:tsk

@maps_review_plant F·HA·2w·1
#EA·PR·SP·AS·need_cog·CE·somat_hyp [p] -
R·n·p·a·w·l·e
prm:S
syn:physical_trace_plant·book_bench_drop·indexed_ghost_page
req:tsk

@street_mark L·HA·28·1
#EA·PR·ambie_rec·spati_pri·need_cog·NS·somat_hyp [p] /
C·n·p·a·w·l·e
prm:S
syn:book_bench_drop·ambient_triple_seed·physical_trace_plant·location_significance_play
req:loc

@book_bench_drop L·HA·1w·1
#GS·AS·EA·NS2·CE·RC·somat_hyp [p] /
C·n·l·a·p·l·t
prm:S→sct
syn:physical_trace_plant·street_mark·postcard_blind_send·ambient_triple_seed
req:loc

@physical_trace_plant L·C·35·1
#EA·AS·UP·spati_pri·CE·NS·somat_hyp [p] /
C·n·p·a·p·n·e
prm:S
syn:book_bench_drop·postcard_blind_send·object_significance_reveal
req:cnf

@postcard_blind_send L·A·2w·1
#GS·AS·AC·NS2·UP·CE·OA·RC [p] /
C·n·p·a·p·l·x
prm:S
syn:book_bench_drop·classified_ad_plant·subscription_infiltration·physical_trace_plant
req:loc

@classified_ad_plant L·HA·21·1
#AS·PR·NS2·AC·CE·need_cog·OA [p] /
C·n·p·a·w·l·d
prm:S→asr
syn:indexed_ghost_page·postcard_blind_send·ambient_triple_seed·book_bench_drop
req:csh·loc

@character_bridge_connection F·HA·28·1
#SP·AC·SN·trust_tra·OA·TR [p] /
B·n·p·i·s·l·e
prm:S
syn:silent_follower·social_graph_bridge·dossier_drop·character_reveal
req:tsk

@sighting_report F·C·2w·2
#SP·ambie_cue·UP·CG·CE [p] /
S·n·l·i·p·l·x
prm:S
syn:silent_follower·character_bridge_connection·character_reveal·social_graph_bridge
req:cnf

@ambient_triple_seed M·HM·1w·2
#PR·coinc_man·CB·AI·need_cog [p] /
X·n·p·i·p·n·x
prm:S
syn:street_mark·maps_review_plant·classified_ad_plant·postcard_blind_send·arc_open
req:loc·tsk

@subscription_infiltration L·A·21·1
#AS·EXV·CG·NS2·CE·CD [p] -
C·n·p·a·p·l·e
prm:S
syn:indexed_ghost_page·classified_ad_plant·postcard_blind_send·dossier_drop
req:tsk

@false_memory_seed L·HA·28·2
#sourc_err·NS2·AS·memor_rec·CE [p] -
S·n·p·i·p·n·x
prm:S→asr
syn:ambient_triple_seed·subscription_infiltration·classified_ad_plant·character_bridge_connection
req:cnf

@birthday_card_unknown_sender L·A·2w·1
#GS·UP·CG·SN·CE·RC [p] ^
R·n·p·a·p·l·x
prm:Q→sct
syn:postcard_blind_send·subscription_infiltration·character_reveal·dossier_drop
req:loc

@glassdoor_reference_plant F·HA·21·1
#AC·SP·AS·ident_rel·OA·CE [p] -
R·n·p·a·w·l·e
prm:S
syn:character_bridge_connection·indexed_ghost_page·silent_follower
req:tsk

@recurring_audio_seed M·HM·2w·2
#AS·PR·AI·emoti_pri·memor_rec·CE·need_cog·CB [p] -
X·n·p·i·p·n·d
prm:S
syn:ambient_triple_seed·street_mark·false_memory_seed·arc_open
req:loc·tsk

@change_talk_elicitation F·C·0·2
#SPT·cogni_red·elabo_lik·CO·CD [btd] -
C·q·h·i·p·m·t
prm:Q
syn:outsider_witness_ceremony·generalization_contract·player_journal_artifact

@outsider_witness_ceremony F·C·0·2
#SV·IA·NC2·belongin·SP·ident_cog·socia_the·motiv_rea [cd] ^
R·q·p·i·ps·m·t
prm:Q
syn:commissioning_letter·change_talk_elicitation·stripping_ceremony
req:cnf

@generalization_contract L·A·0·1
#CO·imple_int·IA·FS·ident_cog [d] >
C·*·h·i·p·s·t
prm:Q
syn:commissioning_letter·change_talk_elicitation·outsider_witness_ceremony·front_loading_beat
req:csh

@front_loading_beat F·A·0·1
#expec_set·CE·PM·imple_int·affec_pri [pb] /
R·nq·l·i·p·l·t
prm:S
syn:generalization_contract·change_talk_elicitation·nomination_framing
req:csh

@commissioning_letter L·A·3d·2
#IA·CO·AA·NC2·FS·ident_cog·motiv_rea [d] >
C·*·p·i·p·l·t
prm:Q
syn:outsider_witness_ceremony·generalization_contract·handwritten_letter·kinesthetic_encoding_beat
req:csh

@kinesthetic_encoding_beat L·C·3d·2
#somat_hyp·CO·artif_cre·IA·episo_enc·ident_cog [tcd] ^
?·qm·m·+·p·m·m
prm:Q
syn:commissioning_letter·generalization_contract·outsider_witness_ceremony·stripping_ceremony
req:csh·loc

@stripping_ceremony L·C·3d·2
#IS·CO·somat_hyp·role_dif·effor_jus·RXN [pb] ~
X·q·m·i·p·s·m
prm:Q
syn:outsider_witness_ceremony·commissioning_letter·kinesthetic_encoding_beat
req:loc

@failure_cascade_reframe F·A·0·1
#CRF·auton_res·CE·IA·react_red·CD·ident_cog·RXN [be] _
R·*·l·i·p·m·t
prm:S
syn:resistance_acknowledgment·alibi_for_reentry
!ctr:simulated_loss

@knowledge_frontier_seed F·A·0·1
#CE·AI·IG·antic_att·CB·behav_act [pb] /
R·nq·l·a·e·l·t
prm:S→slv
syn:front_loading_beat·parallel_threads·accidental_transmission·slow_burn_url
req:csh

@player_journal_artifact L·A·3d·1
#SPT·NC2·IA·elabo_lik·IKEA_eff·ident_cog·motiv_rea [btd] -
C·qm·h·+·p·l·e
prm:Q
syn:outsider_witness_ceremony·change_talk_elicitation·retroactive_recontextualization·commissioning_letter
req:csh

@temporal_rupture_opening F·A·0·2
#effor_jus·RXN·IS·atten_reo·salie_shi·somat_hyp [pb] >
X·nq·p·i·p·m·t
prm:S
syn:stripping_ceremony·kinesthetic_encoding_beat·commissioning_letter
req:csh

@ordeal_threshold L·C·3d·3
#SK·CO·share_vul·ident_con·endor_bon·sunk_fal·ident_cog [bt] ^
X·q·h·+·p·s·m
prm:Q
syn:stripping_ceremony·communitas_beat·outsider_witness_ceremony
req:loc

@absent_witness_invocation L·A·3d·2
#inter_aut·ident_con·CO·sacre_str·ident_cog [tcd] ^
C·qm·m·i·p·l·m
prm:Q
syn:kinesthetic_encoding_beat·generalization_contract·commissioning_letter
req:csh

@communitas_beat F·C·0·2
#belongin·hiera_dis·direc_bon·effor_jus·RXN·socia_the·somat_hyp [bt] -
M·q·m·i·ps·s·t
prm:Q
syn:outsider_witness_ceremony·change_talk_elicitation·stripping_ceremony
req:cnf

@layered_secret_system F·A·3d·2
#IG·IGI·antic_cur·SK·incre_com·CE·socia_the·sunk_fal·CO [be] /
R·q·m·i·ps·l·e
prm:S
syn:knowledge_frontier_seed·absent_witness_invocation·parallel_threads
req:tsk

@benefactor_capture F·A·ongo·3
#autho_bia·recip_nor·trust_sca·compl_com·retro_att·OA·RC·TR·CO·hinds_bia [pbe] /
R·nm·h·+·p·n·x
prm:Q
syn:manufactured_crisis_reveal·strategic_silence_beat·fractal_revelation

@manufactured_crisis_reveal F·A·ongo·3
#retro_att·CD·compl_rec·autho_col·hinds_bia [tc] ^
R·nm·h·+·p·n·x
prm:Q
syn:benefactor_capture·fractal_revelation·distributed_truth_fragment
req:tsk

@fractal_revelation F·A·0·2
#IG·AI·epist_des·CE·CB·CD [bet] /
R·qm·h·a·p·m·t
prm:Q
syn:knowledge_frontier_seed·distributed_truth_fragment·layered_secret_system
req:tsk

@distributed_truth_fragment L·A·3d·1
#AI·IG·CE·PR·CB·need_cog [pb] /
R·nq·m·a·e·l·t
prm:S
syn:knowledge_frontier_seed·parallel_threads·fractal_revelation·benefactor_capture
req:tsk

@strategic_silence_beat F·A·0·2
#misdi_omi·compl_rea·trust_mai·compl_sil·CB·OA·TR·CO [be] -
X·q·l·a·e·n·t
prm:Q
syn:benefactor_capture·manufactured_crisis_reveal·fractal_revelation

@temporal_loop_architecture L·O·days·2
#epist_imm·antic_att·knowl_acc·parti_det·PR·agenc_rew·need_cog·behav_act [pbe] -
R·?·h·i·p·l·t
prm:S
syn:environmental_narrative_space·one_on_one_private_scene·knowledge_frontier_seed·diegetic_archive_site·the_witness
!ctr:manufactured_crisis_reveal
req:loc

@anomaly_attendance F·O·week·3
#colle_for·commi_act·SP·exper_pro·somat_hyp·socia_the·CO·effor_jus [tc] ^
C·q·h·i·w·t·x
prm:Q
syn:queryable_legacy·communitas_beat·territorial_claim
req:loc

@territorial_claim F·A·days·2
#owner_inv·PL·earne_sta·conte_res·micro_ter·endow_eff·NS·effor_jus·LA·proxe_spa [be] /
C·n·m·+·sw·n·d
prm:S
syn:anomaly_attendance·queryable_legacy·spatial_message
req:loc

@queryable_legacy F·A·0·2
#biogr_con·legac_con·exter_val·histo_rec·earne_ide·ident_cog·SQ·SP·effor_jus [dR] _
R·q·l·i·pw·t·x
prm:Q
syn:anomaly_attendance·territorial_claim·player_journal_artifact·post_arc_letter
req:csh·tsk

@trace_exposure F·A·hour·3
#felt_vul·IV·real_sur·urgen_pre·kinet_dre·shame_res·HV·scarc_min·amygd_res [et] ^
X·q·h·a·p·S·d
prm:Q
syn:active_erasure·contract_complicity·surveillance_detection_route·handler_letter
!ctr:simulated_loss
req:tsk

@contract_complicity F·A·days·2
#compl_ins·defer_rev·retro_gui·moral_dis·willi_par·CO·CE·GT·moral_lic [pb] /
X·n·m·+·p·D·d
prm:S
syn:trace_exposure·active_erasure·benefactor_capture·manufactured_crisis_reveal
!ctr:debrief_conversation

@active_erasure F·A·hour·3
#kinet_com·self_imp·irrev_act·compl_des·volun_con·CO [tc] ^
C·q·h·+·ep·S·x
prm:Q
syn:trace_exposure·contract_complicity·exfiltration_protocol
!ctr:commissioning_letter
req:tsk

@forum_intervention F·A·days·3
#rehea_rea·agenc_res·self_pro·somat_hyp·revis_act [ed] /
C·q·h·+·p·S·t
prm:Q
syn:change_talk_elicitation·failure_cascade_reframe·stripping_ceremony
!ctr:ordeal_threshold

@image_theater_freeze F·A·hour·2
#somat_hyp·power_vis·non_kno·freez_fra [pb] -
X·n·m·i·p·S·t
prm:S
syn:kinesthetic_encoding_beat·stripping_ceremony·internal_monologue_voiced
req:loc

@invisible_theater_event L·O·days·3
#real_bou·unwit_par·authe_unc·frame_col·laten_die·CD·RXN [pb] ^
C·n·h·+·ps·?·d
prm:S
syn:briefed_confederate·planted_witness·manufactured_crisis_reveal
req:loc

@mask_anonymity_passage L·O·hour·2
#permi_ano·IS·explo_lic·trans_saf·dual_con·RXN·somat_hyp·CE [pb] ~
C·n·m·i·p·S·t
prm:S
syn:one_on_one_private_scene·environmental_narrative_space·stripping_ceremony
!ctr:one_on_one_private_scene
req:csh·loc

@one_on_one_private_scene M·CR·days·3
#statu_sel·undiv_att·intim_dis·marke_sin·dyadi_int·SQ·PA·TR [et] ^
S·q·l·i·p·S·t
prm:Q
syn:mask_anonymity_passage·outsider_witness_ceremony·commissioning_letter·stripping_ceremony
req:loc
grp:lo·neut·U·0·1.0

@environmental_narrative_space L·O·days·2
#objec_arc·envir_sem·parti_det·narra_exp·space_cha·CE·need_cog·natur_res [pb] /
R·n·m·+·p·D·t
prm:S
syn:deep_backstory_artifacts·physical_dead_drop·distributed_truth_fragment·the_commission
req:csh·loc

@hell_replay F·A·days·3
#emoti_com·charg_mem·styli_rep·tempo_dis·inten_abs·EC·NS·habit·peak_rul [etd] ^
S·q·l·i·p·S·d
prm:Q
syn:internal_monologue_voiced·stripping_ceremony·manufactured_crisis_reveal·commissioning_letter

@framekick_temporal_shift F·A·0·3
#tempo_rup·disor_des·frame_col·multi_con·reali_rec·CD·const_the [et] ^
R·q·m·+·p·S·t
prm:Q
syn:hell_replay·retroactive_recontextualization·manufactured_crisis_reveal·fractal_revelation
!ctr:hell_replay

@internal_monologue_voiced F·A·0·3
#MD·exter_sta·verba_aut·frame_dee·chara_sim·need_cog·impre_man·TR·CD [et] ^
M·q·h·i·p·S·d
prm:Q
syn:image_theater_freeze·change_talk_elicitation·author_narration_beat·one_on_one_private_scene

@author_narration_beat F·A·days·2
#exter_per·omnis_voi·narra_int·autho_sta·retro_wit·const_the·PA [ed] -
M·q·l·i·p·D·t
prm:Q
syn:internal_monologue_voiced·outsider_witness_ceremony·commissioning_letter·hell_replay

@group_synchronization M·O·same·3
#socia_cas·cogni_red·SQ·in_for·share_con·CD [et] ^
C·q·l·+·ps·s·d
prm:Q
syn:distributed_truth_fragment·handler_letter·faction_formation·the_witness
!ctr:manufactured_crisis_reveal
req:cnf

@faction_formation F·~amb·0·2
#socia_the·in_fav·cogni_red·coord_pro·attit_pol·CD [et] /
E·q·m·i·ps·n·?
prm:Q
syn:group_synchronization·social_proof_cascade·the_witness·optional_path
!ctr:retroactive_recontextualization

@shared_crisis_beat H·O·3d·4
#CL·SQ·UG·in_for·share_con·EC [c] ^
C·q·h·+·ps·i·e
prm:Q→cls
syn:faction_formation·faction_allegiance_fork·group_synchronization·graduation_ritual
!ctr:graduation_ritual

@faction_allegiance_fork H·O·3d·3
#IC·CO·CD·attit_pol·socia_the·in_fav [t] ^
C·q·h·i·ps·n·d
prm:Q
syn:faction_formation·shared_crisis_beat·optional_path·graduation_ritual
!ctr:graduation_ritual

@app_location_dispatch M·A·2w·2
#CG·SQ·PL·AG·EAC·PC [be] /
C·nq·h·a·p·n·t
prm:S→slv
syn:environmental_narrative_space·physical_dead_drop·faction_allegiance_fork·shared_crisis_beat
req:loc

@nested_permission_cascade M·A·arcl·2
#CO·SPT·BCM·CD·AU·EAC [be] /
C·n·m·i·p·l·d
prm:S→ids
syn:graduation_ritual·retroactive_recontextualization·commissioning_letter·nested_permission_cascade
!ctr:manufactured_crisis_reveal

@counter_identity_encounter M·CR·3d·3
#IC·MR·CD·FS·CF·ID [et] ^
C·q·p·i·p·s·d
prm:Q→ids
syn:retroactive_recontextualization·outsider_witness_ceremony·graduation_ritual·the_witness
!ctr:graduation_ritual
req:cnf

@reintegration_dispatch L·A·arcl·2
#conti_sig·ICH·TA·FSC·IIV·MEE [d] -
R·q·p·i·p·n·t
prm:Q
syn:commissioning_letter·resonance_letter·integration_letter·graduation_ritual·the_long_echo

@patience_reward F·A·0·2
#ANT·CE·EAC·PR·AN2·CPR [bet] -
C·q·h·a·p·S·e
prm:S→klg
syn:planted_object·environmental_narrative_space·temporal_loop_architecture·the_witness·strategic_silence_beat

@social_pressure_break F·A·0·3
#RXN·AU·IC·SPT·VAD·CD [etc] ^
R·q·h·+·ps·i·d
prm:S→ids
syn:change_talk_elicitation·one_on_one_private_scene·the_witness·incremental_oath·stripping_ceremony
!ctr:manufactured_crisis_reveal
req:cnf
