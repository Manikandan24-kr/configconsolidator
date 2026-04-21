import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# ── Colour palette ────────────────────────────────────────────────────────────
CLR = {
    "header_bg":      "1F3864",   # dark navy
    "header_font":    "FFFFFF",
    "section_bg":     "2E75B6",   # mid blue
    "section_font":   "FFFFFF",
    "captured":       "E2EFDA",   # light green
    "captured_dark":  "70AD47",   # green accent
    "missed":         "FCE4D6",   # light red
    "missed_dark":    "FF0000",   # red accent
    "partial":        "FFF2CC",   # light yellow
    "partial_dark":   "ED7D31",   # orange accent
    "alt_row":        "F2F7FC",   # subtle blue tint for alternating rows
    "white":          "FFFFFF",
    "summary_bg":     "D6E4F0",
    "kpi_blue":       "BDD7EE",
    "kpi_green":      "C6EFCE",
    "kpi_red":        "FFC7CE",
    "kpi_yellow":     "FFEB9C",
}

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="000000", size=11, italic=False):
    return Font(bold=bold, color=color, size=size, italic=italic,
                name="Calibri")

def border_thin():
    s = Side(style="thin", color="B8CCE4")
    return Border(left=s, right=s, top=s, bottom=s)

def border_medium():
    s = Side(style="medium", color="2E75B6")
    return Border(left=s, right=s, top=s, bottom=s)

def align(h="left", v="center", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def write_header_row(ws, row, values, col_start=1):
    for i, val in enumerate(values):
        c = ws.cell(row=row, column=col_start + i, value=val)
        c.fill = fill(CLR["header_bg"])
        c.font = font(bold=True, color=CLR["header_font"], size=11)
        c.alignment = align("center")
        c.border = border_medium()

def write_section_row(ws, row, label, ncols, col_start=1):
    ws.merge_cells(
        start_row=row, start_column=col_start,
        end_row=row, end_column=col_start + ncols - 1
    )
    c = ws.cell(row=row, column=col_start, value=label)
    c.fill = fill(CLR["section_bg"])
    c.font = font(bold=True, color=CLR["section_font"], size=11)
    c.alignment = align("left")
    c.border = border_medium()

def write_data_row(ws, row, values, status, col_start=1, alt=False):
    bg = CLR["white"] if not alt else CLR["alt_row"]
    if status == "captured":
        badge_fill = fill(CLR["captured"])
        badge_font = font(bold=True, color="375623")
    elif status == "missed":
        badge_fill = fill(CLR["missed"])
        badge_font = font(bold=True, color="9C0006")
    elif status == "partial":
        badge_fill = fill(CLR["partial"])
        badge_font = font(bold=True, color="7E4E0C")
    else:
        badge_fill = fill(bg)
        badge_font = font()

    for i, val in enumerate(values):
        c = ws.cell(row=row, column=col_start + i, value=val)
        c.border = border_thin()
        c.alignment = align()
        if i == len(values) - 2:   # "Status" column (second to last)
            c.fill = badge_fill
            c.font = badge_font
            c.alignment = align("center")
        else:
            c.fill = fill(bg)
            c.font = font()


# ═════════════════════════════════════════════════════════════════════════════
wb = openpyxl.Workbook()

# ─────────────────────────────────────────────────────────────────────────────
# SHEET 1 — Executive Summary
# ─────────────────────────────────────────────────────────────────────────────
ws1 = wb.active
ws1.title = "Executive Summary"
ws1.sheet_view.showGridLines = False
ws1.column_dimensions["A"].width = 36
ws1.column_dimensions["B"].width = 22
ws1.column_dimensions["C"].width = 22
ws1.column_dimensions["D"].width = 22
ws1.column_dimensions["E"].width = 22
ws1.row_dimensions[1].height = 10

# Title block
ws1.merge_cells("A2:E2")
c = ws1["A2"]
c.value = "AAAS Style Guide — Tool Coverage Gap Analysis"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=16)
c.alignment = align("center")

ws1.merge_cells("A3:E3")
c = ws1["A3"]
c.value = "Comparison: Config Consolidator App Output  vs.  Internal Manual Ruleset"
c.fill = fill(CLR["section_bg"])
c.font = font(color="FFFFFF", size=11, italic=True)
c.alignment = align("center")

ws1.row_dimensions[2].height = 34
ws1.row_dimensions[3].height = 22

# KPI row labels
kpi_labels = [
    ("App extracted rules", "1,242", CLR["kpi_blue"]),
    ("Manual ruleset requirements", "~1,680", CLR["kpi_blue"]),
    ("Topics well-captured", "9", CLR["kpi_green"]),
    ("Topics partially captured", "4", CLR["kpi_yellow"]),
    ("Topics missed / not captured", "11", CLR["kpi_red"]),
]
ws1.row_dimensions[5].height = 18
ws1.row_dimensions[6].height = 40
ws1.row_dimensions[7].height = 18

ws1.merge_cells("A5:E5")
c = ws1["A5"]
c.value = "AT A GLANCE"
c.fill = fill(CLR["section_bg"])
c.font = font(bold=True, color="FFFFFF", size=11)
c.alignment = align("center")

for col_idx, (label, val, bg) in enumerate(kpi_labels, start=1):
    cl = ws1.cell(row=6, column=col_idx, value=label)
    cv = ws1.cell(row=7, column=col_idx, value=val)
    cl.fill = fill(CLR["header_bg"])
    cl.font = font(bold=True, color="FFFFFF", size=10)
    cl.alignment = align("center")
    cv.fill = fill(bg)
    cv.font = font(bold=True, size=16)
    cv.alignment = align("center")
    cl.border = border_thin()
    cv.border = border_thin()

# Legend
ws1.row_dimensions[9].height = 18
ws1.merge_cells("A9:E9")
c = ws1["A9"]
c.value = "STATUS LEGEND"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=11)
c.alignment = align("center")

