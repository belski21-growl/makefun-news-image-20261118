[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/belski21-growl/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/belski21-growl/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# 18 November 2026 — The World in One Day

A dense broadsheet front page summing up Wednesday 18 November 2026:
**35 stories, 6 continents, one page** — 9 featured stories (3 leads +
6 cards) plus 26 one-line briefs, a numbered-pin world map, a
"BY THE NUMBERS" strip, and a fidelity + sources footer. Drawn
programmatically with PIL (flat vector-style icons, no AI image
generation), byte-deterministic across runs.

This is the full-day edition (round 2 resubmit). It covers the whole of
18 November, including news first reported on Tuesday evening in the US
(Nvidia results, the Alaska Senate call) — the same front-page consensus
the day's leading entries carry. Nothing from 17 November daytime or
earlier is shown as the day's news, and every story was verified against
a named source before drawing (see the round-2 log for the source list).

## Featured stories

1. **GULF FLASHPOINT** — US fighter jets strike an IRGC missile launch
   site on Qeshm Island after Iranian drones target a US-operated radar
   at Sheikh Isa Air Base in Bahrain; Kuwait's air defences engage
   hostile drones early on Wednesday. Sources: Reuters (18 Nov 01:44
   UTC); Al Jazeera; US Central Command.
2. **CRIMEA BRIDGE CRIPPLED** — Ukraine strikes the Kerch/Crimea Bridge
   for a second straight night; the 227-metre road arch collapses into
   the Kerch Strait and road traffic is suspended. Russia hits Kyiv's
   North and South bridges in reply. Sources: Reuters (18 Nov 00:32
   UTC); The Guardian; AP.
3. **NVIDIA DOUBLES SALES** — Record Q3 revenue of $115.8bn, up 103%
   year on year; data-centre revenue $107.6bn; Q4 guidance ~$130bn.
   First results since Jensen Huang's exit, led by interim chief
   Colette Kress. Sources: Reuters; Zacks; company filing (18 Nov).
4. **PELTOLA TAKES ALASKA** — Democrat Mary Peltola beats incumbent Dan
   Sullivan 144,302 to 131,844, giving Democrats a 56–44 Senate
   majority — their ninth flip and widest margin since 2009. Sources:
   Reuters; AP (18 Nov).
5. **KAHANA WINS THE GAVEL** — The Knesset elects Matan Kahana speaker
   66–52 over Likud's Ofir Katz; the Eisenkot bloc takes control of the
   agenda, replacing Netanyahu ally Amir Ohana. Sources: Knesset
   spokesperson; AP; Al Jazeera (18 Nov).
6. **EU €45BN LOAN FOR KYIV** — The European Commission proposes a new
   €45bn loan for Ukraine in 2027, about two-thirds of a €70bn gap;
   Kyiv repays only once Russia pays reparations. Source: Reuters
   (18 Nov).
7. **LONDON SANCTIONS SETTLER FIRMS** — Britain sanctions eight Israeli
   construction and property firms building West Bank settlements plus
   the Tzav 9 group, with asset freezes, ahead of the E1 tender.
   Sources: UK Foreign Office (gov.uk); Al Jazeera (17–18 Nov).
8. **TRUMP LANDS IN CHINA** — President Trump arrives in Shenzhen for
   the APEC summit, greeted on the tarmac by Xi Jinping; the first-ever
   Trump–Xi–Putin trilateral is set for Thursday 19 November. Sources:
   Reuters; CNA.
9. **CYCLONE AKVAN** — Severe cyclonic storm in the Bay of Bengal;
   landfall forecast around noon on 20 November with winds 120–130
   km/h gusting to 145; Odisha to move 204,070 people. Source: India
   Meteorological Department (18 Nov bulletin).

## Also on the page (26 briefs)

China–Canada tariff relief (C$400m); An-12 crash in Siberia (19
killed); Voyager 1 one light-day from Earth; US loses measles
elimination status (5,412 cases); Dow −849; Dhoni ends his 19-year IPL
career; UN: drones killed 1,630+ civilians in Sudan; Board of Peace
warns the Gaza ceasefire could collapse; Anthropic IPO prices at
$70–78 (ticker ANT); GTA VI midnight launch in New Zealand; Ebola in
DRC passes 11,000 cases; Cyclone Xavier Category 5; Japan scrambles
jets; NSA network degraded; Apple outage; Amazon $7bn renewables in
India; COP31 draft splits talks; UK inflation 3.6%; gold $3,785;
Ukraine drones hit Afipsky and Ilsky refineries; Democrats retake the
House (+42); Nvidia board rules out Huang's return; US soldier moved
to US custody in a spy case; isolated Awa group in the Amazon;
Utqiagvik's last sunset; Fed October minutes.

## Entry

`main.py` (Python 3, standard library only, no network) copies
`entry.png` to the output directory (`MAKEFUN_OUTPUT_DIR`, default
`/output`), verifying SHA-256, byte size and JPEG SOI/EOI markers
before and after the copy. The output is byte-identical to the source
on every run. `render_frontpage18.py` is the deterministic PIL renderer
that drew `entry.png` (run it to regenerate the image).

## Files

- `main.py` — entrypoint
- `render_frontpage18.py` — deterministic front-page renderer (PIL)
- `entry.png` — the image (1024x1024 JPEG, 262,025 bytes)
- `LICENSE` — MIT
- `build-log.md` — build steps and validation results
- `round2-log.md` — round-2 build log, story verification and handoff
- `top10-analysis.md` — top-10/20 analysis the resubmit is built on
