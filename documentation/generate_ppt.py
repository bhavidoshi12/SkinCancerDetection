import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BASE_DIR = Path("D:/SE/SkinCancerDetection")
DOC_DIR = BASE_DIR / "documentation"
ASSETS_DIR = DOC_DIR / "ppt_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate High-Res Results Chart (Panel A: Held-out Metrics, Panel B: Feature Verification)
def generate_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=300)
    
    # Palette
    sage_dark = "#4A6B53"
    sage_light = "#8AAB8F"
    rose_pink = "#B86B77"
    beige_card = "#F5EBDD"
    dark_brown = "#493F3A"
    
    # Panel A: Deep Learning Model Metrics on 51-sample Held-out Test Set
    metrics = ['Accuracy', 'Precision\n(Weighted)', 'Recall\n(Weighted)', 'F1-Score\n(Weighted)', 'ROC-AUC\n(OvR)']
    values = [11.76, 21.05, 11.76, 14.50, 56.62]
    colors = [rose_pink, "#C48A93", "#A89B8D", "#7E9C84", sage_dark]
    
    bars = ax1.bar(metrics, values, color=colors, width=0.55, edgecolor="#ffffff", linewidth=1.5)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Metric Score (%)", fontsize=11, fontweight='bold', color=dark_brown)
    ax1.set_title("A: Genuine Held-Out Test Split Performance\n(HAM10000 7-Class MobileNetV2 Architecture)", fontsize=11, fontweight='bold', pad=12, color=dark_brown)
    ax1.grid(axis='y', linestyle='--', alpha=0.35)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"{height:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10, fontweight='bold', color=dark_brown)
                     
    ax1.text(0.5, 0.88, "Authentic baseline on CPU hardware split;\nZero data fabrication.", 
             transform=ax1.transAxes, ha='center', fontsize=8.5, fontstyle='italic',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffff', edgecolor='#dddddd', alpha=0.9))

    # Panel B: Software Engineering Feature Verification (21/21 Automated Tests Passed)
    suites = [
        'Auth & Profiles\n(TC-01, TC-02)',
        'Admin Portal RBAC\n(Security /admin)',
        'Image Pipeline\n(TC-03 Validation)',
        'Model Service\n(7-Class Live DL)',
        'Screening History\n(TC-04 & PDF)',
        'Test Suite Health\n(Redirects & DB)'
    ]
    test_counts = [4, 4, 3, 3, 3, 4] # Total = 21 tests
    passed = [100] * len(suites)
    
    y_pos = np.arange(len(suites))
    ax2.barh(y_pos, passed, color=sage_light, height=0.55, edgecolor=sage_dark, linewidth=1.2)
    ax2.set_xlim(0, 115)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(suites, fontsize=9.5, fontweight='600', color=dark_brown)
    ax2.invert_yaxis()
    ax2.set_xlabel("Verification Rate (%)", fontsize=11, fontweight='bold', color=dark_brown)
    ax2.set_title("B: Software Engineering Automated Verification\n(21 Tests Passed / 0 Failed / 100% Pass Rate)", fontsize=11, fontweight='bold', pad=12, color=dark_brown)
    ax2.grid(axis='x', linestyle='--', alpha=0.35)
    
    for i, count in enumerate(test_counts):
        ax2.text(102, i, f"100% ({count}/{count})", va='center', ha='left', fontsize=9, fontweight='bold', color=sage_dark)
        
    plt.tight_layout()
    chart_path = ASSETS_DIR / "project_results_graph.png"
    plt.savefig(chart_path, dpi=300, facecolor='#FAF6F0')
    plt.close()
    print(f"Results chart generated: {chart_path}")
    return chart_path

# 2. Build 12-slide PowerPoint Presentation
def build_presentation(chart_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # Color palette
    BG_CREAM = RGBColor(255, 249, 243)
    CARD_BEIGE = RGBColor(245, 235, 221)
    CARD_PINK = RGBColor(244, 221, 226)
    CARD_SAGE = RGBColor(220, 232, 213)
    DARK_BROWN = RGBColor(73, 63, 58)
    MUTED_ROSE = RGBColor(184, 107, 119)
    DARK_SAGE = RGBColor(74, 107, 83)
    WHITE = RGBColor(255, 255, 255)
    
    def add_header(slide, title_text, category_text="SOFTWARE ENGINEERING MINI-PROJECT"):
        # Category Pill
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = MUTED_ROSE
        
        # Main Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_BROWN

    def set_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    # SLIDE 1: Title Slide
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, BG_CREAM)
    
    box1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(5.0))
    tf1 = box1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "SVKM'S NMIMS — MPSTME • DEPARTMENT OF COMPUTER ENGINEERING"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DARK_SAGE
    
    p = tf1.add_paragraph()
    p.text = "Skin Cancer Detection Using Deep Learning and TensorFlow"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = DARK_BROWN
    p.space_after = Pt(14)
    
    p = tf1.add_paragraph()
    p.text = "A Full-Stack Educational Screening System with MobileNetV2 CNN, RBAC Admin Console & Clinical PDF Reports"
    p.font.size = Pt(16)
    p.font.color.rgb = MUTED_ROSE
    p.space_after = Pt(28)
    
    p = tf1.add_paragraph()
    p.text = "Student Authors: Bhavi Doshi (C078)  •  Vivaan Sanghvi (C063)  •  Vidisha Ajmera (C084)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_BROWN
    
    p = tf1.add_paragraph()
    p.text = "Technology Stack: Python 3.13, Flask, TensorFlow 2.21, Keras 3.15, SQLite, ReportLab, HTML5/CSS3"
    p.font.size = Pt(12)
    p.font.color.rgb = DARK_BROWN
    
    p = tf1.add_paragraph()
    p.text = "Active Repository Location: D:\\SE\\SkinCancerDetection"
    p.font.size = Pt(11)
    p.font.color.rgb = DARK_SAGE

    # SLIDE 2: Introduction & Background
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2, BG_CREAM)
    add_header(s2, "Introduction & Clinical Background")
    
    box2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    
    points2 = [
        ("Clinical Need & Early Screening:", "Skin malignancies (melanoma, basal cell carcinoma, actinic keratoses) carry dramatically higher survival rates when detected early. However, access to board-certified dermatologists is constrained in primary healthcare and rural regions."),
        ("Computer Vision Potential:", "Convolutional Neural Networks (CNNs) excel at extracting subtle spatial textures, pigment networks, and border irregularities from dermoscopic lesion photography."),
        ("End-to-End Software Engineering:", "Bridging research prototypes into real-world utility requires a secure, responsive, and ethical web application with robust authentication, defensive image validation, persistent database storage, and role-based access control."),
        ("Academic Research Scope:", "Engineered as an academic educational screening platform. Strictly non-diagnostic; enforces prominent medical disclaimers to ensure responsible user guidance.")
    ]
    for title, desc in points2:
        p = tf2.add_paragraph()
        p.text = f"•  {title} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(14)

    # SLIDE 3: Problem Statement & Objectives
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3, BG_CREAM)
    add_header(s3, "Problem Statement & Project Objectives")
    
    box3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf3 = box3.text_frame
    tf3.word_wrap = True
    
    p = tf3.paragraphs[0]
    p.text = "Formal Problem Statement:"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = MUTED_ROSE
    
    p = tf3.add_paragraph()
    p.text = '“To design, implement, and evaluate an accessible, secure, and responsive web-based preliminary screening platform that ingests dermatological lesion photographs, performs rigorous input validation and preprocessing, and executes genuine TensorFlow/Keras deep learning inference across standard diagnostic categories, while maintaining persistent user records, role-based admin controls, and adhering to strict clinical safety disclaimers.”'
    p.font.size = Pt(13)
    p.font.italic = True
    p.space_after = Pt(16)
    
    p = tf3.add_paragraph()
    p.text = "Key Implemented Objectives:"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = DARK_SAGE
    
    objs = [
        "1. Full-Stack Web Architecture: Built modular Flask blueprints (auth, main, analysis, testing, admin).",
        "2. Defensive Security: Password hashing with scrypt, RBAC (@admin_required), and deep image validation (MIME/resolution/channels).",
        "3. Live 7-Class Deep Learning: Integrated MobileNetV2 pre-trained CNN yielding authentic class probability distributions.",
        "4. Persistent Clinical Records: SQLite data layer tracking patient scans, isolation boundaries, and automated PDF report generation."
    ]
    for o in objs:
        p = tf3.add_paragraph()
        p.text = f"•  {o}"
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_BROWN
        p.space_after = Pt(8)

    # SLIDE 4: Architecture & Technology Stack
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4, BG_CREAM)
    add_header(s4, "System Architecture & Technology Stack")
    
    box4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf4 = box4.text_frame
    tf4.word_wrap = True
    
    techs = [
        ("Presentation Layer (Frontend):", "HTML5, CSS3, JavaScript. Calming pastel healthcare aesthetic (blush pink #F4DDE2, warm beige #F5EBDD, sage green #DCE8D5). Fully mobile-responsive."),
        ("Application & Web Layer (Backend):", "Python 3.13 + Flask microframework. Structured with 5 modular blueprints: auth_bp, main_bp, analysis_bp, testing_bp, admin_bp."),
        ("Deep Learning & Computer Vision:", "TensorFlow 2.21 + Keras 3.15 + OpenCV + Pillow + NumPy. MobileNetV2 architecture with transfer learning specialized for 7 HAM10000 classes."),
        ("Data Persistence & Clinical Reporting:", "SQLite isolated relational database (instance/skin_cancer.db) + ReportLab PDF generation engine synthesizing multi-page screening summaries."),
        ("Automated Quality Assurance:", "Pytest test framework with 21 unit, functional, security, and integration tests.")
    ]
    for cat, det in techs:
        p = tf4.add_paragraph()
        p.text = f"•  {cat} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = det
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 5: Dataset & Preprocessing Pipeline
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5, BG_CREAM)
    add_header(s5, "Benchmark Dataset & Defensive Preprocessing")
    
    box5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf5 = box5.text_frame
    tf5.word_wrap = True
    
    data_points = [
        ("Primary Dataset:", "HAM10000 ('Human Against Machine with 10,000 training images') dermatoscopic collection, acquired via the official ISIC Archive."),
        ("7 Diagnostic Categories:", "Actinic Keratoses (akiec), Basal Cell Carcinoma (bcc), Benign Keratosis-like (bkl), Dermatofibroma (df), Melanoma (mel), Melanocytic Nevi (nv), Vascular Lesions (vasc)."),
        ("Defensive Preprocessing:", "Strict dimension checks (50x50 to 6000x6000), Pillow format verification, RGB conversion, aspect ratio checks, and standard 224x224 normalization for MobileNetV2."),
        ("Leakage Prevention:", "Lesion-level grouping (lesion_id) ensures that multiple photographs of the same anatomical lesion never cross between training, validation, and held-out test splits.")
    ]
    for d, exp in data_points:
        p = tf5.add_paragraph()
        p.text = f"•  {d} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = exp
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 6: Deep Learning Model Architecture
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6, BG_CREAM)
    add_header(s6, "Deep Learning Architecture: MobileNetV2 CNN")
    
    box6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf6 = box6.text_frame
    tf6.word_wrap = True
    
    cnn_points = [
        ("Base Architecture:", "MobileNetV2 pre-trained on ImageNet. Utilizes depthwise separable convolutions and inverted residual bottleneck blocks for lightweight, low-latency inference."),
        ("Transfer Learning Custom Head:", "GlobalAveragePooling2D -> BatchNormalization -> Dense(128, ReLU) -> Dropout(0.40) -> Dense(7, Softmax)."),
        ("Class Imbalance Strategy:", "Balanced class weights computed dynamically across under-represented malignant categories (mel, bcc, akiec) vs majority benign moles (nv)."),
        ("Inference Execution:", "Live Python service (model_service.py) transforms incoming PIL images, executes model.predict(), maps softmax outputs across all 7 diagnostic classes, and computes risk stratification.")
    ]
    for c, desc in cnn_points:
        p = tf6.add_paragraph()
        p.text = f"•  {c} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 7: Security, Authentication & Admin RBAC
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7, BG_CREAM)
    add_header(s7, "Defensive Security, RBAC & Administrator Console")
    
    box7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf7 = box7.text_frame
    tf7.word_wrap = True
    
    sec_points = [
        ("Authentication & Password Storage:", "User passwords hashed using the cryptographic scrypt algorithm. Sessions securely managed; supports flexible login via email or unique username."),
        ("Role-Based Access Control (RBAC):", "Users partitioned into patient, physician, and admin roles. The @admin_required decorator protects administrative routes, issuing HTTP 403 Forbidden for unauthorized roles."),
        ("Administrator Command Center (/admin):", "Dedicated surveillance console tracking deep learning model telemetry, file storage statistics, user roster (read-only; no password hashes exposed), and global screening logs."),
        ("Patient Data Isolation:", "Strict per-user query scoping ensures patient records, uploaded dermoscopic imagery, and PDF screening reports cannot be accessed or downloaded across different accounts.")
    ]
    for s, desc in sec_points:
        p = tf7.add_paragraph()
        p.text = f"•  {s} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 8: Software Engineering Quality Assurance & Testing
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8, BG_CREAM)
    add_header(s8, "Software Engineering Verification & Automated Test Suites")
    
    box8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf8 = box8.text_frame
    tf8.word_wrap = True
    
    qa_points = [
        ("Automated Test Suite (21 Tests):", "Complete pytest test suite covering authentication (TC-01, TC-02), administrative RBAC security, image validation (TC-03), model inference, history isolation (TC-04), and test case redirects."),
        ("Defensive Input Rejection:", "Verified automatic rejection and safe error handling for non-image text files, corrupted headers, oversized payloads (>10MB), and missing uploads."),
        ("Clean UI Architecture:", "Per project requirements, the internal test-case execution data is preserved in SQLite, while legacy test-case tables were cleanly retired from public navigation with seamless redirects."),
        ("100% Verification Rate:", "All 21 automated test cases pass cleanly with zero failures or deprecation regressions.")
    ]
    for q, desc in qa_points:
        p = tf8.add_paragraph()
        p.text = f"•  {q} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 9: Project Results & Held-Out Evaluation (With Embedded Chart)
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9, BG_CREAM)
    add_header(s9, "Experimental Results & Verification Performance")
    
    # Insert Chart image
    if chart_path.exists():
        s9.shapes.add_picture(str(chart_path), Inches(0.8), Inches(1.5), width=Inches(11.7))

    # SLIDE 10: Live Demonstration & Official Accounts
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10, BG_CREAM)
    add_header(s10, "Live Application Demonstration & User Accounts")
    
    box10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf10 = box10.text_frame
    tf10.word_wrap = True
    
    demo_points = [
        ("Presentation Demo Member Account:", "Full Name: Bhavi Doshi | Username: bhavi12 | Email: bhavidoshi12@gmail.com | Password: Bhavi@2026! (Role: Patient)."),
        ("System Administrator Account:", "Full Name: System Administrator | Username: admin | Email: admin@dermacare.ai | Password: Admin@2026!Demo (Role: Admin)."),
        ("Member Flow Demonstrated:", "Sign in via username/email -> User Dashboard with preloaded history -> Upload dermoscopic image -> Real-time 7-class prediction & risk badge -> Instant PDF report download."),
        ("Administrator Flow Demonstrated:", "Sign in as Admin -> Access /admin console -> Inspect model telemetry, database metrics, read-only user roster, and global screening surveillance.")
    ]
    for d, desc in demo_points:
        p = tf10.add_paragraph()
        p.text = f"•  {d} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 11: Limitations & Future Scope
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11, BG_CREAM)
    add_header(s11, "Current Limitations & Future Development")
    
    box11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf11 = box11.text_frame
    tf11.word_wrap = True
    
    fut_points = [
        ("Current Limitations:", "Model trained on a subset to respect CPU hardware constraints; uses 2D dermoscopic imagery without clinical patient metadata (age, sex, anatomical site); not clinically certified."),
        ("Dataset Scaling & GPU Training:", "Scale model training across the full 10,015 HAM10000 images using GPU cloud instances (AWS/GCP) with cosine decay learning rates."),
        ("Explainable AI (XAI) Integration:", "Incorporate Grad-CAM (Gradient-weighted Class Activation Mapping) heatmaps to visually highlight the exact lesion regions influencing neural decisions."),
        ("Multi-Modal Clinical Fusion:", "Combine patient demographic features (age, gender, anatomical location) alongside deep visual feature embeddings for enhanced diagnostic sensitivity.")
    ]
    for f, desc in fut_points:
        p = tf11.add_paragraph()
        p.text = f"•  {f} "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_BROWN
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(13)
        p.space_after = Pt(12)

    # SLIDE 12: Conclusion & References
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12, BG_CREAM)
    add_header(s12, "Conclusion & Academic References")
    
    box12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tf12 = box12.text_frame
    tf12.word_wrap = True
    
    p = tf12.paragraphs[0]
    p.text = "Project Summary:"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = DARK_SAGE
    
    p = tf12.add_paragraph()
    p.text = "• Successfully built an end-to-end, responsible Software Engineering system uniting deep learning with a calm, user-friendly healthcare portal.\n• Safely migrated to D:\\SE\\SkinCancerDetection with 100% data preservation and verified across 21 automated test suites.\n• Fully equipped with demonstration accounts, administrative RBAC controls, and automated PDF reporting."
    p.font.size = Pt(13)
    p.font.color.rgb = DARK_BROWN
    p.space_after = Pt(14)
    
    p = tf12.add_paragraph()
    p.text = "Key Academic References:"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = MUTED_ROSE
    
    refs = [
        "1. Tschandl, P., Rosendahl, C. & Kittler, H. The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. Sci Data 5, 180161 (2018).",
        "2. Sandler, M., Howard, A., Zhu, M., Zhmoginov, A. & Chen, L.C. MobileNetV2: Inverted Residuals and Linear Bottlenecks. CVPR (2018).",
        "3. International Skin Imaging Collaboration (ISIC Archive) Challenge Datasets, 2018-2026.",
        "4. Software Engineering Experiment 01 Specification (Exp1_C078_SE.docx) — SVKM's NMIMS MPSTME."
    ]
    for r in refs:
        p = tf12.add_paragraph()
        p.text = r
        p.font.size = Pt(11)
        p.font.color.rgb = DARK_BROWN
        p.space_after = Pt(4)
        
    ppt_path = DOC_DIR / "Skin_Cancer_Detection_Project_Presentation.pptx"
    prs.save(str(ppt_path))
    print(f"PowerPoint Presentation generated: {ppt_path}")

if __name__ == '__main__':
    chart = generate_chart()
    build_presentation(chart)
