import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_filename = r'C:\Users\HP\osintneoai\FEDERAL_SUBMISSION_DOSSIER_2026.pdf'

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Title'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0f172a'),
    alignment=0
)

h1_style = ParagraphStyle(
    'Heading1_Custom',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#1e293b'),
    spaceBefore=12,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'BodyText_Custom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#334155'),
    spaceBefore=4,
    spaceAfter=4
)

bold_body = ParagraphStyle(
    'BoldBody_Custom',
    parent=body_style,
    fontName='Helvetica-Bold'
)

story = []

# Title & Subtitle
story.append(Paragraph("FORMAL CRIMINAL REFERRAL & QUI TAM EVIDENTIARY DOSSIER", title_style))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Target Court Docket:</b> U.S. District Court, CACD — Case No. 8:26-cv-00348-JWH-ADS", body_style))
story.append(Paragraph("<b>Relator / 2022 Whistleblower:</b> Anthony Michael DiMarcello III", body_style))
story.append(Paragraph("<b>Date of Submission:</b> August 07, 2026", body_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceBefore=2, spaceAfter=10))

# Section 1
story.append(Paragraph("I. EXECUTIVE SUMMARY & FORMAL WHISTLEBLOWER DEMAND", h1_style))
story.append(Paragraph("As the original 2022 whistleblower and relator, Anthony Michael DiMarcello III hereby requests an immediate federal investigation into False Claims Act violations (31 U.S.C. § 3729), procurement fraud, civil RICO conspiracy (18 U.S.C. § 1962), and imminent threats to public health under the Clean Air Act (42 U.S.C. § 7412) and CERCLA § 106.", body_style))

story.append(Spacer(1, 6))

# Section 2: Three Smoking Guns
story.append(Paragraph("II. THREE EXPLOSIVE SMOKING GUN EVIDENTIARY PILLARS", h1_style))

pillar_data = [
    [Paragraph("<b>Evidence Pillar</b>", bold_body), Paragraph("<b>Factual Findings & Statutory Violations</b>", bold_body)],
    [
        Paragraph("<b>1. Subsurface Toxins & Aerosolization</b>", body_style),
        Paragraph("Hexavalent Chromium (Cr-VI) present at <b>49 times the legal safety limit</b> at 17642 Beach Blvd. Daily mechanical maintenance practices aerosolize toxic airborne particulates, creating acute inhalation hazards for shelter residents and staff (Clean Air Act & CERCLA § 106).", body_style)
    ],
    [
        Paragraph("<b>2. EEC Environmental Kickback (Contract 20-9204)</b>", body_style),
        Paragraph("EEC Environmental issued technical sign-off facilitating fraudulent OCHCA Closure #20IC002 (omitting active northward plume flow confirmed by LightBox EDR Aquiflow IDs 26 & 27), and was awarded Contract 20-9204 for construction oversight <b>exactly 10 days later</b> (41 U.S.C. § 8702 & 18 U.S.C. § 1343).", body_style)
    ],
    [
        Paragraph("<b>3. City Attorney Michael Gates Scienter</b>", body_style),
        Paragraph("City of Huntington Beach possessed documented written knowledge of the toxic plume since the 2015 property acquisition. City Attorney Michael E. Gates knowingly approved Contract 20-9204 with full prior knowledge, establishing statutory FCA <i>scienter</i> (31 U.S.C. § 3729) and RICO conspiracy (18 U.S.C. § 1962).", body_style)
    ]
]

t = Table(pillar_data, colWidths=[150, 382])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
]))

story.append(t)
story.append(Spacer(1, 10))

# Section 3: LightBox RE API Integration
story.append(Paragraph("III. LIGHTBOX RE API INTEGRATION & ENTERPRISE METADATA", h1_style))

lightbox_data = [
    [Paragraph("<b>Attribute</b>", bold_body), Paragraph("<b>Value / Status</b>", bold_body)],
    [Paragraph("App Display Name", body_style), Paragraph("lightbox", body_style)],
    [Paragraph("Registered App Owner", body_style), Paragraph("drillingoilandgasinfo@gmail.com", body_style)],
    [Paragraph("Product Name", body_style), Paragraph("LightBox API's Evaluation (Approved)", body_style)],
    [Paragraph("Consumer Key", body_style), Paragraph("H81DuBbxyMlfmKIGzVeQ8L7vbUG56x3xwS6yorMK5R5trpUc", body_style)],
    [Paragraph("Consumer Secret", body_style), Paragraph("BRBznu9YHBT6mVwAy3mxV5lzuNTB8aAkx1X435NeKDBwZ6AI8liPVsKb9Zp2w3Bk", body_style)],
    [Paragraph("Credential Expiry", body_style), Paragraph("July 20, 2026 (Credential 1 Approved)", body_style)],
    [Paragraph("Custom Attributes", body_style), Paragraph("No custom attributes (Callback URL: N/A)", body_style)]
]

t2 = Table(lightbox_data, colWidths=[150, 382])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
]))

story.append(t2)
story.append(Spacer(1, 10))

# Section 4: Signature
story.append(Paragraph("IV. RELATOR VERIFICATION & FORMAL SIGNATURE", h1_style))
story.append(Paragraph("I declare under penalty of perjury under the laws of the United States of America that the foregoing statements and evidentiary pillars are true and correct.", body_style))
story.append(Spacer(1, 12))
story.append(Paragraph("<b>Anthony Michael DiMarcello III</b>", bold_body))
story.append(Paragraph("Relator / 2022 Whistleblower", body_style))
story.append(Paragraph("U.S. District Court, CACD — Case No. 8:26-cv-00348-JWH-ADS", body_style))
story.append(Paragraph("GitHub Central Repository: <u>https://github.com/Tonypost949/OsintNeoAi</u>", body_style))

doc.build(story)
print(f"PDF built successfully at: {pdf_filename}")
