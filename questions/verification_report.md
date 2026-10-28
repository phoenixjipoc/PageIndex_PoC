# Verification status of the PDF-only question set

Updated October 27, 2026. This set contains 110 questions and 78 original PDF documents.
It is a filtered subset of the 120-question, 81-document reference audit completed
on October 14, 2026. Filtering did not repeat the original semantic source audit
and does not measure retrieval performance.

## Current set

| Item | Count |
|---|---:|
| Questions available for evaluation | 110 |
| Retained original references marked verified | 99 |
| Retained references with approved corrections | 11 |
| PDF source documents | 78 |
| Complete question pairs | 14 |
| Unanswerable questions | 8 |

## PDF-only filtering

Three non-PDF source documents were removed. Nine questions depending on those
sources were removed from queries, standards and the verified CSV:
DDQ-03, DDQ-11, XD-01, XD-04, XD-08, XD-11, XD-15, XD-16, XD-19.

XD-07 was also removed because its partner XD-08 was removed. The P16 pair is
excluded as a unit. Remaining IDs and pair IDs are preserved without renumbering.
Mixed-source questions were removed in full, preserving the original answers and
acceptance criteria for all retained questions.

Source notes were trimmed to remove comparisons to excluded documents. References
to the original audit corpus describe historical checks, not a new source audit.
The source manifest now contains only the 78 retained, successfully downloaded
PDFs. The redundant candidate list and 20 failed-download records were removed.

## Retained approved corrections

| ID | Problem found | Approved correction |
|---|---|---|
| INV-22 | Specialist consulting scope and firm/key-person experience unclear; TRS permits comparable experience | Name six RFPs, describe requirements and alternatives per file, remove misleading uniform experience range |
| INV-23 | Baltimore five-year term and two two-year options omitted; comparison scope unclear | Name ten files, add Baltimore, use Missouri's explicit one-year-plus-two-year provision |
| SVC-10 | OCERS minimum insurance list conflicts with sample-contract words/numerals | Narrow to the minimum-qualification insurance list; retain sample inconsistency note |
| SVC-24 | Clark early termination described as unconditional | Include the county's unsatisfactory-performance condition and 30-day notice |
| CONS-14 | Hartford list omitted four of ten requirements; main text and appendix differ | Limit to Section 2; include all ten requirements, five insurance limits, deadline and certifications |
| CONS-15 | Creve Coeur quarterly on-site meetings and monthly/as-needed calls presented as alternatives | Require quarterly on-site meetings plus monthly or as-needed calls |
| CONS-16 | Denominator for modal experience requirement undefined | Name ten general-consulting RFPs; mode five years: four five-year, three ten-year, two seven-year, one three-year; retain COAERS alternative |
| DDQ-10 | ILPA ESG section described as six subsections | Correct to seven, adding 19.7 Additional Information and management-company ESG |
| OTH-18 | Actuarial contract comparison omitted three solicitations | Add KCERA, St. Louis PRS and AVFPD; distinguish contract term, one-time work, and service years |
| XD-03 | Counting convention for a jointly named contributor unclear | Count 31 entries; TPG & Y Analytics is one entry |
| XD-17 | LAFPP generic Iran clause treated as operative | Main text exempts PSC-36; retain three operative requirements plus the LAFPP exemption |

## Files and interpretation

- `queries.json`: questions only, for evaluation input.
- `standards.json`: adjudicated answers, acceptance criteria and source scope.
- `questions_verified.csv`: complete retained reference records and audit notes.
- `approved_corrections.jsonl`: the eleven retained approved corrections.
- `../documents/manifest_S.csv`: the 78 PDF sources, URLs, sizes and hashes.
- `../copy_manifest.json`: current file sizes and hashes after filtering.

Use `gold_answer` as the adjudicated reference. `verify_answer` remains the initial
blind answer and may contain later-discovered mistakes. Interpret it together
with `verify_status`, `verify_note` and the final reference. The workflow field
`review_status` remains `auto_drafted`; verification is recorded in `verify_*`.
Full original blind/comparison batches and adjudication artifacts remain outside
this subset and are not included in this folder.

## Consistency checks on this subset

- All three question files contain the same 110 unique IDs and question text.
- Reference answers and passages agree between the CSV and standards.
- Every listed source exists in the PDF corpus; no non-PDF source references remain.
- Each of the 14 retained pairs contains one pair_a and one pair_b question.
- All 11 correction records point to retained questions.
- The 78 PDFs retain their original SHA-256 hashes.
- Current file counts, sizes and hashes are recorded in copy_manifest.json.

These are dataset consistency checks, not a new semantic verification or a
retrieval accuracy result. Automated reference verification remains subject to error.
