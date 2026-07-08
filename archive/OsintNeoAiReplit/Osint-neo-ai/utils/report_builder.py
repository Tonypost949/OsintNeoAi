import sqlite3
import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def build_report(entities, relationships, events, file_scans, title, author, classification="CONFIDENTIAL"):
    """
    Builds a PDF report using reportlab.
    """
    from io import BytesIO
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#00d4ff")
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#00d4ff")
    )

    sub_header_style = ParagraphStyle(
        'SubHeaderStyle',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#c8d8f0")
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#c8d8f0")
    )

    confidential_style = ParagraphStyle(
        'ConfidentialStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.red,
        spaceBefore=20
    )

    elements = []

    # Cover Page
    elements.append(Spacer(1, 100))
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Author: {author}", normal_style))
    elements.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(f"CLASSIFICATION: {classification}", confidential_style))
    elements.append(PageBreak())

    # Executive Summary
    elements.append(Paragraph("Executive Summary", header_style))
    elements.append(Spacer(1, 12))
    
    high_risk_count = len([e for e in entities if e.get('risk_level') == 'High'])
    summary_data = [
        ["Metric", "Value"],
        ["Total Entities Selected", str(len(entities))],
        ["High Risk Entities", str(high_risk_count)],
        ["Relationships Included", str(len(relationships))],
        ["Events Included", str(len(events))],
        ["File Scans Included", str(len(file_scans))]
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e2d50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#0f1628")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1e2d50")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#c8d8f0")),
    ]))
    elements.append(summary_table)
    elements.append(PageBreak())

    # Entities Section
    if entities:
        elements.append(Paragraph("Entities", header_style))
        for entity in entities:
            risk = entity.get('risk_level', 'Unknown')
            risk_color = colors.green
            if risk == 'High': risk_color = colors.red
            elif risk == 'Medium': risk_color = colors.orange
            
            elements.append(Paragraph(f"Entity: {entity.get('label', 'N/A')} ({entity.get('entity_id', 'N/A')})", sub_header_style))
            
            entity_info = [
                ["Field", "Value"],
                ["Type", entity.get('type', 'N/A')],
                ["Category", entity.get('category', 'N/A')],
                ["Risk Level", risk],
                ["Geo Location", entity.get('geo_location', 'N/A')],
                ["Source", entity.get('source', 'N/A')],
                ["Notes", entity.get('notes', 'N/A')]
            ]
            
            t = Table(entity_info, colWidths=[100, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#0f1628")),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#c8d8f0")),
                ('TEXTCOLOR', (1, 3), (1, 3), risk_color), # Risk level color
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))
            
            # Related Relationships for this entity
            entity_label = entity.get('label')
            related_rels = [r for r in relationships if r.get('source_entity') == entity_label or r.get('target_entity') == entity_label]
            if related_rels:
                elements.append(Paragraph("Related Relationships", normal_style))
                rel_data = [["Target/Source", "Type", "Confidence"]]
                for r in related_rels:
                    other = r.get('target_entity') if r.get('source_entity') == entity_label else r.get('source_entity')
                    rel_data.append([other, r.get('relationship_type'), r.get('confidence')])
                
                rt = Table(rel_data, colWidths=[150, 150, 100])
                rt.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e2d50")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#0f1628")),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1e2d50")),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#c8d8f0")),
                ]))
                elements.append(rt)
                elements.append(Spacer(1, 15))
        elements.append(PageBreak())

    # Events Section
    if events:
        elements.append(Paragraph("Events", header_style))
        for event in events:
            event_data = [
                ["Field", "Value"],
                ["ID", event.get('event_id', 'N/A')],
                ["Timestamp", event.get('timestamp', 'N/A')],
                ["Type", event.get('event_type', 'N/A')],
                ["Description", event.get('description', 'N/A')],
                ["Location", event.get('location', 'N/A')],
                ["Involved", event.get('entities_involved', 'N/A')]
            ]
            t = Table(event_data, colWidths=[100, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#0f1628")),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#c8d8f0")),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))
        elements.append(PageBreak())

    # File Scans Section
    if file_scans:
        elements.append(Paragraph("File Scans", header_style))
        for scan in file_scans:
            scan_data = [
                ["Field", "Value"],
                ["File Name", scan.get('file_name', 'N/A')],
                ["Category", scan.get('category', 'N/A')],
                ["Risk Flag", scan.get('risk_flag', 'N/A')],
                ["Names Found", scan.get('names_found', 'N/A')],
                ["Orgs Found", scan.get('orgs_found', 'N/A')],
                ["Case Numbers", scan.get('case_numbers', 'N/A')]
            ]
            t = Table(scan_data, colWidths=[100, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00d4ff")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#0f1628")),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#1e2d50")),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#c8d8f0")),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
