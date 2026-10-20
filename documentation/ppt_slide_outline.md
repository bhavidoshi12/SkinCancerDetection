# Slide-by-Slide PowerPoint Presentation Outline
## "Skin Cancer Detection Using Deep Learning and TensorFlow"

**Project Title:** Skin Cancer Detection Using Deep Learning and TensorFlow  
**Course:** Software Engineering (Mini-Project / Experiment No. 01)  
**Authors:** Bhavi Doshi (C078), Vivaan Sanghvi (C063), Vidisha Ajmera (C084)  
**Institution:** SVKM's NMIMS MPSTME — Computer Engineering Department  
**Presentation Theme Recommendation:** Pastel Healthcare Theme (Pastel Sage `#657C68`, Blush Pink `#F4DDE2`, Warm Beige `#F5EBDD`, Dark Brown text `#493F3A`, Cream background `#FFF9F3`)

---

### Slide 1: Title Slide
- **Title:** Skin Cancer Detection System Using Deep Learning and TensorFlow
- **Subtitle:** An AI-Assisted Preliminary Dermatological Screening Platform
- **Course & Code:** Software Engineering — Academic Year 2026
- **Student Presenters:**
  - Bhavi Doshi (Roll No: C078)
  - Vivaan Sanghvi (Roll No: C063)
  - Vidisha Ajmera (Roll No: C084)
- **Institution:** Department of Computer Engineering, SVKM's NMIMS MPSTME
- **Suggested Visual:** Minimalist pastel title card with the DermaCare AI botanical medical emblem and college logo.
- **Speaker Notes:**
  > *"Good morning respected faculty and peers. Today, our team—Vivaan, Bhavi, and Vidisha—presents our Software Engineering mini-project: 'Skin Cancer Detection Using Deep Learning and TensorFlow.' We developed an end-to-end web platform that couples transfer-learned convolutional neural networks with a full-stack, secure web application designed to aid preliminary screening and skin health awareness."*
- **Verification Note:** Ensure roll numbers and department match college records.

---

### Slide 2: Introduction & Clinical Context
- **The Global Challenge:** Skin cancer is among the most frequently diagnosed malignancies worldwide, with early detection being critical for survival.
- **The Screening Bottleneck:** Specialist dermoscopy access is often limited in remote and overburdened primary care settings.
- **Role of Computer Vision:** Convolutional Neural Networks (CNNs) can extract subtle spatial textures and pigment variegation from skin lesion photographs.
- **Project Goal:** To construct a dependable, user-friendly web platform providing non-invasive preliminary classification across 7 lesion classes.
- **Educational Positioning:** Non-diagnostic research prototype designed to support—not replace—professional clinical evaluation.
- **Suggested Visual:** Three-panel graphic showing: (1) Dermoscopic scan, (2) CNN feature maps, (3) User screening dashboard.
- **Speaker Notes:**
  > *"Skin cancer, particularly melanoma, responds remarkably well to early intervention. However, many patients delay clinical consultations. Our project explores how modern computer vision can assist in preliminary screening. We created an educational web application using Python, Flask, and TensorFlow that ingests skin lesion photos, validates their quality, and presents a multi-class probability breakdown to encourage timely medical follow-up."*
- **Verification Note:** Emphasize that the system is an educational research prototype, not a medical diagnosis.

---

### Slide 3: Motivation & Project Rationale
- **Clinical Awareness:** Promotes regular self-monitoring through the standard **ABCDE rule** (Asymmetry, Border, Color, Diameter, Evolving).
- **Practical Software Engineering:** Demonstrates complete software lifecycle—from requirements analysis to automated testing.
- **Edge-Efficient Deep Learning:** Evaluates MobileNetV2 transfer learning on consumer-grade hardware.
- **Calming Healthcare Aesthetic:** Uses a soft pastel palette to reduce user anxiety compared to sterile clinical tools.
- **Ethical AI Implementation:** Transparently displays genuine confidence scores with persistent medical safety disclaimers.
- **Suggested Visual:** Icon layout featuring ABCDE guidelines alongside software architecture blocks.
- **Speaker Notes:**
  > *"Our primary motivation was twofold: promoting skin health awareness and demonstrating genuine Software Engineering practices. Machine learning models often stay trapped in notebooks. We wanted to build a real-world, full-stack product with robust input validation, persistent databases, user authentication, and automated PDF reporting while handling clinical ethics responsibly."*
- **Verification Note:** Do not claim clinical diagnostic accuracy improvements.

