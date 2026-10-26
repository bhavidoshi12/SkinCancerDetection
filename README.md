# Skin Cancer Detection System Using Deep Learning and TensorFlow
### SVKM's NMIMS — Mukesh Patel School of Technology Management & Engineering
**Course:** Software Engineering (Experiment No. 01)  
**Project Group:** Vivaan Sanghvi (C063), Bhavi Doshi (C078), Vidisha Ajmera (C084)  
**Division / Batch:** Division C / Batch C1  

---

## 1. Project Overview

The **Skin Cancer Detection System** is an AI-assisted healthcare screening web application designed for early detection and educational analysis of dermatological lesions. The application allows users (patients, dermatologists, physicians, and students) to upload skin lesion photographs and receive preliminary classification findings with a model confidence score (when a genuine trained model is loaded) or an informative spatial inspection in safe demo mode.

### Core Objectives
- Provide fast, non-invasive, preliminary screening of skin lesions.
- Educate users on the **ABCDE rule** (Asymmetry, Border, Color, Diameter, Evolving) for melanoma awareness.
- Maintain clinical integrity: distinguish transparently between genuine deep learning model inference and safe educational simulation.
- Include a formal, interactive **Software Engineering Functional Test Case Specification** page (TC-01 to TC-04) with persistent SQLite database storage and CSV export for college lab evaluation.

---

## 2. Technology Stack

- **Backend:** Python 3, Flask, Werkzeug, SQLite
- **Computer Vision & Image Processing:** Pillow (PIL), NumPy, OpenCV
- **Deep Learning / Neural Networks:** TensorFlow & Keras (Convolutional Neural Network)
- **Dataset References:** HAM10000 (Harvard Dataverse) & ISIC (International Skin Imaging Collaboration)
- **Reporting Engine:** ReportLab (Clinical PDF screening reports with embedded imagery)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates
- **Testing Framework:** Pytest (Unit, boundary, integration, and security tests)

### Visual Design & Branding
Designed with a calming healthcare aesthetic using the specified pastel palette:
- **Pastel Blush Pink:** `#F4DDE2`
- **Warm Beige:** `#F5EBDD`
- **Pastel Sage Green:** `#DCE8D5`
- **Cream Background:** `#FFF9F3`
- **Muted Rose:** `#C98F9D`
- **Dark Sage:** `#657C68`
- **Dark Brown Text:** `#493F3A`
- **Pure White:** `#FFFFFF`

---

## 3. Project Directory Structure

```text
skin_cancer_detection/
├── app.py                      # Application entry point, error handlers & context
├── config.py                   # Configuration settings (file size, paths, session)
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables
├── .gitignore                  # Git exclusions for secrets, uploads & SQLite db
├── README.md                   # Complete documentation & startup guide
│
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite schema, user auth, analysis records & test cases
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # Password hashing (scrypt), validation & session guards
│   ├── model_service.py        # TensorFlow inference engine & safety-compliant demo mode
│   └── pdf_service.py          # ReportLab clinical screening PDF generator
│
├── blueprints/
│   ├── __init__.py
│   ├── auth_bp.py              # Routes for /register, /login, /logout
│   ├── main_bp.py              # Routes for /, /how-it-works, /skin-health
│   ├── analysis_bp.py          # Routes for /dashboard, /upload, /results, /history, /report
│   └── testing_bp.py           # Routes for /test-cases, /test-cases/save, /export-csv
│
├── templates/
│   ├── base.html               # Master layout with responsive nav & disclaimers
│   ├── index.html              # Landing page (hero, rationale, 3-step workflow)
│   ├── how_it_works.html       # Pipeline architecture & deep learning explanation
│   ├── skin_health.html        # Skin cancer education & interactive ABCDE rule
│   ├── dashboard.html          # User dashboard, KPI statistics & recent scans
│   ├── upload.html             # Drag-and-drop upload with live preview & validation
│   ├── results.html            # Prediction finding, confidence gauge & actions
│   ├── history.html            # Searchable and filterable history archive
│   ├── record_detail.html      # Individual scan details and metadata
│   ├── test_cases.html         # 10-column Software Engineering specification table
│   ├── auth/
│   │   ├── login.html          # Login form with show/hide password
│   │   └── register.html       # Registration with live password strength meter
│   └── errors/
│       ├── 400.html, 403.html, 404.html, 413.html, 500.html
│
├── static/
│   ├── css/style.css           # Custom pastel stylesheet, typography & print CSS
│   └── js/main.js              # Drag & drop upload, validation & test-case persistence
│
├── ml_models/
│   ├── README.md               # Model specifications (HAM10000 224x224 RGB CNN)
│   └── build_sample_model.py   # Script to export sample Keras CNN architecture
│
├── uploads/                    # Protected user lesion uploads (served with auth check)
│   └── .gitkeep
│
└── tests/
    ├── conftest.py             # Test fixtures with isolated temp database
    ├── test_auth.py            # TC-01 & TC-02 automated unit/integration tests
    ├── test_upload.py          # TC-03 file validation & rejection tests
    ├── test_history_and_report.py # TC-04 history, PDF generation & data isolation
    └── test_testcases.py       # Test case persistence & CSV export tests
```

