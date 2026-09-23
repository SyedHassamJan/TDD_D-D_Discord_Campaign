# TDD Age of Men — Complete System & Architecture Documentation

> **Version:** Middle-Earth Campaign Engine (Turn 1 — 1418 TA)  
> **Repository:** `crokator0012-commits/ZeCampain` / `SyedHassamJan/TDD_D-D_Discord_Campaign`  
> **Setting:** Lord of the Rings / Middle-Earth Grand Campaign  
> **Base Engine:** Reconquista Turn-Based Grand Strategy Web Engine  

---

## 1. Executive Summary & Purpose

**TDD Age of Men** is a browser-based grand strategy wargame application designed to manage a tabletop-style Discord campaign. Rulers (players) command their realms, draft armies, manage settlements, and issue movement orders via Discord. The Game Master (GM) executes the turn on this web tool, simulates strategic movements, resolves sieges and economy, and stages tactical engagements in *Total War: Attila* (or Medieval II).

The entire application runs as a **serverless client-side web application** backed by GitHub's REST API for state persistence and Vercel for continuous deployment.

---

## 2. Technology Stack & Architecture

### 2.1 Core Technologies
- **Frontend Core:** Pure Vanilla JavaScript (ES6+), HTML5 Canvas, Vanilla CSS3.
- **Rendering Engine:** Custom 2D Canvas pipeline with zoom, pan, relief height-shading, boundary-fill overlay, and coordinate projection.
- **State Store:** `campaign.json` (Single Source of Truth) + `<script id="mapdata">` inline fallback.
- **Persistence & API:** GitHub REST API v3 (`PUT /repos/{owner}/{repo}/contents/campaign.json`) via GM Personal Access Token (PAT).
- **Deployment:** Vercel static hosting (`vercel.json`) with rewrite routing.
- **Automation:** Python 3 scripts for tile sync, roster ingestion, map generation, and data repairs.

### 2.2 Key Files & Roles
| File | Role | Description |
| :--- | :--- | :--- |
| `index.html` | **Primary GM Interface** | The main production entry point for Vercel. Includes full GM tools: tile painting, army movement, battle resolution, building editor, economy resolver, and 1-click GitHub publisher. |
| `gm.html` | **GM Standalone View** | Direct GM interface identical to `index.html`. |
| `player.html` | **Player Public View** | Read-only version for players. Disables editing/painting/publishing. Features the **Army Codex**, unit browser, and **Army Plan Code Generator** (`RQ1\|faction\|units`). |
| `campaign.json` | **Live Database** | JSON state holding all active data: factions, provinces, armies, sieges, build queues, turn counters, diplomacy, and logs. |
| `unit.md` | **Unit Codex Raw Roster** | Text roster listing all units, tiers, classes, recruitment costs, and upkeep for all Middle-Earth factions. |
| `sync_all.py` | **Master Automation Pipeline** | Ingests unit icons, builds rosters, processes map tile masks, and updates campaign data. |
| `vercel.json` | **Vercel Config** | Configures rewrites to serve `index.html` as root `/` and provides player routing. |

---

## 3. World & Map Geography

### 3.1 Map Dimensions & Projection
- **Native Resolution:** 3821 × 2687 pixels.
- **Canvas Rendering:** Dynamic transformation matrix supporting smooth mouse drag panning and cursor-centered wheel zooming.
- **Relief Shading (Key `R`):** High-resolution grayscale heightmap overlay blended with terrain textures.

### 3.2 Terrains & Movement Point Costs
Armies receive **3 movement points per season**. Entering a province expends points based on terrain:
- **Plains:** 1 movement point.
- **Hills:** 2 movement points.
- **Mountains:** 3 movement points.
- **Great Fords (≈):** Crossing one of the 10 great rivers costs **+1 additional movement point** unless connected by a **Road**.
- **Road:** Reduces entry cost to **1 movement point** regardless of terrain (except impassable mountains) and bridges any ford.
- **Enemy Territory Rule:** In hostile territory, an army may march at most **one province per season**, regardless of remaining movement points. Entering a province with an enemy army ends movement immediately.

---

## 4. Factions & Realms

