import os
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Brand palette colors
COLOR_CREAM = colors.HexColor('#FFF9F3')
COLOR_DARK_TEXT = colors.HexColor('#493F3A')
COLOR_DARK_SAGE = colors.HexColor('#657C68')
COLOR_PASTEL_SAGE = colors.HexColor('#DCE8D5')
COLOR_PASTEL_PINK = colors.HexColor('#F4DDE2')
COLOR_MUTED_ROSE = colors.HexColor('#C98F9D')
COLOR_WARM_BEIGE = colors.HexColor('#F5EBDD')
COLOR_WHITE = colors.HexColor('#FFFFFF')
COLOR_LIGHT_GRAY = colors.HexColor('#ECE6DF')

def generate_screening_report_pdf(record, user, output_stream):
    """
    Generates a structured, elegant PDF preliminary screening report for an analysis record.
    """
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom typography styles
    style_title = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_DARK_TEXT,
        alignment=0
    )
    
    style_subtitle = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK_SAGE,
        alignment=0
    )
    
    style_badge = ParagraphStyle(
        'ReportBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=COLOR_DARK_SAGE,
        alignment=2
    )
    
    style_section = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=COLOR_DARK_SAGE,
        spaceBefore=12,
        spaceAfter=6
    )
    
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK_TEXT
    )
    
    style_body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK_TEXT
    )
    
    style_disclaimer = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=COLOR_DARK_TEXT
    )
    
    elements = []
    
    # Header Banner Table
    header_data = [
        [
            Paragraph("<b>Skin Cancer Detection System</b><br/><font size='9'>AI-Assisted Preliminary Screening Report</font>", style_title),
            Paragraph(f"<b>Report ID:</b> RPT-2026-{record['id']:05d}<br/><b>Date:</b> {record['created_at'][:19]}", style_badge)
        ]
    ]
    header_table = Table(header_data, colWidths=[330, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_DARK_SAGE, spaceBefore=4, spaceAfter=14))
    
    # Academic & Institutional Attribution
    college_note = Paragraph(
        "<b>Academic Affiliation:</b> SVKM's NMIMS — Mukesh Patel School of Technology Management & Engineering | "
        "Department of Computer Engineering | Software Engineering Mini-Project",
        style_subtitle
    )
    elements.append(college_note)
    elements.append(Spacer(1, 10))
    
    # Metadata Overview Table (Patient + Scan)
    patient_name = user['full_name'] if user else 'Registered User'
    patient_email = user['email'] if user else 'N/A'
    is_demo = bool(record['is_demo'])
    status_display = "GENUINE MODEL PREDICTION" if not is_demo and record['result_status'] == 'genuine_model' else "DEMO MODE (SIMULATED / PREVIEW)"
    
    confidence_display = (
        f"{record['confidence_score']:.1f}%" 
        if record['confidence_score'] is not None 
        else "N/A (Demo Mode — No Fabricated Confidence)"
    )
    
    meta_table_data = [
        [
            Paragraph("<b>Patient Name:</b>", style_body_bold),
            Paragraph(patient_name, style_body),
            Paragraph("<b>Analysis Date:</b>", style_body_bold),
            Paragraph(str(record['created_at']), style_body)
        ],
        [
            Paragraph("<b>User Account:</b>", style_body_bold),
            Paragraph(patient_email, style_body),
            Paragraph("<b>File Name:</b>", style_body_bold),
            Paragraph(record['original_filename'], style_body)
        ],
        [
            Paragraph("<b>Analysis Engine:</b>", style_body_bold),
            Paragraph(record['model_version'] or 'CNN-HAM10000', style_body),
            Paragraph("<b>Mode / Status:</b>", style_body_bold),
            Paragraph(status_display, style_body)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[95, 170, 95, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_WARM_BEIGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_LIGHT_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))
    
    # Diagnostic Result Card
    elements.append(Paragraph("Preliminary Analysis Finding", style_section))
    
    result_bg = COLOR_PASTEL_PINK if ('malignant' in record['classification'].lower() or 'melanoma' in record['classification'].lower()) else COLOR_PASTEL_SAGE
    border_color = COLOR_MUTED_ROSE if ('malignant' in record['classification'].lower() or 'melanoma' in record['classification'].lower()) else COLOR_DARK_SAGE
    
    result_card_data = [
        [
            Paragraph("<b>Classification Result:</b>", style_body_bold),
            Paragraph(f"<b><font size='12'>{record['classification']}</font></b>", style_body)
        ],
        [
            Paragraph("<b>Model Confidence:</b>", style_body_bold),
            Paragraph(f"<b>{confidence_display}</b>", style_body)
        ],
        [
            Paragraph("<b>Clinical Provenance:</b>", style_body_bold),
            Paragraph(
                "Genuine Neural Network Inference Output" if not is_demo 
                else "Simulated Educational Demonstration (No genuine model weights connected)", 
                style_body
            )
        ]
    ]
    result_table = Table(result_card_data, colWidths=[140, 390])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), result_bg),
        ('BOX', (0,0), (-1,-1), 1.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FFFFFF')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 14))
    
    # Visual Image & Findings Row
    elements.append(Paragraph("Lesion Imagery & Observations", style_section))
    
    image_element = None
    file_path = record['file_path']
    if not (file_path and os.path.exists(file_path)) and record.get('stored_filename'):
        from config import Config
        fallback = Config.UPLOAD_FOLDER / record['stored_filename']
        if fallback.exists():
            file_path = str(fallback)

    if file_path and os.path.exists(file_path):
        try:
            image_element = RLImage(file_path, width=2.0*inch, height=2.0*inch)
        except Exception:
            image_element = Paragraph("<i>Image preview unavailable.</i>", style_body)
    else:
        image_element = Paragraph("<i>Image file not available on local server storage.</i>", style_body)
        
    explanation_text = record['explanation'] or "No additional clinical narrative recorded."
    
    # Try reading lesion metadata
    metadata_notes = ""
    try:
        if record['lesion_metadata']:
            meta = json.loads(record['lesion_metadata'])
            if 'width' in meta:
                metadata_notes = f"<br/><br/><b>Image Metrics:</b> Resolution {meta.get('width')}x{meta.get('height')} px | Aspect Ratio: {meta.get('aspect_ratio', 'N/A')} | Contrast Metric: {meta.get('contrast_metric', 'N/A')}"
    except Exception:
        pass
        
    findings_para = Paragraph(f"<b>Interpretation Summary:</b><br/>{explanation_text}{metadata_notes}", style_body)
    
    side_by_side_data = [[image_element, findings_para]]
    side_by_side_table = Table(side_by_side_data, colWidths=[160, 370])
    side_by_side_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (1,0), (1,0), 12),
    ]))
    elements.append(side_by_side_table)
    elements.append(Spacer(1, 14))
    
    # Recommended Next Steps
    elements.append(Paragraph("Recommended Clinical Next Steps", style_section))
    steps_content = Paragraph(
        "1. <b>Professional Dermatological Consultation:</b> Schedule an appointment with a board-certified dermatologist for in-person dermoscopy.<br/>"
        "2. <b>Continuous Self-Examination:</b> Follow the ABCDE guidelines (Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolving size/shape).<br/>"
        "3. <b>Do Not Delay:</b> If you experience rapid changes, ulceration, itching, or bleeding in the lesion, seek clinical evaluation promptly.",
        style_body
    )
    elements.append(steps_content)
    elements.append(Spacer(1, 16))
    
    # Formal Medical Disclaimer Box
    disclaimer_data = [[
        Paragraph(
            "<b>IMPORTANT MEDICAL & LEGAL DISCLAIMER:</b><br/>"
            "This document is an AI-assisted preliminary screening report generated for educational and software engineering demonstration purposes. "
            "It does NOT constitute a clinical medical diagnosis, pathology report, or definitive medical advice. "
            "Deep learning algorithms are subject to false positives, false negatives, and dataset limitations (HAM10000 / ISIC). "
            "Always consult a qualified dermatologist, oncologist, or primary healthcare provider for medical evaluations, dermoscopy, or biopsy.",
            style_disclaimer
        )
    ]]
    disclaimer_table = Table(disclaimer_data, colWidths=[530])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PASTEL_PINK),
        ('BOX', (0,0), (-1,-1), 1, COLOR_MUTED_ROSE),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(disclaimer_table)
    
    doc.build(elements)