---

## 4. Setup and Installation Instructions

Follow these simple steps in **Visual Studio Code** or your Windows terminal.

### Step 1: Open Terminal in Project Folder
Open VS Code, press `` Ctrl + ` `` to open the integrated terminal, and ensure you are in the project folder:
```powershell
cd "C:\Users\Bhavi Doshi\.gemini\antigravity\scratch\skin_cancer_detection"
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
- On Windows (PowerShell):
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell displays an execution policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the command again).*
- On Windows (Command Prompt):
  ```cmd
  venv\Scripts\activate.bat
  ```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 5. Starting the Application

Run the application entry point:
```powershell
python app.py
```
You will see output similar to:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 6. Pre-Registered Presentation & Demonstration Accounts

For academic viva, lab demonstrations, faculty evaluation, and testing synchronization between patient and administrative portals, three official pre-registered accounts are configured and seeded into SQLite:

### A. Patient Account 1: Bhavi Doshi
| Property | Details |
| :--- | :--- |
| **Full Name** | `Bhavi Doshi` |
| **Email Address** | `bhavidoshi12@gmail.com` |
| **Username** | `bhavi12` *(login supported via email or username)* |
| **Password** | `Bhavi@2026!` |
| **Role** | `patient` |
| **Medical Profile** | Fitzpatrick Type II, moderate sun exposure, self-reported mole concerns |
| **Dashboard** | View & update medical history, skin concerns, upload lesion scans, view PDF reports |

### B. Patient Account 2: Vidisha Ajmera
| Property | Details |
| :--- | :--- |
| **Full Name** | `Vidisha Ajmera` |
| **Email Address** | `vidisha.ajmera@dermacare.ai` |
| **Username** | `vidisha_ajmera` |
| **Password** | `Vidisha@2026!` |
| **Role** | `patient` |
| **Medical Profile** | Preloaded benchmark HAM10000 records transparently labelled as demo cases |
| **Dashboard** | Verified by Physician status, synchronized clinical admin notes |

### C. System Administrator Account (Command Center)
| Property | Details |
| :--- | :--- |
| **Full Name** | `System Administrator` |
| **Email Address** | `admin@dermacare.ai` |
| **Username** | `admin` |
| **Password** | `Admin@2026!Demo` |
| **Role** | `admin` |
| **Admin Portal** | Accessible at `/admin` (guarded by `@admin_required` server authorization) |
| **Capabilities** | Search patients by name/email/ID, view full patient details (`/admin/patient/<id>`), update verification status, write clinical notes, inspect uploaded lesions & PDF reports, view security audit trail, and export sanitized CSVs |

To re-seed or verify these demo accounts idempotently at any time without duplicating or overwriting user data:
```powershell
python seed_demo_user.py
```

---

## 7. Persistent Backend Database & Synchronized Patient Records

The application implements a persistent backend storage architecture in SQLite (`instance/skin_cancer.db`) inside the project folder. No temporary browser storage, session variables, or CSV files are used as the primary data store.

### Key Architectural Components
1. **Persistent SQLite Database (`instance/skin_cancer.db`):**
   - `users`: Core account identity, unique integer IDs, full name, email, username, scrypt password hashes, role, timestamps.
   - `patient_medical_profiles`: Separated patient medical information including voluntary medical history, active skin concerns & symptoms, allergies, sun exposure habits, Fitzpatrick skin phototype, family cancer history, contact phone, emergency contact, verification status, and clinical administrative notes.
   - `analysis_records`: Lesion screening submissions, original and unique filenames, relative file paths, model predictions, confidence scores, engine status, symptoms noted by patient, and PDF report paths.
   - `audit_logs`: Immutable security audit log tracking record modifications, actions, timestamps, and authorized administrator user IDs.
2. **Dedicated Persistent File Storage:**
   - `uploads/patient_images/`: Uploaded skin lesion photographs stored using unique safe identifiers (`user_{id}_{uuid}.{ext}`).
   - `uploads/reports/`: Permanent storage for generated ReportLab clinical screening PDF reports.