legend = [
    ("✅  CAPTURED", "captured", "Rule/topic area is represented in the tool output with meaningful coverage."),
    ("⚠️  PARTIAL",  "partial",  "Some rules exist in tool output but with gaps, fragmentation, or shallow coverage."),
    ("❌  NOT CAPTURED", "missed", "Topic exists in the manual ruleset but was absent or nearly absent in tool output."),
]
for ri, (lbl, status, desc) in enumerate(legend, start=10):
    ws1.row_dimensions[ri].height = 22
    cl = ws1.cell(row=ri, column=1, value=lbl)
    cd = ws1.cell(row=ri, column=2, value=desc)
    ws1.merge_cells(start_row=ri, start_column=2, end_row=ri, end_column=5)
    if status == "captured":
        bg, fg = CLR["captured"], "375623"
    elif status == "partial":
        bg, fg = CLR["partial"], "7E4E0C"
    else:
        bg, fg = CLR["missed"], "9C0006"
    cl.fill = fill(bg); cl.font = font(bold=True, color=fg, size=11)
    cl.alignment = align("center"); cl.border = border_thin()
    cd.fill = fill(CLR["alt_row"]); cd.font = font(size=10)
    cd.alignment = align(); cd.border = border_thin()

# Files table
ws1.row_dimensions[14].height = 18
ws1.merge_cells("A14:E14")
c = ws1["A14"]
c.value = "SOURCE FILES"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=11)
c.alignment = align("center")

write_header_row(ws1, 15, ["File", "Type", "Sheets", "Total Items", "Notes"])
files_data = [
    ("StyleGuide_Analysis_Report (1).xlsx", "App Output", "3  (Extracted Rules, Discrepancies & Gaps, Summary)",
     "1,242 rules", "Generated by Config Consolidator after processing 17 AAAS PDFs"),
    ("AAAS styleguide.xlsx", "Manual Ruleset", "22 topic sheets",
     "~1,680 requirements", "Configured by internal team; includes lookup tables, journal-specific rules, CMOS table"),
]
for ri, row in enumerate(files_data, start=16):
    ws1.row_dimensions[ri].height = 36
    for ci, val in enumerate(row, start=1):
        c = ws1.cell(row=ri, column=ci, value=val)
        c.fill = fill(CLR["alt_row"] if ri % 2 == 0 else CLR["white"])
        c.font = font(size=10)
        c.alignment = align()
        c.border = border_thin()

# Root causes
ws1.row_dimensions[19].height = 18
ws1.merge_cells("A19:E19")
c = ws1["A19"]
c.value = "ROOT CAUSES OF GAPS"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=11)
c.alignment = align("center")

causes = [
    "1.  Lookup tables (Trademarks, Units, Statistical Terms, Organizations) — AI extracted general rules but not individual term-by-term entries.",
    "2.  External references (CMOS table) — not present in the ingested PDFs.",
    "3.  Sub-journal differentiation — tool treated all PDFs as one corpus; manual ruleset maps rules per journal (Immunology, Robotics, Signaling, Transl. Med).",
    "4.  Institutional knowledge (Queries sheet, over-editing guidance) — lives in process docs, not style guide PDFs.",
    "5.  Acronym fragmentation — 200+ near-duplicate rules extracted instead of a clean consolidated set; flagged as top discrepancy by the tool itself.",
]
for ri, txt in enumerate(causes, start=20):
    ws1.row_dimensions[ri].height = 28
    ws1.merge_cells(start_row=ri, start_column=1, end_row=ri, end_column=5)
    c = ws1.cell(row=ri, column=1, value=txt)
    c.fill = fill(CLR["alt_row"] if ri % 2 == 0 else CLR["white"])
    c.font = font(size=10)
    c.alignment = align()
    c.border = border_thin()


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 2 — Topic Coverage Matrix
# ─────────────────────────────────────────────────────────────────────────────
ws2 = wb.create_sheet("Topic Coverage Matrix")
ws2.sheet_view.showGridLines = False
ws2.column_dimensions["A"].width = 30
ws2.column_dimensions["B"].width = 28
ws2.column_dimensions["C"].width = 14
ws2.column_dimensions["D"].width = 14
ws2.column_dimensions["E"].width = 60
ws2.column_dimensions["F"].width = 55

ws2.row_dimensions[1].height = 10

ws2.merge_cells("A2:F2")
c = ws2["A2"]
c.value = "Topic Coverage Matrix — Manual Ruleset vs. App Output"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=14)
c.alignment = align("center")
ws2.row_dimensions[2].height = 30

write_header_row(ws2, 3,
    ["Topic Area", "Manual Sheet (rows)", "Manual Reqs", "App Rules", "Status", "Notes"])
ws2.row_dimensions[3].height = 22

