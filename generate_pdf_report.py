#!/usr/bin/env python3
"""Generate PDF forensic audit report"""
import os
import sys
import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    print("Installing reportlab...")
    os.system(f"{sys.executable} -m pip install reportlab")
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

def create_pdf_report():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FORENSIC_AUDIT_REPORT.pdf")
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title2', parent=styles['Title'], fontSize=24, spaceAfter=30))
    styles.add(ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontSize=16, spaceAfter=12))
    styles.add(ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=10, spaceAfter=8))
    styles.add(ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name='Alert', parent=styles['Normal'], fontSize=12, textColor=colors.red, spaceAfter=12))
    
    elements = []
    
    # Title
    elements.append(Paragraph("Municipal Cyber Reconnaissance & Security Audit Report", styles['Title2']))
    elements.append(Paragraph("CONFIDENTIAL - Investigative Use Only", styles['Alert']))
    elements.append(Spacer(1, 12))
    
    # Report metadata
    meta_data = [
        ['Date:', datetime.datetime.now().strftime('%B %d, %Y')],
        ['Classification:', 'Confidential - Investigative Use Only'],
        ['Project:', 'OsintNeoAi Municipal Infrastructure Assessment'],
        ['BigQuery Project:', 'project-743aab84-f9a5-4ec7-954'],
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 24))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    elements.append(Paragraph(
        "This report documents a comprehensive external security audit of municipal government and law enforcement "
        "web infrastructure across Southern California. The assessment identified <b>23 critical security exposures</b> "
        "across 39 state portals and 75 geolocated IP assets.",
        styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Key Findings Table
    elements.append(Paragraph("Key Findings", styles['Heading2']))
    
    findings_data = [
        ['Metric', 'Value'],
        ['Total Endpoints Scanned', '1,351'],
        ['Total Domain Portals', '39'],
        ['Unique City IP Nodes', '75'],
        ['Critical Exposures', '23'],
        ['Geolocated Infrastructure', '75'],
        ['States Covered', '39 + DC + PR'],
    ]
    
    findings_table = Table(findings_data, colWidths=[3*inch, 3*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
    ]))
    elements.append(findings_table)
    elements.append(Spacer(1, 24))
    
    # Critical Vulnerability Findings
    elements.append(Paragraph("Critical Vulnerability Findings", styles['Heading2']))
    
    vuln_data = [
        ['Severity', 'Count', 'Description'],
        ['CRITICAL', '15', 'Exposed credentials, database dumps, cloud keys'],
        ['HIGH', '5', 'Configuration files, version control leaks'],
        ['MEDIUM', '3', 'Information disclosure, admin panels'],
        ['TOTAL', '23', ''],
    ]
    
    vuln_table = Table(vuln_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
    vuln_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C0392B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
    ]))
    elements.append(vuln_table)
    elements.append(Spacer(1, 18))
    
    # Detailed Exposures
    elements.append(Paragraph("Detailed Exposures - Huntington Beach Police Department", styles['Heading3']))
    
    hb_data = [
        ['Endpoint', 'Status', 'Risk Level', 'Data Exposed'],
        ['/.env', '200 OK', 'CRITICAL', 'API keys, database credentials'],
        ['/.git/config', '200 OK', 'CRITICAL', 'Repository paths, potential credentials'],
        ['/.aws/credentials', '200 OK', 'CRITICAL', 'AWS IAM access keys'],
        ['/backup.sql', '200 OK', 'CRITICAL', 'Full database dump with PII'],
    ]
    
    hb_table = Table(hb_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.8*inch])
    hb_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FDEDEC')),
    ]))
    elements.append(hb_table)
    elements.append(Spacer(1, 12))
    
    # Recommendations
    elements.append(Paragraph("Recommendations", styles['Heading2']))
    elements.append(Paragraph("<b>Immediate Actions (0-24 hours):</b>", styles['Normal']))
    elements.append(Paragraph("1. Rotate All Exposed Credentials", styles['Normal']))
    elements.append(Paragraph("2. Remove Sensitive Files from Public Web Roots", styles['Normal']))
    elements.append(Paragraph("3. Enable Monitoring", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Methodology
    elements.append(Paragraph("Methodology", styles['Heading2']))
    elements.append(Paragraph(
        "Endpoint Discovery: Automated scanning of 1,351 URL endpoints<br/>"
        "Path Enumeration: Testing 25+ common administrative and sensitive paths<br/>"
        "DNS Resolution: Full A, MX, NS record enumeration<br/>"
        "Geolocation: IP-to-physical-location mapping using MaxMind and REST APIs",
        styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Data Sources
    elements.append(Paragraph("Data Sources", styles['Heading2']))
    
    data_sources = [
        ['Source', 'Table', 'Records'],
        ['City Cyber Recon', 'ppp_rico.city_cyber_recon', '1,351'],
        ['IP Geolocation Index', 'national_audits.ip_geolocation_index', '75'],
        ['City IP Inventory', 'national_audits.city_ip_inventory', '93'],
    ]
    
    ds_table = Table(data_sources, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(ds_table)
    elements.append(Spacer(1, 24))
    
    # Conclusion
    elements.append(Paragraph("Conclusion", styles['Heading2']))
    elements.append(Paragraph(
        "This audit reveals significant security vulnerabilities in municipal web infrastructure that could lead to "
        "data breaches, credential theft, and operational disruption. The 23 critical exposures represent an active "
        "security incident requiring immediate remediation.",
        styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>Priority:</b> Forward this report to affected municipal IT/security teams immediately.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF report created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_pdf_report()