3. **Two-Way Patient & Admin Dashboard Synchronization:**
   - Both portals read directly from the exact same SQLite database tables.
   - When a patient updates their personal medical concerns or uploads an image, the administrator portal immediately displays the latest information upon search or reload.
   - When an administrator updates a patient's verification status or enters clinical notes, the patient's dashboard immediately updates upon subsequent load.
4. **Data Isolation & Role-Based Access Control:**
   - Server-side authorization ensures non-admin patients can strictly view and download only their own records, images, and reports (HTTP 403 Forbidden for cross-patient access).
   - Administrative endpoints (`/admin`, `/admin/patient/<id>`, `/admin/export-patients-csv`) strictly reject unauthorized or non-admin requests.
5. **Secure CSV Export with Formula Injection Defense:**
   - Administrators can export patient records to CSV (`/admin/export-patients-csv`).
   - Every cell is sanitized against spreadsheet formula injection (CWE-1236), prepending single quotes to values starting with `=`, `+`, `-`, `@`, `\t`, or `\r`.

---

## 7. Deep Learning Pipeline: Training & Evaluation

The system integrates a genuinely trained Convolutional Neural Network (CNN) based on **MobileNetV2** transfer learning on the **HAM10000** dermoscopic dataset.

### A. The 7 Diagnostic Classes (HAM10000 Scheme)
1. `akiec` — Actinic Keratoses and Intraepithelial Carcinoma (Pre-cancerous / Malignant)
2. `bcc` — Basal Cell Carcinoma (Malignant)
3. `bkl` — Benign Keratosis-like Lesions (Benign)
4. `df` — Dermatofibroma (Benign)
5. `mel` — Melanoma (Malignant)
6. `nv` — Melanocytic Nevi / Common Mole (Benign)
7. `vasc` — Vascular Lesions (Benign)

### B. Dataset Acquisition Pipeline
Run the automated downloader to retrieve genuine dermoscopic images and official metadata:
```powershell
python download_ham10000.py
```
- Fetches official `HAM10000_metadata.csv` (10,015 records).
- Downloads 350 genuine dermoscopic images from the official ISIC Archive S3 storage (stratified across all 7 diagnostic classes).
- Verifies image integrity and dimensions.

### C. Model Training Pipeline
Run the reproducible training script:
```powershell
python train_model.py
```
**Architecture & Pipeline Features:**
- **Base Architecture:** MobileNetV2 pre-trained on ImageNet.
- **Custom Classification Head:** GlobalAveragePooling2D $\to$ BatchNormalization $\to$ Dense(128, ReLU) $\to$ Dropout(0.4) $\to$ Dense(7, Softmax).
- **Data Leakage Prevention:** Groups images by `lesion_id` to guarantee that multiple images of the same patient lesion never span both training and testing splits.
- **Stratified Splits:** 70% Train, 15% Validation, 15% Held-out Test.
- **Class Balancing:** Computes balanced class weights via `scikit-learn` to combat natural dataset imbalance.
- **Data Augmentation:** Random horizontal/vertical flip, rotation ($\pm 15^\circ$), and zoom ($\pm 10\%$).
- **Checkpoints & Formats:** Saves `ml_models/skin_cancer_cnn_7class.keras` and backward-compatible `skin_cancer_model.h5`, along with `model_metadata.json` and loss/accuracy curves (`training_curves.png`).

### D. Model Evaluation & Authentic Test Metrics
Run the evaluation script on the held-out test split:
```powershell
python evaluate_model.py
```
*In accordance with academic integrity guidelines, metrics reflect authentic, genuine model performance without fabrication or exaggerated claims:*

| Metric | Held-Out Test Result (51 Samples) |
| :--- | :--- |
| **Evaluated Architecture** | MobileNetV2 (7-Class Softmax) |
| **Overall Test Accuracy** | **11.76%** |
| **Macro Precision** | 0.0383 |
| **Macro Recall (Sensitivity)** | 0.1043 |
| **Macro F1-Score** | 0.0557 |
| **Weighted F1-Score** | 0.0620 |
| **ROC-AUC (Weighted One-vs-Rest)** | **0.5660** |

*Detailed per-class metrics and confusion matrices are persisted to `ml_models/evaluation_report.json`.*

---

## 8. Software Engineering & Quality Assurance

### A. UI Architecture & Test-Case Section Retirement
Per updated project requirements:
- The public user-facing test-case page and its navigation links have been retired to present a clean, patient-centric healthcare interface.
- Visiting `/test-cases` gracefully redirects (HTTP 302) to the application Home page.
- Internal test case data and execution states are preserved intact inside the SQLite database (`test_cases` table) and programmatic CSV exports remain fully functional.