# data: (topic, manual_sheet, manual_reqs, app_rules, status_label, status_key, notes)
coverage_data = [
    # ── CAPTURED ──────────────────────────────────────────────────────────────
    ("section", "✅  WELL CAPTURED", None, None, None, None, None),
    ("Abstract rules",           "Abstract (24 reqs)",                       24,  "~15",  "✅ Captured",  "captured",
     "Tense, acronym spell-out, no citations, P-value formatting, chemical elements — all present."),
    ("Acronym / Abbreviation rules", "Abstract + General.Science.Style",    "~40", "200+", "✅ Captured",  "captured",
     "Over-extracted (200+ fragmented rules). Core rules are present; consolidation needed."),
    ("Capitalization",           "Capitalization (114 reqs)",               114,  "~70",  "✅ Captured",  "captured",
     "Genus/species, sentence case, proper nouns, titles, government offices covered."),
    ("Hyphenation",              "Hyphenation (45) + CMOS table (117)",     162,  "~67",  "✅ Captured",  "captured",
     "60+ editorial + 7 typesetting rules. Note: CMOS external table not ingested (see Missed)."),
    ("References & Citations",   "References.and.Notes (252 reqs)",         252, "~157",  "✅ Captured",  "captured",
     "Journal names, author truncation, book citations, preprints, internet sources — well covered."),
    ("Italics / Typesetting",    "Italics.2023 (53 reqs)",                   53,  "~15",  "✅ Captured",  "captured",
     "Genetics italicization (C. elegans, Drosophila, yeast, plants), gene/protein names captured."),
    ("Numbers",                  "Numbers (48 reqs)",                        48,  "~10",  "✅ Captured",  "captured",
     "Number formatting, ranges, fractions, decimals captured."),
    ("Tense & Voice",            "General.Science.Style",                    "~5", "~3",  "✅ Captured",  "captured",
     "Past tense for results, present for conclusions, active voice preference."),
    ("'Novel/New/First' prohibition", "Abstract + General.Science.Style",   "~4", "~4",  "✅ Captured",  "captured",
     "Captured AND flagged as a conflict (tool notes 'new' is OK for genuinely new technology)."),
    ("Author Affiliations (basic)", "Author Affiliations (11 reqs)",         11,  "~5",  "✅ Captured",  "captured",
     "Affiliation numbering, format rules captured."),

    # ── PARTIAL ───────────────────────────────────────────────────────────────
    ("section", "⚠️  PARTIALLY CAPTURED", None, None, None, None, None),
    ("Punctuation (general)",    "Punctuation (175 reqs)",                  175,  "~25",  "⚠️ Partial",   "partial",
     "Apostrophe, comma, colon, ellipsis, em/en dash captured. Detail sub-rules (appositives, possessives) missing."),
    ("Figures / Tables",         "Figures-tables-equations (71 reqs)",       71,  "~20",  "⚠️ Partial",   "partial",
     "Caption structure, axis labels, font sizes captured. Insight no-number rule, Scheme→Figure rule, citation from reference missed."),
    ("Spelling",                 "Spelling (290 reqs)",                     290,  "~10",  "⚠️ Partial",   "partial",
     "~10 rules + deterministic US English checks. The full 290-row term list was not extracted individually."),
    ("General Science Style",    "General.Science.Style (71 reqs)",          71,  "~15",  "⚠️ Partial",   "partial",
     "Some rules captured (tense, voice, SI units). Over-editing guidance, US English rule, style manual hierarchy missed."),

    # ── NOT CAPTURED ──────────────────────────────────────────────────────────
    ("section", "❌  NOT CAPTURED", None, None, None, None, None),
    ("Trademark lookup table",   "Trademarks (158 reqs)",                   158,   "~5",  "❌ Not Captured", "missed",
     "Only 5 generic rules extracted. Full term-by-term list (Kleenex, Xerox, drug/reagent names) not captured."),
    ("Organizations & Agencies lookup", "Organizations and Agencies (124 reqs)", 124, "~3", "❌ Not Captured", "missed",
     "Institutional acronym lookup (CERN, CNRS, NIH, INSERM, etc.) not extracted — only generic rules."),
    ("Units lookup table",       "Units (9 header rows + external table)",    9,   "~5",  "❌ Not Captured", "missed",
     "Per-unit sft/dft/blank handling table not captured. Only 5 general unit rules extracted."),
    ("Statistical Terms lookup", "Statistical Terms (37 reqs)",              37,   "~1",  "❌ Not Captured", "missed",
     "Term-by-term table (ANOVA, CI, df, SD, SEM, OR, R², etc.) not extracted. Only 1 generic notation rule."),
    ("Serial comma policy",      "Punctuation (175 reqs)",                  "~1",   "0",  "❌ Not Captured", "missed",
     "Explicitly flagged as Gap #6 in tool's own discrepancies sheet. Oxford comma policy absent."),
    ("Apostrophe detail rules",  "Punctuation (175 reqs)",                  "~7",  "~2",  "❌ Not Captured", "missed",
     "7 numbered sub-rules (singular/plural possessives, compound possessives, symbol plurals) not captured."),
    ("Appositives (comma rules)", "Punctuation (175 reqs)",                 "~3",   "0",  "❌ Not Captured", "missed",
     "True vs. non-restrictive appositive comma distinction not extracted."),
    ("Author Affiliations (detail)", "Author Affiliations (11 reqs)",       "~4",   "0",  "❌ Not Captured", "missed",
     "'Single author = no separate email footnote' and 'no co-senior author designation' rules missed."),
    ("CMOS Hyphenation table",   "CMOS_table07-hyphens (117 reqs)",         117,    "0",  "❌ Not Captured", "missed",
     "External Chicago Manual reference — not in any of the 17 ingested AAAS PDFs."),
    ("Sub-journal rules",        "Sci. Immunol / Signal / Robot / Transl. Med (~269 reqs)", 269, "0", "❌ Not Captured", "missed",
     "Journal-specific rules for 4 sub-journals entirely absent. Tool treated all PDFs as one Science corpus."),
    ("Author Queries templates", "Queries (31 items)",                       31,    "0",  "❌ Not Captured", "missed",
     "Standard templated author queries are process documentation — not in style guide PDFs."),
]

row = 4
alt = False
for item in coverage_data:
    if item[0] == "section":
        ws2.row_dimensions[row].height = 20
        write_section_row(ws2, row, item[1], 6)
        row += 1
        alt = False
        continue

    topic, manual_sheet, manual_reqs, app_rules, status_lbl, status_key, notes = item
    ws2.row_dimensions[row].height = 40
    bg = CLR["alt_row"] if alt else CLR["white"]

    values = [topic, manual_sheet, str(manual_reqs), str(app_rules), status_lbl, notes]
    for ci, val in enumerate(values, start=1):
        c = ws2.cell(row=row, column=ci, value=val)
        c.border = border_thin()
        c.alignment = align()
        if ci == 5:   # Status column
            if status_key == "captured":
                c.fill = fill(CLR["captured"]); c.font = font(bold=True, color="375623")
            elif status_key == "partial":
                c.fill = fill(CLR["partial"]); c.font = font(bold=True, color="7E4E0C")
            else:
                c.fill = fill(CLR["missed"]); c.font = font(bold=True, color="9C0006")
            c.alignment = align("center")
        else:
            c.fill = fill(bg); c.font = font(size=10)

    row += 1
    alt = not alt


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 3 — Captured Rules Detail
# ─────────────────────────────────────────────────────────────────────────────
ws3 = wb.create_sheet("Captured Rules Detail")
ws3.sheet_view.showGridLines = False
ws3.column_dimensions["A"].width = 30
ws3.column_dimensions["B"].width = 55
ws3.column_dimensions["C"].width = 22
ws3.column_dimensions["D"].width = 28

