# Reference review (cloud session, 2026-11-04/05)

Scope: references consulted **before** implementing the redesign of the 18-page 논문 중간발표 deck.
Only principles were reused (line hierarchy, alignment, whitespace, direct labelling, common axes,
minimal legends, scale consistency). No diagram, plan, section, stair, escalator, photograph or chart
from any source was copied, traced or redrawn; every figure in the deck is rebuilt from this study's
CSV outputs.

## 1. What could and could not be accessed in this cloud session

Network access in this Claude Code cloud environment is restricted by the environment's network policy.
Three access routes were tried for every URL. The results are recorded as observed; nothing was inferred.

| Route | Tool | Result |
|---|---|---|
| A. Container browser / HTTP | Playwright 1.63 + Chromium (chromium-1243); `curl` | **Denied.** The egress proxy answered `403` to `CONNECT` for every reference host (`connect_rejected`, logged 2026-11-04T23:58:44Z–23:58:48Z): www.cccarchitecture.org, es.aap.cornell.edu, www.oma.com, spacesyntax.com, discovery.ucl.ac.uk, app-help.vectorworks.net, research-figure-guide.nature.com, www.nature.com, www.datawrapper.de, clauswilke.com, jkastellec.scholar.princeton.edu. |
| B. Claude Code `WebFetch` tool (server-side fetcher, three parallel runs) | WebFetch | **Denied.** Every host failed with `getaddrinfo ENOTFOUND <host>` (outside the session's allowed domains). No HTML, PDF or image bytes were saved. |
| C. Claude Code `WebSearch` tool | WebSearch | **Worked.** Returns titles, URLs and search-engine summaries of page content. These are recorded below as `search result only`. |

Consequences, stated plainly:

- **No external reference was opened, and none was visually inspected in this session.** The highest
  status any external reference reaches here is `search result only`.
- The seed ledger (`references_seed.md`) records what was opened during task preparation. Those notes are
  quoted below in a separate column, labelled *preparation note (not verified in this session)*, and are
  never presented as cloud access.
- Seed URLs that also failed to appear in search (CCC Architecture, OMA diagrams, Space Syntax 1998) are
  listed as `not accessible (no search result)` and are **not counted** toward the minimum coverage.
- Internal sources in this repository *were* opened and visually inspected (section 4).

To open the external references in a future session, the hosts above must be added to the cloud
environment's allowed network domains (environment settings → Network access).

## 2. Architecture diagram references

Counted toward the minimum of four: A2, A3, A4, A5, A6 (five, all `search result only`).

| ID | Source (URL) | Creator / source | Access status (this session) | Representational purpose | Principle applied here | Element not copied |
|---|---|---|---|---|---|---|
| A1 | https://www.cccarchitecture.org/analyzing-architecture-through-diagrams | CCC Architecture (site); author not verifiable | **not accessible (no search result)** — route A 403, route B ENOTFOUND; two WebSearch queries did not return this page | *Preparation note (not verified in this session):* circulation and spatial-zone diagrams; circulation separated from programmed space; ghosted context, line weight for hierarchy | Not counted. The same principle is applied below on the authority of A3/A4, not A1 | Plans, buildings, circulation paths |
| A2 | https://es.aap.cornell.edu/research/erciyes | Environmental Systems Lab, Cornell AAP (lab led by Timur Dogan) | **search result only** | Documents an environmental-performance-driven early-design process for a 15,000 m² laboratory building, organised in three phases with Archsim (EnergyPlus) simulation (search summary) | Tie every design question to a simulation output and to the decision it informs; organise evidence by phase → p.6 question → metric → experiment rows; p.9 experiment blocks; p.18 finding → next validation | Building geometry, renderings, energy diagrams, project imagery |
| A3 | https://discovery.ucl.ac.uk/10145356/1/The-Covert-Life-of-Hospital-Archiecture.pdf (record: discovery-pp.ucl.ac.uk/id/eprint/10145356) | Zook, J. & Sailer, K. (eds.), *The Covert Life of Hospital Architecture*, UCL Press 2022, DOI 10.14324/111.9781800080881 | **search result only** (*preparation note:* "analytical-layer and corridor-hierarchy figures inspected") | Space-syntax analyses of hospital environments, incl. intelligibility of public circulation (corridor chapter by Zook & Bafna) | Reduce a building to the few layers that answer the question: faint context, bold analytical marks → p.7 (thin grey floor lines, bold measured boundaries and one example path); p.8 three-floor crop only | Hospital plans, route traces, axial maps, photographs |
| A4 | https://discovery.ucl.ac.uk/id/eprint/10085475/3/Natapov%20Circulation%20Typology%20and%20Wayfinding_publication.pdf | Natapov, Kuliga, Dalton & Hölscher (2020), "Linking building-circulation typology and wayfinding", *Architectural Science Review* 63(1) 34–46, DOI 10.1080/00038628.2019.1675041 | **search result only** | Three circulation types (linear, curved, grid) generated so that they "differ in their geometrical structure but are comparable in their functional and topological organizations" (search summary) | One consistent comparison frame across variants; abstraction paired with a bounded purpose → p.15 one floor × placement matrix on one scale; p.16 four trajectories on identical axes; p.5 explicit scope of the abstraction | Typology drawings, orphanage plans, layouts |
| A5 | https://discovery.ucl.ac.uk/id/eprint/1005/ (DOI https://doi.org/10.1068/b250507) | Chang, D. & Penn, A. (1998), *Environment and Planning B* 25(4) 507–538 | **search result only** (record and abstract-level summary); detailed content taken from the v3 paper's own review of the article (section 4, I1) | Observed pedestrian movement in two London multilevel complexes (Barbican, South Bank); IMCM; "horizontal change of direction" more significant than "vertical grade separation" (search summary) | Keep the observed prior study and the synthetic model in separate columns; state shared problem and non-shared variables; never present the observed study as validation → p.5 | Maps, plans, axial or IMCM figures, gate counts |
| A6 | https://app-help.vectorworks.net/2025/eng/VW2025_Guide/Programming/Creating_a_stacking_diagram.htm | Vectorworks Architect help (programming tools) | **search result only** | Stacking diagram: a floor-by-floor view of how program area is allocated, each floor a horizontal band, program blocks sized by quantity (search summary) | Floors as aligned rows; quantities as horizontal lengths on one common scale; totals checked per column → p.15 proportion matrix with Σ 2F–9F = 1.60 row | Software UI, colour coding, block graphics, building sections |
| A7 | https://open-exam-prep.com/study-guides/are/ch11-pa-programming-feasibility/pa-adjacency-diagrams-graphics | Exam-prep study guide (secondary, not authoritative) | **search result only** | Adjacency matrices rate pairs of spaces; blocking/stacking distributes departments by floor | Matrix form for two crossed design factors → p.9 E1 resistance × attraction-factor matrix (supporting only) | Exam graphics |
| A8 | https://www.oma.com/projects/diagrams | OMA | **not accessible (no search result)** (*preparation note:* "opened as text; image detail not verified") | — | Not used | OMA graphics |
| A9 | https://spacesyntax.com/year-1998/ | Space Syntax Ltd. | **not accessible (no search result)** — search returned only a 2014 Barbican public-realm newsletter (spacesyntax.com/february-newsletter/), which is a different project | *Preparation note:* keep observed studies separate from the present model | Supports p.5 framing only (already covered by A5) | Project listing as evidence |

## 3. Scientific / data-visualisation references

Counted toward the minimum of four: D1, D2, D4, D5, D6, D8 (six, all `search result only`).

| ID | Source (URL) | Creator / source | Access status (this session) | Representational purpose | Principle applied here | Element not copied |
|---|---|---|---|---|---|---|
| D1 | https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/ | Nature Portfolio, Research Figure Guide | **search result only** | Journal figure specifications | Text stays live and editable (not outlined); fonts embedded as TrueType; vector artwork; RGB; no rasterised text → whole deck is HTML/SVG vector with embedded Pretendard and searchable text. The guide's 5–7 pt print sizes were deliberately **not** applied (slide minimum 9 pt, chart labels ≥ 10.5 pt) | Nature house style, print sizes |
| D2 | https://www.nature.com/documents/natrev-artworkguide.pdf | Nature Reviews artwork guide | **search result only** (*preparation note:* pages 1, 2, 4 inspected) | Guidance for schematic artwork | "Use a top–bottom/left–right, logical flow of information"; "Explain all elements in labels or the legend" → every page reads left→right (claim, evidence, caveat); every mark directly labelled | Example artwork |
| D3 | https://www.nature.com/articles/nmeth.1676 | *Nature Methods* "Points of View" commentary on arrows (exact title not verified) | **search result only** | Use of arrows in scientific figures | Arrows "sparingly and clearly" → all decorative arrows removed; only short movement arrows on p.7's example path | Illustrations |
| D4 | https://www.datawrapper.de/academy/how-to-create-a-dot-plot | Datawrapper Academy | **search result only** | Cleveland-style dot plots | Dot plot on one aligned axis, few dots per row, direct labels → p.13 deviance-reduction dot plot (six conditions per row, γ=4 continuous highlighted) | Example data, styling |
| D5 | https://www.datawrapper.de/academy/confidence-intervals-error-bars-datawrapper-bar-charts | Datawrapper Academy (updated 2021-10-18) | **search result only** | Showing confidence intervals / value markers | Show lower and upper bounds explicitly and name the interval (95% CI, its method) → p.12, p.14 interval labels "[lo, hi]" printed next to each estimate | Dataset, chart export |
| D6 | https://clauswilke.com/dataviz/multi-panel-figures.html | Claus O. Wilke, *Fundamentals of Data Visualization* (O'Reilly 2019), ch. 21 | **search result only** | Small multiples vs compound figures | Each panel uses the same axis ranges and scaling; small multiples need no panel letters when the facet label identifies them → p.16 four aligned panels, identical axes; p.10/p.11 shared boundary axis | Book figures |
| D7 | https://clauswilke.com/dataviz/visualizing-uncertainty.html | Wilke, ch. 16 | **search result only** (table of contents only) | Uncertainty of point estimates | Supporting only (covered by D5, D8) | — |
| D8 | https://jkastellec.scholar.princeton.edu/document/50 (DOI 10.1017/S1537592707072209) | Kastellec, J. & Leoni, E. (2007), "Using Graphs Instead of Tables in Political Science", *Perspectives on Politics* 5(4) 755–771 | **search result only** | Coefficient plots replace regression tables | Show model estimates as point + interval against a reference line, ordered rows → p.12 AUFR multipliers with "관계 없음 = ×1.00" line; p.14 erosion forest plot with 0 line; p.13 graph instead of table | Figures, replication code |

## 4. Internal sources opened and visually inspected in this session

| ID | File | Status | Used for | Not copied |
|---|---|---|---|---|
| I1 | `inputs/paper_revised_8pages_v3_column_fixed.pdf` (latest paper; rendered at 150 dpi, all 8 pages; figures on pp. 5–7 inspected) | **opened and visually inspected** | Title, definitions (U, AUFR, RUI, T, R), Eq. 1–6, Tables 1–2, every quantitative claim; Chang & Penn content (Barbican, South Bank, gate counts, IMCM, pp. 507–538) | Figure layouts (slide charts are rebuilt from CSVs) |
| I2 | `inputs/paper_revised_8pages_v2.pdf` | **opened and visually inspected** (rendered, compared with v3) | Comparison only; v3 takes priority (v3 adds the TOP1 upper-boundary rebound 7,077 → 7,209 → 9,112 and the revised title) | — |
| I3 | `inputs/vertical_flow_presentation_clear_titles.pdf` (current deck) | **opened and visually inspected** (all 18 pages at 150 dpi) | Issue list, title inventory | — |
| I4 | `README.md` (repository) | **opened as text** | Fixed colour meaning (continuous = navy, segmented = brown); "use only CSV values" rule | — |
| I5 | `simulation/vertical_flow.gaml` | **opened as text** | Utility `u_dest = ln_size + γ·x − α ln d − β ln Ī (+ δ_down)`; exit `θ0 + θ1·t + θ2·x`; every trip adds the group's persons to each crossed boundary; exit = return to 1F | — |

## 5. The 4–6 most influential references and the principle taken from each

1. **D2 Nature Reviews artwork guide** — left-to-right/top-to-bottom reading order and "explain all elements": every page is claim (title) → evidence (figure) → limit (note), with direct labels.
2. **D8 Kastellec & Leoni (2007)** — estimates as point + interval against a reference line instead of number panels: pp. 12 and 14.
3. **D6 Wilke, multi-panel figures** — identical axes across panels: p. 16 four aligned trajectories; pp. 10–11 shared boundary axis.
4. **A4 Natapov et al. (2020)** — one comparison frame for variants that differ in one respect: pp. 15–16 four placements on one floor × scenario frame.
5. **A3 Zook & Sailer (eds.) (2022)** — ghost the context, emphasise the analytical layer: p. 7 (the only full nine-floor abstraction) and p. 8 (three-floor crop).
6. **D1 Nature figure specifications** — live, embedded, vector text: the final PDF keeps searchable text with one embedded font family.

All six were available only as search results in this session; their principles are generic and were
applied without reproducing any of their material.