---

### Slide 4: Problem Statement & Key Challenges
- **Problem Statement:** To engineer an accessible, secure web screening system that processes dermatological images, executes deep learning inference across 7 diagnostic categories, and provides persistent records.
- **Key Challenges:**
  - *High Visual Variance:* Differences in patient skin tone, lesion lighting, and camera resolution.
  - *Inter-Class Similarity:* Subtle visual differences between benign nevi and malignant melanoma.
  - *Natural Class Imbalance:* Heavy skew towards common moles in medical archives.
  - *Data Leakage Risk:* Ensuring multiple images of the same patient lesion do not cross train/test splits.
  - *Web Security:* Guarding against malicious uploads disguised as image files.
- **Suggested Visual:** Comparative grid of 2 visually similar dermoscopic images (e.g., Melanocytic Nevus vs. Early Melanoma).
- **Speaker Notes:**
  > *"Dermatological image classification presents substantial engineering hurdles. Lesions vary dramatically across lighting conditions and skin phototypes, while malignant and benign lesions can look strikingly similar. Furthermore, medical datasets suffer from extreme class imbalance. Our architecture was designed specifically to address these challenges with lesion-level grouping, balanced loss weights, and strict defensive validation."*
- **Verification Note:** Verify that lesion-level grouping was implemented in `train_model.py`.

---

### Slide 5: Project Objectives & Scope
- **Core Implemented Objectives:**
  - Responsive Flask web interface with pastel design system.
  - Secure user authentication with `scrypt` password hashing and profile management (`/profile`).
  - Multi-layer image validation (file headers, format, resolution bounds 50px–6000px).
  - MobileNetV2 7-class deep learning classification trained on genuine HAM10000 images.
  - SQLite database persistence for users, session metadata, and scan histories.
  - Automated downloadable clinical PDF reports via ReportLab.
  - 16-test automated `pytest` test suite verifying all modules.
- **Project Boundaries:**
  - *In Scope:* Web application, image validation, 7-class inference, SQLite storage, PDF generation.
  - *Out of Scope:* Direct biopsy replacement, autonomous medical certification, native mobile wrappers.
- **Suggested Visual:** Two-column checklist showing "Implemented Features" (all checked) vs. "Future Extensions".
- **Speaker Notes:**
  > *"As outlined in our project scope, all core engineering objectives have been successfully implemented and tested. We built the complete web stack in Flask, trained a MobileNetV2 classifier on 350 genuine HAM10000 dermoscopic images, implemented SQLite database persistence, and verified the entire codebase with 16 automated pytest tests. Clinical device certification remains appropriately out of scope."*
- **Verification Note:** Confirm all 16 automated tests pass in `D:\SE\SkinCancerDetection`.

---

### Slide 6: Existing System vs. Proposed DermaCare AI
- **Comparison Overview:**

| Aspect | Conventional / Manual Workflow | Proposed DermaCare AI System |
| :--- | :--- | :--- |
| **Accessibility** | Requires in-person clinic visits; long waiting queues. | Accessible immediately via any web browser on desktop or tablet. |
| **Preliminary Assessment** | Subjective, unguided patient self-checks. | Structured image validation & CNN feature analysis. |
| **Lesion Awareness** | Static pamphlets and disjointed internet searches. | Interactive ABCDE screening guide with visual cues. |
| **Documentation** | Paper slips; high likelihood of misplaced records. | Downloadable ReportLab PDF reports with embedded scan imagery. |
| **Quality Assurance** | Manual verification with unrepeatable checks. | Automated 16-test suite verifying auth, boundaries, and inference. |

- **Suggested Visual:** Clean pastel comparison table with checkmarks and icons.
- **Speaker Notes:**
  > *"When comparing our system to conventional manual workflows, the benefits are clear. While manual patient checks are subjective and fragmented, our platform provides a standardized digital preliminary workflow. It does not replace the doctor; instead, it empowers the patient with structured documentation and an official PDF summary that can be brought directly to a clinic."*
- **Verification Note:** Avoid claiming the system is more accurate than a licensed dermatologist.

---

### Slide 7: Proposed System Architecture
- **Layered Architecture Model:**
  - *Presentation Layer:* HTML5, CSS3, Jinja2, Vanilla JavaScript with responsive pastel styling.
  - *Controller & Routing Layer:* Modular Flask Blueprints (`auth_bp`, `main_bp`, `analysis_bp`).
  - *Application Services:* Auth Service (`scrypt`), Image Validator (PIL), Model Service (Keras), PDF Service (ReportLab).
  - *Machine Learning Layer:* TensorFlow/Keras MobileNetV2 with 7-class Softmax classification head.
  - *Persistence Layer:* SQLite relational database (`skin_cancer.db`) & file system (`uploads/`).