ws3.merge_cells("A1:D1")
c = ws3["A1"]
c.value = "Captured Rules — Representative Samples from App Output"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=13)
c.alignment = align("center")
ws3.row_dimensions[1].height = 28

write_header_row(ws3, 2, ["Category", "Rule (from App Output)", "Source PDF", "Automation Level"])

captured_rules = [
    # Abstract
    ("section", "ABSTRACT RULES"),
    ("Abstract — structure",
     "Abstracts should start with a brief background sentence giving a broad introduction to the field.",
     "Abstract.2023.pdf", "AI — Moderate"),
    ("Abstract — no references",
     "Do not cite references in the abstract; the investigator's name may be introduced but no numbered citation.",
     "Abstract.2023.pdf", "Deterministic"),
    ("Abstract — P values",
     "P values and other statistical information may appear in the abstract at the author's discretion; use the style p < 0.05.",
     "Abstract.2023.pdf", "Deterministic"),
    ("Abstract — tense",
     "Use simple past tense to state completed operations, observations, and results in the abstract.",
     "Abstract.2023.pdf", "AI — Moderate"),
    ("Abstract — novel/new",
     "Avoid using 'novel,' 'new,' or 'unique' to characterize findings; exception when describing genuinely new technology.",
     "Abstract.2023.pdf", "AI — High"),
    ("Abstract — acronyms",
     "Acronyms introduced in the abstract should be redefined at first use in the main text.",
     "Abstract.2023.pdf", "AI — Moderate"),
    # Capitalization
    ("section", "CAPITALIZATION"),
    ("Capitalization — titles",
     "Sentence case for titles (as of 5/23/14 issue); capitalize the first word after a colon.",
     "Capitalization.general.2023.pdf", "AI — High"),
    ("Capitalization — genus/species",
     "Capitalize genus but lowercase species when they appear together in a title.",
     "Capitalization.general.2023.pdf", "Deterministic"),
    ("Capitalization — proper nouns",
     "Capitalize only proper nouns in names of laws and theories (Planck's constant, Bohr model).",
     "Capitalization.general.2023.pdf", "AI — Moderate"),
    # Hyphenation
    ("section", "HYPHENATION"),
    ("Hyphenation — compound modifiers",
     "Hyphenate compound modifiers before a noun; do not hyphenate in predicative position.",
     "Hyphenation.20023.pdf", "AI — Moderate"),
    ("Hyphenation — adverb -ly",
     "Do not hyphenate adverb + adjective when adverb ends in -ly.",
     "Hyphenation.20023.pdf", "Deterministic"),
    ("Hyphenation — en dash ranges",
     "Use an en dash (not a hyphen) for ranges of numbers, dates, and compound modifiers with a proper noun.",
     "Hyphenation.20023.pdf", "Deterministic"),
    # Numbers
    ("section", "NUMBERS"),
    ("Numbers — spell out one-nine",
     "Spell out whole numbers one through nine; use numerals for 10 and above.",
     "Numbers.2023.pdf", "Deterministic"),
    ("Numbers — leading zero",
     "Include a leading zero before the decimal point for numbers less than 1 (0.05, not .05).",
     "Numbers.2023.pdf", "Deterministic"),
    ("Numbers — ranges",
     "Use an en dash to express number ranges; repeat the full number for clarity (112–115, not 112–15).",
     "Numbers.2023.pdf", "Deterministic"),
    # References
    ("section", "REFERENCES & CITATIONS"),
    ("References — author truncation",
     "List all authors up to six; if more than six, list the first three followed by 'et al.'",
     "References.and.Notes.2023.pdf", "Deterministic"),
    ("References — journal abbreviations",
     "Abbreviate journal names per standard lists; use italic for journal titles.",
     "References.and.Notes.2023.pdf", "AI — High"),
    ("References — preprint (bioRxiv)",
     "For bioRxiv preprints cite as: Author, bioRxiv [Preprint] (year). doi:...",
     "References.and.Notes.2023.pdf", "Deterministic"),
    ("References — DOI format",
     "Include the DOI as a full URL (https://doi.org/...) for all references where available.",
     "References.and.Notes.2023.pdf", "Deterministic"),
    # Italics
    ("section", "ITALICS / TYPESETTING"),
    ("Italics — gene symbols",
     "Italicize gene and allele symbols; roman type for protein products.",
     "Italics.2023.pdf", "AI — High"),
    ("Italics — C. elegans genetics",
     "Italicize gene names in C. elegans (e.g., unc-22); roman for proteins.",
     "Italics.2023.pdf", "AI — High"),
    ("Italics — Drosophila genetics",
     "Italicize Drosophila gene symbols (white, Antennapedia); capitalize dominant alleles.",
     "Italics.2023.pdf", "AI — High"),
    ("Italics — foreign words",
     "Italicize foreign words and phrases not yet adopted into English.",
     "Italics.2023.pdf", "AI — Moderate"),
    # Tense / Voice
    ("section", "TENSE & VOICE"),
    ("Tense — results",
     "Use past tense to report experimental results; present tense to state conclusions.",
     "General.Science.Style.2023.pdf", "AI — Moderate"),
    ("Voice — active preferred",
     "Active voice is more appropriate than passive when author's procedures need distinguishing from others'.",
     "General.Science.Style.2023.pdf", "AI — Moderate"),
    # Acronyms (sample — heavily fragmented)
    ("section", "ACRONYMS (sample — 200+ rules extracted, consolidation needed)"),
    ("Acronyms — first use",
     "Spell out all acronyms and abbreviations the first time they are mentioned in the text.",
     "Acronyms.2025_clean.pdf", "Deterministic"),
    ("Acronyms — abstract redefine",
     "Acronyms introduced in the abstract must be redefined at first use in the main text.",
     "Acronyms.2025_clean.pdf", "AI — Moderate"),
    ("Acronyms — no plural s",
     "Do not add 's' to pluralize acronyms; use 'two PCR experiments', not 'two PCRs'.",
     "Acronyms.2025_clean.pdf", "Deterministic"),
]

