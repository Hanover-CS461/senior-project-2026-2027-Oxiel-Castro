# Steam-lite — a Storefront for Games

**Working title:** *Steam-lite*
**Genre:** Catalog / storefront web app (browse-first, editorial reviews)
**Platform:** Web app (browser)
**Role:** Backup project #3 — the *impressive rebuild*
See `luna-design-and-plan.md` for the primary project.

---

## 1. Framing & Hook

Everyone knows Steam. *Steam-lite* is a storefront-shaped catalog site: curated rows on the home page ("New & Trending," "Top Sellers," "Staff Picks"), a browsable catalog with genre/tag filters and search, and game detail pages that end in a written review. Your own reviews, your own catalog — served from a real database.

Why this works as a backup: it's the most visually impressive of the backup options and the heaviest pure React/TypeScript practice — a storefront is nothing but UI. The database fits this idea more naturally than any other. It shares Luna's stack (so it shares the stack risk — it's the "if I'm going to rebuild, I want it to look great" option, not the "escape the web" option).

---

## 2. Design Thesis (the spine)

> **"Browse first, opinions after."**

The catalog is the product. Browsing, filtering, and discovering should feel like wandering a store you like — and the editorial review at the end of each game page is the payoff. Reviews never gate the browsing experience; they reward it.

---

## 3. Core Systems

### The catalog (the content engine)
- A hand-curated set of **20–30 games**, each with: title, description, genre tags, price, screenshots, and your written editorial review.
- Fully in your control — no external API. The catalog is to this project what enemies are to Luna.
- This is real authoring work: descriptions, tags, and reviews have to read like someone wrote them with care.

### Browse & discovery
- **Home page:** curated rows — "New & Trending," "Top Sellers," "Staff Picks."
- **Catalog page:** browse all games with **genre/tag filters** and **search**.
- **Detail pages:** game page with description, screenshots, tags, price, and the editorial review at the bottom.

### Editorial reviews
- Your own writing, attached to game pages. Read-only content, no different architecturally from the catalog data itself — no accounts, no user input.

### The database (the final stretch)
- The site runs on static data first (pure React/TS, always-works demo).
- Final layer: content moves into **SQLite**, served through a small **read-only API**. The "backed by a real database" moment is the visible full-stack payoff.

---

## 4. Structure

1. Home → curated rows.
2. Catalog → filter by genre/tag, search.
3. Game detail → description, screenshots, price, editorial review.
4. (Stretch, cut-able) wishlist / ratings on the page.

---

## 5. Technical Approach

**React + TypeScript frontend.** Static content first, then:

- A small backend (Node/Express, or Next.js API routes — taste call) + **SQLite**.
- Read-only API: the frontend fetches catalog data; content is authored by you, seeded into the DB.
- No accounts, no auth, no user-generated content, no payments.
- Same learning curve as Luna's first weeks, plus one new layer (backend + SQL) — which is exactly why the browse-first build order exists.

---

## 6. Semester Plan

*As a backup, designed to be completable in a compressed window — browse-first guarantees a working demo at every step.*

- **Weeks 1–2** (compressed: week 1): React/TS basics; static seed catalog (~5 games); home page + one detail page.
- **Weeks 3–4:** full catalog page — filters, search — plus remaining detail pages.
- **Weeks 5–6:** curated rows, editorial reviews, layout polish.
- **Week 7:** the database swap — SQLite + read-only API; the site now serves from the DB.
- **Week 8:** test suite, catalog polish, demo video, presentation prep.

**Compressed variant (late start):** cut curated rows and reviews; keep ~15 games; browse + detail only. The site is still a complete storefront.

### Cut list (cut first if time runs out)
User reviews / accounts · wishlist & cart · payments · carousel animations · search beyond basic filtering · more than ~30 games

---

## 7. Open Questions / Next Decisions
- Backend shape: separate Express + Vite build, or Next.js (one framework)?
- Where do screenshots come from? (Public screenshots are fine for a demo; licensing is a footnote, not a blocker.)
- Filter design: genres, tags, or both?
- Catalog size worth authoring well: 20, or 30?