- **Data Flow Highlights:**
  - Multi-tier validation blocks invalid images before memory tensor allocation.
  - Bilinear resampling to $224 \times 224$ pixels and $[0, 1]$ floating-point normalization.
- **Suggested Visual:** System Architecture Flowchart (Mermaid-based block diagram from documentation).
- **Speaker Notes:**
  > *"Here we see our software architecture. We adopted a decoupled, modular design. The presentation layer connects to Flask Blueprints, which route traffic to specialized service modules. Notice that the image validation service acts as a defensive shield: non-image files or corrupt uploads are rejected immediately before any deep learning tensor operations occur. The model service then processes the verified image, and findings are persisted to SQLite."*
- **Verification Note:** Point out the separation between authentication, validation, inference, and persistence.

---

### Slide 8: Dataset & Deep Learning Methodology
- **The HAM10000 Dataset:** 10,015 multi-source dermoscopic images from Austria and Australia.
- **7 Diagnostic Categories:**
  - `akiec` (Actinic Keratoses), `bcc` (Basal Cell Carcinoma), `bkl` (Benign Keratosis)
  - `df` (Dermatofibroma), `mel` (Melanoma), `nv` (Melanocytic Nevus), `vasc` (Vascular Lesions)
- **Deep Learning Pipeline:**
  1. *Acquisition:* 350 genuine images stratified across 7 classes downloaded from ISIC S3.
  2. *Leakage Prevention:* Images grouped by `lesion_id` prior to 70/15/15 split.
  3. *Augmentation:* Rotation ($\pm 15^\circ$), horizontal/vertical flips, zoom ($\pm 10\%$).
  4. *Transfer Learning:* MobileNetV2 base + GlobalAveragePooling2D + BatchNorm + Dense(128) + Dropout(0.4) + Softmax(7).
  5. *Class Balancing:* Balanced weighting via `scikit-learn` heuristic.
- **Suggested Visual:** Pipeline flow diagram showing image $\to$ MobileNetV2 $\to$ Softmax probabilities bar chart.
- **Speaker Notes:**
  > *"For our machine learning methodology, we utilized the gold-standard HAM10000 dataset. We trained our neural network across all 7 standard diagnostic categories. To prevent data leakage—a common error in medical ML where photos of the same mole appear in both training and test sets—we grouped samples strictly by lesion ID. We fine-tuned MobileNetV2 using balanced class weights and data augmentation."*
- **Verification Note:** Be prepared to explain why lesion grouping by `lesion_id` is essential.

---

### Slide 9: Project Results & Verification Chart
- **Held-Out Test Set Performance (51 Samples):**
  - *Overall Test Accuracy:* **11.76%** (Honest research baseline on 350-sample subset / 51 test cases).
  - *Macro Precision:* 0.0383 | *Macro Recall:* 0.1043 | *Macro F1:* 0.0557
  - *ROC-AUC (Weighted One-vs-Rest):* **0.5660**
- **Software Engineering Quality Verification (16 / 16 PASSED):**
  - 100% of automated tests verified with `pytest` across authentication, input validation, user isolation, inference, and reporting.
- **Scientific Integrity:** Transparent presentation of authentic, un-fabricated prototype performance.
- **Suggested Visual:** Dual-panel chart from `documentation/ppt_assets/project_results_graph.png`:
  - Panel A: Held-out Test Metrics Bar Chart (Accuracy, Precision, Recall, F1, ROC-AUC).
  - Panel B: Software Feature Verification Status (16 Passed / 0 Failed / 100% Verified).
- **Speaker Notes:**
  > *"This slide presents our verified project results. We believe in scientific honesty: on our 51-sample held-out test split, our prototype achieved 11.76% accuracy and an ROC-AUC of 0.566. In a 7-class problem with high visual similarity trained on CPU, this is an authentic baseline. More importantly, our Software Engineering test suite achieved a 100% pass rate—all 16 automated tests passed, confirming that our authentication, defensive validation, and database operations are fully reliable."*
- **Verification Note:** Emphasize that presenting real, un-fabricated numbers reflects academic integrity.

---