row = 3
alt = False
for item in captured_rules:
    if item[0] == "section":
        ws3.row_dimensions[row].height = 18
        write_section_row(ws3, row, item[1], 4)
        row += 1
        alt = False
        continue
    cat, rule, src, auto = item
    ws3.row_dimensions[row].height = 40
    bg = CLR["alt_row"] if alt else CLR["white"]
    for ci, val in enumerate([cat, rule, src, auto], start=1):
        c = ws3.cell(row=row, column=ci, value=val)
        c.fill = fill(bg)
        c.font = font(size=10)
        c.alignment = align()
        c.border = border_thin()
    row += 1
    alt = not alt


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 4 — Missed Rules Detail
# ─────────────────────────────────────────────────────────────────────────────
ws4 = wb.create_sheet("Missed Rules Detail")
ws4.sheet_view.showGridLines = False
ws4.column_dimensions["A"].width = 30
ws4.column_dimensions["B"].width = 70
ws4.column_dimensions["C"].width = 22
ws4.column_dimensions["D"].width = 40

ws4.merge_cells("A1:D1")
c = ws4["A1"]
c.value = "Missed / Not Captured Rules — From Manual Ruleset"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=13)
c.alignment = align("center")
ws4.row_dimensions[1].height = 28

write_header_row(ws4, 2, ["Category", "Rule / Requirement (from Manual Ruleset)", "Manual Sheet", "Why Not Captured"])

