"""
Azure Health — branded PDF builder
Produces three documents:
  1. azure-health-session-prep.pdf
  2. azure-health-consent.pdf
  3. azure-health-intake.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle,
    KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
AZURE      = HexColor("#3E6F8E")   # Deep Azure  — headings
SLATE      = HexColor("#263746")   # Ink Slate   — body text
CREAM      = HexColor("#FAF6EF")   # Cream       — background
SKY        = HexColor("#DCEBF2")   # Soft Sky    — section shading
BONE       = HexColor("#E3DBC9")   # Bone        — dividers

# ---------------------------------------------------------------------------
# Font registration — fall back to Helvetica if custom fonts unavailable
# ---------------------------------------------------------------------------
BODY_FONT   = "Helvetica"
BOLD_FONT   = "Helvetica-Bold"
ITALIC_FONT = "Helvetica-Oblique"

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Shared header / footer canvas callback
# ---------------------------------------------------------------------------
FOOTER_TEXT = (
    "Whole-Person Care \u00b7 Deep Healing \u00b7 Lasting Change"
    "  |  hello@azurehealth.com  |  azurehealthco.com"
)


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    margin = 0.75 * inch

    # ---- header ----
    canvas.setFont(BOLD_FONT, 9)
    canvas.setFillColor(AZURE)
    canvas.drawString(margin, h - 0.45 * inch, "AZURE HEALTH")

    page_label = f"Page {doc.page}"
    canvas.setFont(BODY_FONT, 9)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(w - margin, h - 0.45 * inch, page_label)

    # thin Bone rule below header
    canvas.setStrokeColor(BONE)
    canvas.setLineWidth(0.75)
    canvas.line(margin, h - 0.55 * inch, w - margin, h - 0.55 * inch)

    # ---- footer ----
    canvas.setFont(BODY_FONT, 7.5)
    canvas.setFillColor(SLATE)
    canvas.drawCentredString(w / 2, 0.40 * inch, FOOTER_TEXT)

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------
def _styles():
    """Return a dict of named ParagraphStyles."""
    s = {}

    s["h1"] = ParagraphStyle(
        "h1",
        fontName=BOLD_FONT,
        fontSize=15,
        textColor=AZURE,
        spaceAfter=6,
        spaceBefore=14,
        leading=19,
    )
    s["h2"] = ParagraphStyle(
        "h2",
        fontName=BOLD_FONT,
        fontSize=11.5,
        textColor=AZURE,
        spaceAfter=4,
        spaceBefore=10,
        leading=15,
    )
    s["h3"] = ParagraphStyle(
        "h3",
        fontName=BOLD_FONT,
        fontSize=10,
        textColor=SLATE,
        spaceAfter=3,
        spaceBefore=8,
        leading=13,
    )
    s["body"] = ParagraphStyle(
        "body",
        fontName=BODY_FONT,
        fontSize=9.5,
        textColor=SLATE,
        spaceAfter=4,
        leading=14,
    )
    s["body_italic"] = ParagraphStyle(
        "body_italic",
        fontName=ITALIC_FONT,
        fontSize=9.5,
        textColor=SLATE,
        spaceAfter=4,
        leading=14,
    )
    s["small"] = ParagraphStyle(
        "small",
        fontName=BODY_FONT,
        fontSize=8.5,
        textColor=SLATE,
        spaceAfter=3,
        leading=12,
    )
    s["bullet"] = ParagraphStyle(
        "bullet",
        fontName=BODY_FONT,
        fontSize=9.5,
        textColor=SLATE,
        spaceAfter=3,
        leading=14,
        leftIndent=14,
        bulletIndent=0,
        bulletFontName=BODY_FONT,
        bulletFontSize=9.5,
        bulletColor=AZURE,
    )
    s["note"] = ParagraphStyle(
        "note",
        fontName=ITALIC_FONT,
        fontSize=9,
        textColor=SLATE,
        spaceAfter=6,
        leading=13,
        backColor=SKY,
        borderPad=6,
    )
    s["center"] = ParagraphStyle(
        "center",
        fontName=BODY_FONT,
        fontSize=9.5,
        textColor=SLATE,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=14,
    )
    s["field_label"] = ParagraphStyle(
        "field_label",
        fontName=BOLD_FONT,
        fontSize=8.5,
        textColor=SLATE,
        spaceAfter=1,
        leading=11,
    )
    s["title"] = ParagraphStyle(
        "title",
        fontName=BOLD_FONT,
        fontSize=20,
        textColor=AZURE,
        spaceAfter=4,
        spaceBefore=4,
        leading=24,
        alignment=TA_CENTER,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle",
        fontName=ITALIC_FONT,
        fontSize=11,
        textColor=SLATE,
        spaceAfter=10,
        leading=14,
        alignment=TA_CENTER,
    )
    return s


def divider(story, color=BONE, thickness=0.75, space_before=8, space_after=8):
    story.append(Spacer(1, space_before))
    story.append(HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=space_after))


def section_header(story, text, st):
    story.append(Spacer(1, 4))
    story.append(Paragraph(text, st["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BONE, spaceAfter=4))


def bullet_item(story, text, st):
    story.append(Paragraph(f"\u2022\u2003{text}", st["bullet"]))


def checkbox_item(story, text, st):
    story.append(Paragraph(f"\u2610\u2003{text}", st["bullet"]))


def _doc(filename, title_str):
    path = os.path.join(BASE_DIR, filename)
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
        title=title_str,
        author="Amanda Blanchet, PA-C — Azure Health",
    )
    return doc, path


def underline_field(label, width="3in"):
    """Return a two-cell table: bold label on left, underline on right."""
    return Table(
        [[label, ""]],
        colWidths=[None, width],
        style=TableStyle([
            ("FONTNAME", (0, 0), (0, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), SLATE),
            ("LINEBELOW", (1, 0), (1, 0), 0.5, SLATE),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]),
    )


# ===========================================================================
# PDF 1 — Preparing for Your Session
# ===========================================================================
def build_session_prep():
    st = _styles()
    doc, path = _doc("azure-health-session-prep.pdf", "Preparing for Your Session — Azure Health")
    story = []

    # Title block
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Preparing for Your Session", st["title"]))
    story.append(Paragraph("Azure Health  |  Amanda Blanchet, PA-C, Reiki Master", st["subtitle"]))
    divider(story, color=AZURE, thickness=1.5, space_before=2, space_after=10)

    # Intro
    story.append(Paragraph(
        "Thank you for choosing to work together. To support the deepest possible experience, "
        "a little preparation goes a long way. The following guidelines will help ensure your "
        "space and body are ready to receive this work.",
        st["body_italic"]
    ))
    story.append(Spacer(1, 6))

    # --- Your Space ---
    section_header(story, "Your Space", st)
    items = [
        "A quiet room where you will not be disturbed",
        "Approximately 7\u00d73 feet of clear floor space for a massage table (Amanda will bring this)",
        "Two comfortable chairs for an initial conversation",
        "The ability to dim the lights or draw curtains",
        "A blanket within reach",
        "Room temperature set to your comfort \u2014 sessions involve lying still, so slightly warmer is better",
    ]
    for item in items:
        bullet_item(story, item, st)

    # --- What to Wear ---
    section_header(story, "What to Wear", st)
    for item in [
        "Comfortable, loose-fitting clothing",
        "Minimal jewelry \u2014 you are welcome to remove it upon arrival",
    ]:
        bullet_item(story, item, st)

    # --- Before Your Session ---
    section_header(story, "Before Your Session", st)
    before_items = [
        "Avoid all alcohol and recreational drugs for at least 72 hours prior",
        "No pets in the session area during your appointment",
        "Ideally, arrange for other household members to be out of the home, or in a separate, quiet area",
        "Hydrate well the day before and morning of your session",
        "Eat a light meal 2\u20134 hours before \u2014 do not arrive fasting or overly full",
        "Avoid caffeine for at least 2 hours prior",
        "Plan for rest and quiet time following the session; avoid scheduling demanding activities afterward",
    ]
    for item in before_items:
        bullet_item(story, item, st)

    story.append(Spacer(1, 8))

    # Sub-section: Ketamine
    ketamine_content = [
        Paragraph("If Ketamine Is Part of Your Session", st["h3"]),
    ]
    ketamine_items = [
        "No food or drink (except water) for 90 minutes before your session",
        "The 72-hour alcohol and drug restriction above applies and is especially important",
        "Plan to rest for the remainder of the day in a calm, comfortable environment",
    ]
    for item in ketamine_items:
        ketamine_content.append(Paragraph(f"\u2022\u2003{item}", st["bullet"]))

    # Shaded box for ketamine sub-section
    table = Table(
        [[ketamine_content]],
        colWidths=[6.75 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SKY),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("ROUNDEDCORNERS", [4]),
        ]),
    )
    story.append(KeepTogether(table))

    # --- Mentally and Emotionally ---
    section_header(story, "Mentally and Emotionally", st)
    mental_items = [
        "Consider spending a few quiet minutes before the session \u2014 journaling, breathing, or simply sitting with what you are hoping to release or receive",
        "Set a simple intention, even just a word or feeling",
        "Silence your phone before Amanda arrives",
        "This time is yours. There is nothing to perform or produce.",
    ]
    for item in mental_items:
        bullet_item(story, item, st)

    # --- Questions ---
    section_header(story, "Questions", st)
    story.append(Paragraph(
        "If anything feels unclear or you have concerns before your session, please reach out.",
        st["body"]
    ))
    story.append(Paragraph(
        "<link href='mailto:hello@azurehealth.com'><u>hello@azurehealth.com</u></link>",
        st["body"]
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"  Created: {path}")


# ===========================================================================
# PDF 2 — Consent to Treatment
# ===========================================================================
def build_consent():
    st = _styles()
    doc, path = _doc("azure-health-consent.pdf", "Consent to Treatment — Azure Health")
    story = []

    # Title block
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Consent to Treatment", st["title"]))
    story.append(Paragraph("Azure Health  |  Amanda Blanchet, PA-C", st["subtitle"]))
    divider(story, color=AZURE, thickness=1.5, space_before=2, space_after=10)

    # Client header fields
    header_data = [[
        Paragraph("<b>Client Name:</b> ___________________________", st["small"]),
        Paragraph("<b>Date of Birth:</b> ___________________", st["small"]),
        Paragraph("<b>Date:</b> ___________________", st["small"]),
    ]]
    header_table = Table(
        header_data,
        colWidths=[2.8 * inch, 2.05 * inch, 1.9 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, -1), SKY),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, BONE),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, BONE),
        ]),
    )
    story.append(header_table)
    story.append(Spacer(1, 10))

    def numbered_section(num, title_text):
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"{num}.  {title_text}", st["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BONE, spaceAfter=4))

    # 1. Nature of Services
    numbered_section("1", "Nature of Services")
    story.append(Paragraph(
        "Azure Health provides integrative health services including energy-based healing, light hands-on work, "
        "nervous system regulation support, and where clinically appropriate, ketamine-assisted therapy. "
        "Sessions are conducted by Amanda Blanchet, PA-C.",
        st["body"]
    ))

    # 2. Acknowledgment of Integrative Care
    numbered_section("2", "Acknowledgment of Integrative Care")
    story.append(Paragraph(
        "I understand that services provided through Azure Health are integrative in nature and are not a "
        "substitute for conventional medical or psychiatric care.",
        st["body"]
    ))

    # 3. Consent to Treatment
    numbered_section("3", "Consent to Treatment")
    story.append(Paragraph(
        "I consent to receive the services described above, including light hands-on energy work over clothing. "
        "I understand I may withdraw consent at any time.",
        st["body"]
    ))

    # 4. Ketamine (if applicable)
    numbered_section("4", "Ketamine (if applicable)")
    story.append(Paragraph(
        "I understand that ketamine is a controlled substance used in a medically supervised context. "
        "I have disclosed my full medical history. I understand the risks include temporary perceptual changes, "
        "elevated heart rate or blood pressure, nausea, and in rare cases more serious effects.",
        st["body"]
    ))

    # 5. Confidentiality
    numbered_section("5", "Confidentiality")
    story.append(Paragraph(
        "My health information will be kept confidential except as required by law.",
        st["body"]
    ))

    # 6. Emergency Contact
    numbered_section("6", "Emergency Contact")
    ec_data = [[
        Paragraph("<b>Name:</b> _______________________", st["small"]),
        Paragraph("<b>Relationship:</b> _______________________", st["small"]),
        Paragraph("<b>Phone:</b> _______________________", st["small"]),
    ]]
    ec_table = Table(
        ec_data,
        colWidths=[2.3 * inch, 2.3 * inch, 2.15 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]),
    )
    story.append(ec_table)

    # 7. Signature block
    numbered_section("7", "Signature")
    story.append(Spacer(1, 6))

    sig_data = [
        [Paragraph("<b>Client Name (print):</b>", st["small"]),
         Paragraph("_______________________________", st["small"]), "", ""],
        ["", "", "", ""],
        [Paragraph("<b>Client Signature:</b>", st["small"]),
         Paragraph("_________________________________", st["small"]),
         Paragraph("<b>Date:</b>", st["small"]),
         Paragraph("_______________", st["small"])],
        ["", "", "", ""],
        [Paragraph("<b>Practitioner Signature:</b>", st["small"]),
         Paragraph("___________________________", st["small"]),
         Paragraph("<b>Date:</b>", st["small"]),
         Paragraph("_______________", st["small"])],
        ["", "", "", ""],
        ["", Paragraph("<i>Amanda Blanchet, PA-C</i>", st["small"]), "", ""],
    ]
    sig_table = Table(
        sig_data,
        colWidths=[1.6 * inch, 3.0 * inch, 0.7 * inch, 1.45 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]),
    )
    story.append(sig_table)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"  Created: {path}")


# ===========================================================================
# PDF 3 — Medical Intake Form
# ===========================================================================
def build_intake():
    st = _styles()
    doc, path = _doc("azure-health-intake.pdf", "Medical Intake Form — Azure Health")
    story = []

    # Title block
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Medical Intake Form", st["title"]))
    story.append(Paragraph("Azure Health  |  Amanda Blanchet, PA-C, Reiki Master", st["subtitle"]))
    divider(story, color=AZURE, thickness=1.5, space_before=2, space_after=6)

    story.append(Paragraph(
        "This form is confidential and used solely to support your care. "
        "Please complete as thoroughly as possible.",
        st["note"]
    ))
    story.append(Spacer(1, 8))

    def sec(num, title_text):
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Section {num}: {title_text}", st["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BONE, spaceAfter=4))

    def field_row(*fields):
        """fields = list of (label, underline_width_fraction) tuples or plain strings."""
        cells = []
        for f in fields:
            if isinstance(f, tuple):
                label, width = f
            else:
                label, width = f, 2.0
            cells.append(Paragraph(f"<b>{label}</b> {'_' * int(width * 8)}", st["small"]))
        col_w = 6.75 * inch / len(cells)
        t = Table(
            [cells],
            colWidths=[col_w] * len(cells),
            style=TableStyle([
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]),
        )
        story.append(t)

    # --- Section 1: Personal Information ---
    sec("1", "Personal Information")
    field_row(("Full Name:", 2.5), ("Date of Birth:", 1.5), ("Date:", 1.2))
    field_row(("Address:", 5.5),)
    field_row(("City:", 2.5), ("State:", 1.0), ("Zip:", 1.0))
    field_row(("Phone:", 2.0), ("Email:", 2.5))
    field_row(("Emergency Contact Name:", 2.0), ("Relationship:", 1.5), ("Phone:", 1.5))
    field_row(("Preferred Pharmacy (name & location):", 3.5),)

    # --- Section 2: PCP ---
    sec("2", "Primary Care Provider")
    field_row(("PCP Name:", 2.0), ("Practice / Clinic:", 2.0), ("Phone:", 1.5))
    field_row(("Date of Last Visit:", 2.5),)

    # --- Section 3: Medical History ---
    sec("3", "Medical History")
    story.append(Paragraph("Please check any conditions that apply, past or present:", st["body"]))
    story.append(Spacer(1, 4))

    conditions_left = [
        "Hypertension / High blood pressure",
        "Diabetes or pre-diabetes",
        "Thyroid disorder",
        "Autoimmune condition",
        "Chronic pain",
        "Cancer (current or history)",
        "Neurological condition",
        "Respiratory condition (asthma, COPD, etc.)",
    ]
    conditions_right = [
        "Cardiac condition or arrhythmia",
        "Kidney disease",
        "Liver disease",
        "Chronic fatigue",
        "Migraines or frequent headaches",
        "Sleep disorder",
        "Other",
    ]

    max_rows = max(len(conditions_left), len(conditions_right))
    cond_data = []
    for i in range(max_rows):
        left = Paragraph(f"\u2610  {conditions_left[i]}", st["small"]) if i < len(conditions_left) else Paragraph("", st["small"])
        right = Paragraph(f"\u2610  {conditions_right[i]}", st["small"]) if i < len(conditions_right) else Paragraph("", st["small"])
        cond_data.append([left, right])

    cond_table = Table(
        cond_data,
        colWidths=[3.375 * inch, 3.375 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), SKY),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, SKY]),
            ("GRID", (0, 0), (-1, -1), 0.3, BONE),
        ]),
    )
    story.append(cond_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Please describe any checked conditions:", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))

    # --- Section 4: Surgical History ---
    sec("4", "Surgical History")
    story.append(Paragraph("List any past surgeries and approximate dates:", st["body"]))
    for _ in range(3):
        story.append(Paragraph("____________________________________________________________________________________", st["small"]))

    # --- Section 5: Current Medications ---
    sec("5", "Current Medications")
    med_header = [
        Paragraph("<b>Medication Name</b>", st["small"]),
        Paragraph("<b>Dose</b>", st["small"]),
        Paragraph("<b>Frequency</b>", st["small"]),
        Paragraph("<b>Prescribing Provider</b>", st["small"]),
    ]
    med_rows = [med_header]
    for _ in range(8):
        med_rows.append([Paragraph("", st["small"])] * 4)

    med_table = Table(
        med_rows,
        colWidths=[2.4 * inch, 1.0 * inch, 1.4 * inch, 1.95 * inch],
        rowHeights=[None] + [18] * 8,
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZURE),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.4, BONE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, SKY]),
        ]),
    )
    story.append(med_table)

    # --- Section 6: Allergies ---
    sec("6", "Allergies")
    story.append(Paragraph("<b>Medication allergies and reactions:</b>", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Environmental or other allergies:</b>", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))

    # --- Section 7: Psychiatric and Mental Health ---
    sec("7", "Psychiatric and Mental Health History")
    story.append(Paragraph("<b>Current or past mental health diagnoses:</b>", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Current mental health provider (if any):</b>", st["small"]))
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "\u2610  No     \u2610  Yes \u2014 please describe: ____________________________"
        "          <b>Prior psychiatric hospitalizations:</b>",
        st["small"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "\u2610  No     \u2610  Yes \u2014 please describe: ____________________________"
        "          <b>Prior suicide attempt(s):</b>",
        st["small"]
    ))

    # --- Section 8: Specific Screening ---
    sec("8", "Specific Screening")
    story.append(Paragraph("Please indicate if any of the following apply to you, past or present:", st["body"]))
    story.append(Spacer(1, 4))

    screening_left = [
        "Seizure disorder",
        "Uncontrolled high blood pressure",
        "Significant heart disease or arrhythmia",
        "Liver disease",
        "Schizophrenia or schizoaffective disorder",
        "Active or recent psychosis",
    ]
    screening_right = [
        "History of mania or bipolar disorder",
        "Frequent or heavy alcohol use",
        "Active substance misuse",
        "Current pregnancy or breastfeeding",
        "Dissociative disorder",
        "PTSD",
    ]
    screen_data = []
    for i in range(max(len(screening_left), len(screening_right))):
        left = Paragraph(f"\u2610  {screening_left[i]}", st["small"]) if i < len(screening_left) else Paragraph("", st["small"])
        right = Paragraph(f"\u2610  {screening_right[i]}", st["small"]) if i < len(screening_right) else Paragraph("", st["small"])
        screen_data.append([left, right])

    screen_table = Table(
        screen_data,
        colWidths=[3.375 * inch, 3.375 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), SKY),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, SKY]),
            ("GRID", (0, 0), (-1, -1), 0.3, BONE),
        ]),
    )
    story.append(screen_table)

    # --- Section 9: GAD-7 ---
    sec("9", "GAD-7 \u2014 Generalized Anxiety")
    story.append(Paragraph(
        "Over the last two weeks, how often have you been bothered by the following?",
        st["body"]
    ))
    story.append(Paragraph(
        "<b>Scale:</b>  0 = Not at all  |  1 = Several days  |  2 = More than half the days  |  3 = Nearly every day",
        st["small"]
    ))
    story.append(Spacer(1, 4))

    gad_items = [
        "Feeling nervous, anxious, or on edge",
        "Not being able to stop or control worrying",
        "Worrying too much about different things",
        "Trouble relaxing",
        "Being so restless that it is hard to sit still",
        "Becoming easily annoyed or irritable",
        "Feeling afraid as if something awful might happen",
    ]

    gad_header = [
        Paragraph("<b>#</b>", st["small"]),
        Paragraph("<b>Item</b>", st["small"]),
        Paragraph("<b>0</b>", st["small"]),
        Paragraph("<b>1</b>", st["small"]),
        Paragraph("<b>2</b>", st["small"]),
        Paragraph("<b>3</b>", st["small"]),
    ]
    gad_rows = [gad_header]
    for i, item in enumerate(gad_items):
        gad_rows.append([
            Paragraph(str(i + 1), st["small"]),
            Paragraph(item, st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
        ])
    gad_rows.append([
        Paragraph("<b>Score:</b>", st["small"]),
        Paragraph("____   <b>Scoring:</b>  0\u20134 Minimal  |  5\u20139 Mild  |  10\u201314 Moderate  |  15\u201321 Severe", st["small"]),
        "", "", "", "",
    ])

    gad_table = Table(
        gad_rows,
        colWidths=[0.3 * inch, 4.35 * inch, 0.525 * inch, 0.525 * inch, 0.525 * inch, 0.525 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZURE),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -2), 0.4, BONE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [CREAM, SKY]),
            ("SPAN", (1, len(gad_rows) - 1), (-1, len(gad_rows) - 1)),
            ("BACKGROUND", (0, len(gad_rows) - 1), (-1, len(gad_rows) - 1), SKY),
        ]),
    )
    story.append(gad_table)

    # --- Section 10: PHQ-9 ---
    sec("10", "PHQ-9 \u2014 Depression Screening")
    story.append(Paragraph(
        "Over the last two weeks, how often have you been bothered by any of the following?",
        st["body"]
    ))
    story.append(Paragraph(
        "<b>Scale:</b>  0 = Not at all  |  1 = Several days  |  2 = More than half the days  |  3 = Nearly every day",
        st["small"]
    ))
    story.append(Spacer(1, 4))

    phq_items = [
        "Little interest or pleasure in doing things",
        "Feeling down, depressed, or hopeless",
        "Trouble falling or staying asleep, or sleeping too much",
        "Feeling tired or having little energy",
        "Poor appetite or overeating",
        "Feeling bad about yourself \u2014 or that you are a failure or have let yourself or your family down",
        "Trouble concentrating on things, such as reading the newspaper or watching television",
        "Moving or speaking so slowly that other people could have noticed. Or the opposite \u2014 being so fidgety or restless that you have been moving around a lot more than usual",
        "Thoughts that you would be better off dead, or of hurting yourself in some way",
    ]

    phq_header = [
        Paragraph("<b>#</b>", st["small"]),
        Paragraph("<b>Item</b>", st["small"]),
        Paragraph("<b>0</b>", st["small"]),
        Paragraph("<b>1</b>", st["small"]),
        Paragraph("<b>2</b>", st["small"]),
        Paragraph("<b>3</b>", st["small"]),
    ]
    phq_rows = [phq_header]
    for i, item in enumerate(phq_items):
        phq_rows.append([
            Paragraph(str(i + 1), st["small"]),
            Paragraph(item, st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
        ])
    phq_rows.append([
        Paragraph("<b>Score:</b>", st["small"]),
        Paragraph(
            "____   <b>Scoring:</b>  0\u20134 None  |  5\u20139 Mild  |  10\u201314 Moderate  |  15\u201319 Mod. Severe  |  20\u201327 Severe",
            st["small"]
        ),
        "", "", "", "",
    ])

    phq_table = Table(
        phq_rows,
        colWidths=[0.3 * inch, 4.35 * inch, 0.525 * inch, 0.525 * inch, 0.525 * inch, 0.525 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZURE),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -2), 0.4, BONE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [CREAM, SKY]),
            ("SPAN", (1, len(phq_rows) - 1), (-1, len(phq_rows) - 1)),
            ("BACKGROUND", (0, len(phq_rows) - 1), (-1, len(phq_rows) - 1), SKY),
        ]),
    )
    story.append(phq_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Item 10:</b> If you checked off any problems, how difficult have these problems made it for you to "
        "do your work, take care of things at home, or get along with other people?",
        st["small"]
    ))
    story.append(Paragraph(
        "\u2610  Not difficult at all     \u2610  Somewhat difficult     \u2610  Very difficult     \u2610  Extremely difficult",
        st["small"]
    ))

    # --- Section 11: Mood Episode Screening ---
    sec("11", "Mood Episode Screening")
    story.append(Paragraph(
        "Has there ever been a period of time when you were not your usual self and\u2026",
        st["body"]
    ))
    story.append(Spacer(1, 4))

    mood_items = [
        "You felt so good or so hyper that other people thought you were not your normal self, or you were so hyped up that you got into trouble?",
        "You were so irritable that you shouted at people or started fights or arguments?",
        "You felt much more self-confident than usual?",
        "You got much less sleep than usual and found you didn\u2019t really miss it?",
        "You were much more talkative or spoke much faster than usual?",
        "Thoughts raced through your head or you couldn\u2019t slow your mind down?",
        "You were so easily distracted by things around you that you had trouble concentrating or staying on task?",
        "You had much more energy than usual?",
        "You were much more active or did many more things than usual?",
        "You were much more social or outgoing than usual \u2014 for example, you telephoned friends in the middle of the night?",
        "You were much more interested in sex than usual?",
        "You did things that were unusual for you or that other people might have seen as foolish, risky, or out of control?",
        "Spending money got you or your family into trouble?",
    ]

    mood_header = [
        Paragraph("<b>#</b>", st["small"]),
        Paragraph("<b>Item</b>", st["small"]),
        Paragraph("<b>Yes</b>", st["small"]),
        Paragraph("<b>No</b>", st["small"]),
    ]
    mood_rows = [mood_header]
    for i, item in enumerate(mood_items):
        mood_rows.append([
            Paragraph(str(i + 1), st["small"]),
            Paragraph(item, st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
        ])

    mood_table = Table(
        mood_rows,
        colWidths=[0.3 * inch, 5.15 * inch, 0.65 * inch, 0.65 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZURE),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.4, BONE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, SKY]),
        ]),
    )
    story.append(mood_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>If you answered YES to more than one item above:</b>", st["small"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Did several of these occur during the same period of time?  \u2610  Yes  \u2610  No",
        st["small"]
    ))
    story.append(Paragraph(
        "How much of a problem did this cause?  \u2610  No problem  \u2610  Minor problem  \u2610  Moderate problem  \u2610  Serious problem",
        st["small"]
    ))
    story.append(Paragraph(
        "Have any blood relatives experienced similar episodes or been diagnosed with bipolar disorder?  \u2610  Yes  \u2610  No",
        st["small"]
    ))

    # --- Section 12: Substance Use ---
    sec("12", "Substance Use")
    sub_header = [
        Paragraph("<b>Substance</b>", st["small"]),
        Paragraph("<b>Current Use</b>", st["small"]),
        Paragraph("<b>Past Use</b>", st["small"]),
        Paragraph("<b>Never</b>", st["small"]),
        Paragraph("<b>Notes</b>", st["small"]),
    ]
    sub_rows_data = [
        ("Alcohol", "If current, approximate drinks per week: ______"),
        ("Cannabis", "If current, approximate frequency: ______"),
        ("Tobacco / nicotine", ""),
        ("Other substances", ""),
    ]
    sub_rows = [sub_header]
    for substance, note in sub_rows_data:
        sub_rows.append([
            Paragraph(substance, st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph("\u2610", st["small"]),
            Paragraph(note, st["small"]),
        ])

    sub_table = Table(
        sub_rows,
        colWidths=[1.4 * inch, 0.9 * inch, 0.9 * inch, 0.7 * inch, 2.85 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZURE),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ALIGN", (1, 0), (3, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.4, BONE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, SKY]),
        ]),
    )
    story.append(sub_table)

    # --- Section 13: Reason for Seeking Care ---
    sec("13", "Reason for Seeking Care")
    story.append(Paragraph(
        "What brings you here, and what are you hoping to experience or shift?",
        st["body"]
    ))
    for _ in range(4):
        story.append(Paragraph("____________________________________________________________________________________", st["small"]))

    # --- Section 14: How Did You Hear About Azure Health ---
    sec("14", "How Did You Hear About Azure Health?")
    story.append(Paragraph("____________________________________________________________________________________", st["small"]))

    # --- Section 15: Certification and Signature ---
    sec("15", "Certification and Signature")
    story.append(Paragraph(
        "I certify that the information provided above is accurate and complete to the best of my knowledge. "
        "I understand that withholding or misrepresenting information may affect the safety and "
        "appropriateness of my care.",
        st["body"]
    ))
    story.append(Spacer(1, 8))

    cert_data = [[
        Paragraph("<b>Name (print):</b> ______________________________", st["small"]),
        Paragraph("<b>Date:</b> _______________________", st["small"]),
    ]]
    cert_row1 = Table(
        cert_data,
        colWidths=[4.0 * inch, 2.75 * inch],
        style=TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]),
    )
    story.append(cert_row1)
    story.append(Paragraph("<b>Signature:</b> ________________________________________", st["small"]))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print(f"  Created: {path}")


# ===========================================================================
# Main
# ===========================================================================
if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["session_prep", "consent", "intake"]
    print("Building Azure Health PDFs...")
    if "session_prep" in targets:
        build_session_prep()
    if "consent" in targets:
        build_consent()
    if "intake" in targets:
        build_intake()
    print("Done.")