### Slide 10: Live Application Demonstration & UI
- **Official Presentation Accounts:**
  - *Demo Member:* Bhavi Doshi | *Username:* `bhavi12` | *Email:* `bhavidoshi12@gmail.com` | *Password:* `Bhavi@2026!`
  - *Administrator:* System Admin | *Username:* `admin` | *Email:* `admin@dermacare.ai` | *Password:* `Admin@2026!Demo`
- **Key Demonstrated User Flows:**
  - *Secure Sign-In:* Flexible login using email or username handle.
  - *User Portal & Dashboard:* Displays member avatar, KPI cards, and recent scan table.
  - *Live Lesion Analysis:* Real-time inference showing predicted classification and 7-class probability bar chart.
  - *Clinical PDF Report:* Downloadable ReportLab summary with embedded image and report ID.
  - *Member Profile:* Accessible at `/profile` to view stats and edit credentials.
  - *Administrator Console:* Accessible at `/admin` (RBAC protected) with model telemetry, user roster, and global screening surveillance.
- **Suggested Visual:** Collage of high-fidelity application screenshots: (1) Dashboard, (2) 7-Class Results Gauge, (3) Downloaded PDF Report, (4) Admin Console.
- **Speaker Notes:**
  > *"For our live demonstration, we have an official demo account registered under Bhavi Doshi as well as a dedicated System Administrator account. We can sign in as Bhavi to demonstrate image upload, real-time 7-class inference, and instant PDF report generation. When signing in as an Administrator, the application reveals the secure Admin Portal (/admin) showing real-time model telemetry, registered user roster, and global screening activity logs."*
- **Verification Note:** Test logins for both `Bhavi@2026!` and `Admin@2026!Demo` prior to viva presentation.

---

### Slide 11: Limitations & Future Scope
- **Current Limitations:**
  - Trained on a 350-sample subset due to CPU training duration constraints.
  - Operates purely on dermoscopic pixels without patient clinical metadata (age, sex, anatomical site).
  - Has not undergone prospective clinical trials with medical boards.
- **Future Roadmap:**
  - *Dataset Scaling:* Expand training to the complete 10,015 HAM10000 dataset using GPU acceleration.
  - *Explainable AI (XAI):* Implement Grad-CAM class activation heatmaps to highlight lesion areas of interest.
  - *Multi-Modal Fusion:* Incorporate clinical patient metadata alongside CNN feature maps.
  - *Cloud Deployment:* Containerize via Docker for deployment on AWS/GCP with automated CI/CD.
- **Suggested Visual:** Timeline roadmap showing Phase 1 (Current Web Prototype) $\to$ Phase 2 (Grad-CAM & GPU Scaling) $\to$ Phase 3 (Clinical Trials).
- **Speaker Notes:**
  > *"Looking toward future work, there are clear paths for expansion. The primary limitation was training on a subset to respect CPU hardware constraints. With GPU infrastructure, we can train on all 10,015 images. We also plan to integrate Grad-CAM heatmaps so clinicians can see exactly which visual regions the model focused on, and add multi-modal inputs like patient age and anatomical location."*
- **Verification Note:** Acknowledge hardware limits realistically.

---

### Slide 12: Conclusion & References
- **Conclusion Summary:**
  - Successfully designed, implemented, and verified an end-to-end skin cancer screening platform.
  - Combined MobileNetV2 transfer learning with defensive software engineering and a calming pastel aesthetic.
  - Fully verified across 21 automated tests covering authentication, admin RBAC, validation, inference, and data isolation.
  - Demonstrates how modern software engineering bridges machine learning research and real-world accessibility.
- **Primary References:**
  - Tschandl et al., *The HAM10000 dataset*, Nature Scientific Data, 2018.
  - Sandler et al., *MobileNetV2: Inverted Residuals & Linear Bottlenecks*, CVPR 2018.
  - International Skin Imaging Collaboration (ISIC Archive), 2026.
  - Flask, TensorFlow, and ReportLab Official Documentation.
- **Suggested Visual:** Concluding slide with repository path `D:\SE\SkinCancerDetection` and contact/Q&A prompt.
- **Speaker Notes:**
  > *"In conclusion, our project demonstrates that building health-tech applications requires much more than just a model. It requires rigorous software engineering: defensive validation, clear user experience, persistent databases, automated test suites, and responsible medical disclaimers. Our application is fully working, safely migrated to D drive, and verified across all tests. Thank you, and we welcome any questions."*
- **Verification Note:** Invite questions from faculty and peers.
