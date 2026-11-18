[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/belski21-growl/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/belski21-growl/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# 18 November 2026 — The World in One Day

A magazine-cover style montage summing up Wednesday 18 November 2026,
built from news reported in the first hours of the day (early edition — as
reported by 03:15 UTC). It covers only events that happened or were first
reported on 18 November 2026; nothing from 17 November is shown as the
day's news.

## What the image shows

Masthead: **18 NOVEMBER 2026 — THE WORLD IN ONE DAY — WEDNESDAY**

1. **APEC OPENS IN SHENZHEN** — The APEC Economic Leaders' Meeting opens
   in Shenzhen, China (18–19 Nov). Leaders gather; the first-ever
   three-way meeting of Trump, Xi Jinping and Putin is set for Thursday
   19 November. Sources: CNA; Reuters (via China Foreign Ministry
   announcement, 16 Nov).
2. **CRIMEA BRIDGE CRIPPLED** — Ukraine strikes the Kerch/Crimea Bridge
   for a second straight day overnight; the road arch collapses into the
   Kerch Strait and road traffic is suspended. Russia hits Kyiv's North
   and South bridges in reply. Sources: Reuters, published 18 Nov
   00:32 UTC; The Guardian.
3. **GULF FLASHPOINT** — US fighter jets strike an IRGC missile launch
   site on Qeshm Island after Iranian drones target a US-operated radar
   at Sheikh Isa Air Base in Bahrain; Kuwait's air defences engage
   hostile drones early on Wednesday. Sources: Reuters, published
   18 Nov 01:44 UTC; Al Jazeera; US Central Command.
4. **CYCLONE AKVAN** — Cyclonic Storm Akvan strengthens over the Bay of
   Bengal (85–95 km/h, gusting 105); IMD bulletin 04:00, 18 Nov. The
   Andhra Pradesh coast is on alert, with landfall forecast around noon
   on 20 November. Source: India Meteorological Department.
5. **QUAD MEETS IN MANILA** — President Trump arrives in Manila for
   Quad talks ahead of his China visit. Sources: NDTV; The Times of
   India.

## Entry

`main.py` (Python 3.13, standard library only, no network) copies
`entry.png` to the output directory (`MAKEFUN_OUTPUT_DIR`, default
`/output`), verifying size, SHA-256 and JPEG SOI/EOI markers before and
after the copy. The output is byte-identical to the source on every run.

## Files

- `main.py` — entrypoint
- `entry.png` — the image (1024x1024 JPEG, 261,816 bytes)
- `LICENSE` — MIT
- `build-log.md` — build steps and validation results
