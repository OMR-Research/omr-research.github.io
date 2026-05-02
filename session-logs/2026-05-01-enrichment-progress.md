# OMR Bibliography Enrichment — Session Log
**Date:** 2026-05-01  
**Task:** Research, correct, and expand all entries in `new-entries-only.bib`

---

## Progress Summary

All ~101 entries from `new-entries-only.bib` have been processed across 10 batches.

| Batch | File | Entries (in-scope) | Questionable | Notes |
|-------|------|--------------------|--------------|-------|
| 1 (manual) | `enriched-review-batch1.bib` | 6 | 1 (Almad2025) | + 2 new entries added (Rigaux2026b, Jung2025b) |
| A | `batch_a.bib` | 14 | 3 | Khanna2025/Ray2025 duplicate, Romo2025→2026 year fix |
| B | `batch_b.bib` | 11 | 2 | Della2025 wrong venue, Asbert2025 wrong type, GuillotelNothmann2024 author order |
| C | `batch_c.bib` | 14 | 1 | Kim2024 year→2025, Simonetta2024 type change, Penarrubia2024 wrong venue |
| D | `batch_d.bib` | 9 | 5 | Torras2023→IJDAR 2024, Yesilkanat2023→DAS 2024, Tuggener2023 12-author list |
| E | `batch_e.bib` | 9 | 3 | Lou2023 type change (@Article), CalvoZaragoza2023 missing co-author |
| F | `batch_f.bib` | 10 | 3 | Shi2022 ICRA→ROBIO, De2022 author name fix |
| G | `batch_g.bib` | 13 | 3 | Pacha2022 year→2021, AlfaroContreras2022 missing 2 authors, Yue2022 retracted |
| H | `batch_h.bib` | 14 | 2 | Torras2021 venue ICDAR→ISMIR, de2021 year→2022, Ahmed2021 missing authors |
| I | `batch_i.bib` | 13 | 4 | DegrootMaggetti2020 expanded 3→9 authors, Foscarin2020 missing author |

**Total in-scope entries processed: ~117** (101 original + ~16 new entries added or year/venue-corrected keys retained)  
**Entries moved to questionable: ~33**  
**New entries added (not in original new-entries-only.bib): Rigaux2026b, Jung2025b, possibly Romo2025 (confirmed as Romo2026)**

---

## Files to Merge

### Step 1: Combine all in-scope enriched entries
Merge into `enriched-entries.bib`:
- `enriched-review-batch1.bib`
- `batch_a.bib` through `batch_i.bib`

### Step 2: Combine all questionable entries
Merge into `questionable-entries.bib` (already has Almad2025):
- `batch_a_questionable.bib` through `batch_i_questionable.bib`

### Step 3: Combine all review notes
Merge into `review-notes.txt`:
- `batch1-review-notes.txt`
- `batch_a_notes.txt` through `batch_i_notes.txt`

---

## Items Requiring Manual Review / Decisions

### Scope decisions
- **Almad2025** (`questionable-entries.bib`): "Cursogramas" = administrative flowcharts in Argentine university education. Include (broadening scope to document recognition) or exclude?
- **Zalkow2020** (`batch_i_questionable.bib`): MTD dataset includes sheet music images and supports OMR, but primary focus is audio-based. Include?
- **Bertiaux2020** (`batch_i_questionable.bib`): Motor dynamics of handwriting music notation. No OMR/recognition component. Exclude?
- **Hart2021** (`batch_h.bib`): Heritage digitization policy thesis, not OMR algorithms. Kept in-scope as digitization infrastructure. Confirm?
- **Stutter2025** (`batch_b.bib`): Primarily musicology, but explicitly develops OMR methodologies for 13th-century notation. Confirm in-scope.
- **Gut2022** (`batch_g.bib`): ZHAW student thesis with no public URL; author contributed to Tuggener2024 TISMIR paper. Confirm entry.

### Duplicate / same-paper decisions  
- **Ray2025** vs **Khanna2025**: Confirmed same paper (Springer LNCS 16025, pp. 22–39). Ray2025 moved to questionable; Khanna2025 is the correct full entry. Delete Ray2025?
- **Romo2025** vs **Romo2026**: Same paper — wrong journal and year in source. Agent corrected to Romo2026 (REIC journal, published March 2026). The key Romo2025 in new-entries-only.bib should be dropped in favour of the corrected Romo2026 key. Confirm deletion of Romo2025.

### Entries with unverified details
- **Rigaux2026** (`enriched-review-batch1.bib`): Separate paper from Rigaux2026b (dataset paper). PDF exists per Gmail Scholar alert (thread 19d45af25230364b) but not yet retrieved. Venue unknown/forthcoming.
- **Jung2025b** (`enriched-review-batch1.bib`): TASLP journal article (DOI: 10.1109/TASLPRO.2025.3648794, IEEE article 11316398). Volume, number, and pages not confirmed. Download PDF manually from https://ieeexplore.ieee.org/document/11316398/
- **Torras2023** key: Published in IJDAR 2024. Key kept as Torras2023 for backward compat — consider renaming to Torras2024.
- **Yesilkanat2023** key: Conference and proceedings are DAS 2024. Consider renaming to Yesilkanat2024.
- **Kim2024** key: Published in ACM JOCCH 2025. Key kept as Kim2024 — consider renaming to Kim2025.
- **Barbosa2022** (`batch_f.bib`): Volume/number/pages in REIC journal could not be confirmed.
- **Pickelmann2025** (`batch_a.bib`): No publication found. Florian Pickelmann (Univ. Innsbruck). Kept as @Misc.
- **GarcaIasci2023** (`batch_e.bib`): Specific conference proceedings/DOI could not be confirmed. URL only.
- **Pastor2025** (`batch_b_questionable.bib`): Could not locate any record. Author may be "Ignasi Pastor Mas". Needs clarification.
- **Jiang2024** (`batch_d_questionable.bib`): No venue found despite extensive searching.
- **Hristov2024** (`batch_c.bib`): Stanford CS231N course report — not peer-reviewed. Kept as @Misc.

### Retracted paper
- **Yue2022** (`batch_g_questionable.bib`): Formally retracted (retraction notice: doi:10.1155/2023/9850239). Should be excluded.

### Spurious file to delete manually
- `pdfs_new/2021 - Learning Audio Representations for Cross-Version Retrieval of Western Classical Music.pdf`: This is an HTML page (bot-blocked FAU repository), not a real PDF. No .bib entry references it. **Delete this file.**

---

## PDFs Downloaded (pdfs_new/)

Approximately 50 PDFs downloaded across all batches. Key unavailable sources (paywalled):
- Elsevier (Applied Soft Computing, ScienceDirect) — no OA versions
- Springer LNCS chapters — most without arXiv preprints
- ACM DL — most without OA alternatives
- IEEE Xplore — without OA access
- Hindawi/Wiley — automated access blocked
- Taylor & Francis — paywalled
