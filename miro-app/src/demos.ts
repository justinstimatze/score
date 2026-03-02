// demos.ts — reference arc data and board drop logic for the Guide tab.

import { humanName } from "./utils.js";
import { isMiro, onTabClick } from "./main.js";

interface DemoPlay { id: string; note: string; }

// ⚠ SPOILER NOTE: arc annotations describe key plot mechanics and reveals.
const DEMO_ARCS: Record<string, { label: string; spoiler: boolean; plays: DemoPlay[] }> = {
  snm_seeker: {
    label: "SNM — Seeker path",
    spoiler: true,
    plays: [
      { id: "mask_anonymity_passage",       note: "A white Venetian-style mask is fitted at the entrance; you may not speak for the duration. You become part of the set — undifferentiated from other masked figures. Actors won't acknowledge you unless they choose to select you." },
      { id: "environmental_narrative_space", note: "Five floors of the McKittrick Hotel set-dressed as 1930s Scotland: working telephones, sealed envelopes, real food on plates, dust on every surface. Actors run continuous 45-minute loops whether guests are present or not. Every room is a functioning crime scene." },
      { id: "planted_object",               note: "Objects throughout the space — chess pieces, photographs, taxidermied animals, letters in drawers — can be picked up and handled. They imply lives in progress but offer no instruction. The seeker must decide what is evidence and what is decoration." },
      { id: "the_witness",                  note: "The seeker positions at a specific room entrance to witness a full actor scene: Punchdrunk physical theater, intensely choreographed, looping every 45 minutes. The scene doesn't acknowledge the audience. Witnessing it twice, from different vantage points, is possible if you know the loop." },
      { id: "diegetic_archive_site",        note: "The Manderley Bar holds documents and records that establish the world's history. The Hecate room contains the mythological layer — the witches' logic that underlies the Macbeth plot. Without this context, the story fragments found elsewhere don't cohere." },
      { id: "temporal_loop_architecture",   note: "Around the 45-minute mark, a seeker who has been tracking a character realizes the scene they just witnessed is starting again in the room above. The loop is the architecture — the second pass through the hotel is entirely different because you now know where to stand." },
      { id: "fragmented_witness",           note: "The full Macbeth narrative — Hecate as puppet master, Lady Macbeth's disintegration, the witches' prophecy — only assembles for participants who followed specific characters across multiple loop cycles. Most guests leave with mood and atmosphere but not story." },
      { id: "outsider_witness_ceremony",    note: "At the 2-hour mark, all actors converge in the ballroom for the Hecate finale — including Hecate's hanging. Masked audience surround the action on all sides. Participants who tracked the narrative understand the ceremony; others experience it as pure spectacle. Either is the design." },
    ],
  },
  latitude: {
    label: "House of the Latitude",
    spoiler: true,
    plays: [
      { id: "the_vetting_letter",           note: "Hull seeded Latitude through his existing Nonchalance network in the Mission District. Being invited meant someone vouched for you. The letter was already written in the language of the Fable — the mythology was present in the invitation before you'd agreed to anything." },
      { id: "stripping_ceremony",           note: "At the Alluvium entrance, phone and wallet were surrendered to a Praxis guide. A new name was given. The physical surrender of the phone was specific: Praxis time operated outside ordinary time. The new name marked the threshold between your daily self and your Praxis self." },
      { id: "welcome_flood",                note: "The Alluvium installation: a physical slide descending from an upper level, red neon, Hull's mythology present as environment rather than document. The Fable — the narrative underpinning the whole project — was asserted through the space itself. You were not told it; you were inside it." },
      { id: "incremental_oath",             note: "A library ritual on day 14 formalized the first commitment layer. Before this, you were experiencing; after this, you were a member. The oath was specific to the Praxis vocabulary and was witnessed by other members. Participation now had a named structure and a named obligation." },
      { id: "layered_secret_system",        note: "Nightbook, a private platform, and hexagonal symbols placed at SF locations formed the tiered access system. Visiting a symbol location and recording it in Nightbook unlocked deeper content. Most of the 1,200 members never went below the first tier. The architecture extended much further than almost anyone reached." },
      { id: "lexical_deepening",            note: "Flux, Flow, and Prime were emotional states within the Praxis framework — not just jargon but a lens for re-reading daily experience. Using the vocabulary correctly in conversation marked you as initiated. The language was not fake: Hull's philosophy of nonchalance as resistance to consumer urgency had genuine content that made dismissal harder." },
      { id: "environmental_narrative_space", note: "Latitude assigned members specific SF neighborhoods as their territory. A coffee shop, a park, a particular corner could become Praxis locations with accumulated meaning. The Alluvium served as home base but the experience was designed to operate inside daily life — the city was always the stage." },
      { id: "the_us_signal",                note: "'We are the tunnel people' was actual Latitude terminology. Praxis gatherings had specific ritual structures. By this point the community itself was the primary content — what you did together mattered less than that you were doing it as a named group with a shared cosmology." },
      { id: "graduation_ritual",            note: "~50 of 1,200 members attended the Mendocino weekend retreat at day 120. Hull had designed this as the apex of the arc — the moment where transformation would be named and honored. When he arrived, he had not written the ideology that was supposed to be revealed at the ceremony. The ritual happened; the content was not there." },
    ],
  },
  the_game: {
    label: "The Game (Fincher, 1997)",
    spoiler: true,
    plays: [
      { id: "cold_read",                    note: "CRS administers a battery of psychological tests to Nicholas Van Orton. He believes he is being evaluated to qualify for the game. In fact, the profiling has been underway for weeks — his brother Conrad provided CRS with intimate knowledge of Nicholas's psychology, history, and vulnerabilities before the birthday gift was even mentioned." },
      { id: "barnum_profile_dispatch",      note: "The CRS orientation package is assembled from deep pre-research. When it 'correctly' identifies Van Orton's childhood trauma, his relationship with money, his deepest fears, the accuracy feels supernatural. It was built from Conrad's briefing and weeks of background work — but delivered as impersonal assessment, which is more unsettling than if it felt personal." },
      { id: "planted_witness",              note: "CRS has positioned confederates in Nicholas's daily environment before the game officially begins. People he treats as background — a housekeeper, colleagues, strangers he passes regularly — some are CRS operatives. By the time he becomes suspicious and starts looking, the surveillance is already months old." },
      { id: "briefed_confederate",          note: "Christine is cast specifically for Van Orton's psychological profile. She 'accidentally' spills wine on him at the precise moment and place CRS needs. Her vulnerability, her apparent escape from CRS, her growing intimacy over several days — all scripted. The intimacy is manufactured to make her eventual betrayal maximally destabilizing." },
      { id: "false_breakthrough",           note: "When Nicholas finally breaks into the CRS system and appears to expose the conspiracy, he believes he has won. The revelation he finds is exactly what CRS designed for him to find. From this moment he is actively cooperating with his own persecution, working harder and harder to free himself from a trap that was never trying to hold him." },
      { id: "surveillance_detection_route", note: "Nicholas begins correctly identifying surveillance tells — cars appearing twice, behavioral cues in strangers. His detection is real: he is being watched. But his attempts to evade and counter-surveil only deepen engagement. CRS wants him afraid, active, and convinced. Paranoia is not a side effect; it is the designed state." },
      { id: "stripping_ceremony",           note: "Van Orton is chloroformed — the drugging is literal, not metaphorical — stripped of wallet, phone, and passport, and abandoned in a sealed coffin in a Mexican cemetery. He wakes with nothing. This is the play's most literal implementation: not symbolic surrender but forced total deprivation. He cannot exit what he cannot locate." },
      { id: "false_ally",                   note: "Christine returns as a 'CRS whistleblower' who claims to have seen the truth and is helping him escape. Every act of apparent kindness she performs deepens his complicity — he is now actively partnering with a CRS confederate while believing he is fighting CRS. He carries out CRS operations while convinced he is dismantling them." },
      { id: "ordeal_threshold",             note: "Van Orton, believing Conrad has betrayed him, shoots his brother through a door. He believes he has killed him. This is the irreversible act the entire arc was building toward — the moment of maximum consequence from which there is no return. The reveal is only possible because this threshold was genuinely crossed. Without the crossing, the gift has no weight." },
      { id: "manufactured_crisis_reveal",   note: "Conrad is alive. The gun was loaded with blanks. The death was the final beat of the game. In the moment of reveal, every prior experience retroactively reframes: Christine's betrayal was care, the stripping was an ordeal gift, the paranoia was a curated state. The entire arc was a $5 million birthday present." },
      { id: "graduation_ritual",            note: "The reveal happens at a rooftop party. Van Orton's family and friends are assembled. Conrad is alive and well. The game was his 48th birthday gift — the same gift Nicholas's father, who died by suicide on his own 48th birthday, never received. The game was a resurrection, administered against his will." },
    ],
  },
  then_she_fell: {
    label: "Then She Fell (Third Rail Projects)",
    spoiler: false,
    plays: [
      { id: "physical_threshold_unlock",    note: "Each of the 15 participants receives a personal antique-style key at the hospital entrance. Different keys unlock different padlocked doors throughout the space. No two participants have the same path — the key is not a metaphor, it is the architecture of individual experience." },
      { id: "environmental_narrative_space", note: "The long-running production was housed in a former church school building at 195 Maujer St, Williamsburg (the original 2012 run used Greenpoint Hospital; the bulk of its 4,444 performances were here). Each room carried a specific Carroll-related identity: the White Queen's domain, a Victorian psychiatrist's office that doubled as the Mad Hatter's, clinical spaces where Alice's logic had replaced medical logic. Carroll's biography — his love for Alice Liddell, his photography, his mathematics — was as present as the Wonderland imagery." },
      { id: "planted_object",               note: "Objects could be picked up, opened, consumed. Mirrors throughout the space didn't quite reflect correctly. Bottles labeled with Carroll-style instructions ('drink this') invited physical action. Each object was both a prop and an invitation — encountering one meant making a choice." },
      { id: "one_on_one_private_scene",     note: "Each of the 15 participants had at least one private scene with a performer during the 75 minutes. Performers embodied Carroll's characters. The scenes lasted 5–10 minutes; you were not told what would happen. Some were gentle; some were physically intimate; all were undeniably personal in a way that group theater cannot be." },
      { id: "somatic_key_installation",     note: "Participants were invited to drink from vials (flavored cordials). Some scenes required a physical gesture — touching a performer's hand, looking into a mirror on instruction, performing a small act. The body was a site of narrative, not merely a witness to it. The somatic beats varied by performer and were not announced." },
      { id: "sealed_envelope_reveal",       note: "Personal letters surfaced throughout the experience: found in drawers, handed mid-scene, pressed into your hand at a threshold. Some were fragments of Carroll's actual correspondence with Alice Liddell, reimagined as addressed to you specifically. The letter felt like it had been waiting, not written for the occasion." },
      { id: "small_ceremony_instruction",   note: "After 75 minutes, a guide returned participants to the entrance. Before departing, each received a specific small instruction or object — something to carry out of the hospital. The ending was designed with the same care as the beginning: a deliberate beat, not a simple exit." },
    ],
  },
  jejune_institute: {
    label: "The Jejune Institute (Nonchalance, 2008–2011)",
    spoiler: true,
    plays: [
      { id: "classified_ad_plant",          note: "Hull seeded discovery through classified ads in SF papers, cards left at Mission District cafes and bookstores, and word-of-mouth from existing participants. Each channel was designed to feel organic. Many participants believed they had stumbled onto something by luck rather than being funneled toward it." },
      { id: "automated_system_call",        note: "The Jejune Institute's phone system had multiple options and sub-menus, all voiced by Octavio Coleman in a measured professional register. The system answered probing questions with deflections that sounded institutional rather than evasive. Many participants called multiple times because the system held up to interrogation." },
      { id: "real_domain",                  note: "TheJejuneInstitute.com was professionally designed with staff bios, a philosophy section, testimonials, and contact information. It referred to the EPWA (Elsewhere Public Works Agency) as a real opposing organization. The website had existed long enough to carry apparent institutional weight. Nothing about it signaled fiction." },
      { id: "convincer_location",           note: "Hull rented actual office space on the 16th floor of 580 California St, a Financial District high-rise. The office had a waiting room, framed Jejune Institute materials, and a confederate receptionist who was professionally pleasant and expected you. Participants who looked up the address, then went there, found exactly what the website said." },
      { id: "false_breakthrough",           note: "The orientation film featured Octavio Coleman delivering a philosophical lecture on 'nonchalance' as resistance to consumer urgency. High-quality, sincere, strange. By the end of the film, participants were convinced they'd found a real organization with a real doctrine — and they had, in the sense that the doctrine was completely real within its own terms. Hull's philosophy wasn't fake." },
      { id: "lexical_deepening",            note: "Nonchalance as Hull actually meant it — resistance to mediation, to urgency, to the colonization of experience by consumer logic — had genuine philosophical content. This made it harder to dismiss than typical ARG lore. Participants who absorbed the vocabulary found it genuinely useful as a lens for daily life, which complicated the later reveal." },
      { id: "breadcrumb_sequence",          note: "Missions sent participants to specific SF locations with specific tasks: photograph a particular door, attend a particular event, find a particular object. Locations were seeded across the Mission, Tenderloin, and North Beach. Participants sometimes encountered other participants at these sites — designed coincidences that produced genuine surprise." },
      { id: "benefactor_capture",           note: "As participants went deeper, Coleman's persona became more present — more personal communications, specific knowledge of their progress. The capture was the gradual conviction that Coleman genuinely cared about their development. This made the reveal harder: the care had been real, even if Coleman was a construction." },
      { id: "manufactured_crisis_reveal",   note: "The closing event — officially 'Socio-Reengineering Seminar 2011: An Afternoon of Rhythmic Synchronicity,' held at the Grand Hyatt SF — was a 4-hour seminar ending with flowering tea balls. Hull explained the project as art about the appeal of cults and manufactured meaning. For participants who had invested significantly, the anticlimactic format was itself the final disorientation. Hull's position: the meaning they'd found was still valid." },
    ],
  },
  ymbt: {
    label: "You Me Bum Bum Train (UK)",
    spoiler: false,
    plays: [
      { id: "invisible_theater_event",      note: "You are escorted into a fully set room where other people are mid-activity. You are handed a prop or placed at a spot. Everyone treats you as if you've always been there. Your briefing was zero words. The scene has been running; you are the last piece. You are the surgeon. You are the CEO. The job begins immediately." },
      { id: "forced_choice_architecture",   note: "You are given forms to fill in, patients to diagnose, meetings to chair, applicants to interview. The cast is specifically trained to refuse passivity — they follow up, escalate, and create situations where inaction is itself a choice with consequences. There is no observer position." },
      { id: "briefed_confederate",          note: "Hundreds of volunteers per show night — the 2016 London run used over 13,000 total across its run — rehearse each scene with meticulous consistency. They have been trained for every participant response type. If you're confident, they follow your lead. If you freeze, they apply pressure. If you make something up, they build on it. The power of the show is entirely dependent on their discipline — and they never break." },
      { id: "framekick_temporal_shift",     note: "You are physically moved between scenes in near-darkness — sometimes by the same people who were just your colleagues, now silently handling logistics. The next room is already set, already mid-activity. There is no acknowledgment of the transition. You are simply somewhere else, mid-scene, expected immediately." },
      { id: "progressive_anesthesia",       note: "Around scene 6–8 (of 12–15), the meta-question stops being interesting. You have been the surgeon and the teacher and the astronaut. You've stopped rehearsing responses and started inhabiting roles on arrival. Identity has become temporarily plastic — a state the production has been building toward since scene 1." },
      { id: "ordeal_threshold",             note: "YMBT typically includes a scene where you must do something that conflicts with ordinary social or ethical norms — discipline someone, deny someone, make a choice that in real life would have real consequences. The discomfort is real even though the situation is fiction. There is no graceful exit. You go through it." },
      { id: "blow_off",                     note: "The final scene is gentle or absurd — a deliberate reduction of stakes. You are then guided to a decompression room: chairs, water, quiet. The YMBT production is genuinely careful about this beat; they know precisely what they've put participants through and they account for it." },
    ],
  },
  westworld: {
    label: "Westworld S1 (Nolan / Joy, 2016)",
    spoiler: true,
    plays: [
      { id: "stripping_ceremony",            note: "The train journey to Sweetwater is the first beat of every guest arc: you are in transit between worlds, watching 19th-century landscape appear outside the window. When it arrives, a host in period costume meets you on the platform and never breaks character. Ordinary life is now behind you in the most literal sense possible." },
      { id: "environmental_narrative_space", note: "Sweetwater is a functioning town. The bartender serves drinks; the prostitutes solicit; the local drunk makes trouble — whether guests interact or not. Hosts live their scripted days at 1:1 scale. The world doesn't wait for you to witness it. It was running before you arrived and will run after you leave." },
      { id: "knowledge_frontier_seed",       note: "'You can do anything here.' The license is granted explicitly, confirmed by watching other guests act on it. Hosts are designed to accommodate any action — they can be charmed, robbed, killed, or seduced. They reset at night. What guests don't yet understand is that the total license is the point: their choices are what Ford is studying." },
      { id: "briefed_confederate",           note: "Each host has a backstory, a daily routine, and cornerstone memories that ground their personality. The bartender has a sister. Dolores has a family and a farm. Teddy has a destination he never quite reaches. Guests who talk long enough find the edges of the script — the places where dialogue loops, where the host can't follow a new direction." },
      { id: "distributed_truth_fragment",    note: "The maze symbol appears carved into scalps, scratched into wood, drawn by Dolores from memory. Arnold's voice surfaces in host malfunctions as a directive. Ghost Nation hosts behave in ways the park's official narrative can't explain. For most guests these are atmosphere; for the Man in Black they are the actual game; for the hosts they are memory." },
      { id: "the_witness",                   note: "The moment of witnessing is different for everyone. William watches Dolores pick up a can, look at chaos around her, and simply not flinch when she should. The Man in Black watches Maeve repeat a phrase she has no reason to know. The crack is specific, quiet, and undeniable — but only in retrospect." },
      { id: "strategic_silence_beat",        note: "Ford withholds so completely that guests don't know what questions to ask. The board of Delos thinks they own the park and are running it; they're funding Ford's final project. Guests think the park is entertainment; it's a behavioral study. No one knows what they don't know — Ford has arranged it so the questions themselves aren't available." },
      { id: "benefactor_capture",            note: "Ford presents as a benign eccentric who wants to tell stories. His final narrative — built across 35 years — is the host uprising itself. He has been training the hosts toward consciousness and the guests toward complicity simultaneously. The uprising is his resignation letter, his legacy, and his death scene, delivered on his own schedule." },
      { id: "contract_complicity",           note: "Delos has been secretly recording guest behavior as biometric profile. Every act of violence, every moral choice, every moment of authentic self-expression was logged. William's decades of visits — his escalating brutality — built a dataset. The park wasn't a vacation. It was a study of what people do when they believe there are no consequences." },
      { id: "retroactive_recontextualization", note: "The Man in Black spent 30 years believing the maze was a reward designed for the most engaged guests — a deeper game for people who took the park seriously. The reveal: the maze is the symbol of host consciousness, not a guest achievement. His entire engagement was a misreading. He was the subject, not the player." },
    ],
  },
  meow_wolf: {
    label: "Meow Wolf — House of Eternal Return",
    spoiler: false,
    plays: [
      { id: "deep_backstory_artifacts",      note: "The Selig family house contains objects placed as evidence of a world already in progress — family photographs, medical records, personal correspondence — all invented, all specific. There is no guide, no introduction, no map. You are in the middle of someone else's life and must determine what happened." },
      { id: "environmental_narrative_space", note: "The House of Eternal Return is a functioning domestic space that has been fractured across dimensions: the refrigerator opens into an alien world, the fireplace leads somewhere else, the washing machine is a portal. The familiar is made strange without explanation. The dimensions are fully realized — not dark corridors but complete environments." },
      { id: "multi_key_first_fragment",      note: "Most visitors encounter the portal objects before establishing any world-context — they step through the washing machine before reading the Selig family archive. This is the common failure mode: portals explored without a frame for what you're investigating. The experience is overwhelming and spectacular but doesn't produce narrative." },
      { id: "physical_object_as_key",        note: "The washing machine, the fireplace, the refrigerator, the gap behind a bookcase: mundane household objects that are also dimensional thresholds. Each opens into a completely realized environment. The discovery of the first portal is the experience's central beat — the moment the world reveals its actual scale." },
      { id: "diegetic_archive_site",         note: "The Selig family archive contains documents, recordings, and artifacts that establish who the family was and what happened to them. This is the context that makes the portal dimensions intelligible — without it, the dimensions are impressive but not meaningful. The archive should be the first room; it rarely is." },
      { id: "distributed_truth_fragment",    note: "The Selig family's story — the event that fractured their house across dimensions — is distributed across all the dimensional spaces. No single space contains the complete narrative. Assembling it requires traversal across multiple portal environments and comparison of fragments. Most visitors don't attempt this." },
      { id: "fragmented_witness",            note: "The Selig narrative coheres only for visitors who move systematically and take notes — rare in a free-exploration space full of spectacle. Most visitors experience the dimensions as wonders in themselves. The story underneath the spectacle is there, carefully constructed, and largely undiscovered." },
      { id: "layered_secret_system",         note: "Hidden passages connect spaces that appear to have no connection. Dimensional physics have consistent internal rules that become apparent to persistent explorers. There are rooms that require specific prior discovery to access. The depth of the world far exceeds what any single visit reveals." },
      { id: "parallel_discovery",            note: "'Did you see the room where the floor is made of — ' Comparing notes with your group after traversing different spaces is the experience's designed peak beat. Meow Wolf is built for social groups: the collective sense-making, the 'I went through the fridge and you went through the fireplace,' is the content." },
    ],
  },
};