missed_rules = [
    ("section", "TRADEMARK RULES"),
    ("Trademarks — general",
     "Use a generic term where possible. If a trademark is used, include the generic term (Kleenex tissues, Vaseline petroleum jelly).",
     "Trademarks", "Generic rule present in app; the 158-row term list was not extracted."),
    ("Trademarks — no pluralization",
     "Trademarks should not be pluralized. Use the generic term: 'two Kodak cameras', not 'two Kodaks'.",
     "Trademarks", "Rule not captured — lookup table entries not ingested individually."),
    ("Trademarks — no verb use",
     "Trademarks should not be used as verbs: one photocopies a page on a Xerox copier; one does not 'Xerox' a page.",
     "Trademarks", "Not captured in app output."),
    ("Trademarks — no possessive",
     "Trademarks should not be used in the possessive form, unless the apostrophe is part of the name (Levi's, McDonald's).",
     "Trademarks", "Not captured in app output."),
    ("Trademarks — drug names",
     "For drugs, give the trade name and commercial source in parentheses after the generic term at first use.",
     "Trademarks", "Not captured; requires per-term lookup logic."),
    ("Trademarks — specific term list",
     "[Full list of ~150 specific trademarked terms with capitalization guidance, e.g., Band-Aid, Freon, Styrofoam, Teflon, Velcro…]",
     "Trademarks", "Term-by-term table not extracted by AI — requires structured table parsing."),

    ("section", "STATISTICAL TERMS LOOKUP"),
    ("Statistical Terms — ANOVA",    "ANOVA — use as-is, roman, all caps.", "Statistical Terms", "Term table not extracted."),
    ("Statistical Terms — CI",        "CI — confidence interval, roman.", "Statistical Terms", "Term table not extracted."),
    ("Statistical Terms — df",        "df — degrees of freedom, roman lowercase.", "Statistical Terms", "Term table not extracted."),
    ("Statistical Terms — n/N",       "n — sample size (lowercase); N — total population (uppercase).", "Statistical Terms", "Term table not extracted."),
    ("Statistical Terms — SD / SEM",  "SD and SEM — roman type, no periods.", "Statistical Terms", "Term table not extracted."),
    ("Statistical Terms — significant", "'Significant' should only be used in a statistical sense; avoid loose use.", "Statistical Terms", "Not captured as standalone rule."),
    ("Statistical Terms — R²",        "R² — roman italic R with superscript 2.", "Statistical Terms", "Term table not extracted."),

    ("section", "UNITS LOOKUP TABLE"),
    ("Units — sft/dft system",
     "sft = spell out on first use, use abbreviation thereafter. dft = define on first use. Blank = use abbreviation throughout, no definition required.",
     "Units", "Header explanation captured but per-unit instructions (the full table) not extracted."),
    ("Units — specific per-unit handling",
     "[Full table of ~400 unit entries specifying sft/dft/blank for each unit symbol, e.g., mol, Hz, Pa, Gy, Sv, Da…]",
     "Units", "Structured lookup table — AI extracted general rules, not individual entries."),

    ("section", "ORGANIZATIONS & AGENCIES LOOKUP"),
    ("Orgs — affiliation state abbreviations",
     "In affiliation footnotes, use two-letter abbreviations for US states; spell out Post Box and Canadian provinces.",
     "Organizations and Agencies", "Not captured as explicit rule."),
    ("Orgs — institutional acronym list",
     "[Lookup table: AB-DLO, ALSAC, CERN, CNRS, EA, INSERM, UMR, USR, UNESCO — use these acronyms without spelling out in affiliation footnotes.]",
     "Organizations and Agencies", "Acronym lookup table not extracted — only generic 'well-known = OK as-is' rule captured."),
    ("Orgs — acknowledgement abbreviations",
     "In acknowledgement footnotes, abbreviate NIH, NSF etc.; spell out if they occur elsewhere in the text.",
     "Organizations and Agencies", "Not captured."),

    ("section", "PUNCTUATION — DETAIL RULES"),
    ("Punctuation — serial comma",
     "Serial (Oxford) comma policy: [not explicitly stated in PDFs — gap confirmed by tool itself as Discrepancy #6].",
     "Punctuation", "Flagged as gap in app's own Discrepancies sheet. Policy absent from PDFs."),
    ("Punctuation — apostrophe singular possessive",
     "Possessive of a singular noun: add apostrophe + s even if noun ends in s. (Burns's, Marx's, Nicholas's, Dickens's)",
     "Punctuation", "Detail sub-rule not extracted."),
    ("Punctuation — apostrophe plural possessive",
     "Possessive of plural noun ending in sibilant: add apostrophe only (the Eyewitnesses' report).",
     "Punctuation", "Detail sub-rule not extracted."),
    ("Punctuation — symbol plurals",
     "Add 's to form plural of symbols (×'s). Avoid making symbols possessive.",
     "Punctuation", "Detail sub-rule not extracted."),
    ("Punctuation — contractions",
     "Avoid contractions (you're, he's, it's, didn't). Write out in full.",
     "Punctuation", "Not captured as standalone rule."),
    ("Punctuation — appositives",
     "Only a true appositive (exclusively interchangeable) is set off by commas. Non-restrictive appositives do not use commas.",
     "Punctuation", "Appositive distinction not extracted."),

    ("section", "FIGURES / TABLES — DETAIL RULES"),
    ("Figures — Insight section (no numbers)",
     "Figures and tables in the Science Insight section do not have numbers; refer as 'the first figure', 'the second table'.",
     "Figures-tables-equations", "Specific edge-case rule not captured."),
    ("Figures — Scheme relabeling",
     "Schemes are no longer permissible; relabel as figures and renumber existing figures accordingly.",
     "Figures-tables-equations", "Policy change rule not captured."),
    ("Figures — citation from a reference",
     "When citing a figure/table/equation from a reference, the word should be lowercase and spelled out (e.g., 'figure 3 of (9)').",
     "Figures-tables-equations", "Specific nuance rule not captured."),
    ("Figures — callout as sentence subject",
     "Avoid having a panel callout be the subject of a sentence, though it is acceptable if necessary.",
     "Figures-tables-equations", "Editorial preference rule not captured."),

    ("section", "AUTHOR AFFILIATIONS — DETAIL RULES"),
    ("Affiliations — single author email",
     "For a single author, there is no need for a separate footnote for the email address; include it in the affiliation.",
     "Author Affiliations", "Edge-case rule not captured."),
    ("Affiliations — no co-senior author",
     "Do not allow designations of co-senior authors; change to 'These authors contributed equally to this work'.",
     "Author Affiliations", "Policy rule not captured."),

    ("section", "GENERAL SCIENCE STYLE — MISSED"),
    ("General Style — US English",
     "Use US English spellings only, except in author affiliations, organizations, journal/book titles, and place names.",
     "General.Science.Style", "General rule captured; explicit exception carve-outs not extracted."),
    ("General Style — avoid over-editing",
     "Avoid over-editing; retain the author's language as much as possible once it is grammatically correct.",
     "General.Science.Style", "Editorial guidance — subjective; not extractable as checkable rule."),
    ("General Style — style manual hierarchy",
     "Consult Science style manual first, then Webster's New International, then Chicago Manual of Style.",
     "General.Science.Style", "Process/reference guidance — not captured."),
    ("General Style — no special font for emphasis",
     "Do not use italics, boldface, or any special font for emphasis; the author's words should be sufficient.",
     "General.Science.Style", "Not captured as standalone rule."),

    ("section", "SUB-JOURNAL SPECIFIC RULES (4 journals — entirely absent)"),
    ("Science Immunology — checkpoints",
     "[~68 journal-specific requirements for Science Immunology manuscripts]",
     "Sci. Immunol Check Points", "Tool treats all PDFs as one corpus — no journal differentiation."),
    ("Science Signaling — checkpoints",
     "[~69 journal-specific requirements for Science Signaling manuscripts]",
     "Sci. Signal Check Points", "Tool treats all PDFs as one corpus — no journal differentiation."),
    ("Science Robotics — checkpoints",
     "[~64 journal-specific requirements for Science Robotics manuscripts]",
     "Sci. Robot Check Points", "Tool treats all PDFs as one corpus — no journal differentiation."),
    ("Science Translational Medicine — checkpoints",
     "[~68 journal-specific requirements for Science Transl. Med manuscripts]",
     "Sci. Transl. Med Check Points", "Tool treats all PDFs as one corpus — no journal differentiation."),

    ("section", "EXTERNAL / PROCESS CONTENT (not in PDFs)"),
    ("CMOS Hyphenation table",
     "[117-row Chicago Manual of Style compound word hyphenation lookup table]",
     "CMOS_table07-hyphens", "External reference — not in any ingested PDF."),
    ("Author Queries templates",
     "[31 standard templated author queries used during editing workflow]",
     "Queries", "Process documentation — not style guide content; out of scope for PDF extraction."),
]