### B. Automated Test Suite (33 Tests — 100% Pass Rate)
Run the full automated test suite using `pytest` or by double-clicking `run_tests.bat`:
```powershell
python -m pytest -v
```
**Test Suite Verification: 33 / 33 PASSED (100%)**
- `test_patient_sync.py` (12 tests — Backend Persistence & Synchronization Verification):
  - `Scenario 01`: Patient registration persistence in SQLite database.
  - `Scenario 02`: Server restart simulation (data survives restart and fresh client sessions).
  - `Scenario 03`: Patient medical history, skin concerns, and risk factors saving & retrieval.
  - `Scenario 04`: Admin dashboard & patient detail views reflect patient-entered medical information.
  - `Scenario 05`: Admin updates to verification status and clinical notes immediately reflect on patient dashboard.
  - `Scenario 06`: Lesion image uploads saved to dedicated persistent directory (`uploads/patient_images/`) with symptoms noted.
  - `Scenario 07`: Prediction history and official PDF report generation and retrieval by authorized user.
  - `Scenario 08`: Cross-patient data isolation (Patient A cannot view or download Patient B's records, images, or PDFs — HTTP 403).
  - `Scenario 09`: Admin-only endpoints (`/admin`, `/admin/patient/<id>`, `/admin/export-patients-csv`) strictly blocked for non-admins (HTTP 403).
  - `Scenario 10`: Demo / educational benchmark simulation records clearly labelled separately from genuine deep learning inferences.
  - `Scenario 11`: Authorized admin CSV export sanitizes spreadsheet formula injection characters (`=`, `+`, `-`, `@`, `\t`, `\r` — CWE-1236).
  - `Scenario 12`: Application startup & database initialization idempotency (no schema corruption or data loss on restart).
- `test_auth.py` (4 tests):
  - `TC-01`: Registration, valid credentials login, dashboard redirection.
  - `TC-02`: Unregistered email blocking, wrong password rejection.
  - Session guards: Unauthenticated access rejection for `/dashboard`.
  - Username login, profile page view (`/profile`), and profile details update.
- `test_admin.py` (4 tests):
  - Unauthenticated access to `/admin` redirected to `/login`.
  - Authenticated non-admin accounts receive HTTP 403 Forbidden.
  - Authenticated admin accounts have full access to `/admin` telemetry, KPI cards, and user roster.
  - Navigation bar dynamically shows "Admin Portal" only to administrative users.
- `test_upload.py` (4 tests):
  - `TC-03`: Rejection of `.txt` documents, fake renamed images, missing files, and acceptance of valid image uploads.
- `test_history_and_report.py` (2 tests):
  - `TC-04`: Viewing history records, valid ReportLab PDF generation with embedded images, and user data isolation.
- `test_testcases.py` (4 tests):
  - Safe redirect for retired UI routes, SQLite execution persistence, and CSV export.
- `test_model_service.py` (3 tests):
  - Genuine TensorFlow model detection and loading.
  - 224x224 RGB image normalization, 7-class softmax output format, and probability consistency ($\sum p \approx 100\%$).
  - Strict image dimension and corruption boundary checking.

---

## 9. Academic Presentation & Documentation Assets

All academic presentation and documentation deliverables are located in `documentation/`:
- **`Skin_Cancer_Detection_Project_Presentation.pptx`**: 12-slide widescreen PowerPoint presentation formatted in the calming pastel palette with embedded high-resolution results chart.
- **`ppt_slide_outline.md`**: Complete slide-by-slide outline with detailed speaker notes, presentation tips, and verification checklists.
- **`project_overview_for_ppt.md`**: In-depth academic report covering sections A through O (Introduction, Architecture, Algorithms, Metrics, Security, Ethics).
- **`ppt_assets/project_results_graph.png`**: 300 DPI dual-panel publication graphic showing held-out evaluation metrics and 100% automated test verification.
- **`ppt_assets/held_out_metrics_summary.csv`**: Machine-readable summary of held-out test split evaluation.

---

## 10. Medical Disclaimer

> **IMPORTANT CLINICAL NOTICE:** This software application is developed as an academic college project for preliminary screening and educational exploration. It is **NOT** a clinical diagnostic medical device, medical certificate, or pathology service. Artificial intelligence models can produce false positive and false negative results. Users should never ignore or delay professional medical advice based on this platform. Always consult a licensed dermatologist or qualified physician for dermoscopic examination and biopsy.

