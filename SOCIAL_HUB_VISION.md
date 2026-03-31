# PSP Social Hub — product vision

**One sentence:** The easiest and coolest way for millennial gamers to hang out around PSP multiplayer again — not “accurate emulation first,” but *hop in, pick a game, jump into a room, and play with friends like it’s 2009 again.*

## What this fork is (three pillars)

1. **The emulator fork** — centerpiece; features should reinforce the social loop, not only traditional emulator depth.
2. **The social hub** — rooms, presence, lightweight identity, rhythm (events).
3. **Curated game-night culture** — recurring nights, genre lanes, small scene before “open platform.”

Position as **portable multiplayer nightlife for grown-up gamers** (digital PSP barcade): late-night adhoc energy, old-forum warmth with less friction, not a museum or ROM warehouse.

---

## Social lanes (where people go)

Structure the hub so intent is obvious:

| Lane | Games (examples) |
|------|-------------------|
| **Fight Club** | Tekken 6, Dissidia 012, Darkstalkers Chronicle |
| **Hunter Lodge** | Monster Hunter Freedom Unite, Phantasy Star Portable 2 |
| **Shooter Block** | SOCOM Fireteam Bravo, Resistance: Retribution, Coded Arms |
| **Weird UMD Zone** | Half-Minute Hero, Work Time Fun, Fat Princess, Power Stone Collection |

---

## Launch anchors (first four)

Ship netplay confidence and messaging around:

1. **Tekken 6** — competitive anchor  
2. **Dissidia 012** — competitive anchor  
3. **Monster Hunter Freedom Unite** — co-op progression  
4. **Phantasy Star Portable 2** — co-op progression  

Then add a **weekly “weird card” rotation** (one oddball title) so the hub feels alive.

---

## Curated support (first ~10 titles)

Treat these as the **v1 supported list** for compatibility buckets, copy, and QA — not “every PSP game ever.”

**Fighters:** Tekken 6, Dissidia 012, Darkstalkers Chronicle, Power Stone Collection  

**Co-op / action RPG:** Monster Hunter Freedom Unite, Phantasy Star Portable 2  

**Shooter / action:** SOCOM Fireteam Bravo, Resistance: Retribution, Coded Arms  

**Oddball / party:** Half-Minute Hero, Fat Princess, Work Time Fun  

*(Power Stone appears in both fighter and weird lanes in the pitch — keep one primary lane in UI to avoid confusion; secondary tag “also great for parties” works.)*

---

## Fork priorities (social loop)

1. **Dead-simple room flow** — create room, share invite, see who’s playing what, launch into same session, rejoin after disconnects. Target: game-night friction near zero.  
2. **Curated compatibility buckets** — “Fight Night / Hunt / Shooter / Weird” with explicit supported lists, not an infinite catalog.  
3. **Presence & light profiles** — currently playing; favorite genres / PSP games; status (“down for fighters,” “co-op tonight”).  
4. **Eventized play** — recurring rituals (e.g. Friday Fight Night, Saturday hunts, Sunday weird roulette), even if small at first.  
5. **Integrated lobby feel** — open rooms, light chat or Discord bridge, reactions, screenshots/clips, “next game” votes; social glue over raw feature count.

**Fork-native ideas to differentiate:** one-click join friend session, community presets per game, recommended control maps, live session cards (“4 in Tekken 6 now”), event banners, per-game compatibility rating in hub, post-match stat snapshots, clip hooks, polished room/invite codes, seasonal featured games.

---

## MVP v1 (narrow)

- Custom launcher / polished fork build  
- **Stable netplay for 3–5 flagship titles** (the four anchors + one rotating weird pick is enough)  
- Simple create / join room flow  
- Discord integration (server + rich presence / deep links where useful)  
- Game pages with **“best for”** tags (lane + night type)  
- **Weekly scheduled play nights** (even one recurring slot counts)

**Defer early:** huge social graph, full library support, deep profile ecosystem, marketplace/mod portal, complex global rankings.

---

## Phase 1 roadmap (concrete)

### Client / fork

- ✅ Hub UI entry points per lane; flagship games pinned (lane cards: Fight Club, Hunter Lodge, Shooter Block, Weird UMD Zone).
- ✅ Light profiles — display name, status line, pinned games, favorite lane.
- ✅ Social Hub onboarding screen for new users.
- ✅ Discord Rich Presence — current game shown in Discord automatically.
- ✅ “Join Discord” shortcut in Hub tab and side menu.
- ✅ Improved ad hoc lobby picker — streamlined flow for starting and joining local-wireless sessions.
- 🔁 Room model: create, invite code or link, list open rooms by game/lane — Multiplayer Rooms entry point exists; full flow in progress.
- ⬜ “Join same session” path from invite + rejoin-after-drop UX.
- ⬜ Session discovery widget (who’s in what game).
- ⬜ Telemetry hooks only if needed for stability — privacy-conscious, minimal by default.

