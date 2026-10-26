"""
Generates a comprehensive, publication-quality academic PDF:
'Skin Cancer Detection System — Architecture, Code & Dataset Guide'
SVKM's NMIMS MPSTME — Computer Engineering Department
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Palette
COLOR_CREAM = colors.HexColor('#FFF9F3')
COLOR_DARK_BROWN = colors.HexColor('#493F3A')
COLOR_DARK_SAGE = colors.HexColor('#657C68')
COLOR_PASTEL_SAGE = colors.HexColor('#DCE8D5')
COLOR_PASTEL_PINK = colors.HexColor('#F4DDE2')
COLOR_MUTED_ROSE = colors.HexColor('#C98F9D')
COLOR_WARM_BEIGE = colors.HexColor('#F5EBDD')
COLOR_WHITE = colors.HexColor('#FFFFFF')
COLOR_LIGHT_GRAY = colors.HexColor('#E2D9CE')
COLOR_ACCENT_GREEN = colors.HexColor('#2E5934')
COLOR_DANGER_RED = colors.HexColor('#9C2838')

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#6E635D'))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Skin Cancer Detection Using Deep Learning & TensorFlow | Project Documentation")
            self.setStrokeColor(COLOR_LIGHT_GRAY)
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "SVKM's NMIMS MPSTME — Computer Engineering Department (Academic Year 2025-2026)")
        self.setStrokeColor(COLOR_LIGHT_GRAY)
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        
        self.restoreState()

def build_pdf(output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_DARK_BROWN,
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK_SAGE,
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=COLOR_DARK_BROWN,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=COLOR_DARK_SAGE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=COLOR_DARK_BROWN,
        spaceAfter=6
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    code_inline = ParagraphStyle(
        'CodeInline',
        parent=body_style,
        fontName='Courier',
        fontSize=8,
        leading=11
    )
    
    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_DARK_BROWN
    )
    
    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=COLOR_DARK_BROWN
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=COLOR_DARK_BROWN
    )

    elements = []
    
    # Header Banner Box
    header_content = [
        [
            Paragraph("<b>Skin Cancer Detection System Using Deep Learning</b><br/>"
                      "<font size='10' color='#657C68'>Comprehensive Software Engineering Architecture, Code Breakdown & Dataset Guide</font>", title_style)
        ],
        [
            Paragraph("<b>Academic Affiliation:</b> SVKM's NMIMS — Mukesh Patel School of Technology Management & Engineering | Department of Computer Engineering<br/>"
                      "<b>Project Team:</b> Vivaan Sanghvi (C063), Bhavi Doshi (C078), Vidisha Ajmera (C084) | <b>Batch:</b> Division C / Batch C1", subtitle_style)
        ]
    ]
    header_table = Table(header_content, colWidths=[504])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_WARM_BEIGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 14))
    
    # Executive Summary Card
    exec_summary = [
        [
            Paragraph("<b>DOCUMENT EXECUTIVE SUMMARY:</b><br/>"
                      "This document presents the complete technical specification of the Skin Cancer Detection web application. "
                      "It explains: (1) what code resides in every file and its software engineering purpose, (2) the exact provenance "
                      "of the HAM10000 / ISIC dermoscopy dataset, (3) how the dataset was ingested, preprocessed, augmented, and trained "
                      "using MobileNetV2 transfer learning, and (4) the specific attributes, diagnostic categories, and benchmark cases extracted from the dataset.", callout_style)
        ]
    ]
    summary_table = Table(exec_summary, colWidths=[504])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PASTEL_SAGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_DARK_SAGE),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 14))
    
    # =========================================================================
    # PART 1: CODE EXPLANATION (FILE-BY-FILE BREAKDOWN)
    # =========================================================================
    elements.append(Paragraph("1. Code Architecture & File-by-File Breakdown", h1_style))
    elements.append(Paragraph(
        "The application follows the industry-standard <b>Model-View-Controller (MVC)</b> software pattern using Python Flask. "
        "Separating application configuration, persistence (SQLite), business logic (TensorFlow/ReportLab), and views (Jinja2) ensures high maintainability, testability, and strict patient data security.",
        body_style
    ))
    
    files_data = [
        [Paragraph("File / Module", th_style), Paragraph("Contents & Implementation Details", th_style), Paragraph("Software Engineering Purpose", th_style)],
        
        [Paragraph("<b>app.py</b>", td_style),
         Paragraph("Flask application factory (<code>create_app()</code>), directory verification, blueprint registration, error handlers (400, 403, 404, 413, 500), and context injection.", td_style),
         Paragraph("Main entry point for local execution and production deployment.", td_style)],
         
        [Paragraph("<b>config.py</b>", td_style),
         Paragraph("Central configuration class: upload file size limits (10 MB), allowed formats (.jpg, .jpeg, .png), absolute paths for SQLite DB, uploads, and model weights.", td_style),
         Paragraph("Prevents hardcoding across modules; isolates runtime settings.", td_style)],
         
        [Paragraph("<b>database/db.py</b>", td_style),
         Paragraph("SQLite database engine (<code>get_db_connection()</code>), schema creation (<code>users</code>, <code>patient_medical_profiles</code>, <code>analysis_records</code>, <code>audit_logs</code>), automated non-destructive schema migrations, queries, and audit log writers.", td_style),
         Paragraph("Primary backend persistence layer. Ensures zero data loss across server restarts.", td_style)],
         
        [Paragraph("<b>services/<br/>auth_service.py</b>", td_style),
         Paragraph("Password hashing with <code>scrypt</code> (salt + iterations), authentication verification, session management, and route authorization decorators (<code>@login_required</code>, <code>@admin_required</code>).", td_style),
         Paragraph("Guarantees Role-Based Access Control (RBAC) and prevents plain-text password storage.", td_style)],
         
        [Paragraph("<b>services/<br/>model_service.py</b>", td_style),
         Paragraph("Image inspection (Pillow dimensions, channels, corruption check), normalization to [0.0, 1.0], TensorFlow MobileNetV2 inference (<code>model.predict()</code>), 7-class softmax probability scoring, and transparent fallback simulation.", td_style),
         Paragraph("Encapsulates computer vision and deep learning execution in an isolated service.", td_style)],
         
        [Paragraph("<b>services/<br/>pdf_service.py</b>", td_style),
         Paragraph("ReportLab PDF generation: embeds lesion thumbnail, patient demographics, clinical classification, confidence gauge, medical disclaimers, and hospital-grade header/footer layout. Saves to <code>uploads/reports/</code>.", td_style),
         Paragraph("Produces formal clinical screening documents for patients and consulting dermatologists.", td_style)],
         
        [Paragraph("<b>blueprints/<br/>auth_bp.py</b>", td_style),
         Paragraph("Routes for <code>/login</code>, <code>/register</code>, <code>/logout</code>, and <code>/profile</code>. Validates input credentials, manages sessions, and supports login by either email or username.", td_style),
         Paragraph("Handles user account lifecycle and profile updates.", td_style)],
         
        [Paragraph("<b>blueprints/<br/>analysis_bp.py</b>", td_style),
         Paragraph("Routes for <code>/upload</code>, <code>/analyze</code>, <code>/dashboard</code>, <code>/history</code>, <code>/results/&lt;id&gt;</code>, <code>/report/&lt;id&gt;</code>, and <code>/patient/medical-profile/update</code>. Enforces patient data isolation (HTTP 403 for unauthorized cross-patient access).", td_style),
         Paragraph("Core patient interaction controller for lesion evaluation, symptom capture, and report downloading.", td_style)],
         
        [Paragraph("<b>blueprints/<br/>admin_bp.py</b>", td_style),
         Paragraph("Routes for <code>/admin</code> (telemetry, KPI metrics, patient search), <code>/admin/patient/&lt;id&gt;</code> (clinical updates, physician notes, verification), and <code>/admin/export-patients-csv</code> with CWE-1236 formula injection defense.", td_style),
         Paragraph("Clinical command center for administrators and consulting dermatologists.", td_style)],
         
        [Paragraph("<b>blueprints/<br/>main_bp.py</b>", td_style),
         Paragraph("Public informational routes: <code>/</code> (landing hero), <code>/how-it-works</code> (ML pipeline explanation), and <code>/skin-health</code> (educational ABCDE melanoma rule).", td_style),
         Paragraph("Educational awareness and public health screening outreach.", td_style)],
         
        [Paragraph("<b>templates/<br/>dashboard.html</b>", td_style),
         Paragraph("Patient dashboard displaying personal medical card, active skin concerns, dermatological risk factors, physician notes, past scan archive, and clear actual vs. demo record badges.", td_style),
         Paragraph("Patient-facing view reflecting live synchronized backend records.", td_style)],
         
        [Paragraph("<b>templates/admin/<br/>patient_detail.html</b>", td_style),
         Paragraph("Administrative patient detail view: medical history on the left, uploaded lesion photo gallery on the right, authorized verification dropdown, clinical notes form, and immutable audit trail.", td_style),
         Paragraph("Two-way synchronization interface between clinic and patient.", td_style)],
         
        [Paragraph("<b>tests/<br/>test_patient_sync.py</b>", td_style),
         Paragraph("Automated Pytest test suite containing 12 comprehensive scenarios: registration persistence, server restart simulation, admin sync, cross-patient isolation (403), CSV formula defense, and schema idempotency.", td_style),
         Paragraph("Quality assurance suite guaranteeing 100% test pass rate across requirements.", td_style)]
    ]
    
    files_table = Table(files_data, colWidths=[90, 244, 170])
    files_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_WARM_BEIGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_LIGHT_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(files_table)
    elements.append(Spacer(1, 14))
    
    # =========================================================================
    # PART 2: WHERE DID WE GET THE DATASET FROM?
    # =========================================================================
    elements.append(Paragraph("2. Dataset Origin & Provenance", h1_style))
    elements.append(Paragraph(
        "The model and educational benchmarks are powered by the <b>HAM10000 (\"Human Against Machine with 10,000 training images\")</b> dataset, "
        "recognized internationally as the benchmark research corpus for automated dermatological screening:",
        body_style
    ))
    
    dataset_points = [
        "<b>Institutional Authors:</b> ViDIR Group (Department of Dermatology, Medical University of Vienna, Austria) and Cliff Rosendahl (School of Medicine, The University of Queensland, Australia).",
        "<b>Hosting Organization:</b> The International Skin Imaging Collaboration (<b>ISIC Archive</b>), supported by the Society for Melanoma Research.",
        "<b>Dataset Acquisition Pipeline (<code>download_ham10000.py</code>):</b>",
        "&nbsp;&nbsp;&bull; <b>Metadata CSV:</b> The official <code>HAM10000_metadata.csv</code> (containing 10,015 clinical records) is downloaded from verified academic repositories.",
        "&nbsp;&nbsp;&bull; <b>Dermoscopic Imagery:</b> High-resolution dermoscopic image files (.jpg) are retrieved directly from the official ISIC Archive Amazon Web Services S3 cloud repository: <code>https://isic-archive.s3.amazonaws.com/images/{image_id}.jpg</code>.",
        "&nbsp;&nbsp;&bull; <b>Integrity Verification:</b> Every downloaded photograph is programmatically opened and verified using Pillow (PIL) to eliminate truncated, corrupted, or non-RGB files prior to training."
    ]
    for pt in dataset_points:
        elements.append(Paragraph(pt, body_style))
    elements.append(Spacer(1, 10))
    
    # =========================================================================
    # PART 3: HOW DID WE CONNECT AND TRAIN IT?
    # =========================================================================
    elements.append(Paragraph("3. Connection, Preprocessing & Deep Learning Training Pipeline", h1_style))
    elements.append(Paragraph(
        "The model training workflow is implemented in <code>train_model.py</code> using TensorFlow and Keras. "
        "The end-to-end pipeline consists of four rigorous engineering stages:",
        body_style
    ))
    
    stages_data = [
        [Paragraph("Pipeline Stage", th_style), Paragraph("Technical Implementation", th_style), Paragraph("Clinical / Algorithmic Rationale", th_style)],
        
        [Paragraph("<b>1. Lesion-Grouped Splitting</b>", td_style),
         Paragraph("Dataset split into <b>Train (70%)</b>, <b>Validation (15%)</b>, and <b>Held-out Test (15%)</b> strictly grouped by <code>lesion_id</code> using Scikit-Learn.", td_style),
         Paragraph("<b>Eliminates Data Leakage:</b> Multiple photos of the same mole never appear across both train and test splits, preventing artificial over-optimism.", td_style)],
         
        [Paragraph("<b>2. Input Preprocessing & Augmentation</b>", td_style),
         Paragraph("Images resized to 224x224 RGB pixels. Normalized from [0, 255] to [0.0, 1.0]. On training images only, applied random horizontal/vertical flips, rotations (&plusmn;15&deg;), zoom (&plusmn;10%), and contrast adjustments.", td_style),
         Paragraph("Standardizes tensor inputs for MobileNetV2 and teaches the CNN to recognize skin lesions regardless of patient orientation or ambient lighting.", td_style)],
         
        [Paragraph("<b>3. Transfer Learning Architecture</b>", td_style),
         Paragraph("<b>Base:</b> MobileNetV2 pretrained on ImageNet (1.4 million images).<br/>"
                   "<b>Custom Top:</b> <code>GlobalAveragePooling2D()</code> &rarr; <code>BatchNormalization()</code> &rarr; <code>Dense(128, ReLU)</code> &rarr; <code>Dropout(0.3)</code> &rarr; <code>Dense(7, Softmax)</code>.", td_style),
         Paragraph("Leverages general feature extractors (edges, cellular textures) while fine-tuning specialized top layers for dermatological lesion patterns.", td_style)],
         
        [Paragraph("<b>4. Class Imbalance Compensation</b>", td_style),
         Paragraph("Calculated balanced class weights: <code>compute_class_weight('balanced', classes=..., y=...)</code>. Compiled with <code>Adam(learning_rate=1e-4)</code> and <code>SparseCategoricalCrossentropy</code>.", td_style),
         Paragraph("<b>Protects High-Risk Classes:</b> Benign moles represent ~67% of records. Class weighting forces the optimizer to treat rare/lethal melanomas with equal importance.", td_style)]
    ]
    stages_table = Table(stages_data, colWidths=[110, 214, 180])
    stages_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_WARM_BEIGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_LIGHT_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(stages_table)
    elements.append(Spacer(1, 14))
    
    # =========================================================================
    # PART 4: WHAT SPECIFICALLY HAVE WE USED FROM THE DATASET?
    # =========================================================================
    elements.append(Paragraph("4. Specific Dataset Attributes & Reference Benchmarks Utilized", h1_style))
    elements.append(Paragraph(
        "From the raw HAM10000 dataset, the application specifically extracts and utilizes four key data elements:",
        body_style
    ))
    
    classes_data = [
        [Paragraph("Code", th_style), Paragraph("Full Diagnostic Disease Category", th_style), Paragraph("Clinical Severity & Risk Level", th_style), Paragraph("Educational Reference Case Preloaded", th_style)],
        
        [Paragraph("<b>mel</b>", td_style),
         Paragraph("<b>Melanoma</b>", td_style),
         Paragraph("<font color='#9C2838'><b>Malignant Skin Cancer (High Risk / Urgent)</b></font>", td_style),
         Paragraph("<code>HAM10000_ISIC_0029314.jpg</code> (Superficial Melanoma)", td_style)],
         
        [Paragraph("<b>bcc</b>", td_style),
         Paragraph("<b>Basal Cell Carcinoma</b>", td_style),
         Paragraph("<font color='#9C2838'><b>Malignant Non-Melanoma</b></font>", td_style),
         Paragraph("<code>HAM10000_ISIC_0024310.jpg</code> (BCC Lesion)", td_style)],
         
        [Paragraph("<b>akiec</b>", td_style),
         Paragraph("<b>Actinic Keratoses / Intraepithelial Carcinoma</b>", td_style),
         Paragraph("<font color='#B37D28'><b>Pre-cancerous / Squamous Risk</b></font>", td_style),
         Paragraph("Preloaded in HAM10000 Benchmark Suite", td_style)],
         
        [Paragraph("<b>nv</b>", td_style),
         Paragraph("<b>Melanocytic Nevi</b>", td_style),
         Paragraph("<font color='#2E5934'><b>Common Benign Mole</b></font>", td_style),
         Paragraph("<code>HAM10000_ISIC_0024306.jpg</code> (Benign Nevus)", td_style)],
         
        [Paragraph("<b>bkl</b>", td_style),
         Paragraph("<b>Benign Keratosis-like Lesions</b>", td_style),
         Paragraph("<font color='#2E5934'><b>Non-Cancerous (Seborrheic Keratosis)</b></font>", td_style),
         Paragraph("<code>HAM10000_ISIC_0024312.jpg</code> (Solar Lentigo)", td_style)],
         
        [Paragraph("<b>df</b>", td_style),
         Paragraph("<b>Dermatofibroma</b>", td_style),
         Paragraph("<font color='#2E5934'><b>Benign Dermal Nodule</b></font>", td_style),
         Paragraph("Preloaded in HAM10000 Benchmark Suite", td_style)],
         
        [Paragraph("<b>vasc</b>", td_style),
         Paragraph("<b>Vascular Lesions</b>", td_style),
         Paragraph("<font color='#2E5934'><b>Benign (Angioma / Hemangioma)</b></font>", td_style),
         Paragraph("Preloaded in HAM10000 Benchmark Suite", td_style)]
    ]
    classes_table = Table(classes_data, colWidths=[40, 160, 154, 150])
    classes_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_WARM_BEIGE),
        ('BOX', (0,0), (-1,-1), 1, COLOR_LIGHT_GRAY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_LIGHT_GRAY),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(classes_table)
    elements.append(Spacer(1, 10))
    
    spec_points = [
        "<b>1. Diagnostic Labels (<code>dx</code> column):</b> Used as target ground-truth classification labels across the 7 disease classes shown above.",
        "<b>2. Image Identifier (<code>image_id</code> column):</b> Used to index physical dermoscopic files (e.g. <code>ISIC_0024306.jpg</code>) and map them to histopathologic biopsy findings.",
        "<b>3. Lesion Identifier (<code>lesion_id</code> column):</b> Used during data splitting to prevent cross-contamination and guarantee valid statistical evaluation.",
        "<b>4. Diagnostic Validation Type (<code>dx_type</code> column):</b> Filters for histopathologically verified ground-truth lesions (gold-standard biopsies).",
        "<b>5. Preloaded Educational Benchmark Cases:</b> Embedded into pre-registered demo accounts (<b>Bhavi Doshi</b> and <b>Vidisha Ajmera</b>) to allow lab examiners, viva evaluators, and students to test full image inspection, risk categorization, and PDF generation workflows reliably without requiring internet connectivity."
    ]
    for pt in spec_points:
        elements.append(Paragraph(pt, body_style))
    elements.append(Spacer(1, 12))
    
    # Disclaimer Box
    disclaimer_content = [
        [
            Paragraph("<b>ACADEMIC & CLINICAL DISCLAIMER:</b><br/>"
                      "This document and the associated software application are developed for educational evaluation and preliminary screening demonstration at SVKM's NMIMS MPSTME. "
                      "This software is NOT a certified clinical diagnostic medical device. Artificial intelligence algorithms can produce false positive and false negative results. "
                      "Always consult a licensed dermatologist or medical oncologist for clinical dermoscopy, biopsy, and professional healthcare advice.", callout_style)
        ]
    ]
    disc_table = Table(disclaimer_content, colWidths=[504])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PASTEL_PINK),
        ('BOX', (0,0), (-1,-1), 1, COLOR_MUTED_ROSE),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(disc_table)
    
    # Build PDF
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {output_path}")

if __name__ == '__main__':
    target = Path("documentation") / "Skin_Cancer_Detection_Project_Architecture_and_Dataset_Guide.pdf"
    build_pdf(target)
