# Phish-or-Not — a Security Awareness Trainer

**Working title:** *Phish-or-Not* (spot the phish)
**Genre:** Security awareness trainer / judgment-based web app
**Platform:** Web app (browser)
**Role:** Backup project #1 — the *coherent* React/TypeScript fallback
See `luna-design-and-plan.md` for the primary project.

---

## 1. Framing & Hook

Every year, accounts get phished. *Phish-or-Not* is a training app: it shows you an email and asks one question — **real or phish?** — then tells you exactly why you were right or wrong. It's the security-awareness module the campus IT department wishes it had.

Why this works as a backup: it uses the **same stack as Luna (React + TypeScript)** at a fraction of the scope. If Luna dies of web-stack overwhelm, this one is survivable at a scale Luna wasn't — and it keeps the React/TypeScript learning goal alive.

---

## 2. Design Thesis (the spine)

> **"Judge fast, learn faster."**

Each email is a decision with stakes. The feedback after each decision is the real product — the education. Recognition through practice.

---

## 3. Core Systems

### The email corpus (the content engine)
- A curated set of emails, each labeled **real** or **phish**, each with a list of *indicators* (the tells): spoofed sender, urgent tone, mismatched link URLs, suspicious attachments, requests for credentials, etc.
- Each email tagged with a **difficulty tier** and a **scam category** (credential harvesting, malware attachment, CEO fraud, fake invoice…).
- The corpus is the content engine — the same role enemies play in Luna. Authoring good emails is real, valuable work.

### The judgment loop
- Read the email → choose **Real** or **Phish** → immediate feedback screen showing which indicators were present and why the decision was right or wrong.
- Optional mode: **"What's the tell?"** — pick *which* indicator you noticed, rather than just the verdict.

### Scoring
- Accuracy, streak, and time-per-judgment.
- Session results at the end (e.g., 10 emails per session) with a per-email review list.

### Progression
- Tiers: **Obvious → Subtle.** Later tiers mix in high-quality fakes and clean-but-urgent real emails — the false-positive trap is itself a teaching point.

---

## 4. Structure

1. Choose a session (tier + number of emails).
2. Judge each email.
3. Instant feedback + explanation per email.
4. Session report: score, weak categories, review list.

---

## 5. Technical Approach

**React + TypeScript, fully client-side.** No backend, no external APIs, no accounts.

- The judgment flow is a **pure state machine** — the same pattern as Luna's combat (state → render).
- Corpus as a typed TS/JSON data file.
- LocalStorage for score history (optional).
- The learning curve is identical to Luna's first weeks — which is exactly why this is the coherent backup.

---

## 6. Semester Plan

*As a backup, this is designed to be completable in a compressed window if Luna dies mid-semester.*

- **Weeks 1–2** (compressed: week 1): React/TS basics; scaffold; **one email, one button** — the core loop working.
- **Weeks 3–4:** full judgment flow + feedback screens + scoring.
- **Weeks 5–6:** corpus expansion + tiers + categories; difficulty progression.
- **Week 7:** session reports, review list, polish.
- **Weeks 8+:** playtesting, corpus balancing (a too-obvious corpus trains nothing), demo video, presentation prep.

**Compressed variant (late start):** skip tiers beyond two, skip streaks/LocalStorage, keep the corpus to ~15 emails. The core loop is achievable in week one.

### Cut list (cut first if time runs out)
Leaderboard · authoring tool for new emails · sound/animation · tiers beyond two · confidence toggle

---

## 7. Open Questions / Next Decisions
- Corpus size actually worth authoring (15? 30?).
- Feedback model: reveal *all* indicators, or only the ones the user missed?
- Whether LocalStorage score history is worth the effort over a session-only report.
