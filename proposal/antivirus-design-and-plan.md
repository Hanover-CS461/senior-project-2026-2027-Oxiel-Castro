# SafeScan — an Educational Antivirus Scanner

**Working title:** *SafeScan*
**Genre:** Educational malware scanner (desktop tool)
**Platform:** Desktop (Python 3) — no web dependency
**Role:** Backup project #2 — the *escape hatch*
See `luna-design-and-plan.md` for the primary project.

---

## 1. Framing & Hook

Point it at a folder; it inspects every file, flags the suspicious ones, **explains why**, and quarantines them. It's not a product — it's a demonstration that you understand how scanners actually work: signatures, rules, heuristics, quarantine.

Why this works as a backup: **pure Python, on home turf.** Zero web ecosystem. If Luna dies and you need to finish something, this is the fastest path to a finished, defensible project.

---

## 2. Design Thesis (the spine)

> **"Trust nothing, explain everything."**

Every file gets a verdict, and every suspicious verdict comes with a reason you can read. Detection *quality* matters less than **explainable** detection.

---

## 3. Core Systems

### The scan pipeline (per file)
1. **Signature check** — hash the file (SHA-256) and compare against a known-bad hash database.
2. **YARA rules** — match file bytes/strings against a small rule set, using the real `yara-python` library (the industry-standard rule engine). You write the *rules*; you don't write the engine.
3. **Heuristics** — for PE files: high entropy (packed/encrypted), suspicious import combinations (e.g., `VirtualAlloc` + `WriteProcessMemory`), unusual section names. For scripts: regex patterns of known-bad commands.
4. **Verdict + reasons** — clean / flagged, with the exact indicators listed.

### Quarantine
- Flagged files move to an isolated vault folder (preserving original paths), with a **restore** action.
- Optional: simple encryption (e.g., AES via a key) to make the vault inert.

### Reports
- Per-file results plus a scan summary, exportable as **JSON or an HTML page** you can open in any browser.

### The sample corpus (the demo)
- The **EICAR test file** (the standard, harmless string every real AV flags) plus a handful of synthetic samples you author: a fake malicious PE, a suspicious PowerShell script.
- Documented so the demo is reproducible and safe — no real malware ever touches the lab.

---

## 4. Structure

1. Choose a directory to scan.
2. Run the pipeline over every file.
3. Review verdicts and read the reasons.
4. Quarantine / restore.
5. Export the report.

---

## 5. Technical Approach

**Python 3, standard library first.** Optional libraries: `pefile` for PE parsing, `yara-python` for YARA.

- CLI-first, so the detection logic is easy to test with `pytest`.
- No web, no accounts, no servers. (A web UI would be scope creep — the whole point of this project is escaping the web.)

---

## 6. Semester Plan

*Escape-hatch timing: designed to be completable in a compressed window from a mid-semester start.*

- **Week 1:** directory walk + hashing + signature DB + EICAR demo working.
- **Week 2:** YARA integration + first rules.
- **Weeks 3–4:** heuristics (PE analysis; script patterns) + verdict/reason output.
- **Week 5:** quarantine + restore.
- **Week 6:** report export + sample corpus polish.
- **Week 7:** test suite + README + demo script.

### Cut list (cut first if time runs out)
Real-time monitoring · GUI beyond a report viewer · network scanning · ML-based detection · signature auto-update · anything that touches files you didn't explicitly choose

---

## 7. Open Questions / Next Decisions
- Scope of file types: PE-only, or scripts too? (PE-only keeps the heuristics tight.)
- Hand-write the YARA rule set vs. package a small known rule set.
- How much quarantine encryption is worth the effort for a demo.
