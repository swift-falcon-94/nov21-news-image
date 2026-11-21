# nov21-news-image

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/swift-falcon-94/nov21-news-image/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/swift-falcon-94/nov21-news-image/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image summing up the world news of Saturday 21 November 2026: 54 verified stories across 6 continents — the M6.7 Peru earthquake (USGS, no fatalities, M5.0 aftershock) and a second quake in Kamchatka, COP31 still without a deal on Saturday morning in Antalya, India reaching 486/4 for a 118-run lead on Day 3 in Wellington, BepiColombo's Mercury orbit insertion at 19:24 CET after an eight-year journey, the aftermath of Russia's Kyiv bridge barrage and the missiles that fell in Poland, six killed in Gaza despite the ceasefire, Cyclone Akvan dissipating over Odisha, Wall Street's crash (Nasdaq −5.3% on Friday), Bolsonaro in hospital, and a foiled attack in Pakistan — with a coordinate-drawn world map, a UTC timeline strip, a date-check box, and a source list. Drawn in code with Python's standard library only; the program writes entry.png deterministically, with no network and no photos.

Date handling: the big 20 November stories (Kyiv barrage, Gaza ground operation, Wall Street crash, Nvidia, Bolsonaro) are dated "(20 NOV)" on their cards and in the also-items, and the 19 November items (Shenzhen pact, ICJ verdict, Van Gogh sale) carry "(19 NOV)". The date-check box lists only items from 21 November. The Peru magnitude is the final USGS figure, M6.7 — the M6.9 figure from a secondary feed is not used. Gaza's toll uses the civil-defence figure of 6 killed; Al Jazeera reported 7. Premier League Saturday fixtures are listed, not results: at build time the matches had not kicked off yet.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

Entered on [make.fun](https://make.fun/?ref=3ds1297d&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards
