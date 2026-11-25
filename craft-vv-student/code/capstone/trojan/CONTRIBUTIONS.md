# Contributions — Group #15 Final Project

**Members:** Minh Hoang Ho 5182391 · Matias Guillen 5523210 · William Wright 4735092 · Adrian Emeterio 5470594
**Repo:** [GitHub](https://github.com/iiTzPevin/Verification-And-Validation-Final-Project)
**Track:** Track C
**Last Updated:** 11-24-2026

---

## Final Project — 12-10-2026

| Member | What They Owned | Evidence (Commits / Files / PRs) | Approx. Share |
|--------|-----------------|----------------------------------|--------------:|
| Minh Hoang Ho | Made the SVA and formal files | `sva/`, `formal/` | 25% |
| Matias Guillen | Made the test file | `test_final.py` | 25% |
| William Wright | Made the test file | `test_final.py` | 25% |
| Adrian Emeterio | Made the test file | `test_final.py` | 25% |

**Shared Or Paired Work:** Matias, William, and Adrian worked together on `test_final.py`, and the whole team worked together on the write-ups and the report.

**What Slipped, And Who Picked It Up:** Nothing slipped, and everyone finished their part.

## Whole-Project Summary

| Member | Principal Contributions | Overall Share |
|--------|-------------------------|--------------:|
| Minh Hoang Ho | The SVA and formal files, and the write-ups | 25% |
| Matias Guillen | The test file, and the write-ups | 25% |
| William Wright | The test file, and the write-ups | 25% |
| Adrian Emeterio | The test file, and the write-ups | 25% |

**The Three Things This Team Did That We Would Each Defend In An Interview:**

1. We proved P1 and P2 for every possible key with formal instead of hoping random stimulus would hit the trigger, and the solver found 0xDEADBEEF on its own.
2. Every assertion has a cover next to it and every cover was hit, so none of our assertions passed without being checked.
3. We showed that 100% coverage and a passing scoreboard did not catch the trojan, which is why we needed the directed magic key test and formal.

## Non-Code Contributions

| Member | Contribution | Where It Shows |
|--------|--------------|----------------|
| The whole team | Writing the write-ups and the report | `vplan.md`, `closure.md`, `FINDINGS.md`, `nonvacuity.md`, `proofs.md`, `strategies.md`, `CONTRIBUTIONS.md`, `README.md`, and `REPORT.pdf` |

## AI Assistance

| Where | Used For | Verified By | Where The Verification Shows |
|-------|----------|-------------|------------------------------|
| Lecture slides 1–6 and the Track C guide | Explaining the lecture material so we could apply it to secure_gate | The whole team | How the methods are used in `sva/`, `formal/`, and `test_final.py` |
| It was used on `test_final.py`, `sva/`, `formal/`, the Makefile, and the write-ups | Used to help checked the code for bugs and against SPEC.md | The whole team | The eustis runs with 5 / 5 tests passing, 7 / 7 on the released pool, the SVA and sby results, and the write-ups matching those logs |

---

## Attestation

- [ X ] Every claim above can be traced to the repo history.
- [ X ] This file was updated as the work happened, not reconstructed at the end.
- [ X ] Every member has read this file and agrees it is accurate.
- [ X ] Each member has separately submitted their **confidential individual peer eval** outside this repo, by the deadline.