Middle-Earth is populated by over 40 distinct lore-accurate factions, including:
- **Gondor** (Capital: Minas Tirith / South Ithilien)
- **Mordor** (Capital: Barad-dûr / Cirith Ungol)
- **Rohan** (Capital: Edoras / Meduseld)
- **Woodland Realm** (Capital: Thranduil's Halls)
- **Lothlórien** (Capital: Caras Galadhon)
- **Imladris / Rivendell** (Capital: Rivendell)
- **Ered Luin** (Capital: Belegost / Nogrod)
- **Erebor** (Capital: Erebor / The Lonely Mountain)
- **Dale** (Capital: Dale / Esgaroth)
- **Isengard** (Capital: Orthanc / Isengard)
- **Harad / Lostladen / Mahud** (Southron kingdoms and desert clans)
- **Rhurrim / Balcoth / Dorwinion** (Eastern realms and Rhûn confederations)
- **Anduin Vale / Beornings / Gundabad / Dol Guldur / Rhudaur**

Each faction possesses:
- `id` and `name`: Unique identifier.
- `color`: Hex color used for province fills, borders, and army tokens.
- `treasury`: Current liquid wealth in **castas** (gold).
- `capital`: Key fortress province ID.
- `zeal`: Current religious / morale fervor bank (0 to 6 max).

---

## 5. Economic & Settlement Systems

### 5.1 Currency
All financial transactions use **castas** (referred to interchangeably as gold). Income arrives at the **end of each season**.

### 5.2 Settlement Tiers & Base Yields
Every province has a developmental tier that dictates its economic output and garrison strength:

| Tier | Settlement Classification | Base Seasonal Yield | Default Garrison | Siege Clock |
| :---: | :--- | :---: | :---: | :---: |
| **0** | Wilderness / Hamlet / Unfortified | **250 castas** | 50 men | Falls to occupation (No siege) |
| **1** | Town / Small Settlement | **500 castas** | 200 men | Falls to occupation (No siege) |
| **2** | Fortified City (Small) | **850 castas** | 600–1,500 men | **3 seasons** |
| **3** | Fortified City (Standard) | **1,300 castas** | 1,200 men | **3 seasons** |
| **4** | Great Fortress / Realm Capital | **5,000 castas** | 2,000 men | **4 seasons** |

### 5.3 Buildings & Works
Provinces can hold infrastructure upgrades that generate income, expand recruitment, or strengthen defense:

| Building Type | Key ID | Cost | Seasonal Benefit / Effect |
| :--- | :--- | :---: | :--- |
| **Market** | `market` | 2,400 | +300 castas per season. |
| **Port** | `port` | 4,000 | +600 castas per season; +1 season to siege defense. |
| **Muster Ground** | `muster_ground` | 5,000 | +1 army to the realm's Army Cap. |
| **Road** | `road` | 3,000 | Reduces province entry cost to 1; bridges fords. |
| **Granary** | `granary` | 2,500 | +1 season to siege defense clock. |
| **Grain Farm** | `grain_farm` | Variable | +150 to +300 castas per season. |
| **Silver / Gold Mine** | `silver_mine`, `gold_mine` | 1,250+ (upgrade) | High-value trade income (+500 to +1,000 castas). |
| **Timber Yard** | `timber_yard` | Standard | Regional forestry output. |
| **Herbal Garden** | `healing_herb_garden` | Standard | Attrition recovery and defense buff. |
| **Barracks** | `barracks` | 2,000 (per level) | Unlocks higher tier regiments (Levels 1, 2, 3). |
| **Animal Pens** | `goat_pen`, `sheep_pen` | 500 | Rural livestock output. |

### 5.4 Settlement Expansion
- **Village → Town:** 15,000 castas (1 season).
- **Town → Small City:** 20,000 castas (1 season — stone walls constructed).
- **Small City → Large City:** 30,000 castas (1 season).

---

## 6. Military & Army Mechanics

### 6.1 Army Cap (Host Limit)
A realm cannot field unlimited armies. The host limit is strictly enforced:
$$\text{Army Cap} = 1 + \left\lfloor \frac{\text{Provinces Owned}}{4} \right\rfloor$$
* **Muster Ground Rule:** Every army beyond the **first** requires a designated **Muster Ground** building in a friendly province.

### 6.2 Seasonal Upkeep System
Armies require seasonal maintenance. Upkeep scales based on the realm's total number of fielded hosts, ordered from **most expensive to least expensive**:

| Host Rank (by cost) | Upkeep Percentage Paid |
| :--- | :---: |
| **1st Host** (Most expensive) | **0% (FREE)** |
| **2nd Host** | **25%** of base upkeep |
| **3rd Host** | **50%** of base upkeep |
| **4th Host** | **75%** of base upkeep |
| **5th Host & above** | **100%** of base upkeep |

* **Crusade / Jihad Armies:** Hosts sworn to a holy war/crusade via Zeal cost **0 upkeep** and ignore the army cap until the war concludes.

### 6.3 Army Composition Limits
Each individual host is restricted by doctrine to prevent unrealistic army spam:
- **Pike / Heavy Spear Infantry:** Maximum **4** regiments.
- **Missile Infantry (Archers / Crossbows):** Maximum **5** regiments.
- **Shock & Heavy Cavalry:** Maximum **2** regiments *(General's Bodyguard does not count against this limit)*.
- **Missile Cavalry (Horse Archers):** Maximum **2** regiments.
- **Artillery (Catapults / Onagers):** Maximum **1** engine battery.
- **Total Regiments:** Capped at `CAPU` (typically 15 to 20 units per host).

### 6.4 The Player Codex & Army Plan Codes
Players open the unit catalog by pressing **`C`** in `player.html`. Clicking units drafts an army and calculates recruitment and upkeep costs.
When finished, the player clicks **Copy Plan**, which generates a formatted Discord string:
```text
═══ ARMY PLAN — Gondor ═══
4/15 units · 480 men · 3,450g raise · 1,725g/turn upkeep
  1× Gondor Sword Militia
  1× Ringlo Vale Men-at-Arms
  1× Pelargir Marines
  1× Ithilien Rangers

▸ CODE (paste to the GM):
RQ1|Gondor|gondor_gondor_sword_militia,gondor_aor_ringlovale_men_at_arms,gondor_aor_pelagir_marines,gondor_aor_ithilien_rangers
```
The GM can paste this `RQ1` code directly into the GM interface to instantiate the army instantly.

---

## 7. War, Sieges & Battle Resolution

### 7.1 Battles
- **Trigger:** Hostile armies occupying the same province.
- **Engine:** Battles are resolved manually in *Total War: Attila* or simulated by GM arbitration.
- **Terrain Mapping:** Battle map selection corresponds to province terrain (Plains, Hills, Mountains, Fort, City).
- **Alliances:** Allied hosts present in the province may choose to reinforce.
- **Defeat & Retreat:** A defeated host must retreat to an adjacent friendly province. If no adjacent friendly province is reachable, the entire host is **eliminated**.
- **Ransom (1✦):** Victor may demand 2,000 castas. If the loser refuses, the victor gains +2✦ Zeal.

### 7.2 Sieges & Assaults
- **Unfortified (Tier 0 & 1):** Instantly occupied when enemy troops enter without defenders.
- **Fortified Cities (Tier 2+):**
  - Small City: 3 seasons siege clock.
  - Great City: 4 seasons siege clock (+1 season if Port or Granary present).
  - First season: Siege engines constructed (no assault).
  - Subsequent seasons: Breaches open; attacker may assault or starve defenders out.
  - Sally: Besieged garrison and armies may sally out to engage besiegers.

---

## 8. The Zeal System (✦)

Zeal represents divine favor, morale, and religious enthusiasm. Each realm accrues **+1✦ per season** (up to a maximum bank of 6✦).

| Cost | Action | Effect |
| :---: | :--- | :--- |
| **1✦** | **Force March** | Gives host +1 movement point this season, but causes weariness (enemy chooses the battlefield if attacked). |
| **1✦** | **Zealous Annex** | Immediately annexes an occupied village/town without waiting for seasonal resolution. |
| **1✦** | **Ransom** | Demand 2,000 castas after battle victory. |
| **1✦** | **Declare War** | Lawful declaration of war (free with legitimate GM cause; costs **2✦** against fellow faith). |
| **2✦** | **Sabotage Siege** | Saboteurs extend an enemy siege clock by +1 season. |
| **2✦** | **Raid** | Plunders an enemy province; its next season's income is diverted to you. |
| **3✦ + 1,500g** | **Bribe the Gates** | Infiltrators open the gates, accelerating siege clock by 1 season. |
| **3✦ + 1,500g** | **Entrench** | Army builds a fortified encampment; fought on a fort battle map. |
| **10✦** | **Crusade / Jihad** | Summons a sacred host: free to muster, zero upkeep, does not count against army cap. Disbands when war ends. |

* **Losing Capital:** A realm whose capital falls gains **+2✦**.
* **Betrayal Penalty:** Breaking a truce or betraying an alliance incurs a severe penalty of **−3✦** and chronicled infamy.

---

## 9. Turn Sequence & Resolution

Each game year consists of four seasons: **Spring → Summer → Autumn → Winter**.

### 9.1 Player Turn Phase
Realms submit orders to the GM over Discord in turn order:
1. Movement orders (from province A to B).
2. Muster orders (drafting units via `RQ1` codes).
3. Construction orders (starting buildings or settlement upgrades).
4. Diplomatic declarations (wars, peace, alliances, truces).

### 9.2 Season Resolution (GM Automation)
When all players have acted, the GM resolves the turn in `index.html`:
1. **Battles Resolved:** Casualties applied, victors awarded territory or ransoms.
2. **Sieges Advanced:** Clocks decrement by 1; breached holds surrendered.
3. **Occupations Annexed:** Occupied territories officially transfer ownership.
4. **Economy Executed:**
   $$\text{Treasury}_{\text{new}} = \text{Treasury}_{\text{old}} + \sum \text{Province Value} + \sum \text{Building Incomes} - \sum \text{Scaled Upkeeps}$$
5. **Zeal Accrual:** +1✦ added to all qualifying realms (capped at 6).
6. **Chronicle Written:** Turn events, diplomatic changes, and conquests logged.
7. **1-Button Publish:** GM clicks **⇧ Publish** to commit `campaign.json` directly to GitHub.

---

## 10. Data Schema Reference (`campaign.json`)

The entire state is structured as a clean JSON object:

```json
{
  "title": "TDD Age of Men",
  "turn": 1,
  "year": 1418,
  "season": "Spring",
  "w": 3821,
  "h": 2687,
  "sea": "#162838",
  "factions": [
    {
      "id": "Gondor",
      "name": "Gondor",
      "color": "#1F5E99",
      "treasury": 5000,
      "capital": "Province_433",
      "zeal": 6
    }
  ],
  "provinces": [
    {
      "id": "Province_433",
      "modern": "Province 433",
      "displayName": "Minas Tirith",
      "owner": "Gondor",
      "tier": 4,
      "terrain": "plains",
      "value": 5000,
      "move": 2,
      "garrison": 2000,
      "bld": ["barracks", "market"],
      "bldLevel": { "barracks": 3, "market": 1 },
      "adj": ["Province_305", "Province_446"],
      "cx": 2350.5,
      "cy": 1650.2,
      "siege": null,
      "occ": null,
      "buildQueue": []
    }
  ],
  "armies": [
    {
      "name": "Host of South Ithilien",
      "faction": "Gondor",
      "at": "Province_446",
      "men": 480,
      "order": null,
      "units": [
        "gondor_gondor_sword_militia",
        "gondor_aor_ringlovale_men_at_arms"
      ],
      "xp": [0, 1],
      "upkeep": 1725.0
    }
  ],
  "wars": [],
  "battles": [],
  "truces": {},
  "allies": [],
  "order": ["Gondor", "Mordor", "Rohan"],
  "active": 0,
  "log": []
}
```

---

## 11. GitHub & Vercel Publishing Pipeline

### 11.1 How 1-Click Publishing Works
1. In `index.html` / `gm.html`, `publishTurn()` executes:
   - Targets `https://api.github.com/repos/crokator0012-commits/ZeCampain/contents/campaign.json`.
   - Sends `Authorization: Bearer <TOKEN>`.
   - Fetches current file `sha`.
   - Sends `PUT` request with base64-encoded campaign JSON and commit message (`Turn X — Season Year`).
2. GitHub updates `main` branch.
3. Vercel webhook detects commit and triggers deployment within 30 seconds.
4. Players refresh `player.html` and receive updated turn state via cache-busted fetch:
   ```javascript
   pull("./campaign.json?t=" + Date.now());
   ```

### 11.2 Required GitHub Token Scopes
- **Scope required:** `repo` (Full control of private repositories).
- Created at [github.com/settings/tokens/new](https://github.com/settings/tokens/new).
- Tokens without `repo` scope will be rejected by GitHub with HTTP 404.

---

## 12. Instructions for Future AI Agents & Developers

When making modifications or adding new features:
1. **Never break Canvas performance:** Do not attach heavy event listeners inside the main render loop `draw()`.
2. **Preserve `campaign.json` integrity:** When adding provinces or factions, maintain all schema fields (`id`, `owner`, `tier`, `value`, `garrison`, `adj`, `bld`, `bldLevel`, `buildQueue`).
3. **Synchronize both views:** Any gameplay logic or UI improvements applied to `index.html` must be reflected in `gm.html`, and read-only player elements must be verified in `player.html`.
4. **Git Remote Sync:** Both remotes (`origin` -> `crokator0012-commits/ZeCampain` and `syed` -> `SyedHassamJan/TDD_D-D_Discord_Campaign`) must be kept in sync by pushing commits to both:
   ```bash
   git push origin main; git push syed main
   ```
5. **No CLI cd commands:** Antigravity agents must always execute commands directly in working directory without changing paths.
