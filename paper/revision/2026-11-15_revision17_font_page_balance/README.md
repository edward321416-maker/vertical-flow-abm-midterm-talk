# Thesis Revision 17: genuine fonts and page-8 balance (2026-11-15)

This revision corrects the final-page white space without artificially changing the A4/2-column manuscript's official 9pt body font size, 13.5pt leading, or 16/19/15mm margins. Figures 1-2 are rendered at full column width; table row leading was raised to readable 8pt/12pt, table caption-to-body spacing changed from -3pt to +2pt, and one redundant sentence was shortened. Page 8 now begins with Section 5.2.

## Validation

8 pages; PDF 1.4; 7 figures / 10 tables (each caption once); source TeX compiled twice; 0 Overfull/Underfull/Missing glyph warnings; no text outside page bounds; numeric multiset 432/432 preserved. Final-page bottom blank measured from PDF including the required bottom margin: 65.23 mm in Rev16, 21.28 mm in Rev17 (43.95 mm reduction).

## Font status — NOT FULLY RESOLVED

Official HWP requires Korean HumanMyeongjo (휴먼명조) and English Times New Roman. These proprietary genuine fonts are not installed/licensed in the current Linux renderer. The submitted PDF therefore embeds Noto Serif CJK KR and Tinos, respectively. It is **not** genuine-font-identical. The editable LaTeX source and actual source diff are included in the local complete package supplied in conversation; that source uses conditional font detection and selects genuine fonts when installed in an authorized environment. Re-render and revalidate the 8-page result after switching fonts; font metrics change pagination. No proprietary font files were supplied or uploaded.

## Source references

- Original official HWP (archived earlier in this repository): paper/format_audit/official_template/aik_journal_sample_20250218.hwp
- Hancom FAQ about the two 휴먼명조 files: https://recruit.hancom.com/support/faqCenter/faq/detail/2680
- Microsoft Times New Roman reference: https://learn.microsoft.com/en-us/typography/font-list/times-new-roman

No independent simulation rerun or field-traffic validation is claimed. Original Revision16 and main remain intact.