### Discord

- ⬜ Channels aligned to lanes: `#fight-club`, `#hunter-lodge`, `#shooter-block`, `#weird-umd`, `#general`, `#lfg`.
- ⬜ Event posts template: game, time (timezone), room/invite instructions, “new player OK” flag.
- ⬜ Role or tag strategy: optional `@Fight Night` / `@Hunt` for pings without noise.
- ⬜ Pin rules: curated list link, how to get the client build, netplay troubleshooting one-pager.

### Landing / copy (angles)

- ⬜ Headline options in the spirit of: *Portable multiplayer after dark* / *Your PSP adhoc crew, without the 2009 setup pain.*
- ⬜ Bullets: curated multiplayer nights, one client, rooms not forums, built for friends and small groups.
- ⬜ Clear CTA: download client, join Discord, see this week’s schedule.
- ⬜ Legal/ethical line users expect: bring your own dumps; no ROM hosting narrative.

### Ops / culture

- ⬜ Run **one** recurring night weekly minimum before scaling.
- ⬜ Capture clips/screenshots from real sessions for social proof.
- ⬜ Tune fork from **actual** disconnect, desync, and invite pain — not hypothetical compatibility lists.

---

## Phase 2 roadmap — next milestone (concrete)

Phase 1 proves the loop with a closed circle of friends. Phase 2 opens the door slightly: **small public onboarding**, **curated game pages**, a **real landing experience**, and **simple profiles** — still curated, not a free-for-all catalog.

### Client / fork

- First-run and “returning player” onboarding: lane picker, where to find events, how rooms and invites work, link-out to Discord.  
- **Game pages** for the v1 supported list: lane tags, netplay notes (ports, typical issues), recommended PPSSPP settings presets where they help, and “best for” copy (Fight Night vs hunt vs party).  
- **Simple profiles**: display name, optional avatar, favorite lane(s), 2–3 pinned games, short status line (“down for Tekken tonight”). No heavy social graph yet.  
- Discovery polish: filter rooms by lane and game; highlight “tonight’s featured” from ops without hard-coding only four titles forever.

### Discord

- Onboarding posts pinned per lane + a single **#start-here** with rules, client link, and schedule.  
- Light moderation kit: what to post in LFG vs lane channels, spam/report flow, volunteer mod expectations for a small public wave.  
- Optional bot or workflow: event RSVP or reaction counts so hosts know headcount (keep it simple).

### Landing / copy

- **Polished landing**: hero, three pillars recap, anchor games strip, Discord CTA, download CTA, this week’s schedule embed or static block.  
- Small **FAQ**: dumps/ROM ethics, “is this official PPSSPP,” supported platforms, netplay troubleshooting link to the one-pager from Phase 1.  
- Basic SEO and share cards (title/description/image) so links look credible in Discord and social.

### Ops / culture

- Run **two** recurring slots if volume allows (e.g. fight + hunt), or one anchor night + rotating genre — still small, still curated.  
- Publish a short **public code of conduct** (inclusive, no harassment, respect hosts).  
- Gather structured feedback: one form or thread template for “game X disconnect pattern” to feed fork fixes.

**Exit criteria (Phase 2)**  
Anyone new can land on the site, install the client, join Discord, find a game page and a room or event within one session — without DMs to a founder.

---

## Launch strategy (phases)

| Phase | Focus |
|-------|--------|
| **1** | Invite friends, 4 anchor games, weekly events, gather stories/media, fix real netplay UX pain. |
| **2** | Small public onboarding, curated game pages, polished landing, simple profiles. |
| **3** | Broader reach, ladders for select titles, deeper social, cloud saves / richer discovery. |

---

## Branding notes

**Vibe:** sleek, nostalgic, slightly underground / arcade / portable-tech — not corporate platform.

**Visual direction:** black / charcoal / silver / electric blue; XMB-inspired motion; glossy handheld-era cues; subtle scanlines, loading ring, battery motifs; 2000s wireless adhoc energy.

**Name directions (brainstorm only):** Adhoc Social, Sector UMD, Night Lobby, Neon Adhoc, 333 MHz Club, Midnight UMD, XMB Nights, PSP Social Club, Adhoc Nights, Portable Arena, UMD Union — pick when positioning and domain handles are tested.

---

## Relationship to upstream PPSSPP

This document describes **product and community positioning** for a downstream fork. Upstream remains the emulation core; this fork adds hub workflows, curated multiplayer focus, and scene-first growth while contributing fixes upstream where appropriate.