row = 3
alt = False
for item in missed_rules:
    if item[0] == "section":
        ws4.row_dimensions[row].height = 18
        write_section_row(ws4, row, item[1], 4)
        row += 1
        alt = False
        continue
    cat, rule, sheet, reason = item
    ws4.row_dimensions[row].height = 44
    bg = CLR["alt_row"] if alt else CLR["white"]
    for ci, val in enumerate([cat, rule, sheet, reason], start=1):
        c = ws4.cell(row=row, column=ci, value=val)
        c.fill = fill(CLR["missed"] if ci == 1 else bg)
        c.font = font(size=10, bold=(ci == 1))
        c.alignment = align()
        c.border = border_thin()
    row += 1
    alt = not alt


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 5 — Discrepancies Flagged by Tool
# ─────────────────────────────────────────────────────────────────────────────
ws5 = wb.create_sheet("Tool Discrepancies")
ws5.sheet_view.showGridLines = False
ws5.column_dimensions["A"].width = 6
ws5.column_dimensions["B"].width = 14
ws5.column_dimensions["C"].width = 12
ws5.column_dimensions["D"].width = 48
ws5.column_dimensions["E"].width = 60
ws5.column_dimensions["F"].width = 50

ws5.merge_cells("A1:F1")
c = ws5["A1"]
c.value = "Discrepancies & Conflicts Flagged by the Config Consolidator Tool"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=13)
c.alignment = align("center")
ws5.row_dimensions[1].height = 28

write_header_row(ws5, 2, ["#", "Type", "Severity", "Title", "Description", "Recommendation"])

discrepancies = [
    (1, "Conflict",   "Medium", "Conflicting guidance on use of 'new' in abstracts",
     "Rule advises to avoid 'novel'/'new'; a separate rule allows 'new' when describing genuinely new technology.",
     "Clarify precise conditions when 'new' is acceptable."),
    (2, "Ambiguity",  "Medium", "Ambiguous rules on acronym spelling out and exceptions",
     "Multiple rules govern acronym usage and exceptions but without a clear hierarchy or decision tree.",
     "Provide an explicit decision tree or summary table."),
    (3, "Ambiguity",  "Medium", "Ambiguous rule for acronym redefinition: abstract vs. main text",
     "One rule says define in abstract; another says redefine at first use in main text. Interaction unclear.",
     "Clarify the general policy for abstract-to-main-text acronym continuity."),
    (4, "Ambiguity",  "Low",    "Ambiguity on acronym pluralization",
     "One rule says do not add 's' to pluralize; another implies 's' is acceptable in certain contexts.",
     "Provide a clear rule distinguishing when 's' is appropriate."),
    (5, "Conflict",   "Low",    "Inconsistency on spelling out units in the abstract",
     "One rule says spell out all units in abstract including kelvin; another lists exceptions.",
     "Detail unit abbreviation rules specifically for abstracts vs. main text."),
    (6, "Gap",        "Medium", "Missing serial comma (Oxford comma) guidance",
     "No rule addresses use of serial commas in lists anywhere in the extracted rules.",
     "Add explicit serial comma policy."),
    (7, "Gap",        "High",   "No explicit citation style rule in main text",
     "Several rules concern citations in abstracts but comprehensive main-text citation formatting is absent.",
     "Include comprehensive citation/reference formatting rules for main text."),
    (8, "Overlap",    "Low",    "Multiple rules on spelling out acronyms at first use",
     "Several rules repeat the same instruction to spell out acronyms at first use.",
     "Consolidate into a single comprehensive rule."),
    (9, "Overlap",    "Low",    "Multiple rules on spelling out chemical compound names",
     "Rules on spelling out chemical names, ionic state, and isotopes overlap significantly.",
     "Link related chemical nomenclature and acronym spelling rules."),
    (10, "Conflict",  "Medium", "Conflicting instructions on small capitals with chemical/acronym names",
     "One rule requires small capitals for 'ECL' as a chemical acronym; another says use uppercase.",
     "Clarify whether ECL is an exception requiring small caps."),
    (11, "Conflict",  "High",   "Inconsistent acronym definition and first-use capitalization rules",
     "Multiple rules conflict on how to define acronyms at first use and whether to capitalize the spelled-out form.",
     "Provide a clear hierarchy: spell out on first use unless on an accepted-as-is list."),
    (12, "Ambiguity", "Medium", "Unclear capitalization style for acronyms and initialisms",
     "Rules vary: some say all caps always; others list exceptions for mixed-case acronyms.",
     "Add comprehensive capitalization policy with explicit exceptions."),
    (13, "Ambiguity", "Medium", "Inconsistent hyphenation and dash usage in compound terms and acronyms",
     "Multiple rules mention hyphens and en dashes with slightly different contexts.",
     "Unify guidelines with exact contexts for hyphen vs. en dash."),
    (14, "Overlap",   "Low",    "Multiple rules reiterate defining acronyms on first use",
     "Rules editorial.acronyms.1, .definition.1, .expansion.1 all say the same thing.",
     "Consolidate into one comprehensive rule."),
    (15, "Gap",       "High",   "No guidance on serial comma in acronym expansions or lists",
     "Extensive acronym rules cover formatting but say nothing about comma style within the expansion.",
     "Include explicit rules on punctuation style in acronym expansions."),
    (16, "Gap",       "Medium", "Lack of guidance on acronym usage in plural and possessive forms",
     "Only one possessive acronym rule exists; no guidance on plural possessives or edge cases.",
     "Add guidance on possessive acronym forms and exceptions."),
    (17, "Ambiguity", "Medium", "Unclear author-preference vs. strict rules for acronyms",
     "One rule says follow author style if consistent; others impose strict capitalization.",
     "Clarify where author preference overrides guide rules."),
    (18, "Conflict",  "Medium", "Overlapping/conflicting use of abbreviation 'sft' for standard formatting",
     "Multiple rules suggest different interpretations of sft (spell-out-first) in different contexts.",
     "Provide clear guidance on sft definition and its application."),
    (19, "Ambiguity", "Low",    "Confusing rule IDs — possible duplicates for acronym usage",
     "Multiple rules share the same ID (e.g., editorial.acronyms.1) with different content.",
     "Use unique, clear IDs and consolidate duplicates."),
    (20, "Conflict",  "Medium", "Pluralization of acronyms — contradictory rules",
     "Rule says do not add 's'; another says 's' is acceptable for well-known acronyms used as nouns.",
     "Publishers should clarify preferred pluralization approach."),
]