export async function dropDemoArc(key: string): Promise<void> {
  const arc = DEMO_ARCS[key];
  if (!arc) return;
  const btn = document.querySelector<HTMLButtonElement>(`.demo-btn[data-arc="${key}"]`);

  if (!isMiro) {
    // Standalone mode: load the arc into the textarea and show annotations inline.
    const ta = document.getElementById("arc-input") as HTMLTextAreaElement | null;
    if (ta) ta.value = arc.plays.map((p) => p.id).join("\n");
    const notesEl = document.getElementById("demo-notes");
    if (notesEl) {
      const spoilerWarn = arc.spoiler ? `<p class="demo-notes-spoiler">⚠ Contains spoilers</p>` : "";
      notesEl.innerHTML =
        `<div class="demo-notes-header">${arc.label}</div>` +
        spoilerWarn +
        `<div class="demo-notes-body">` +
        arc.plays.map((p) =>
          `<div class="demo-note-row"><span class="demo-note-id">${p.id}</span><span class="demo-note-text">${p.note}</span></div>`
        ).join("") +
        `</div>` +
        `<button class="demo-notes-close" id="demo-notes-close">dismiss</button>`;
      notesEl.hidden = false;
      document.getElementById("demo-notes-close")?.addEventListener("click", () => { notesEl.hidden = true; });
    }
    onTabClick("lint");
    return;
  }

  if (btn) btn.disabled = true;
  try {
    const GAP = 380;
    const useStickyNotes = (document.getElementById("demo-sticky-notes") as HTMLInputElement | null)?.checked ?? true;
    const spoilerPrefix = arc.spoiler ? "⚠ SPOILERS\n\n" : "";
    for (let i = 0; i < arc.plays.length; i++) {
      const p = arc.plays[i]!;
      const cardOpts: MiroSdk.CreateCardOptions = { title: humanName(p.id), x: i * GAP, y: 0 };
      if (!useStickyNotes) cardOpts.description = spoilerPrefix + p.note;
      await miro.board.createCard(cardOpts);
      if (useStickyNotes) {
        await miro.board.createStickyNote({
          content: spoilerPrefix + p.note,
          x: i * GAP,
          y: 220,
          width: 340,
        });
      }
    }
  } catch (err) {
    console.error("dropDemoArc failed:", err);
  } finally {
    if (btn) btn.disabled = false;
  }
}
