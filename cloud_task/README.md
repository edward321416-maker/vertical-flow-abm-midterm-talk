# Claude Code Cloud — 논문 중간발표 시각화 개선 실행 패키지

This folder is an input bundle for the **midterm presentation** redesign in Claude Code Cloud.

## Verified inputs
- `CLAUDE_CLOUD_TASK.md`: task instructions, design references, research validation and final PDF criteria
- `inputs/vertical_flow_presentation_clear_titles.pdf`: 18-slide source presentation (optimized, searchable PDF)
- `inputs/paper_revised_8pages_v2(2).pdf`: 8-page research paper (optimized, searchable; the visible contact email on the author block was **redacted for public GitHub publication**)
- Additional analysis CSVs and GAMA/R code remain in the repository's original paths.

The repository is **public**. Treat any contents committed to this branch as public. Do not copy credentials, personally identifying contact details, or unpublished private material into outputs.

## Run from the checked-out branch
```powershell
claude --cloud "Read cloud_task/CLAUDE_CLOUD_TASK.md in full. Verify the two cloud_task/inputs PDFs and source CSV files, then complete the actual midterm presentation PDF redesign. Render/audit every page and deliver cloud_task/output/vertical_flow_midterm_refined.pdf. Preserve original research files. Use existing credits/tools only; no extra billing."
```

The source PDF can be rendered by fitz/PyMuPDF. The agent should perform the actual redesign, not merely issue a plan. Preserve the slide content and citations while replacing repetitive layouts and opaque RQ/E1/E2 headings with reader-facing Korean. Maintain white background/black typography, with color only for meaningful chart distinctions.