sev_colors = {"High": ("FFC7CE", "9C0006"), "Medium": ("FFEB9C", "7E4E0C"), "Low": ("E2EFDA", "375623")}
type_colors = {"Conflict": ("FFC7CE", "9C0006"), "Ambiguity": ("FFEB9C", "7E4E0C"),
               "Gap": ("FCE4D6", "843C0C"), "Overlap": ("EAF1FB", "1F3864")}

for ri, (num, typ, sev, title, desc, rec) in enumerate(discrepancies, start=3):
    ws5.row_dimensions[ri].height = 50
    alt = ri % 2 == 0

    for ci, val in enumerate([num, typ, sev, title, desc, rec], start=1):
        c = ws5.cell(row=ri, column=ci, value=val)
        c.alignment = align()
        c.border = border_thin()
        if ci == 2 and typ in type_colors:
            bg, fg = type_colors[typ]
            c.fill = fill(bg); c.font = font(bold=True, color=fg, size=10)
            c.alignment = align("center")
        elif ci == 3 and sev in sev_colors:
            bg, fg = sev_colors[sev]
            c.fill = fill(bg); c.font = font(bold=True, color=fg, size=10)
            c.alignment = align("center")
        else:
            c.fill = fill(CLR["alt_row"] if alt else CLR["white"])
            c.font = font(size=10)


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 6 — Recommendations
# ─────────────────────────────────────────────────────────────────────────────
ws6 = wb.create_sheet("Recommendations")
ws6.sheet_view.showGridLines = False
ws6.column_dimensions["A"].width = 6
ws6.column_dimensions["B"].width = 22
ws6.column_dimensions["C"].width = 14
ws6.column_dimensions["D"].width = 55
ws6.column_dimensions["E"].width = 50

ws6.merge_cells("A1:E1")
c = ws6["A1"]
c.value = "Recommendations — Closing the Coverage Gap"
c.fill = fill(CLR["header_bg"])
c.font = font(bold=True, color="FFFFFF", size=13)
c.alignment = align("center")
ws6.row_dimensions[1].height = 28

write_header_row(ws6, 2, ["#", "Area", "Priority", "Recommendation", "Expected Outcome"])

recs = [
    (1, "Acronym Rules",            "High",
     "Consolidate the 200+ fragmented acronym rules into a single canonical set with a decision tree (abstract, first use, plural, possessive, redefinition).",
     "Eliminates the top source of discrepancies; produces a clean, implementable ruleset."),
    (2, "Lookup Tables",            "High",
     "Ingest structured lookup tables (Trademarks, Units, Statistical Terms, Organizations) as CSV/Excel and link them to extracted rules rather than trying to extract them via LLM.",
     "Captures ~400+ missed term-level requirements; enables deterministic lookup checks."),
    (3, "Sub-journal Differentiation", "High",
     "Add a 'journal applicability' dimension to the extraction pipeline so rules can be tagged per sub-journal (Science, Sci. Immunol., Sci. Robot., etc.).",
     "Aligns tool output with manual ruleset's journal-level granularity."),
    (4, "Serial Comma Policy",      "Medium",
     "Add explicit serial comma rule (the tool already flagged this as a gap). Confirm AAAS stance and hardcode as a deterministic rule.",
     "Closes Gap #6 from the tool's own discrepancy report."),
    (5, "CMOS Table Ingestion",     "Medium",
     "Manually import the CMOS_table07-hyphens data as a supplementary source. It is not an AAAS PDF but is part of the editorial workflow.",
     "Adds 117 hyphenation rules currently entirely absent."),
    (6, "Punctuation Detail Rules", "Medium",
     "Extend punctuation extraction to cover apostrophe sub-rules (possessive singular/plural), appositives, and the contraction ban.",
     "Closes the partial gap in the Punctuation sheet."),
    (7, "Figures Detail Rules",     "Low",
     "Add rules for: Insight no-number figures, Scheme→Figure relabeling, lowercase citation from reference.",
     "Addresses 3 specific missed rules in the Figures sheet."),
    (8, "Author Affiliations",      "Low",
     "Add rules for: single-author email in affiliation, co-senior author prohibition.",
     "Closes 2 specific missed rules in Author Affiliations sheet."),
    (9, "Author Queries",           "Low",
     "Keep Queries sheet as a separate process artifact — it is out of scope for PDF extraction. Document it as a supplementary workflow component.",
     "Sets correct scope expectations; avoids confusing process docs with style rules."),
    (10, "Automation Reassessment", "Medium",
     "Review the 232 rules currently tagged 'Needs Human Review' against the manual ruleset; many may be downgraded to deterministic once lookup tables are integrated.",
     "Increases automation coverage from ~35% (437 deterministic) toward 50%+."),
]

pri_colors = {"High": ("FFC7CE", "9C0006"), "Medium": ("FFEB9C", "7E4E0C"), "Low": ("E2EFDA", "375623")}

for ri, (num, area, pri, rec, outcome) in enumerate(recs, start=3):
    ws6.row_dimensions[ri].height = 55
    alt = ri % 2 == 0
    bg = CLR["alt_row"] if alt else CLR["white"]
    for ci, val in enumerate([num, area, pri, rec, outcome], start=1):
        c = ws6.cell(row=ri, column=ci, value=val)
        c.alignment = align()
        c.border = border_thin()
        if ci == 3 and pri in pri_colors:
            pbg, pfg = pri_colors[pri]
            c.fill = fill(pbg); c.font = font(bold=True, color=pfg, size=10)
            c.alignment = align("center")
        else:
            c.fill = fill(bg); c.font = font(size=10)

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
out_path = "AAAS_Gap_Analysis.xlsx"
wb.save(out_path)
print(f"Saved: {out_path}")
